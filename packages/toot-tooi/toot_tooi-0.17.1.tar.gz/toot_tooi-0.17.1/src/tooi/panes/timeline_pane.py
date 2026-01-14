import asyncio

from textual import getters, work
from textual.binding import Binding
from textual.containers import Horizontal
from textual.widgets import TabPane

from tooi.app import TooiApp
from tooi.api.timeline import Timeline
from tooi.context import is_mine
from tooi.data import events, statuses
from tooi.data.events import Event
from tooi.entities import Status
from tooi.goto import GotoContextTimeline, GotoAccountTimeline
from tooi.http import APIError
from tooi.messages import EventHighlighted, GotoMessage, ShowAccount, ShowImages, StatusReply
from tooi.messages import EventMessage, StatusEdit
from tooi.messages import ShowSource, ShowStatusMenu
from tooi.widgets.dialog import DeleteStatusDialog
from tooi.widgets.event_detail import EventDetail
from tooi.widgets.event_list import EventList
from tooi.widgets.status_bar import StatusBar
from tooi.widgets.status_detail import StatusDetail


class TimelinePane(TabPane):
    """A tab pane that shows events from a timeline."""

    app = getters.app(TooiApp)

    BINDINGS = [
        Binding("a", "show_account", "Account"),
        Binding("u", "show_source", "Source"),
        Binding("t", "show_thread", "Thread"),
        Binding("p", "show_user_timeline", "User timeline"),
        Binding("m", "show_media", "View media"),
        Binding("e", "status_edit", "Edit"),
        Binding("r", "status_reply", "Reply"),
        Binding("f", "status_favourite", "(Un)Favourite"),
        Binding("b", "status_boost", "(Un)Boost"),
        Binding("d", "status_delete", "Delete"),
        Binding("v", "open_in_browser", "Open in Browser"),
        Binding("space,enter", "show_context_menu", "Context Menu", priority=True),
        Binding("left,h", "scroll_left", "Scroll Left", show=False),
        Binding("right,l", "scroll_right", "Scroll Right", show=False),
        Binding("s", "show_sensitive", "Show Sensitive", show=False),
        Binding("full_stop", "refresh_timeline", "Refresh timeline"),
    ]

    class EventUpdated(EventMessage):
        pass

    class EventDeleted(EventMessage):
        pass

    def __init__(
        self,
        timeline: Timeline,
        *,
        initial_focus: str | None = None,
        title: str | None = None,
    ):
        super().__init__(title or timeline.name)
        self.timeline = timeline
        self.generator = timeline.fetch()
        self.generator_exhausted = False
        self.fetching = False
        self.initial_focus = initial_focus

    @property
    def status_bar(self) -> StatusBar:
        return self.app.screen.query_one(StatusBar)

    @work
    async def on_mount(self):
        self.loading = True
        await self.fetch_timeline()

        if self.initial_focus:
            self.event_list.focus_event(self.initial_focus)

        # Start our background worker to load new statuses.  We start this even if the timeline
        # can't update, because it may have some other way to acquire new events.
        self.fetch_events()

        # Start the timeline periodic refresh, if configured.
        if self.timeline.can_update and self.app.options.timeline_refresh > 0:
            self.timeline.periodic_refresh(self.app.options.timeline_refresh)

        # Start streaming.
        if self.app.options.streaming and self.timeline.can_stream:
            await self.timeline.streaming(True)

    async def on_unmount(self):
        await self.timeline.close()

    def compose(self):
        yield Horizontal(EventList(), EventDetail())

    @property
    def event_list(self):
        return self.query_one(EventList)

    @property
    def event_detail(self):
        return self.query_one(EventDetail)

    @work(group="fetch_events")
    async def fetch_events(self):
        # Fetch new events from the timeline and post messages for them.
        while events := await self.timeline.get_events_wait():
            self.event_list.prepend_events(events)
            self.query_one(EventList).refresh_events()

    async def refresh_timeline(self):
        # Handle timelines that don't support updating.
        if not self.timeline.can_update:
            await self.fetch_timeline()
        else:
            # This returns immediately; any updates will be handled by fetch_events.
            await self.timeline.update()

    async def fetch_timeline(self):
        try:
            events = await anext(self.generator)
            self.event_list.replace(events)
        except StopAsyncIteration:
            self.generator_exhausted = True
            self.event_list.replace([])  # No statuses
        except APIError as ex:
            self.app.show_error_modal("Could not load timeline", ex=ex)
        finally:
            self.loading = False

    def on_event_highlighted(self, message: EventHighlighted):
        # Update event details only if focused event has changed
        current_event = self.event_detail.event
        if not current_event or current_event.id != message.event.id:
            self.show_event_detail(message.event)

    @work(exclusive=True, group="show_event_detail")
    async def show_event_detail(self, event: Event):
        # Having a short sleep here allows for smooth scrolling. Since `@work`
        # has `exclusive=True` this task will be canceled if it is called again
        # before the current one finishes. When scrolling down the event list
        # quickly, this happens before the sleep ends so the status is not
        # drawn at all until we stop scrolling.
        await asyncio.sleep(0.05)

        self.event_detail.event = event
        asyncio.create_task(self.maybe_fetch_next_batch())

    def update_event(self, event: Event):
        self.event_list.update_event(event)
        self.event_detail.event = event

    def remove_event(self, event: Event):
        self.event_list.remove_event(event)

    def action_show_context_menu(self):
        event = self.event_detail.event
        if event and event.status:
            self.post_message(ShowStatusMenu(event.status))

    @work
    async def action_status_favourite(self):
        if (event := self.event_list.current) and event.status is not None:
            assert event.status is not None
            original = event.status.original

            if original.favourited:
                await self._unfavourite(original.id)
            else:
                await self._favourite(original.id)

            await self._post_event_update(event)

    async def _favourite(self, status_id: str):
        async with self.status_bar.run_with_progress(
            progress="Favouriting...",
            success="✓ Status favourited",
            error="Failed favouriting status",
        ):
            await statuses.favourite(status_id)

    async def _unfavourite(self, status_id: str):
        async with self.status_bar.run_with_progress(
            progress="Unfavouriteing...",
            success="✓ Status unfavouriteed",
            error="Failed unfavouriting status",
        ):
            await statuses.unfavourite(status_id)

    @work
    async def action_status_boost(self):
        if (event := self.event_list.current) and event.status is not None:
            assert event.status is not None
            original = event.status.original

            if original.reblogged:
                await self._unboost(original.id)
            else:
                await self._boost(original.id)

            await self._post_event_update(event)

    async def _boost(self, status_id: str):
        async with self.status_bar.run_with_progress(
            progress="Boosting...",
            success="✓ Status boosted",
            error="Failed boosting status",
        ):
            await statuses.boost(status_id)

    async def _unboost(self, status_id: str):
        async with self.status_bar.run_with_progress(
            progress="Unboosting...",
            success="✓ Status unboosted",
            error="Failed unboosting status",
        ):
            await statuses.unboost(status_id)

    # TODO: this is crap because Mastodon tends to lag and will return the old
    # event data post boost/favourite unless we wait a bit. A better approach
    # might be to stream and apply updates to statuses?
    async def _post_event_update(self, event: Event):
        # NB: It might be possible to avoid having to reload the event, but it's
        # way more complicated than it seems at first. For an attempt, which
        # doesn't event work with notification events, see here:
        # https://paste.sr.ht/~ihabunek/f160e10528f71ed3eef67dbe8c74cb569dc62c9f
        updated_event = await events.reload(event)
        self.post_message(self.EventUpdated(updated_event))

    @work
    async def action_status_delete(self):
        if (event := self.event_list.current) and (status := event.status) and is_mine(status):
            deleted = await self.app.push_screen_wait(DeleteStatusDialog(status))
            if deleted:
                # TODO: select next event in list?
                self.event_detail.event = None
                self.post_message(self.EventDeleted(event))

    def action_open_in_browser(self):
        if (status := self._current_status()) and status.original.url:
            self.app.open_url(status.original.url)

    def action_show_sensitive(self):
        for sd in self.event_detail.query(StatusDetail):
            sd.reveal()

    def action_show_account(self):
        if status := self._current_status():
            self.post_message(ShowAccount(status.original.account))

    def action_show_source(self):
        if status := self._current_status():
            self.post_message(ShowSource(status))

    def action_show_thread(self):
        if status := self._current_status():
            self.post_message(GotoMessage(GotoContextTimeline(status)))

    def action_show_user_timeline(self):
        if status := self._current_status():
            self.post_message(GotoMessage(GotoAccountTimeline(status.original.account)))

    async def action_status_edit(self):
        if status := self._current_status():
            source = await statuses.source(status.original.id)
            self.post_message(StatusEdit(status.original, source))

    def action_status_reply(self):
        if status := self._current_status():
            self.post_message(StatusReply(status))

    def action_scroll_left(self):
        self.event_list.focus()

    def action_scroll_right(self):
        self.event_detail.focus()

    def action_show_media(self):
        if status := self._current_status():
            media_attachments = [m for m in status.original.media_attachments if m.type == "image"]
            if media_attachments:
                self.post_message(ShowImages(media_attachments))

    async def action_refresh_timeline(self):
        await self.refresh_timeline()

    async def maybe_fetch_next_batch(self):
        if self.should_fetch():
            self.fetching = True
            async with self.status_bar.run_with_progress("Loading statuses..."):
                try:
                    next_events = await anext(self.generator)
                    self.event_list.append_events(next_events)
                except StopAsyncIteration:
                    self.generator_exhausted = True
            self.fetching = False

    def should_fetch(self):
        if not self.generator_exhausted and not self.fetching and self.event_list.index is not None:
            diff = self.event_list.count - self.event_list.index
            return diff < 10

    def _current_status(self) -> Status | None:
        if event := self.event_list.current:
            return event.status

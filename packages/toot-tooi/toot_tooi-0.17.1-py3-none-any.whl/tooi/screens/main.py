from functools import cached_property

from textual import getters, on, work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import Footer, TabbedContent, TabPane

from tooi import goto, messages
from tooi.api import timeline
from tooi.api.timeline import Timeline
from tooi.app import TooiApp
from tooi.context import account_name
from tooi.data.instance import InstanceInfo
from tooi.entities import Account, Status
from tooi.panes.conversations_pane import ConversationsPane
from tooi.panes.search_pane import SearchPane
from tooi.panes.timeline_pane import TimelinePane
from tooi.screens.account import AccountScreen
from tooi.screens.compose import ComposeScreen
from tooi.screens.goto_screen import GotoScreen
from tooi.screens.instance import InstanceScreen
from tooi.screens.source import SourceScreen
from tooi.screens.status_context import StatusMenuScreen
from tooi.widgets.header import Header
from tooi.widgets.status_bar import StatusBar


class MainScreen(Screen[None]):
    """
    The primary app screen, which contains tabs for content.
    """

    app = getters.app(TooiApp)

    DEFAULT_CSS = """
    MainScreen {
        StatusBar {
            height: 2; /* prevent overlap with Footer */
        }
    }
    """

    BINDINGS = [
        Binding("c", "compose", "Compose"),
        Binding("g", "goto", "Goto"),
        Binding("i", "show_instance", "Show Instance"),
        Binding("ctrl+d,ctrl+w", "close_current_tab", "Close tab"),
        Binding("ctrl+pageup", "previous_tab", "Previous tab"),
        Binding("ctrl+pagedown", "next_tab", "Next tab"),
        Binding("/", "open_search_tab", "Search"),
        Binding("1", "select_tab(1)", "Select tab #1", show=False),
        Binding("2", "select_tab(2)", "Select tab #2", show=False),
        Binding("3", "select_tab(3)", "Select tab #3", show=False),
        Binding("4", "select_tab(4)", "Select tab #4", show=False),
        Binding("5", "select_tab(5)", "Select tab #5", show=False),
        Binding("6", "select_tab(6)", "Select tab #6", show=False),
        Binding("7", "select_tab(7)", "Select tab #7", show=False),
        Binding("8", "select_tab(8)", "Select tab #8", show=False),
        Binding("9", "select_tab(9)", "Select tab #9", show=False),
        Binding("0", "select_tab(10)", "Select tab #10", show=False),
    ]

    def __init__(self, instance: InstanceInfo, account: Account):
        super().__init__()
        self.instance = instance
        self.account = account

    def compose(self) -> ComposeResult:
        yield Header("tooi")
        with TabbedContent():
            yield TimelinePane(timeline.HomeTimeline(self.instance))
        yield StatusBar()
        yield Footer()

    @cached_property
    def tabs(self):
        return self.query_one(TabbedContent)

    # --- Actions --------------------------------------------------------------

    def action_compose(self):
        self.app.push_screen(ComposeScreen(self.instance))

    def action_goto(self):
        self._open_goto_screen()

    async def action_open_search_tab(self):
        await self._open_pane(SearchPane("Search"))

    def action_show_instance(self):
        self.app.push_screen(InstanceScreen(self.instance))

    def action_select_tab(self, index: int):
        self._activate_tab(index)

    def action_previous_tab(self):
        self._change_active_index(-1)

    def action_next_tab(self):
        self._change_active_index(+1)

    async def action_close_current_tab(self):
        await self._close_current_tab()

    # --- Message handlers -----------------------------------------------------

    @on(TabbedContent.TabActivated)
    def on_tab_activated(self, message: TabbedContent.TabActivated):
        tab_pane = self.tabs.get_pane(message.tab)
        if isinstance(tab_pane, TimelinePane):
            tab_pane.event_list.focus()

    @on(TimelinePane.EventUpdated)
    def on_event_updated(self, message: TimelinePane.EventUpdated):
        for tab in self.query(TimelinePane):
            tab.update_event(message.event)

    @on(TimelinePane.EventDeleted)
    def on_event_deleted(self, message: TimelinePane.EventDeleted):
        for tab in self.query(TimelinePane):
            tab.remove_event(message.event)

    @on(messages.GotoMessage)
    def on_goto(self, message: messages.GotoMessage):
        self._handle_goto(message.where)

    @on(messages.StatusEdit)
    def on_status_edit(self, message: messages.StatusEdit):
        if message.status.account.acct == self.account.acct:
            self.app.push_screen(
                ComposeScreen(
                    self.instance,
                    edit=message.status,
                    edit_source=message.status_source,
                )
            )

    @on(messages.StatusReply)
    def on_status_reply(self, message: messages.StatusReply):
        self.app.push_screen(ComposeScreen(self.instance, message.status))

    @on(messages.ShowAccount)
    def on_show_account(self, message: messages.ShowAccount):
        self._open_account_screen(message.account)

    @on(messages.ShowSource)
    def on_show_source(self, message: messages.ShowSource):
        self.app.push_screen(SourceScreen(message.status))

    @on(messages.ShowStatusMenu)
    def on_show_status_menu(self, message: messages.ShowStatusMenu):
        self._open_status_context_screen(message.status)

    # --- Internals ------------------------------------------------------------

    async def _open_pane(self, pane: TabPane):
        async with self.batch():
            await self.tabs.add_pane(pane)
            assert pane.id is not None
            self.tabs.active = pane.id

    async def _open_timeline(self, timeline: Timeline, initial_focus: str | None = None):
        await self._open_pane(TimelinePane(timeline, initial_focus=initial_focus))

    async def _open_account_timeline(self, account: Account):
        title = account_name(account.acct)
        await self._open_timeline(timeline.AccountTimeline(self.instance, title, account.id))

    async def _open_context_timeline(self, status: Status):
        # TODO: composing a status: event id by hand is probably not ideal.
        event_id = f"status-{status.id}"
        tl = timeline.ContextTimeline(self.instance, status.original.id)
        await self._open_timeline(tl, initial_focus=event_id)

    @work
    async def _open_account_screen(self, account: Account):
        self.app.close_modals()
        if message := await self.app.push_screen_wait(AccountScreen(account)):
            self.post_message(message)

    @work
    async def _open_status_context_screen(self, status: Status):
        self.app.close_modals()
        if message := await self.app.push_screen_wait(StatusMenuScreen(status)):
            self.post_message(message)

    @work
    async def _open_goto_screen(self):
        where = await self.app.push_screen_wait(GotoScreen())
        if where:
            self._handle_goto(where)

    @work
    async def _handle_goto(self, where: goto.Goto):
        match where:
            case goto.GotoHomeTimeline():
                await self._open_timeline(timeline.HomeTimeline(self.instance))
            case goto.GotoPersonalTimeline():
                await self._open_account_timeline(self.account)
            case goto.GotoLocalTimeline():
                await self._open_timeline(timeline.LocalTimeline(self.instance))
            case goto.GotoFederatedTimeline():
                await self._open_timeline(timeline.FederatedTimeline(self.instance))
            case goto.GotoHashtagTimeline():
                await self._open_timeline(timeline.TagTimeline(self.instance, where.tag))
            case goto.GotoNotifications():
                await self._open_timeline(timeline.NotificationTimeline(self.instance))
            case goto.GotoConversations():
                await self._open_pane(ConversationsPane())
            case goto.GotoAccountTimeline():
                await self._open_account_timeline(where.account)
            case goto.GotoContextTimeline():
                await self._open_context_timeline(where.status)
            case _:
                pass

    def _activate_tab(self, index: int):
        tabs = self.tabs.query(TabPane)
        if index <= len(tabs):
            with self.app.batch_update():
                tab = tabs[index - 1]
                if tab.id is not None:
                    self.tabs.active = tab.id

    def _change_active_index(self, delta: int):
        panes = self.tabs.query(TabPane).nodes
        if len(panes) < 2:
            return

        active_index = self._get_active_pane_index(panes)
        if active_index is None:
            return

        index = (active_index + delta) % len(panes)
        pane = panes[index]
        if pane.id is not None:
            self.tabs.active = pane.id

    def _get_active_pane_index(self, panes: list[TabPane]) -> int | None:
        for index, pane in enumerate(panes):
            if pane.id == self.tabs.active:
                return index

    async def _close_current_tab(self):
        # Don't close last tab
        if self.tabs.tab_count > 1:
            await self.tabs.remove_pane(self.tabs.active)

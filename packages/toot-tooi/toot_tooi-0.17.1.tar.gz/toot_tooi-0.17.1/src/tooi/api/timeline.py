"""
Timelines API
https://docs.joinmastodon.org/methods/timelines/
"""
import asyncio
import logging
import re
from abc import ABC, abstractmethod
from typing import AsyncGenerator, Dict, Mapping, Optional, Sequence, Union
from urllib.parse import quote, urlparse

from tooi.api import statuses
from tooi.api.streaming import StreamSubscription
from tooi.asyncio import AsyncAtomic, AsyncWorker, run_async_task
from tooi.data import accounts
from tooi.data.events import Event, NotificationEvent, StatusEvent
from tooi.data.instance import InstanceInfo
from tooi.entities import Context, Notification, Status
from tooi.http import request
from tooi.utils.from_dict import from_dict, from_dict_list, from_response
from tooi.utils.string import str_bool

EventGenerator = AsyncGenerator[Sequence[Event], None]
PrimitiveData = Optional[Union[str, int, float, bool]]
QueryParams = Dict[str, Union[str, int]]


# Max 80, as of Mastodon 4.1.0
DEFAULT_LIMIT = 40
logger = logging.getLogger(__name__)


def _get_next_path(headers: Mapping[str, str]) -> str | None:
    """Given timeline response headers, returns the path to the next batch"""
    links = headers.get("Link", "")
    matches = re.match(r'<([^>]+)>; rel="next"', links)
    if matches:
        parsed = urlparse(matches.group(1))
        return "?".join([parsed.path, parsed.query])
    return None


async def fetch_timeline(
    path: str,
    params: QueryParams | None = None,
    limit: int | None = None,
    since_id: str | None = None
):
    _params: QueryParams = params or {}
    _params["limit"] = limit or DEFAULT_LIMIT
    if since_id:
        _params["since_id"] = since_id

    next_path = path
    while next_path:
        response = await request("GET", next_path, params=_params)
        events = await response.json()

        if len(events) == 0:
            next_path = None
        else:
            yield events
            next_path = _get_next_path(response.headers)


class Timeline(ABC):
    """
    Base class for a timeline.  A timeline generates Events, which can be retrieved via its fetch()
    or fetch_wait() methods.  The type of events the timeline generates depends on which subclass is
    instantiated.
    """

    # How many events to queue at once before attempts to queue more events start to block.
    # 128 should be a reasonable amount to allow a large timeline refresh to queue fully
    # without blocking.  Increasing this doesn't significantly affect memory usage, because these
    # events will be turned into timeline events anyway, but it may cause the timeline to be updated
    # slower if many events being added block get_events().  This may need to be tuned later or
    # perhaps removed entirely (set to zero).
    QUEUE_SIZE = 128

    def __init__(self,
                 name: str,
                 instance: InstanceInfo,
                 can_update: bool = False,
                 can_stream: bool = False):
        self.instance = instance
        self.name = name
        self.can_update = can_update
        self.can_stream = can_stream
        self._update_running = AsyncAtomic[bool](False)
        self._update_task = None
        self._periodic_refresh_task = None
        self._queue: asyncio.Queue[Event] = asyncio.Queue(maxsize=self.QUEUE_SIZE)

    def _assert_can_update(self):
        if not self.can_update:
            raise (NotImplementedError("this Timeline cannot update"))

    async def close(self):
        if update_task := self._update_task:
            update_task.cancel()

        if periodic_refresh_task := self._periodic_refresh_task:
            periodic_refresh_task.cancel()

    async def update(self):
        self._assert_can_update()
        await self._interlocked_update()

    def periodic_refresh(self, frequency: int):
        self._assert_can_update()
        self._periodic_refresh_task = run_async_task(self._periodic_refresh(frequency))

    def streaming(self, enable: bool):
        raise NotImplementedError("this Timeline cannot stream")

    async def _periodic_refresh(self, frequency: int):
        while True:
            await asyncio.sleep(frequency)
            await self._interlocked_update()

    async def get_events(self) -> list[Event]:
        """
        Return a list of pending events which have been queued to the timeline since the last time
        get_events() or get_events_wait() were called.  This function always returns immediately.
        If no events are available, an empty list will be returned.
        """
        events: list[Event] = []

        while True:
            try:
                event = self._queue.get_nowait()
                self._queue.task_done()
            except asyncio.QueueEmpty:
                return events

            events.append(event)

    async def get_events_wait(self) -> list[Event]:
        """
        Return a list of pending events which have been queued to the timeline since the last time
        get_events() or get_events_wait() were called.  If no events are available, wait until at
        least one event is available.
        """

        # Wait for the first event.
        event = await self._queue.get()
        self._queue.task_done()

        # We got at least one event, fetch any more that happen to be pending.
        events = [event] + await self.get_events()

        return events

    async def _dispatch(self, event: Event):
        """
        Push a new event into the queue.  This will block if the queue is full.
        """
        await self._queue.put(event)

    async def _interlocked_update(self):
        async def _run_update():
            try:
                await self._update()
            finally:
                self._update_task = None
                await self._update_running.set(False)

        if await self._update_running.compare_and_swap(False, True) is True:
            # Update is already running.
            return

        self._update_task = run_async_task(_run_update())

    async def _update(self) -> None:
        """
        This function is called to instruct the timeline implementation to fetch
        more events and dispatch them.  This function will be called in a
        separate runner, so it's fine to await here without blocking the UI.
        """
        raise (NotImplementedError("this Timeline cannot update"))

    @abstractmethod
    async def fetch(self, limit: int | None = None) -> EventGenerator:
        """
        This is the non-queue-based fetch function which is used when fetching
        the initial timeline.
        """
        ...


class StatusTimeline(Timeline):
    """
    StatusTimeline is the base class for timelines which only return statuses.
    """

    def __init__(
            self,
            name: str,
            instance: InstanceInfo,
            path: str,
            params: QueryParams | None = None,
            stream_name: str | None = None):

        super().__init__(name, instance, can_update=True, can_stream=(stream_name is not None))
        self.path = path
        self.params = params
        self._stream_name: str | None = stream_name
        self._subscription: StreamSubscription | None = None
        self._most_recent_id: str | None = None
        self._streaming_task: AsyncWorker | None = None
        self._seen_events: set[str] = set()
        # _lock protects self._seen_events
        self._lock = asyncio.Lock()

    async def close(self):
        async with self._lock:
            if self._streaming_task is not None:
                self._streaming_task.cancel()
                self._streaming_task = None

            if self._subscription is not None:
                await self._subscription.close()
                self._subscription = None

        await super().close()

    async def fetch(self, limit: int | None = None) -> EventGenerator:
        async for eventlist in fetch_timeline(self.path, self.params, limit):
            events = [StatusEvent(from_dict(Status, s)) for s in eventlist]

            # Track the most recent id we've fetched, which will be the first, for update().
            if self._most_recent_id is None and len(events) > 0:
                self._most_recent_id = events[0].status.id

            yield events

    async def _update(self):
        # Fetch all the events before taking the lock
        events: list[Event] = []
        generator = fetch_timeline(self.path, params=self.params, since_id=self._most_recent_id)
        async for eventlist in generator:
            events += [StatusEvent(from_dict(Status, s)) for s in eventlist]

        # Use the first (most recent) event id for _most_recent_id.
        if len(events) > 0:
            self._most_recent_id = events[0].status.id

        # We need the events in chronological order.
        events.reverse()

        new_events: set[str] = set()

        async with self._lock:
            for event in events:
                # Skip any events we already handled via streaming.
                if event.id not in self._seen_events:
                    await self._dispatch(event)

                # Indicate we saw this event in case it turns up on the stream too.
                new_events.add(event.id)

            # Reset the seen events cache for the next fetch.
            self._seen_events = new_events

    async def streaming(self, enable):
        if enable:
            async with self._lock:
                self._subscription = await self.instance.streamer.subscribe(self._stream_name)
                self._streaming_task = run_async_task(self._stream())
        else:
            pass

    async def _stream(self):
        while True:
            sevt = await self._subscription.get()

            async with self._lock:
                match sevt.event:
                    case "update":
                        event = StatusEvent(from_dict(Status, sevt.payload))

                        # If we already saw this event, ignore it.
                        if event.id not in self._seen_events:
                            # Otherwise mark it as seen for _update().
                            self._seen_events.add(event.id)
                            await self._dispatch(event)

                    case _:
                        logger.info(f"StatusTimeline: no use for event type {sevt.event}")


class HomeTimeline(StatusTimeline):
    """
    HomeTimeline loads events from the user's home timeline.
    This timeline only ever returns events of type StatusEvent.
    """

    def __init__(self, instance: InstanceInfo):
        super().__init__(
                "Home",
                instance,
                "/api/v1/timelines/home",
                stream_name=StreamSubscription.USER)


class PublicTimeline(StatusTimeline):
    """PublicTimeline loads events from the public timeline."""
    def __init__(
            self,
            name: str,
            instance: InstanceInfo,
            local: bool,
            stream_name: str | None = None):

        super().__init__(
                name,
                instance,
                "/api/v1/timelines/public",
                {"local": str_bool(local)},
                stream_name=stream_name)

        self.local = local


class LocalTimeline(PublicTimeline):
    """
    LocalTimeline loads events from the user's local instance timeline.
    This timeline only ever returns events of type StatusEvent.
    """
    def __init__(self, instance: InstanceInfo):
        super().__init__("Local", instance, True, stream_name=StreamSubscription.PUBLIC_LOCAL)


class FederatedTimeline(PublicTimeline):
    """
    FederatedTimeline loads events from the user's federated timeline.
    This timeline only ever returns events of type StatusEvent.
    """
    def __init__(self, instance: InstanceInfo):
        super().__init__("Federated", instance, False, stream_name=StreamSubscription.PUBLIC_REMOTE)


class AccountTimeline(StatusTimeline):
    """
    AccountTimeline loads events from the given account's timeline.
    This timeline only ever returns events of type StatusEvent.
    This requires the account id; to fetch based on a username use AccountTimeline.from_name.
    """
    def __init__(self,
                 instance: InstanceInfo,
                 title: str,
                 account_id: str,
                 replies: bool = True,
                 reblogs: bool = True):

        self.account_id = account_id
        self.replies = replies
        self.reblogs = reblogs

        super().__init__(
                title,
                instance,
                f"/api/v1/accounts/{self.account_id}/statuses",
                {
                    "exclude_replies": str_bool(not self.replies),
                    "exclude_reblogs": str_bool(not self.reblogs)
                })

    @staticmethod
    async def from_name(
            instance: InstanceInfo,
            account_name: str,
            replies: bool = True,
            reblogs: bool = True):
        account = await accounts.lookup(account_name)
        return AccountTimeline(instance, account_name, account.id, replies, reblogs)


class NotificationTimeline(Timeline):
    """
    NotificationTimeline loads events from the user's notifications.
    https://docs.joinmastodon.org/methods/notifications/
    """

    def __init__(self, instance: InstanceInfo):
        super().__init__("Notifications", instance, can_update=True, can_stream=True)
        self._most_recent_id: str | None = None
        self._streaming_task = None
        self._subscription: StreamSubscription | None = None
        self._seen_events: set[str] = set()
        # _lock protects self._seen_events
        self._lock = asyncio.Lock()

    async def close(self):
        async with self._lock:
            if self._streaming_task is not None:
                self._streaming_task.cancel()
                self._streaming_task = None

            if self._subscription is not None:
                await self._subscription.close()
                self._subscription = None

        await super().close()

    async def fetch(self, limit: int | None = None) -> EventGenerator:
        path = "/api/v1/notifications"
        async for items in fetch_timeline(path, limit=limit):
            notifications = from_dict_list(Notification, items)
            events = [NotificationEvent(n) for n in notifications]

            # Track the most recent id we've fetched, which will be the first, for update().
            if self._most_recent_id is None and len(events) > 0:
                self._most_recent_id = events[0].notification.id

            yield events

    async def _update(self, limit: int | None = None):
        # Fetch all the events before taking the lock
        path = "/api/v1/notifications"
        events: list[Event] = []

        async for items in fetch_timeline(path, limit=limit, since_id=self._most_recent_id):
            notifications = from_dict_list(Notification, items)
            events += [NotificationEvent(n) for n in notifications]

        # Use the first (most recent) event id for _most_recent_id.
        if len(events) > 0:
            self._most_recent_id = events[0].status.id

        # We need the events in chronological order.
        events.reverse()

        async with self._lock:
            for event in events:
                # Skip any events we already handled via streaming.
                if event.id not in self._seen_events:
                    await self._dispatch(event)

            # Clear the seen events cache for the next fetch.
            self._seen_events.clear()

    async def streaming(self, enable):
        if enable:
            async with self._lock:
                self._subscription = await self.instance.streamer.subscribe(
                        StreamSubscription.USER)
                self._streaming_task = run_async_task(self._stream())
        else:
            pass

    async def _stream(self):
        assert self._subscription
        while True:
            sevt = await self._subscription.get()

            async with self._lock:
                match sevt.event:
                    case "update" | "delete" | "status.update":
                        # Ignore events handled by other timelines.
                        pass

                    case "notification":
                        event = NotificationEvent(from_dict(Notification, sevt.payload))
                        # Track the events we've seen from streaming; these will be discarded in the
                        # next fetch(), to avoid generating duplicate events.
                        self._seen_events.add(event.id)
                        await self._dispatch(event)

                    case _:
                        logger.info(f"NotificationTimeline: no use for event type {sevt.event}")


class TagTimeline(StatusTimeline):
    """
    TagTimeline loads events from the given hashtag.
    This timeline only ever returns events of type StatusEvent.
    """
    def __init__(
            self,
            instance: InstanceInfo,
            hashtag: str,
            local: bool = False,
            remote: bool = False):

        self.local = local

        # Normalise the hashtag to not begin with a hash
        if hashtag[0:1] == '#':
            hashtag = hashtag[1:]

        if len(hashtag) == 0:
            raise (ValueError("TagTimeline: tag is empty"))

        self.hashtag = hashtag

        super().__init__(
                f"#{self.hashtag}",
                instance,
                f"/api/v1/timelines/tag/{quote(self.hashtag)}",
                params={
                    "local": str_bool(local),
                    "remote": str_bool(remote),
                })


class ContextTimeline(Timeline):
    """
    TagTimeline loads events from the thread the given status is part of.
    This timeline only ever returns events of type StatusEvent.
    """
    def __init__(self, instance: InstanceInfo, status_id: str):
        super().__init__("Thread", instance)
        self._status_id = status_id

    async def fetch(self, limit: int | None = None) -> EventGenerator:
        status_response, context_response = await asyncio.gather(
            statuses.get(self._status_id),
            statuses.context(self._status_id),
        )
        status = await from_response(Status, status_response)
        context = await from_response(Context, context_response)
        all_statuses = context.ancestors + [status] + context.descendants
        yield [StatusEvent(s) for s in all_statuses]

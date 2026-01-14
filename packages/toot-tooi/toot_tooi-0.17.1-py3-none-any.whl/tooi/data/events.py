from abc import ABC, abstractmethod
from datetime import datetime

from tooi.data import notifications, statuses
from tooi.entities import Account, Notification, Status


class Event(ABC):
    """
    An Event is something that happens on a timeline.
    """

    def __init__(self, id: str):
        self.id = id

    @property
    @abstractmethod
    def created_at(self) -> datetime: ...

    @property
    @abstractmethod
    def status(self) -> Status | None: ...

    @property
    @abstractmethod
    def account(self) -> Account: ...


class StatusEvent(Event):
    """
    Represents a new status being posted on a timeline.
    """

    def __init__(self, status: Status):
        self._status = status
        super().__init__(f"status-{status.id}")

    @property
    def status(self) -> Status:
        return self._status

    @property
    def created_at(self) -> datetime:
        return self.status.created_at

    @property
    def account(self) -> Account:
        return self.status.original.account


class NotificationEvent(Event):
    """
    Represents an event from the notification timeline.
    """

    def __init__(self, notification: Notification):
        self.notification = notification
        super().__init__(f"notification-{notification.id}")

    @property
    def created_at(self) -> datetime:
        return self.notification.created_at

    @property
    def account(self) -> Account:
        return self.notification.account

    @property
    def status(self) -> Status | None:
        return self.notification.status


async def reload(event: Event) -> Event:
    match event:
        case StatusEvent():
            status = await statuses.get(event.status.id)
            return StatusEvent(status)
        case NotificationEvent():
            notification = await notifications.get(event.notification.id)
            return NotificationEvent(notification)
        case _:
            raise ValueError(f"Unknown event class: {event}")

from textual.message import Message
from tooi.data.events import Event
from tooi.entities import Account, MediaAttachment, Status, StatusSource
from tooi.goto import Goto

# Common message types


class AccountMessage(Message, bubble=True):
    def __init__(self, account: Account) -> None:
        super().__init__()
        self.account = account


class EventMessage(Message, bubble=True):
    def __init__(self, event: Event) -> None:
        super().__init__()
        self.event = event


class StatusMessage(Message, bubble=True):
    def __init__(self, status: Status) -> None:
        super().__init__()
        self.status = status


# Custom messages


class GotoMessage(Message):
    def __init__(self, where: Goto) -> None:
        super().__init__()
        self.where = where


class EventSelected(EventMessage):
    pass


class EventHighlighted(EventMessage):
    pass


class ShowImages(Message):
    def __init__(self, media_attachments: list[MediaAttachment]) -> None:
        super().__init__()
        self.media_attachments = media_attachments


class ShowAccount(AccountMessage):
    pass


class ShowSource(StatusMessage):
    pass


class ShowStatusMenu(StatusMessage):
    pass


class StatusReply(StatusMessage):
    pass


class StatusEdit(StatusMessage):
    def __init__(self, status: Status, status_source: StatusSource):
        super().__init__(status)
        self.status_source = status_source


class LoggedIn(Message):
    pass

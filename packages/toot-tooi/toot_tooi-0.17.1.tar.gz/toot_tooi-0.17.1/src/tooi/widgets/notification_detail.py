from textual.widget import Widget
from textual.widgets import Static

from tooi.context import is_me
from tooi.entities import Notification
from tooi.widgets.account import AccountHeader
from tooi.widgets.status_detail import StatusDetail, StatusHeader


class NotificationDetail(Widget):
    def __init__(self, notification: Notification):
        super().__init__()
        self.notification = notification

    def compose(self):
        notification = self.notification
        account = self.notification.account
        status = self.notification.status

        match notification.type:
            case "favourite":
                yield StatusHeader(f"{account.display_name} favourited your status")
                if status:
                    yield StatusDetail(status)

            case "follow":
                yield StatusHeader(f"{account.display_name} followed you")
                yield AccountHeader(account)

            case "follow_request":
                yield StatusHeader(f"{account.display_name} requested to follow you")
                yield AccountHeader(account)

            case "mention":
                yield StatusHeader(f"{account.display_name} mentioned you")
                if status:
                    yield StatusDetail(status)

            case "poll":
                if is_me(account.acct):
                    yield StatusHeader("A poll you authored has ended")
                else:
                    yield StatusHeader("A poll you voted in has ended")
                if status:
                    yield StatusDetail(status)

            case "reblog":
                yield StatusHeader(f"{account.display_name} boosted your post")
                if status:
                    yield StatusDetail(status)

            case "status":
                yield StatusHeader(f"{account.display_name} posted a new status")
                if status:
                    yield StatusDetail(status)

            case "update":
                yield StatusHeader("A status you boosted has been edited")
                if status:
                    yield StatusDetail(status)

            case _:
                yield Static(f"<unknown notification type: {notification.type}>", markup=False)

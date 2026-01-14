from textual.containers import Horizontal, Vertical
from textual.widget import Widget
from textual.widgets import Label

from tooi.context import account_name
from tooi.entities import Account
from tooi.widgets.image import RemoteImage


class AccountHeader(Widget):
    DEFAULT_CSS = """
    AccountHeader {
        height: 2;

        .avatar_image {
            height: 2;
            width: 4;
            margin-right: 1;
        }
        .account_name {
            height: 1;
            color: green;
        }
        .display_name {
            height: 1;
            color: yellow;
        }
    }
    """

    def __init__(self, account: Account, *, classes: str | None = None):
        super().__init__(classes=classes)
        self.account = account

    def compose(self):
        acct = account_name(self.account.acct)
        display_name = self.account.display_name or ""

        yield Horizontal(
            RemoteImage(self.account.avatar_static, classes="avatar_image"),
            Vertical(
                Label(f"@{acct}", markup=False, classes="account_name"),
                Label(display_name, markup=False, classes="display_name"),
            ),
        )

from typing import cast

from textual import getters, on
from textual.message import Message

from tooi.app import TooiApp
from tooi.entities import Status
from tooi.goto import GotoHashtagTimeline
from tooi.messages import GotoMessage, ShowAccount
from tooi.screens.modal import ModalScreen, ModalTitle
from tooi.widgets.menu import Menu, MenuHeading, MenuItem, TagMenuItem

# TODO: add mentioned accounts to context menu


class StatusMenuScreen(ModalScreen[Message | None]):
    app = getters.app(TooiApp)

    DEFAULT_CSS = """
    StatusMenuScreen {
        ListView {
            height: auto;
        }
        #hashtags {
            margin-top: 1;
        }
    }
    """

    def __init__(self, status: Status):
        self.status = status
        super().__init__()

    def compose_modal(self):
        yield ModalTitle(f"Status #{self.status.id}")
        yield Menu(*self.menu_items())

    def menu_items(self):
        account = self.status.account
        yield MenuHeading("Accounts:")
        yield MenuItem("show_account", f"@{account.acct}")

        if self.status.reblog:
            account = self.status.reblog.account
            yield MenuItem("show_original_account", f"@{account.acct}")

        if tags := self.status.original.tags:
            yield MenuHeading("Hashtags:", id="hashtags")
            for tag in tags:
                yield TagMenuItem("show_tag", tag)

    @on(Menu.ItemSelected)
    def on_item_selected(self, message: Menu.ItemSelected):
        message.stop()

        match message.item.code:
            case "show_account":
                self.dismiss(ShowAccount(self.status.account))
            case "show_original_account":
                self.dismiss(ShowAccount(self.status.original.account))
            case "show_tag":
                item = cast(TagMenuItem, message.item)
                self.dismiss(GotoMessage(GotoHashtagTimeline(item.tag.name)))
            case _:
                pass

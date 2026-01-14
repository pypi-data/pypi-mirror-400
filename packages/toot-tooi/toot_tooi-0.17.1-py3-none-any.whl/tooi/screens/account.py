from typing import Awaitable

from textual import getters, on, work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.message import Message
from textual.widget import Widget
from textual.widgets import Footer, Label

from tooi import entities
from tooi.app import TooiApp
from tooi.context import is_me
from tooi.data import accounts
from tooi.entities import Account, Relationship
from tooi.goto import GotoAccountTimeline
from tooi.http import ResponseError
from tooi.messages import GotoMessage
from tooi.screens.modal import ModalScreen, ModalTitle
from tooi.widgets.account import AccountHeader
from tooi.widgets.chip import Chip
from tooi.widgets.markdown import Markdown
from tooi.widgets.menu import Menu, MenuItem
from tooi.widgets.status_bar import StatusBar


class AccountScreen(ModalScreen[Message | None]):
    app = getters.app(TooiApp)

    DEFAULT_CSS = """
    #account_note {
        margin: 0;
        margin-top: 1;
    }
    #relationship_error {
        color: $error;
    }
    #relationship_placeholder {
        color: $text-muted;
        height: 3;
        content-align: center middle;
    }
    StatusBar {
        height: 2;
    }
    """

    BINDINGS = [
        # TODO: currently disabled, consider if we want to keep it
        # Binding("enter,space", "open_account_menu", "Account Menu"),
        Binding("f", "follow", "(un)Follow"),
        Binding("b", "block", "(un)Block"),
        Binding("m", "mute", "(un)Mute"),
        Binding("p", "pin", "(un)Pin"),
        Binding("t", "show_timeline", "Show Timeline"),
    ]

    def __init__(self, account: Account):
        self.account = account
        self.relationship: Relationship | None = None
        super().__init__()

    def compose_modal(self) -> ComposeResult:
        account = self.account
        yield AccountHeader(account)
        yield Markdown(account.note_md, id="account_note")

        for f in account.fields:
            yield AccountField(f)

        if account.bot:
            yield Chip("Automated")

        yield Label("Loading relationships...", id="relationship_placeholder")
        yield StatusBar()
        yield Footer()

    def on_mount(self):
        self.load_relationship()

    def action_follow(self):
        if self.relationship and not is_me(self.account.acct):
            if self.relationship.following:
                self._relationship_action(accounts.unfollow(self.account.id))
            else:
                self._relationship_action(accounts.follow(self.account.id))

    def action_mute(self):
        if self.relationship and not is_me(self.account.acct):
            if self.relationship.muting:
                self._relationship_action(accounts.unmute(self.account.id))
            else:
                self._relationship_action(accounts.mute(self.account.id))

    @work
    async def action_block(self):
        if self.relationship and not is_me(self.account.acct):
            if self.relationship.blocking:
                self._relationship_action(accounts.unblock(self.account.id))
            else:
                title = "Block account"
                text = f"Are you sure you want to block {self.account.acct}?"
                if await self.app.confirm(title, text=text, confirm_label="Block"):
                    self._relationship_action(accounts.block(self.account.id))

    @work
    async def action_open_account_menu(self):
        menu = AccountMenuScreen(self.account)
        message = await self.app.push_screen_wait(menu)
        self.dismiss(message)

    @work
    async def action_show_timeline(self):
        self.dismiss(GotoMessage(GotoAccountTimeline(self.account)))

    @work
    async def load_relationship(self):
        relationship = await accounts.relationship(self.account.id, with_suspended=True)
        if relationship:
            self.relationship = relationship
            self.show_relationships(AccountRelationship(self.account, relationship))
        else:
            widget = Label("Failed loading relationships", id="relationship_error")
            self.show_relationships(widget)

    def show_relationships(self, widget: Widget):
        with self.app.batch_update():
            self.query("#relationship_placeholder").remove()
            self.query("#relationship_error").remove()
            self.query("AccountRelationship").remove()
            self.mount(widget, before=self.query_one(StatusBar))

    @work
    async def _relationship_action(self, action: Awaitable[Relationship]):
        """
        Run an avaitable which alters the relationship and returns the altered
        Relationship instance.
        """
        try:
            self.relationship = await action
            widget = AccountRelationship(self.account, self.relationship)
            self.show_relationships(widget)
        except ResponseError as ex:
            self.app.show_error_modal(title="Operation failed", ex=ex)


class AccountRelationship(Widget):
    DEFAULT_CSS = """
    AccountRelationship {
        height: auto;

        #account_chips {
            height: auto;
        }
    }
    """

    def __init__(self, account: Account, relationship: Relationship):
        self.account = account
        self.relationship = relationship
        super().__init__()

    def compose(self):
        with Horizontal(id="account_chips"):
            if self.relationship.following:
                yield Chip("Following")
            if self.relationship.followed_by:
                yield Chip("Follows you")
            if self.relationship.blocking:
                yield Chip("Blocked")
            if self.relationship.blocked_by:
                yield Chip("Blocks you")
            if self.relationship.muting:
                yield Chip("Muted")


class AccountField(Widget):
    DEFAULT_CSS = """
    AccountField {
        height: auto;
    }
    .account_field_name {
        text-style: bold;
    }
    .account_field_value {
        margin: 0;
    }
    """

    def __init__(self, field: entities.AccountField):
        self.field = field
        super().__init__()

    def compose(self):
        yield Label(self.field.name, markup=False, classes="account_field_name")
        yield Markdown(self.field.value_md, classes="account_field_value")


class AccountMenuScreen(ModalScreen[Message | None]):
    def __init__(self, account: Account):
        self.account = account
        super().__init__()

    def compose_modal(self) -> ComposeResult:
        yield ModalTitle(f"Account @{self.account.acct}")
        yield Menu(*self.compose_items())

    def compose_items(self):
        yield MenuItem(code="goto_timeline", label="View timeline", key="t")

    @on(Menu.ItemSelected)
    def on_item_selected(self, message: Menu.ItemSelected):
        message.stop()

        match message.item.code:
            case "goto_timeline":
                self.dismiss(GotoMessage(GotoAccountTimeline(self.account)))
            case _:
                self.dismiss()

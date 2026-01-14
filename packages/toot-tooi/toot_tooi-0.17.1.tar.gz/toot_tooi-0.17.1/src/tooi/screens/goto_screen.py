from __future__ import annotations

from textual import getters, log, on, work
from textual.app import ComposeResult
from textual.binding import Binding
from textual.widgets import Input, Static

from tooi import goto
from tooi.app import TooiApp
from tooi.screens.modal import ModalScreen, ModalTitle
from tooi.widgets.menu import Menu, MenuItem


class GotoScreen(ModalScreen[goto.Goto | None]):
    app = getters.app(TooiApp)

    DEFAULT_CSS = """
    GotoScreen ListView {
        height: auto;
    }
    """

    def compose_modal(self) -> ComposeResult:
        yield ModalTitle("Go to")
        yield Menu(
            MenuItem(code="goto_personal", label="Personal timeline", key="p"),
            MenuItem(code="goto_home", label="Home timeline", key="h"),
            MenuItem(code="goto_local", label="Local timeline", key="l"),
            MenuItem(code="goto_federated", label="Federated timeline", key="f"),
            MenuItem(code="goto_notifications", label="Notifications", key="n"),
            MenuItem(code="goto_conversations", label="Conversations", key="c"),
            MenuItem(code="goto_hashtag", label="Hashtag timeline", key="t"),
        )

    @on(Menu.ItemSelected)
    def on_item_selected(self, message: Menu.ItemSelected):
        message.stop()

        match message.item.code:
            case "goto_home":
                self.dismiss(goto.GotoHomeTimeline())
            case "goto_personal":
                self.dismiss(goto.GotoPersonalTimeline())
            case "goto_local":
                self.dismiss(goto.GotoLocalTimeline())
            case "goto_federated":
                self.dismiss(goto.GotoFederatedTimeline())
            case "goto_hashtag":
                self.goto_hashtag()
            case "goto_conversations":
                self.dismiss(goto.GotoConversations())
            case "goto_notifications":
                self.dismiss(goto.GotoNotifications())
            case _:
                log.error("Unknown selection")
                self.dismiss(None)

    @work
    async def goto_hashtag(self):
        tag = await self.app.push_screen_wait(GotoHashtagScreen())
        if tag:
            self.dismiss(goto.GotoHashtagTimeline(tag))
        else:
            self.dismiss(None)


class GotoHashtagScreen(ModalScreen[str | None]):
    DEFAULT_CSS = """
    GotoHashtagScreen Input {
        margin-top: 1;
    }
    """

    BINDINGS = [
        Binding("escape", "quit", "Close"),
    ]

    def compose_modal(self):
        self.input = Input(placeholder="Hash")
        self.status = Static("")
        yield Static(" Enter hashtag:")
        yield self.input
        yield self.status

    def on_input_submitted(self):
        value = self.input.value.strip()
        if value:
            self.input.disabled = True
            self.status.update(" [green]Looking up hashtag...[/]")
            self.dismiss(value)
        else:
            self.status.update(" [red]Enter a hash tag value.[/]")

import traceback

from textual import getters, on
from textual.app import ComposeResult
from textual.containers import Horizontal, VerticalScroll
from textual.widgets import Button, Static

from tooi.app import TooiApp
from tooi.screens.modal import ModalScreen, ModalTitle

# TODO: add button to report error on codeberg?
# TODO: add collapsible exception stack trace


class ErrorBox(ModalScreen[None]):
    app = getters.app(TooiApp)

    DEFAULT_CSS = """
    ErrorBox  {
        .container {
            height: 1fr;
            margin: 1 0;
            &:focus {
                background: $background-lighten-1;
            }
        }
        .buttons {
            height: 3
        }
        Button {
            width: 1fr;
        }
    }
    """

    def __init__(self, title: str, message: str | None, exception: BaseException | None = None):
        self.error_title = title
        self.error_message = message
        self.exception = exception
        super().__init__()

    def compose_modal(self) -> ComposeResult:
        yield ModalTitle(self.error_title, error=True)
        yield VerticalScroll(
            Static(self._format_message(), markup=False),
            classes="container",
        )
        yield Horizontal(
            Button("Copy", id="button_copy", flat=True),
            Button("Dismiss", id="button_dismiss", flat=True),
            classes="buttons",
        )

    @on(Button.Pressed, "#button_dismiss")
    def handle_dismiss(self):
        self.dismiss()

    @on(Button.Pressed, "#button_copy")
    def handle_copy(self):
        text = f"{self.error_title}\n\n{self._format_message()}"
        self.app.copy_to_clipboard(text)
        self.app.notify("Error copied to clipboard")

    def _format_message(self):
        message = self.error_message.strip() if self.error_message else ""
        if self.exception:
            if message:
                message += "\n\n"
            for line in traceback.format_exception(self.exception):
                message += line

        if not message:
            message = "No details provided"

        return message

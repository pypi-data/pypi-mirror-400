from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.widgets import Static, Button

from tooi.screens.modal import ModalScreen, ModalTitle


class MessageBox(ModalScreen[None]):
    DEFAULT_CSS = """
    MessageBox  {
        Button {
            width: 100%;
        }
        .container {
            margin: 1 0;
        }
    }
    """

    def __init__(self, title: str, body: str | None, error: bool = False):
        self.message_title = title
        self.message_body = body
        self.error = error
        super().__init__()

    def compose_modal(self) -> ComposeResult:
        yield ModalTitle(self.message_title, error=self.error)
        if self.message_body:
            yield VerticalScroll(
                Static(self.message_body.strip(), markup=False),
                classes="container",
            )
        yield Button("OK")

    def on_button_pressed(self, message: Button.Pressed):
        self.dismiss()

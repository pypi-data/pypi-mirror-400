import asyncio

from textual import on, work
from textual.app import ComposeResult
from textual.widgets import Label

from tooi.api import statuses
from tooi.entities import Status
from tooi.http import APIError
from tooi.screens.modal import ModalScreen, ModalTitle
from tooi.widgets.menu import Menu, MenuItem


class ConfirmationDialog(ModalScreen[bool]):
    def __init__(
        self,
        modal_title: str,
        *,
        modal_text: str | None = None,
        confirm_label: str = "Confirm",
        cancel_label: str = "Cancel",
        show_status_bar: bool = False,
    ):
        self.modal_title = modal_title
        self.modal_text = modal_text
        self.confirm_label = confirm_label
        self.cancel_label = cancel_label
        self.show_status_bar = show_status_bar
        super().__init__()

    def compose_modal(self) -> ComposeResult:
        yield ModalTitle(self.modal_title)
        if self.modal_text:
            yield Label(self.modal_text)
        yield Menu(
            MenuItem("confirm", self.confirm_label),
            MenuItem("cancel", self.cancel_label),
        )
        hide_class = "" if self.show_status_bar else "hide"
        yield Label("", classes=f"dialog_status_bar {hide_class}")

    @on(Menu.ItemSelected)
    def _on_item_selected(self, message: Menu.ItemSelected):
        message.stop()

        match message.item.code:
            case "confirm":
                self.on_confirm()
            case "cancel":
                self.on_cancel()
            case _:
                pass

    def on_confirm(self) -> None:
        self.dismiss(True)

    def on_cancel(self) -> None:
        self.dismiss(False)

    def show_message(self, msg: str, style: str | None = None):
        msg = f"[{style}]{msg}[/]" if style else msg
        self.query_one(".dialog_status_bar", Label).update(msg)


class DeleteStatusDialog(ConfirmationDialog):
    def __init__(self, status: Status):
        self.status = status
        super().__init__(
            modal_title="Delete status?",
            confirm_label="Delete",
            cancel_label="Cancel",
            show_status_bar=True,
        )

    def on_confirm(self) -> None:
        self.delete()

    @work
    async def delete(self):
        assert self.status.id
        try:
            await statuses.delete(self.status.id)
            self.show_message("Status deleted", style="green")
            await asyncio.sleep(0.3)
            self.dismiss(True)
        except APIError as ex:
            self.show_message(f"Failed deleting status: {ex}", style="red")

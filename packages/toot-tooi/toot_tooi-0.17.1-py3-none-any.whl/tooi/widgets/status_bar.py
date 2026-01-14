from __future__ import annotations

from contextlib import asynccontextmanager
from uuid import uuid4

from textual import getters
from textual.reactive import reactive
from textual.widget import Widget

from tooi import MessageId
from tooi.app import TooiApp


class StatusBar(Widget):
    app = getters.app(TooiApp)

    DEFAULT_CSS = """
    StatusBar {
        height: 1;
        dock: bottom;
    }
    """

    MAX_TIMEOUT = 60

    messages: reactive[dict[MessageId, str]] = reactive(lambda: {})

    def render(self):
        return " [gray]|[/gray] ".join([m for m in self.messages.values()])

    def set_message(self, text: str, timeout: float | None = None) -> MessageId:
        """
        Show a message in the status bar.

        The message will be removed after `timeout` seconds have passed (max MAX_TIMEOUT).
        """
        if not timeout or timeout > self.MAX_TIMEOUT:
            timeout = self.MAX_TIMEOUT

        message_id = uuid4()

        def _clear():
            self.clear_message(message_id)

        self.set_timer(timeout, callback=_clear)
        self.messages[message_id] = text
        self.mutate_reactive(StatusBar.messages)
        return message_id

    def set_success_message(self, text: str, timeout: float | None = None) -> MessageId:
        return self.set_message(f"[green]{text}[/green]", timeout)

    def set_error_message(self, text: str, timeout: float | None = None) -> MessageId:
        return self.set_message(f"[red]{text}[/red]", timeout)

    def clear_message(self, message_id: MessageId | None):
        """
        Clear a message with given ID before its timeout has expired.

        Does nothing if the message has already exired or message_id is None.
        """
        if message_id and message_id in self.messages:
            del self.messages[message_id]
            self.mutate_reactive(StatusBar.messages)

    @asynccontextmanager
    async def run_with_progress(
        self,
        progress: str,
        success: str | None = None,
        error: str | None = None,
    ):
        message_id = self.set_message(f"[gray]{progress}[/]")

        try:
            yield
            if success:
                self.set_success_message(success, 1)
        except Exception as ex:
            self.app.show_error_modal(message=error, ex=ex)
        finally:
            self.clear_message(message_id)

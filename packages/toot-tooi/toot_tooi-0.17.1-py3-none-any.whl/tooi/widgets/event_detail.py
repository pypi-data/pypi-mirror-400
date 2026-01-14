from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.reactive import reactive
from textual.widgets import Static

from tooi.data.events import Event, NotificationEvent, StatusEvent
from tooi.widgets.notification_detail import NotificationDetail
from tooi.widgets.status_detail import StatusDetail


class EventDetail(VerticalScroll):
    event: reactive[Event | None] = reactive(None, recompose=True)

    # Add j/k bindings for scrolling
    BINDINGS = [
        Binding("up,k", "scroll_up", "Scroll Up", show=False),
        Binding("down,j", "scroll_down", "Scroll Down", show=False),
    ]

    DEFAULT_CSS = """
    EventDetail {
        width: 2fr;
        height: 100%;
        padding: 0 1;

        /* Make it the same as ListView */
        background: $surface;
        &:focus {
            background-tint: $foreground 5%;
        }
    }
    """

    def compose(self):
        match self.event:
            case None:
                yield Static("Nothing selected")
            case StatusEvent():
                yield StatusDetail(self.event.status)
            case NotificationEvent():
                yield NotificationDetail(self.event.notification)
            case _:
                yield Static("Not implemented")

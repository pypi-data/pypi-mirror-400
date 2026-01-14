from rich.console import RenderableType
from textual import getters
from textual.app import ComposeResult
from textual.containers import Vertical
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Static, Link as TLink

from tooi.app import TooiApp
from tooi.entities import MediaAttachment, Status
from tooi.utils.classes import class_dict
from tooi.utils.datetime import format_datetime
from tooi.widgets.account import AccountHeader
from tooi.widgets.image import RemoteImage
from tooi.widgets.link import Link
from tooi.widgets.markdown import Markdown
from tooi.widgets.poll import Poll


class StatusDetail(Widget):
    app = getters.app(TooiApp)

    _revealed: set[str] = set()

    DEFAULT_CSS = """
    StatusDetail {
        height: auto;

        .status_content {
            margin-top: 1;
        }

        .spoiler_text {
            margin-top: 1;
        }

        .sensitive_content {
            height: auto;
        }

        StatusSensitiveNotice { display: none; }

        &.hide_sensitive {
            .sensitive_content { display: none; }
            StatusSensitiveNotice { display: block; }
            StatusSensitiveOpenedNotice { display: none; }
        }
    }
    """

    def __init__(self, status: Status):
        super().__init__()
        self.status = status
        self.sensitive = self.status.original.sensitive
        self.set_class(self.sensitive and not self.revealed, "hide_sensitive")

    def reveal(self):
        status_id = self.status.original.id
        if status_id in self._revealed:
            self._revealed.discard(status_id)
        else:
            self._revealed.add(status_id)

        self.set_class(self.sensitive and not self.revealed, "hide_sensitive")

    @property
    def revealed(self) -> bool:
        # TODO: take into account user preferences defined on the instance
        # see: instance.get_always_show_sensitive()
        return (
            self.app.options.always_show_sensitive
            or self.status.original.id in self._revealed
        )

    def compose(self) -> ComposeResult:
        status = self.status.original

        if self.status.reblog:
            yield StatusHeader(f"boosted by {self.status.account.acct}")

        yield AccountHeader(status.account)

        if status.spoiler_text:
            yield Static(status.spoiler_text, markup=False, classes="spoiler_text")

        if status.sensitive:
            yield StatusSensitiveNotice()
            yield StatusSensitiveOpenedNotice()

        # Content which should be hidden if status is sensitive and not revealed
        with Vertical(classes="sensitive_content"):
            yield Markdown(status.content_md, classes="status_content")

            if status.poll:
                yield Poll(status.poll)

            if status.card:
                yield StatusCard(status)

            for attachment in status.original.media_attachments:
                yield StatusMediaAttachment(attachment)

        yield StatusMeta(status)


class StatusHeader(Static):
    DEFAULT_CSS = """
    StatusHeader {
        color: gray;
        border-bottom: ascii gray;
    }
    """

    def __init__(self, renderable: RenderableType = ""):
        super().__init__(renderable, markup=False)


class StatusCard(Widget):
    DEFAULT_CSS = """
    StatusCard {
        border: round white;
        padding: 0 1;
        height: auto;
        margin-top: 1;

        .title {
            text-style: bold;
        }
    }

    """

    def __init__(self, status: Status):
        self.status = status
        super().__init__()

    def compose(self):
        card = self.status.original.card

        if not card:
            return

        yield Link(card.url, card.title, classes="title")

        if card.author_name:
            yield Static(f"by {card.author_name}", markup=False)

        if card.description:
            yield Static("")
            yield Static(card.description, markup=False)

        if card.image:
            yield RemoteImage(card.image)

        yield TLink(card.url)


class StatusMediaAttachment(Widget):
    DEFAULT_CSS = """
    StatusMediaAttachment {
        border-top: ascii gray;
        height: auto;

        .title {
            text-style: bold;
        }

        .media_image {
            margin: 1 0;
        }
    }
    """

    def __init__(self, attachment: MediaAttachment):
        self.attachment = attachment
        super().__init__()

    def compose(self):
        yield Static(f"Media attachment ({self.attachment.type})", markup=False, classes="title")

        if self.attachment.description:
            yield Static(self.attachment.description, markup=False)

        if self.attachment.type == "image":
            yield RemoteImage(
                self.attachment.preview_url,
                blurhash=self.attachment.blurhash,
                aspect_ratio=self.attachment.aspect_ratio,
                classes="media_image",
            )

        yield Link(self.attachment.url)


class StatusMeta(Widget):
    app = getters.app(TooiApp)

    DEFAULT_CSS = """
    StatusMeta {
        color: gray;
        border-top: ascii gray;
        layout: horizontal;
        height: auto;

        .highlighted {
            color: $accent;
        }
    }

    StatusMeta > * {
        width: auto;
    }
    """

    status: reactive[Status | None] = reactive(None, recompose=True)

    def __init__(self, status: Status):
        super().__init__()
        self.status = status

    def visibility_string(self, status: Status):
        vis = f"{status.visibility.capitalize()}"
        if status.local_only:
            vis += " (local only)"
        return vis

    def format_timestamp(self, status: Status):
        relative = self.app.options.relative_timestamps
        created_ts = format_datetime(status.created_at, relative=relative)

        if status.edited_at:
            edited_ts = format_datetime(status.edited_at, relative=relative)
            return f"{created_ts} (edited {edited_ts} ago)"

        return created_ts

    def compose(self):
        status = self.status
        if not status:
            return

        original = status.original

        yield Static(self.format_timestamp(status), markup=False, classes="timestamp")
        yield Static(" · ")

        yield Static(
            f"{original.reblogs_count} boosts",
            markup=False,
            classes=class_dict(highlighted=status.reblogged),
        )
        yield Static(" · ")
        yield Static(
            f"{original.favourites_count} favourites",
            markup=False,
            classes=class_dict(highlighted=status.favourited),
        )
        yield Static(" · ")
        yield Static(f"{original.replies_count} replies", markup=False)
        yield Static(" · ")
        yield Static(self.visibility_string(original), markup=False)


class StatusSensitiveNotice(Static):
    DEFAULT_CSS = """
    StatusSensitiveNotice {
        margin-top: 1;
        padding-left: 1;
        color: red;
        border: round red;
    }
    """

    def __init__(self):
        super().__init__("Marked as sensitive. Press S to view.")


class StatusSensitiveOpenedNotice(Static):
    app = getters.app(TooiApp)

    DEFAULT_CSS = """
    StatusSensitiveOpenedNotice {
        margin-top: 1;
        padding-left: 1;
        color: gray;
        border: round gray;
    }
    """

    def __init__(self):
        label = "Marked as sensitive."
        if not self.app.options.always_show_sensitive:
            label += " Press S to hide."
        super().__init__(label)

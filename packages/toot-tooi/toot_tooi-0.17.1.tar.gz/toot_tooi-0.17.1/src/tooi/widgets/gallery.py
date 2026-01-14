from pathlib import Path

from textual import getters, work
from textual.app import App
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Footer, Link, Rule, Static
from textual_image.widget import Image

from tooi.app import TooiApp
from tooi.cache import download_images_cached
from tooi.entities import MediaAttachment
from tooi.screens.modal import ModalScreen, ModalTitle


## TODO:
# * small images are currently strtched to fill the modal which makes them
#   blurry, perhaps we want to keep them small?


class GalleryScreen(ModalScreen[None]):
    app = getters.app(TooiApp)

    DEFAULT_CSS = """
    GalleryScreen {
        .modal_container {
            max-width: 95%;
            max-height: 95%;
        }
        .loading, .error {
            height: 100%;
            text-align: center;
            content-align: center middle;
        }
        .error {
            color: $error;
        }

        Rule {
            margin: 0;
            color: $text-muted;
        }

        Link {
            margin-bottom: 1;
        }
    }
    """

    paths: reactive[list[Path] | None] = reactive(None, recompose=True)
    exception: reactive[Exception | None] = reactive(None, recompose=True)

    BINDINGS = [
        Binding("right,j", "next", "Next"),
        Binding("left,k", "prev", "Previous"),
    ]

    # TODO: use low res images as placeholders?
    def __init__(self, media_attachments: list[MediaAttachment]):
        super().__init__()
        self.media_attachments = media_attachments
        self.index = 0

    @work
    async def on_mount(self):
        try:
            urls = [m.url for m in self.media_attachments]
            self.paths = await download_images_cached(urls)
        except Exception as ex:
            self.exception = ex
            self.app.show_error_modal(message="Failed loading images", ex=ex)

    def compose_modal(self):
        media = self.media_attachments[self.index]
        description = media.description.strip() if media.description else ""

        yield ModalTitle("Gallery")
        if self.paths:
            yield GalleryImage(self.paths[self.index])
            yield Rule()
            yield ImageDescription(description)
            yield Link(media.url)

        elif self.exception:
            yield Static(f"Failed loading images :(\n\n{repr(self.exception)}", classes="error")
        else:
            yield Static("Loading...", classes="loading")
        yield Footer()

    def action_next(self):
        self.switch_image(+1)

    def action_prev(self):
        self.switch_image(-1)

    def switch_image(self, delta: int):
        self.index = (self.index + delta) % len(self.media_attachments)
        if self.paths:
            self.query_one(GalleryImage).path = self.paths[self.index]

        description = self.media_attachments[self.index].description
        description = description.strip() if description else ""
        self.query_one(ImageDescription).description = description


class ImageDescription(VerticalScroll):
    DEFAULT_CSS = """
    ImageDescription {
        height: auto;
        max-height: 5;
        margin-bottom: 1;

        &:focus {
            background: $background-lighten-2;
        }
    }
    """

    description = reactive("")

    def __init__(self, description: str):
        super().__init__(Static(description))
        self.description = description

    def watch_description(self, old: str, new: str) -> None:
        for s in self.query(Static):
            if new:
                s.update(new)
            else:
                s.update("[gray]No description[/]")


class GalleryImage(Widget, can_focus=True):
    DEFAULT_CSS = """
    GalleryImage {
        align-vertical: middle;
        align-horizontal: center;
        height: 1fr;

        &:focus {
            background: $background-lighten-2;
        }

        Image {
            width: auto;
            height: auto;
        }
    }
    """

    path: reactive[Path | None] = reactive(None, recompose=True)

    def __init__(self, path: Path):
        super().__init__()
        self.path = path

    def compose(self):
        if self.path is None:
            yield Static("No image")
        elif not self.path.exists():
            yield Static(f"[red]Image not found:[/]\n{self.path}")
        else:
            yield Image(self.path)


if __name__ == "__main__":
    from tooi.lorem import ALICE

    class TestApp(App[None]):
        CSS_PATH = Path(__file__).parent.parent / "app.css"

        MEDIA_ATTACHMENTS = [
            MediaAttachment(
                id="1",
                type="image",
                url="https://placecats.com/800/600",
                preview_url="https://placecats.com/800/600",
                remote_url="https://placecats.com/800/600",
                meta={},
                description="This is a cat",
                blurhash="",
            ),
            MediaAttachment(
                id="2",
                type="image",
                url="https://placecats.com/800/200",
                preview_url="https://placecats.com/800/200",
                remote_url="https://placecats.com/800/200",
                meta={},
                description="",
                blurhash="",
            ),
            MediaAttachment(
                id="3",
                type="image",
                url="https://placecats.com/200/800",
                preview_url="https://placecats.com/200/800",
                remote_url="https://placecats.com/200/800",
                meta={},
                description="cat " * 100,
                blurhash="",
            ),
            MediaAttachment(
                id="4",
                type="image",
                url="https://placecats.com/50/50",
                preview_url="https://placecats.com/50/50",
                remote_url="https://placecats.com/50/50",
                meta={},
                description=ALICE,
                blurhash="",
            ),
        ]

        def compose(self):
            yield Static("app")

        def on_mount(self):
            self.push_screen(GalleryScreen(self.MEDIA_ATTACHMENTS))

    TestApp().run()

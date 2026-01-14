from pathlib import Path

from textual import work
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Pretty, Static
from textual_image.widget import Image

from tooi import cache


class RemoteImage(Widget):
    """Render an image from the web.

    Images are cached in the user cache dir.
    """
    DEFAULT_CSS = """
    RemoteImage {
        height: auto;

        Image {
            height: auto;
            width: auto;
            max-height: 20;
        }
    }
    """
    path: reactive[Path | None] = reactive(None, recompose=True)
    exception: reactive[Exception | None] = reactive(None, recompose=True)

    def __init__(
        self,
        url: str,
        *,
        id: str | None = None,
        classes: str | None = None,
        blurhash: str | None = None,
        aspect_ratio: float | None = None,
    ):
        self.url = url
        super().__init__(id=id, classes=classes)

        cache_path = cache.image_cache_path(url)
        if cache_path.exists():
            self.path = cache_path

        # TODO: blurhash placeholder?

    def compose(self):
        if self.path:
            yield Image(self.path)
        elif self.exception:
            yield Static("Error loading image:")
            yield Pretty(self.exception)
        else:
            yield Static("Loading image...")

    async def on_mount(self):
        if not self.path:
            self.call_after_refresh(self.fetch_image)

    @work
    async def fetch_image(self):
        try:
            self.path = await cache.download_image_cached(self.url)
        except Exception as ex:
            self.exception = ex

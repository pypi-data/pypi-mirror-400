import re
from urllib.parse import urlparse
from markdown_it import MarkdownIt
from textual import getters, on, widgets

from tooi.app import TooiApp
from tooi.goto import GotoHashtagTimeline
from tooi.messages import GotoMessage


class Markdown(widgets.Markdown):
    app = getters.app(TooiApp)

    DEFAULT_CSS = """
    Markdown {
        padding: 0;
    }
    """

    def __init__(
        self,
        markdown: str | None = None,
        *,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ):
        super().__init__(
            markdown,
            name=name,
            id=id,
            classes=classes,
            open_links=False,
            # Configure the Markdown parser not to parse inline HTML but leave it as-is
            parser_factory=lambda: MarkdownIt(options_update={"html": False}),
        )

    @on(widgets.Markdown.LinkClicked)
    def handle_link_clicked(self, message: widgets.Markdown.LinkClicked):
        message.stop()
        parsed = urlparse(message.href)

        # Handle Hashtag clicks
        if m := re.match(r"/tags/(\w+)", parsed.path):
            hashtag = m.group(1)
            goto = GotoHashtagTimeline(hashtag)
            self.post_message(GotoMessage(goto))
        else:
            self.app.open_url(message.href)

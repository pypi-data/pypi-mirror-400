from __future__ import annotations

from typing import NamedTuple

from textual.command import DiscoveryHit, Hit, Hits, Provider
from textual.types import IgnoreReturnCallbackType
from textual.visual import VisualType


class TooiCommandsProvider(Provider):
    async def startup(self) -> None:
        from tooi.app import TooiApp

        assert isinstance(self.app, TooiApp)

        self.commands = [
            Command(
                display="Switch Account",
                text="Switch Account",
                command=self.app.open_accounts_screen,
                help="Log into another account",
            )
        ]

    async def discover(self) -> Hits:
        for command in self.commands:
            yield DiscoveryHit(
                display=command.display,
                command=command.command,
                text=command.text,
                help=command.help,
            )

    async def search(self, query: str) -> Hits:
        matcher = self.matcher(query)
        for command in self.commands:
            score = matcher.match(command.text)
            if score > 0:
                yield Hit(
                    score=score,
                    match_display=matcher.highlight(command.text),
                    command=command.command,
                    text=command.text,
                    help=command.help,
                )


class Command(NamedTuple):
    display: VisualType
    command: IgnoreReturnCallbackType
    help: str
    text: str

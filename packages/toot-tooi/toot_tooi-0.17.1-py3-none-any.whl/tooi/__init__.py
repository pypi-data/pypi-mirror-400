from importlib import metadata
from uuid import UUID

try:
    __version__ = metadata.version("toot-tooi")
except metadata.PackageNotFoundError:
    __version__ = "0.0.0"


APP_NAME = "tooi"
APP_WEBSITE = "https://codeberg.org/ihabunek/tooi"
USER_AGENT = f"{APP_NAME}/{__version__}"

MessageId = UUID
"""Uniquely identifies a message in the status bar allowing it to be cleared."""

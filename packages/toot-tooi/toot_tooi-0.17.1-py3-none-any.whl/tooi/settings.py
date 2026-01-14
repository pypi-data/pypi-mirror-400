from pathlib import Path
import click

from functools import lru_cache
from platformdirs import user_config_path
from pydantic import BaseModel, Field
from tomlkit import parse
from typing import Any, Optional, Type, TypeVar

from tooi.utils.from_dict import from_dict


DISABLE_SETTINGS = False
TOOI_CONFIG_DIR_NAME = "tooi"
TOOI_SETTINGS_FILE_NAME = "settings.toml"
TOOI_STYLESHEET_FILE_NAME = "styles.tcss"


class Options(BaseModel):
    always_show_sensitive: Optional[bool] = None
    image_viewer: Optional[str] = None
    relative_timestamps: bool = False
    streaming: bool = False
    timeline_refresh: int = 0


class Configuration(BaseModel):
    options: Options = Field(default_factory=Options)


def get_config_dir() -> Path:
    """Returns the path to tooi config directory"""
    return user_config_path("tooi")


def get_settings_path() -> Path:
    return get_config_dir() / TOOI_SETTINGS_FILE_NAME


def get_stylesheet_path() -> Path:
    return get_config_dir() / TOOI_STYLESHEET_FILE_NAME


def _load_settings() -> dict[str, Any]:
    # Used for testing without config file
    if DISABLE_SETTINGS:
        return {}

    path = get_settings_path()
    if path.exists():
        try:
            with path.open() as f:
                return parse(f.read())
        except Exception:
            raise click.ClickException(f"Cannot load settings from '{path}'")

    return {}


@lru_cache(maxsize=None)
def get_settings():
    settings = _load_settings()
    return from_dict(Configuration, settings)


T = TypeVar("T")


def get_setting(key: str, type: Type[T], default: Optional[T] = None) -> Optional[T]:
    """
    Get a setting value. The key should be a dot-separated string,
    e.g. "commands.post.editor" which will correspond to the "editor" setting
    inside the `[commands.post]` section.
    """
    settings = get_settings()
    return _get_setting(settings, key.split("."), type, default)


def _get_setting(dct: Any, keys: list[str], type: Type[T], default: T | None = None) -> T | None:
    if len(keys) == 0:
        if isinstance(dct, type):
            return dct
        else:
            # TODO: warn? cast? both?
            return default

    key = keys[0]
    if isinstance(dct, dict) and key in dct:
        return _get_setting(dct[key], keys[1:], type, default)

    return default

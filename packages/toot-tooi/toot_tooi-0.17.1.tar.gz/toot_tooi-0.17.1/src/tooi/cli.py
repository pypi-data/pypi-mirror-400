import logging
import platform
from os import path
from typing import Optional

import click
from textual.logging import TextualHandler

from tooi import __version__
from tooi.app import TooiApp
from tooi.cache import get_cache_dir
from tooi.credentials import get_credentials_path
from tooi.settings import Options, get_settings, get_settings_path, get_stylesheet_path
from tooi.utils.file import dir_size, format_size

# If this is removed, the app hangs on boot for some reason
# TODO: try to debug and report an issue
from textual_image.widget import Image

from tooi.utils.image import get_image_support


def get_default_map():
    return get_settings().options.model_dump()


# Tweak the Click context
# https://click.palletsprojects.com/en/8.1.x/api/#context
CONTEXT = dict(
    # Enable using environment variables to set options
    auto_envvar_prefix="TOOI",
    # Add shorthand -h for invoking help
    help_option_names=["-h", "--help"],
    # Always show default values for options
    show_default=True,
    # Load option defaults from settings
    default_map=get_default_map(),
)


@click.command(context_settings=CONTEXT)
@click.option(
    "--image-viewer",
    help="""Path to a binary which will be invoked when viewing images, will be
    passed a list of paths to images. If not specified, the internal gallery
    widget will be used instead.""",
)
@click.option(
    "-S",
    "--always-show-sensitive",
    type=click.BOOL,
    default=None,
    help="Override server preference to expand toots with content warnings automatically",
)
@click.option(
    "-R",
    "--relative-timestamps",
    is_flag=True,
    help="Use relative timestamps in the timeline",
)
@click.option(
    "-r",
    "--timeline-refresh",
    type=click.INT,
    default=0,
    help="How often to automatically refresh timelines (in seconds)",
)
@click.option(
    "-s",
    "--streaming",
    is_flag=True,
    help="Use real-time streaming to fetch timeline updates",
)
@click.option("--env", is_flag=True, help="Print environment data and exit")
@click.version_option(None, "-v", "--version", package_name="toot-tooi")
def tooi(
    always_show_sensitive: Optional[bool],
    image_viewer: Optional[str],
    relative_timestamps: bool,
    streaming: bool,
    timeline_refresh: int,
    env: bool,
):
    options = Options(
        always_show_sensitive=always_show_sensitive,
        image_viewer=image_viewer,
        relative_timestamps=relative_timestamps,
        streaming=streaming,
        timeline_refresh=timeline_refresh,
    )

    # Streaming is not reliable, so if it's enabled, force timeline_refresh to be enabled as well;
    # this catches any events that streaming missed.
    if options.streaming and not options.timeline_refresh:
        options.timeline_refresh = 120

    if env:
        print_env(options)
        return

    app = TooiApp(options)
    app.run()


def main():
    logging.basicConfig(level=logging.INFO, handlers=[TextualHandler()])
    logging.getLogger("http").setLevel(logging.WARNING)
    tooi()


def print_env(options: Options):
    click.echo(f"tooi v{__version__}")
    click.echo(f"Python {platform.python_version()}")
    click.echo(f"{platform.platform()}")
    click.echo()

    click.secho("## Files & cache", underline=True)
    click.echo()

    cache_dir = get_cache_dir()
    cache_size = format_size(dir_size(cache_dir))
    click.echo(f"Cache dir: {get_cache_dir()} ({cache_size})")

    credentials_path = get_credentials_path()
    click.echo(f"Credentials: {credentials_path}")

    settings_path = get_settings_path()
    settings_exists = path.exists(settings_path)
    click.echo(f"Settings: {settings_path} ({'found' if settings_exists else 'not found'})")

    stylesheet_path = get_stylesheet_path()
    stylesheet_exists = path.exists(stylesheet_path)
    click.echo(f"Stylesheet: {stylesheet_path} ({'found' if stylesheet_exists else 'not found'})")
    click.echo()

    click.secho("## Options", underline=True)
    click.echo()
    for k, v in options.model_dump().items():
        click.echo(f"{k} = {v}")
    click.echo()

    image_support = get_image_support()
    click.secho("## Image support", underline=True)
    click.echo()
    click.echo(f"TGP (Kitty) images: {image_support.tgp_supported}")
    click.echo(f"Sixel images: {image_support.sixel_supported}")
    click.echo(f"Is TTY: {image_support.is_tty}")
    click.echo(f"Default: {image_support.default}")

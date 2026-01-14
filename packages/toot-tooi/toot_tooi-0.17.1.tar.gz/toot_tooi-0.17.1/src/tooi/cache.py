import asyncio
import logging
import shutil
import tempfile
from hashlib import sha256
from pathlib import Path
from urllib.parse import urlparse

from aiohttp import ClientSession
from platformdirs import user_cache_path

from tooi import APP_NAME

logger = logging.getLogger(__name__)


def get_cache_dir() -> Path:
    return user_cache_path(APP_NAME, ensure_exists=True)


def get_images_cache_dir() -> Path:
    cache_dir = get_cache_dir() / "images"
    cache_dir.mkdir(exist_ok=True)
    return cache_dir


# TODO: limit cache size to a reasonable amount
# TODO: use async file access
async def download_image_cached(url: str) -> Path:
    target_path = image_cache_path(url)

    if not target_path.exists():
        logger.debug(f"Downloading image {url} to {target_path}")

        async with ClientSession() as session:
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                async with session.get(url) as response:
                    response.raise_for_status()
                    async for chunk in response.content.iter_chunked(128 * 1024):
                        tmp.write(chunk)
            shutil.move(tmp.name, target_path)

    return target_path


async def download_images_cached(urls: list[str]) -> list[Path]:
    downloads = [download_image_cached(url) for url in urls]
    return await asyncio.gather(*downloads)


def image_cache_path(url: str) -> Path:
    cache_dir = get_images_cache_dir()
    path = urlparse(url).path
    suffix = Path(path).suffix
    url_hash = sha256(url.encode()).hexdigest()
    filename = url_hash + suffix
    return cache_dir / filename

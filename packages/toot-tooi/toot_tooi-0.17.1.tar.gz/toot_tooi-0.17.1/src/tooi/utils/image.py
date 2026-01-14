from dataclasses import dataclass
from enum import StrEnum, auto
from textual_image.renderable import Image, is_tty
from textual_image.renderable import sixel, tgp
from textual_image.renderable.halfcell import Image as HalfcellImage
from textual_image.renderable.sixel import Image as SixelImage
from textual_image.renderable.tgp import Image as TGPImage
from textual_image.renderable.unicode import Image as UnicodeImage


class ImageType(StrEnum):
    sixel = auto()
    tgp = auto()
    halfcell = auto()
    unicode = auto()


@dataclass
class ImageSupport:
    tgp_supported: bool
    sixel_supported: bool
    is_tty: bool
    default: ImageType | None


def get_image_support() -> ImageSupport:
    if Image is SixelImage:
        default = ImageType.sixel
    elif Image is TGPImage:
        default = ImageType.tgp
    elif Image is HalfcellImage:
        default = ImageType.halfcell
    elif Image is UnicodeImage:
        default = ImageType.unicode
    else:
        default = None  # improbable

    return ImageSupport(
        tgp_supported=tgp.query_terminal_support(),
        sixel_supported=sixel.query_terminal_support(),
        is_tty=is_tty or False,
        default=default,
    )

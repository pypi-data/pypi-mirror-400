"""
PET util package.

Textbook compatibility expects:

    from pet.util import audio
    audio.say("...")

Other legacy modules (audio_tools/image_tools/tools) are preserved as thin wrappers.
"""
from __future__ import annotations

from . import audio  # module export for textbook
from .audio import say, str_to_mp3, file2mp3, combine_mp3file, overlay_mp3file
from .identity import id_card_to_age
from .image import img_to_ndarray, img_info, file_to_img, ndarray_to_img, save

__all__ = [
    "audio",
    "say",
    "str_to_mp3",
    "file2mp3",
    "combine_mp3file",
    "overlay_mp3file",
    "id_card_to_age",
    "img_to_ndarray",
    "img_info",
    "file_to_img",
    "ndarray_to_img",
    "save",
]

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Union

import numpy as np


def _require_pillow():
    try:
        from PIL import Image  # type: ignore
        return Image
    except Exception as e:
        raise ImportError("Image utilities require 'Pillow'. Install via: pip install pillow") from e


def img_to_ndarray(filename: Union[str, Path]) -> np.ndarray:
    Image = _require_pillow()
    return np.array(Image.open(str(filename)))


def img_info(filename: Union[str, Path]) -> Dict[str, Any]:
    Image = _require_pillow()
    image = Image.open(str(filename))
    return dict(format=image.format, size=image.size, mode=image.mode)


def file_to_img(filename: Union[str, Path]):
    Image = _require_pillow()
    return Image.open(str(filename))


def ndarray_to_img(ndar: np.ndarray):
    Image = _require_pillow()
    return Image.fromarray(ndar)


def save(img, out_filename: Union[str, Path]) -> None:
    img.save(str(out_filename))

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Optional, Union

from ._audio_engine import get_engine


def say(contents: str, echo: bool = False) -> None:
    """
    Text-to-speech for a given string.

    Textbook compatibility:
      from pet.util import audio
      audio.say("...")
    """
    engine = get_engine()
    engine.say(contents)
    if echo:
        print(contents)
    engine.runAndWait()


def str_to_mp3(contents: str, filename: Union[str, Path] = 'pet.mp3', echo: bool = True) -> Path:
    """
    Convert a string to an mp3 file (best effort).

    Note: pyttsx3 itself may output wav depending on platform. This helper keeps
    the original interface but does not guarantee codec availability.
    """
    engine = get_engine()
    filename = Path(filename)
    if echo:
        print(contents)
    try:
        engine.save_to_file(contents, str(filename))
        engine.runAndWait()
    except Exception as e:
        raise RuntimeError(f"Failed to generate audio file: {filename}") from e
    return filename


def file2mp3(text_file: Union[str, Path], filename: Optional[Union[str, Path]] = None, encoding: str = "utf-8") -> Path:
    """
    Read a text file and convert it to mp3.
    """
    text_file = Path(text_file)
    if filename is None:
        filename = text_file.with_suffix(".mp3")
    contents = text_file.read_text(encoding=encoding, errors="ignore")
    return str_to_mp3(contents, filename=filename, echo=False)


def combine_mp3file(files: Iterable[Union[str, Path]], out: Union[str, Path] = "combined.mp3") -> Path:
    """
    Concatenate multiple mp3 files.
    Requires: pydub (and typically ffmpeg on the system).
    """
    try:
        from pydub import AudioSegment  # type: ignore
    except Exception as e:
        raise ImportError("combine_mp3file requires 'pydub'. Install via: pip install pydub") from e

    segments = []
    for f in files:
        f = Path(f)
        segments.append(AudioSegment.from_mp3(str(f)))
    combined = segments[0]
    for seg in segments[1:]:
        combined += seg
    out = Path(out)
    combined.export(str(out), format="mp3")
    return out


def overlay_mp3file(f1: Union[str, Path], f2: Union[str, Path], out: Union[str, Path] = "overlay.mp3") -> Path:
    """
    Overlay two mp3 files.
    Requires: pydub (and typically ffmpeg on the system).
    """
    try:
        from pydub import AudioSegment  # type: ignore
    except Exception as e:
        raise ImportError("overlay_mp3file requires 'pydub'. Install via: pip install pydub") from e

    sounds = [AudioSegment.from_mp3(str(Path(i))) for i in [f1, f2]]
    sound = sounds[0].overlay(sounds[1])
    out = Path(out)
    sound.export(str(out), format="mp3")
    return out

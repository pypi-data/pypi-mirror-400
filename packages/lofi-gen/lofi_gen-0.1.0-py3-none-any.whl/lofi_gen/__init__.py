"""lofi-gen: A Python package for generating Lofi music using AI models."""

from lofi_gen.music.models import MusicGenModel, BaseMusicGenModel
from lofi_gen.music.pipelines import LongMusicGenerator

__version__ = "0.1.0"

__all__ = [
    "MusicGenModel",
    "BaseMusicGenModel",
    "LongMusicGenerator",
    "__version__",
]

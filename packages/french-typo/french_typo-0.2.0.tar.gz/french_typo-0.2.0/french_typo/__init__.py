from pathlib import Path

__version__ = Path(__file__).resolve().parent.parent.joinpath("VERSION").read_text().strip()

from .formatter import format_text

__all__ = ["format_text"]

from .note import Note
from .synthesizer import Synthesizer
from .wave import Wave

__all__ = ["Note", "Synthesizer", "Wave"]

if __name__ == "__main__":
    raise ImportError("Cannot run this module, must be imported by another program or module")

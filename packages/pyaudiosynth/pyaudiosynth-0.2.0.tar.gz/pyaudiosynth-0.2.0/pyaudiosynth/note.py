from dataclasses import dataclass
from .wave import Wave

@dataclass
class Note:
    """
    A class for holding note information

    :param name: The note name to play (piano note)
    :type name: str
    :param ms: The length to play the note for in milliseconds (optional, defaults to Synthesizer default_nlen)
    :type ms: float | None
    :param wave: The waveform to play (optional, defaults to Synthesizer default_wave)
    :type wave: Wave | None
    """

    name: str
    ms: float|None = None
    wave: Wave|None = None

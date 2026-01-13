from dataclasses import dataclass
from .wave import Wave

@dataclass
class Note:
    name: str
    ms: float|None = None
    wave: Wave|None = None

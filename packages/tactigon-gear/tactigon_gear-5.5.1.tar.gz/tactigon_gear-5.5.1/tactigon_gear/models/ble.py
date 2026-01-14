from enum import Enum
from dataclasses import dataclass

class BLESelector(Enum):
    NONE = 0
    SENSORS = 1
    AUDIO = 2

class BLECommands(Enum):
    WRITE = 1
    READ = 2

class BLECommandWord(Enum):
    UPDATE_TOUCH1       = 0x41
    UPDATE_TOUCH2       = 0x42
    WRITE_TOUCH         = 0x43
    START               = 0x00
    STOP                = 0x01
    STATUS              = 0xFF

class BLECommandMask(Enum):
    SENSORFUSION        = b'\x00\x00\x01\x00'
    ECOMPASS            = b'\x00\x00\x00\x40'

@dataclass
class BLECommand:
    command: BLECommands
    characteristic: str
    payload: bytes | None = None
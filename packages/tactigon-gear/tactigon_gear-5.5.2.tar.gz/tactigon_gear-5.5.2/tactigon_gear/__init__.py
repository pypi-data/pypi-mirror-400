__version__ = "5.5.2"

__all__ = [
    "TSkin", "TSkinSocket",
    "BLESelector",
    "TSkinConfig", "Hand", "Acceleration", "Angle", "Gyro",
    "TouchConfig", "OneFingerGesture", "TwoFingerGesture",
    "GestureConfig", "Gesture",
    "VoiceConfig", "TSpeechObject", "TSpeech", "HotWord", "Transcription",
    "SocketConfig"
]

from .tskin import TSkin
from .tskin_socket import TSkinSocket

from .models.ble import BLESelector
from .models.tskin import TSkinConfig, Hand, Acceleration, Angle, Gyro
from .models.touch import TouchConfig, OneFingerGesture, TwoFingerGesture
from .models.gesture import GestureConfig, Gesture
from .models.audio import VoiceConfig, TSpeechObject, TSpeech, HotWord, Transcription
from .models.socket import SocketConfig
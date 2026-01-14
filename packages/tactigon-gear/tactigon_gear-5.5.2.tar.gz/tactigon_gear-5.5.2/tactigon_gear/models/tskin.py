from dataclasses import dataclass
from enum import Enum

from .ble import BLESelector
from .gesture import GestureConfig, Gesture
from .touch import TouchConfig, OneFingerGesture, TwoFingerGesture

class Hand(Enum):
    RIGHT = "right"
    LEFT = "left"

@dataclass
class Acceleration:
    x: float
    y: float
    z: float

    def toJSON(self) -> dict:
        return {
            "x": self.x,
            "y": self.y,
            "z": self.z,
        }

@dataclass
class Angle:
    roll: float
    pitch: float
    yaw: float

    def toJSON(self) -> dict:
        return {
            "roll": self.roll,
            "pitch": self.pitch,
            "yaw": self.yaw,
        }

@dataclass
class Gyro:
    x: float
    y: float
    z: float

    def toJSON(self) -> dict:
        return {
            "x": self.x,
            "y": self.y,
            "z": self.z,
        }

@dataclass
class Touch:
    one_finger: OneFingerGesture
    two_finger: TwoFingerGesture
    x_pos: float
    y_pos: float

    def __eq__(self, __value: object) -> bool:
        if isinstance(__value, Touch):
            return (
                self.one_finger == __value.one_finger 
                and self.two_finger == __value.two_finger
                and self.x_pos == __value.x_pos
                and self.y_pos == __value.y_pos
            )
        
        return False
    
    def toJSON(self) -> dict:
        return {
            "one_finger": self.one_finger.value,
            "two_finger": self.two_finger.value,
            "x_pos": self.x_pos,
            "y_pos": self.y_pos
        }
    
@dataclass
class TSkinState:
    connected: bool
    sleep: bool
    battery: float | None
    selector: BLESelector | None
    touch: Touch | None
    angle: Angle | None
    gesture: Gesture | None

    def toJSON(self) -> dict:
        return {
            "connected": self.connected,
            "sleep": self.sleep,
            "battery": self.battery,
            "selector": self.selector.value if self.selector else None,
            "touch": self.touch.toJSON() if self.touch else None,
            "angle": self.angle.toJSON() if self.angle else None,
            "gesture": self.gesture.toJSON() if self.gesture else None,
        }
    

@dataclass
class TSkinConfig:
    address: str
    hand: Hand
    name: str = "Tactigon"
    touch_config: TouchConfig | None = None
    gesture_config: GestureConfig | None = None

    @classmethod
    def FromJSON(cls, json: dict):
        return cls(
            json["address"], 
            Hand(json["hand"]),
            json["name"] if "name" in json else cls.name,
            TouchConfig.FromJSON(json["touch_config"]) if "touch_config" in json and json["touch_config"] is not None else None,
            GestureConfig.FromJSON(json["gesture_config"]) if "gesture_config" in json and json["gesture_config"] is not None else None,
        )
    
    def toJSON(self) -> dict:
        return {
            "address": self.address,
            "hand": self.hand.value,
            "name": self.name,
            "touch_config": self.touch_config.toJSON() if self.touch_config else None,
            "gesture_config": self.gesture_config.toJSON() if self.gesture_config else None,
        }
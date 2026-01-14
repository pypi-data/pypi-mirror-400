import operator
import struct
from dataclasses import dataclass
from enum import Enum
from functools import reduce


from .ble import BLECommandWord

class OneFingerGesture(Enum):
    NONE = 0x00
    SINGLE_TAP = 0x01
    TAP_AND_HOLD = 0x02
    SWIPE_X_NEG = 0x04
    SWIPE_X_POS = 0x08
    SWIPE_Y_NEG = 0x20
    SWIPE_Y_POS = 0x10

class TwoFingerGesture(Enum):
    NONE = 0x00
    TWO_FINGER_TAP = 0x01
    SCROLL = 0x02
    ZOOM = 0x04

@dataclass
class TouchConfig:
    FORMAT_CFG1 = ">BBHHHHBHBHHH"
    FORMAT_CFG2 = ">BBHHHBBHHHHH"
    FORMAT_CMD  = ">BBHHHHHHHHH"

    swipe_initial_time: int
    swipe_initial_distance: int
    swipe_consecutive_time: int
    swipe_consecutive_distance: int
    swipe_angle: int
    scroll_initial_distance: int
    scroll_angle: int
    zoom_initial_distance: int
    zoom_consecutive_distance: int
    tap_time: int
    tap_distance: int
    hold_time: int
    one_finger_gesture: list[OneFingerGesture]
    two_finger_gesture: list[TwoFingerGesture]

    @classmethod
    def FromJSON(cls, json):
        return cls(
            json["swipe_initial_time"],
            json["swipe_initial_distance"],
            json["swipe_consecutive_time"],
            json["swipe_consecutive_distance"],
            json["swipe_angle"],
            json["scroll_initial_distance"],
            json["scroll_angle"],
            json["zoom_initial_distance"],
            json["zoom_consecutive_distance"],
            json["tap_time"],
            json["tap_distance"],
            json["hold_time"],
            [OneFingerGesture(f) for f in json["one_finger_gesture"]],
            [TwoFingerGesture(f) for f in json["two_finger_gesture"]],
        )
    
    @classmethod
    def Default(cls):
        return cls(
            swipe_initial_time=200,
            swipe_initial_distance=25,
            swipe_consecutive_time=150,
            swipe_consecutive_distance=25,
            swipe_angle=23,
            scroll_initial_distance=50,
            scroll_angle=37,
            zoom_initial_distance=50,
            zoom_consecutive_distance=5,
            tap_time=300,
            tap_distance=75,
            hold_time=10,
            one_finger_gesture=[OneFingerGesture.SINGLE_TAP, OneFingerGesture.TAP_AND_HOLD],
            two_finger_gesture=[TwoFingerGesture.TWO_FINGER_TAP]
        )
    
    @classmethod
    def High(cls):
        c = cls.Default()
        c.tap_time = 150
        c.tap_distance = 50
        return c

    @classmethod
    def Medium(cls):
        return cls.Default()

    @classmethod
    def Low(cls):
        c = cls.Default()
        c.tap_time = 600
        c.tap_distance = 150
        c.hold_time = 50
        return c

    def toJSON(self):
        return {
            "swipe_initial_time": self.swipe_initial_time,
            "swipe_initial_distance": self.swipe_initial_distance,
            "swipe_consecutive_time": self.swipe_consecutive_time,
            "swipe_consecutive_distance": self.swipe_consecutive_distance,
            "swipe_angle": self.swipe_angle,
            "scroll_initial_distance": self.scroll_initial_distance,
            "scroll_angle": self.scroll_angle,
            "zoom_initial_distance": self.zoom_initial_distance,
            "zoom_consecutive_distance": self.zoom_consecutive_distance,
            "tap_time": self.tap_time,
            "tap_distance": self.tap_distance,
            "hold_time": self.hold_time,
            "one_finger_gesture": [ofg.value for ofg in self.one_finger_gesture],
            "two_finger_gesture": [tfg.value for tfg in self.two_finger_gesture],
        }

    def set_sensitivity(self, sensitivity: int):
        if sensitivity == 1:
            self.tap_time = 600
            self.tap_distance = 150
            self.hold_time = 50
        elif sensitivity == 2:
            self.tap_time = 300
            self.tap_distance = 75
        else:
            self.tap_time = 150
            self.tap_distance = 50

    def toBytes(self) -> tuple[bytes, bytes, bytes]:
        cfg1 = struct.pack(self.FORMAT_CFG1,
            BLECommandWord.UPDATE_TOUCH1.value,
            16,
            self.swipe_initial_time,
            self.swipe_initial_distance,
            self.swipe_consecutive_time,
            self.swipe_consecutive_distance,
            self.swipe_angle,
            self.scroll_initial_distance,
            self.scroll_angle,
            self.zoom_initial_distance,
            self.zoom_consecutive_distance,
            0
        )

        cfg2 = struct.pack(self.FORMAT_CFG2,
            BLECommandWord.UPDATE_TOUCH2.value,
            8,
            self.tap_time,
            self.tap_distance,
            self.hold_time,
            reduce(operator.ior, [g.value for g in self.one_finger_gesture]) if self.one_finger_gesture else 0,
            reduce(operator.ior, [g.value for g in self.two_finger_gesture]) if self.two_finger_gesture else 0,
            0,
            0,
            0,
            0,
            0,
        )

        save = struct.pack(self.FORMAT_CMD, BLECommandWord.WRITE_TOUCH.value,1,0,0,0,0,0,0,0,0,0)
        return cfg1, cfg2, save

    def update(self, cfg1: bytes, cfg2: bytes):
        word_cfg1, length_cfg1, *data_cfg1 = struct.unpack(self.FORMAT_CFG1, cfg1)
        word_cfg2, length_cfg2, *data_cfg2 = struct.unpack(self.FORMAT_CFG2, cfg2)

        if BLECommandWord(word_cfg1) != BLECommandWord.UPDATE_TOUCH1 or \
            BLECommandWord(word_cfg2) != BLECommandWord.UPDATE_TOUCH2 or \
            length_cfg1 != 16 or \
            length_cfg2 != 8:
            return False

        self.swipe_initial_time = data_cfg1[0]
        self.swipe_initial_distance = data_cfg1[1]
        self.swipe_consecutive_time = data_cfg1[2]
        self.swipe_consecutive_distance = data_cfg1[3]
        self.swipe_angle = data_cfg1[4]
        self.scroll_initial_distance = data_cfg1[5]
        self.scroll_angle = data_cfg1[6]
        self.zoom_initial_distance = data_cfg1[7]
        self.zoom_consecutive_distance = data_cfg1[8]
        self.tap_time = data_cfg2[0]
        self.tap_distance = data_cfg2[1]
        self.hold_time = data_cfg2[2]
        self.one_finger_gesture = [g for g in OneFingerGesture if bool(g.value & data_cfg2[3])]
        self.two_finger_gesture = [g for g in TwoFingerGesture if bool(g.value & data_cfg2[4])]

        return True
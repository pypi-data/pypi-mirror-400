from os import path
from dataclasses import dataclass, field
from typing import List

from .tskin import Hand

@dataclass
class UserData:
    user_id: str
    auth_key: str

    @classmethod
    def FromJSON(cls, json):
        return cls(**json)


@dataclass
class ClientConfig:
    MODEL_NAME: str
    SERVER_URL: str

    MODEL_GESTURES: List[str] = field(default_factory=list)
    MODEL_SPLIT_RATIO: float = 0.3
    MODEL_DATA_PATH: str = "data/models/"
    MODEL_SESSIONS: List[str] = field(default_factory=list)

    TRAINING_SESSIONS: List[str] = field(default_factory=list)

    @property
    def model_data_full_path(self):
        return path.join(self.MODEL_DATA_PATH, self.MODEL_NAME)
    
    @classmethod
    def FromJSON(cls, json):
        return cls(
            json["MODEL_NAME"],
            json["SERVER_URL"],
            json["MODEL_GESTURES"] if "MODEL_GESTURES" in json and json["MODEL_GESTURES"] is not None else [],
            json["MODEL_SPLIT_RATIO"] if "MODEL_SPLIT_RATIO" in json and json["MODEL_SPLIT_RATIO"] is not None else 0.3,
            json["MODEL_DATA_PATH"] if "MODEL_DATA_PATH" in json and json["MODEL_DATA_PATH"] is not None else "data/models/",
            json["MODEL_SESSIONS"] if "MODEL_SESSIONS" in json and json["MODEL_SESSIONS"] is not None else [],
            json["TRAINING_SESSIONS"] if "TRAINING_SESSIONS" in json and json["TRAINING_SESSIONS"] is not None else [],
        )


@dataclass
class DataCollectionConfig:
    SESSION_INFO: str
    HAND: Hand
    GESTURE_NAME: List[str]
    RAW_DATA_PATH: str = "data/raw"

    @property
    def raw_data_full_path(self) -> str:
        return path.join(self.RAW_DATA_PATH)

    @classmethod
    def FromJSON(cls, json):
        return cls(
            json["SESSION_INFO"],
            Hand(json["HAND"]),
            json["GESTURE_NAME"],
            json["RAW_DATA_PATH"] if "RAW_DATA_PATH" in json and json["RAW_DATA_PATH"] is not None else "data/raw"
        )
    

@dataclass
class HAL:
    ADDRESS: str
    NUM_SAMPLE: int = 10

    @classmethod
    def FromJSON(cls, json: dict):
        return cls(
            json["ADDRESS"],
            json["NUM_SAMPLE"] if "NUM_SAMPLE" in json and json["NUM_SAMPLE"] is not None else 10
        )
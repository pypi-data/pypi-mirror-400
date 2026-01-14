from datetime import datetime
from dataclasses import dataclass

@dataclass
class Gesture:
    gesture: str
    probability: float
    confidence: float
    displacement: float

    def toJSON(self) -> dict:
        return {
            "gesture": self.gesture,
            "probability": self.probability,
            "confidence": self.confidence,
            "displacement": self.displacement,
        }

@dataclass
class GestureConfig:
    model_path: str
    encoder_path: str
    name: str
    created_at: datetime
    num_sample: int = 10
    gesture_prob_th: float = 0.85
    confidence_th: float = 5

    @classmethod
    def FromJSON(cls, json: dict):
        return cls(
            json["model_path"],
            json["encoder_path"],
            json["name"],
            datetime.fromisoformat(json["created_at"]),
            json["num_sample"] if "num_sample" in json and json["num_sample"] is not None else cls.num_sample,
            json["gesture_prob_th"] if "gesture_prob_th" in json and json["gesture_prob_th"] is not None else cls.gesture_prob_th,
            json["confidence_th"] if "confidence_th" in json and json["confidence_th"] is not None else cls.confidence_th,
            )
    
    def toJSON(self) -> dict:
        return {
            "model_path": self.model_path,
            "encoder_path": self.encoder_path,
            "name": self.name,
            "created_at": self.created_at.isoformat()
        }
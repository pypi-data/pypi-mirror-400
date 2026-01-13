from os import path
from dataclasses import dataclass
from enum import Enum

from typing import List, Dict, Union, Optional

SAMPLE_RATE = 16000
SAMPLE_WIDTH = 2
N_CHANNELS = 1
AUDIO_FRAME_LENGTH = 80

@dataclass
class TactigonSpeechResponse:
    complete: bool
    payload: Dict

@dataclass
class HotWord:
    word: str
    boost: int = 1

    @classmethod
    def FromJSON(cls, config):
        return cls(config["word"], config["boost"])
    
    @classmethod
    def FromBytes(cls, data: bytes):
        return cls(
            "".join([chr(c) for c in data[1::]]),
            int.from_bytes(data[0:1], byteorder="big")
        )
    
    def toJSON(self) -> object:
        return {
            "word": self.word,
            "boost": self.boost
        }
    
    def toBytes(self) -> bytes:
        return self.boost.to_bytes(1, 'big') + bytes([ord(c) for c in self.word])

class TSpeech:
    hotwords: List[HotWord]
    children: "TSpeechObject | None"

    def __init__(self, hotwords: Union[List[HotWord], HotWord], children: "TSpeechObject | None" = None):
        self.hotwords = hotwords if isinstance(hotwords, list) else [hotwords]
        self.children = children

    @classmethod
    def FromJSON(cls, json_obj, feedback_audio_path = ""):
        try:
            children = json_obj["children"]
        except:
            children = None

        return cls(
            [HotWord.FromJSON(hw) for hw in json_obj.get("hotwords", [])],
            children=TSpeechObject.FromJSON(children, feedback_audio_path) if children else None,
        )
    
    @classmethod
    def FromBytes(cls, data: bytes, level: int = 0):
        end = child_index = data.find(b"|")

        if end == -1:
            end = len(data)

        print(child_index, data, data[:end], data[child_index+1:])
        return cls(
            [HotWord.FromBytes(hw) for hw in data[:end].split(b',')],
            TSpeechObject.FromBytes(data[child_index+1:], level + 1) if child_index > -1 else None
        )

    @property
    def has_children(self):
        return self.children
    
    def toJSON(self) -> dict:
        return {
            "hotwords": [hw.toJSON() for hw in self.hotwords],
            "children": self.children.toJSON() if self.children else None
        }
    
    def toBytes(self, level: int = 0):
        return b','.join([hw.toBytes() for hw in self.hotwords]) + (b'|' + self.children.toBytes(level + 1) if self.children else b'')

class TSpeechObject:
    t_speech: List[TSpeech]
    feedback: str

    def __init__(self, t_speech: List[TSpeech], feedback: str = ""):
        self.t_speech = t_speech
        self.feedback = feedback

    @staticmethod
    def is_valid_json(json: Dict) -> bool:
        return "t_speech" in json

    @classmethod
    def FromJSON(cls, json_obj, feedback_audio_path = "") -> Optional["TSpeechObject"]:
        if not TSpeechObject.is_valid_json(json_obj):
            return None

        try:
            feedback = path.join(feedback_audio_path, json_obj["feedback"])
        except:
            feedback = ""

        return cls(
            [TSpeech.FromJSON(t, feedback_audio_path) for t in json_obj.get("t_speech", [])],
            feedback=feedback
        )
    
    @classmethod
    def FromBytes(cls, data: bytes, level: int = 0):
        sep = b'-' + level.to_bytes(1, 'big')
        return cls(
            [TSpeech.FromBytes(ts, level) for ts in data.rsplit(sep)]
        )
    
    def toJSON(self) -> dict:
        return {
            "t_speech": [ts.toJSON() for ts in self.t_speech],
            "feedback": self.feedback
        }
    
    def toBytes(self, level: int = 0) -> bytes:
        return (b'-'+ level.to_bytes(1, 'big')).join([ts.toBytes(level) for ts in self.t_speech])

class TStreamStatus(Enum):
    STREAMING = 1
    STOPPED = 2

@dataclass
class Transcription:
    text: str
    path: List[HotWord]
    time: float
    timeout: bool

    @classmethod
    def FromJSON(cls, json: dict):
        return cls(
            text=json.get("text", ""),
            path=[HotWord.FromJSON(hw) for hw in json.get("path", [])],
            time=json.get("time", 0),
            timeout=json.get("payload", True)
        )


    def toJSON(self) -> dict:
        return {
            "text": self.text,
            "path": [hw.toJSON() for hw in self.path] if self.path else [],
            "time": self.time,
            "timeout": self.timeout
        }
    
@dataclass
class VoiceConfig:
    model: str
    scorer: Union[str, None] = None
    beam_width: int = 1024
    voice_timeout: int = 5
    silence_timeout: int = 3

    stop_hotword: Union[HotWord, None] = None

    @property
    def model_full_path(self) -> str:
        return path.join(self.model)
    
    @property
    def scorer_full_path(self) -> Union[str, None]:
        if self.scorer is None:
            return None
        
        return path.join(self.scorer)

    @classmethod
    def FromJSON(cls, json: dict):
        return cls(
            json["model"],
            json.get("scrore", None),
            json.get("beam_width", 1024),
            json.get("voice_timeout", 8),
            json.get("silence_timeout", 3),
        )
    
    def toJSON(self) -> dict:
        return {
            "model": self.model,
            "scorer": self.scorer,
            "beam_width": self.beam_width,
            "voice_timeout": self.voice_timeout,
            "silence_timeout": self.silence_timeout
        }
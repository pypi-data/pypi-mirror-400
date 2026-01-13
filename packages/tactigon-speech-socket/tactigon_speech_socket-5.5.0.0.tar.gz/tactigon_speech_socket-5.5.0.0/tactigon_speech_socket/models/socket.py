from enum import Enum
from dataclasses import dataclass

class SocketEvent(Enum):
    CLIENT_CONNECT      = 1
    CLIENT_RECEIVE      = 2

    COMMAND_RECV        = 3
    AUDIO_RECV           = 4

class SocketCommand(Enum):
    DISCONNECTED        = b''
    ACK                 = int(1).to_bytes(1, 'big', signed=False)
    LISTEN              = int(2).to_bytes(1, 'big', signed=False)
    RECORD              = int(4).to_bytes(1, 'big', signed=False)
    PLAY                = int(5).to_bytes(1, 'big', signed=False)
    TEXT_SO_FAR         = int(6).to_bytes(1, 'big', signed=False)
    AUDIO               = int(7).to_bytes(1, 'big', signed=False)
    RESULT              = int(8).to_bytes(1, 'big', signed=False)
    STOP                = int(254).to_bytes(1, 'big', signed=False)

@dataclass
class SocketConfig:
    host: str
    port: int = 50007
    ping: int = 5

    @classmethod
    def FromJSON(cls, json):
        return cls(
            json["host"],
            json["port"] if "port" in json else cls.port,
            json["ping"] if "ping" in json else cls.ping,
        )

def get_or_default(json: dict, name: str, default):
    try:
        return json[name]
    except:
        return default
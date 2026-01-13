# Tactigon Speech Socket

![The tactigon team](https://avatars.githubusercontent.com/u/63020285?s=200&v=4)

This package enables the wearable device Tactigon Skin to stream audio to a stt middleware over a socket connection

## Prerequisites
In order to use the Tactigon Gear SDK the following prerequisites needs to be observed:

* Python version: following versions has been used and tested. It is STRONGLY recommended to use these ones depending on platform.
  * Linux: 3.8.x

## Installing

Install and update using pip:

`pip install tactigon-speech-socket`

## A Simple Example

```python

import setup_path
import logging
# from tactigon_socket import SocketClient

from tactigon_speech_socket import TSkinSpeech
from tactigon_speech_socket.models.audio import VoiceConfig

logging.basicConfig(
    filename="receive.log",
    level=logging.DEBUG
)

def main():
    voice_config = VoiceConfig(
        "deepspeech-0.9.3-models.tflite",
        "my_Scorer_file.scorer"
    )
    try:
        ts = TSkinSpeech("localhost", 50006, voice_config)
        ts.start()
    except KeyboardInterrupt:
        pass
    finally:
        ts.join()


if __name__ == "__main__":
    main()
```

## Links
- [Tactigon SOUL](https://github.com/TactigonTeam/Tactigon-Soul/wiki)
- [SDK](https://github.com/TactigonTeam/Tactigon-SDK)
- [Documentation](https://github.com/TactigonTeam/Tactigon-SDK/wiki)
- [Blog](https://www.thetactigon.com/blog/)
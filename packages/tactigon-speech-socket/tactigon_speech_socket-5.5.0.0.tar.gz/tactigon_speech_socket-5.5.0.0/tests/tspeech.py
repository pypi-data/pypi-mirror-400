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
        "shapes.scorer"
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
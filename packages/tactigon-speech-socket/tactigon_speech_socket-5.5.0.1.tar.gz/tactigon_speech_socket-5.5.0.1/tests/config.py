import setup_path
import logging
import json

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

    with open("tests/voice_config.json", "w") as cfg_file:
        json.dump(voice_config.toJSON(), cfg_file, indent=4)

if __name__ == "__main__":
    main()
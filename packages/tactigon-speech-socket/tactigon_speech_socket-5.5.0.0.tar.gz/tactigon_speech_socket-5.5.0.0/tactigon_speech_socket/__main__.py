import logging
import argparse
import signal
import json
from tactigon_speech_socket import TSkinSpeech
from tactigon_speech_socket.models.audio import VoiceConfig

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

def run():
    parser = argparse.ArgumentParser("Tactigon Speech over Socket")
    parser.add_argument("-c", "--config", help="Voice configuration file", type=str, required=True)
    parser.add_argument("-a", "--address", help="Server address", type=str, default="0.0.0.0")
    parser.add_argument("-p", "--port", help="Server port", type=int, default=50006)
    args = parser.parse_args()

    with open(args.config) as cfg_file:
        voice_config = VoiceConfig.FromJSON(json.load(cfg_file))

    server = TSkinSpeech(args.address.strip(), args.port, voice_config)

    signal.signal(signal.SIGTERM, lambda s, h: server.join())
    signal.signal(signal.SIGINT, lambda s, h: server.join())

    try:
        server.start()
    except KeyboardInterrupt:
        server.join()

if __name__ == "__main__":
    run()
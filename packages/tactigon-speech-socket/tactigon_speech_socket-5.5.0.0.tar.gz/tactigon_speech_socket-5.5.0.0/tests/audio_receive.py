import setup_path
import logging
# from tactigon_socket import SocketClient

from tactigon_speech_socket.connection.client import Client

logging.basicConfig(
    # filename="receive.log",
    level=logging.DEBUG
)

def main():
    with Client("localhost", 50006) as c:
        input()


if __name__ == "__main__":
    main()
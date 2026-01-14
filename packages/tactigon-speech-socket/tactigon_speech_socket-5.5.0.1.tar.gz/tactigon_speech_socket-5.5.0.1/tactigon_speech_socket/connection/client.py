import time
import selectors
import socket
import logging
from threading import Thread, Event

from typing import Union, List, Dict, Optional

from ..models.socket import SocketCommand
from ..middleware.packet_manager import PacketManager

class Client(Thread):
    _client: socket.socket
    _stop_event: Event

    _connected: bool = False

    def __init__(self, url: str, port: int):
        Thread.__init__(self)
        self._stop_event = Event()
        self._address = (url, port)
        self._logger = logging.getLogger(Client.__name__)
        self._packet_manager = PacketManager(self._logger)

    @property
    def connected(self) -> bool:
        return self._connected

    def run(self):
        self._logger.debug("Started!")
        
        while not self._stop_event.is_set():
            selector = selectors.EpollSelector()
            _client_key: Optional[selectors.SelectorKey] = None

            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self._client:
                try:
                    self._client.connect(self._address)
                    self._logger.debug("Connected to %s", self._address)

                    _client_key = selector.register(self._client, selectors.EVENT_READ)

                    while not self._stop_event.is_set():
                        events = selector.select(0.1)
                        for key, mask in events:
                            if key == _client_key:
                                packet_size = self._packet_manager.recv_bytes(self._client, 4)
                                bufsize = int.from_bytes(packet_size, byteorder="big", signed=False)
                                # self._logger.debug("Packet size %s", bufsize)
                                packet_body = self._packet_manager.recv_bytes(self._client, bufsize)
                                # self._logger.debug("Packet body %s", packet_body)
                                command, payload = self._packet_manager.unpack_command(packet_body)
                                # self._logger.debug("Got command %s", command)
                                self.task(command, payload)

                    selector.unregister(self._client)

                except Exception as e:
                    if _client_key:
                        selector.unregister(self._client)
                    self._logger.error(e)

            selector.close()
            time.sleep(1)

        self._logger.debug("Stopped!")

    def __enter__(self):
        self.start()
        return self
    
    def __exit__(self, *args, **kwargs):
        self.join()
        
    def task(self, command: SocketCommand, payload: Union[Dict, List[bytes]]):
        pass

    def send(self, command: SocketCommand, payload: Union[Dict, List[bytes]]):
        try:
            self._client.send(self._packet_manager.pack_command(command, payload))
        except Exception as e:
            self._logger.error("Cannot send command %s", e)

    def join(self, timeout: Optional[float] = None):
        self._logger.debug("Called stop...")
        self._stop_event.set()
        Thread.join(self, timeout)
        self._logger.debug("Joined!")



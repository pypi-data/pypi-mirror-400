__version__ = "5.5.0.0"

import logging
import time
from collections import deque
from typing import Any, Optional, List, Union, Dict
from threading import Event


from .models.audio import VoiceConfig
from .models.socket import SocketCommand
from .connection.client import Client
from .middleware.tactigon_speech import TactigonSpeech

class TSkinSpeech:
    _stop_event: Event
    _logger: logging.Logger
    _client: Client
    _tactigon_speech: TactigonSpeech

    _audio_buffer: deque
    _command: Optional[SocketCommand]
    _ack_sent: bool
    _payload: Any

    def __init__(self, url: str, port: int, config: VoiceConfig):
        self._stop_event = Event()
        self._logger = logging.getLogger(TSkinSpeech.__name__)
        self._client = Client(url, port)

        self._audio_buffer = deque()

        self._tactigon_speech = TactigonSpeech(config)

        self._client.task = self.on_data
        self._command = None
        self._ack_sent = False
        self._logger.debug("Created!")

    def start(self):
        self._client.start()
        self._tactigon_speech.start()
        self._logger.debug("Started..")

        while not self._stop_event.is_set():
            time.sleep(0.1)

            if not self._command:
                continue

            command_response = self._tactigon_speech.response
            if command_response:
                if command_response.complete:
                    self._client.send(
                        SocketCommand.RESULT, 
                        command_response.payload
                    )
                    self._command = None
                    self._ack_sent = False
                else:
                    text_so_far = command_response.payload.get("text_so_far", None)
                    if text_so_far:
                        self._client.send(SocketCommand.TEXT_SO_FAR, {"text_so_far": text_so_far})

                continue

            if self._tactigon_speech.is_working:
                if self._command == SocketCommand.STOP:
                    self._tactigon_speech.stop()
                else:
                    pass
                    # TODO: notify the server that the command is discarded...
                continue

            self._tactigon_speech.command = self._command
            self._tactigon_speech.payload = self._payload

    def join(self, timeout: Optional[float] = None):
        self._logger.debug("Called stop...")
        self._tactigon_speech.join(timeout)
        self._client.join(timeout)

    def on_data(self, command: SocketCommand, payload: Union[Dict, List[bytes]]):
        if command == SocketCommand.AUDIO:
            if self._command not in [SocketCommand.RECORD, SocketCommand.LISTEN]:
                return
            
            if not self._ack_sent:
                self._client.send(SocketCommand.ACK, {})
                self._ack_sent = True
            
            # Got AUDIO command. the payload should be a list of audio stream...
            # I just need to add the audio stream to the audio buffer.
            for audio in payload:
                self._tactigon_speech.append_audio(audio)

        else:
            self._logger.debug("Got %s command. %s", command, payload)
            self._command = command
            self._payload = payload

        
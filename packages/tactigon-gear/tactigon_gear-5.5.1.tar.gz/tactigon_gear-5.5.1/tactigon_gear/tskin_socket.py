import threading
import io
from typing import Optional, Any


from .tskin import TSkin
from .connection.listener import Listener
from .models.tskin import TSkinConfig
from .models.audio import TSpeechObject, Transcription, HotWord
from .notifications.audio import TRIGGER_NOTIFICATION_AUDIO
from .models.socket import SocketConfig, SocketCommand

class TSkinSocket(TSkin):
    AUDIO_PACKET_LEN: int = 50
    config: TSkinConfig
    server_config: SocketConfig

    _listener: Listener
    _command: SocketCommand | None
    _audio_data: list[bytes]

    def __init__(self, config: TSkinConfig, socket_config: SocketConfig, debug: bool = False):
        TSkin.__init__(self, config, debug)

        self.server_config = socket_config
        self._listener = Listener(self.server_config.host, self.server_config.port)
        self._listener.task = self.on_response

        self._command = None
        self._audio_data = []

    def handle_audio(self, char, data: bytearray):
        self._audio_data.append(self.adpcm_engine.extract_data(data))

        if len(self._audio_data) >= self.AUDIO_PACKET_LEN:
            self._listener.send(SocketCommand.AUDIO, self._audio_data)
            self._audio_data.clear()

    def on_response(self, command: SocketCommand, payload: dict):
        if command == SocketCommand.ACK:
            self._logger.info("Ready to stream audio!")

        if command == SocketCommand.RESULT:
            if "transcription" in payload:
                self._transcription = Transcription.FromJSON(payload["transcription"])
                self._logger.debug("Transcription %s", self._transcription)

        if command in [SocketCommand.RESULT, SocketCommand.DISCONNECTED, SocketCommand.STOP]:
            self.select_sensors()
            self._command = None     

    def send_command(self, command: SocketCommand, payload: dict = {}):
        self._listener.send(command, payload)

    def start(self):
        TSkin.start(self)
        self._listener.start()

    def join(self, timeout: Optional[float] = None):
        self.stop()
        self._listener.join(timeout)
        TSkin.join(self, timeout)

    @property
    def is_listening(self) -> bool:
        return self._command == SocketCommand.LISTEN

    def listen(self, speech: Optional[TSpeechObject] = None) -> bool:
        if self._command is not None:
            return False
        
        self.send_command(SocketCommand.LISTEN, speech.toJSON() if speech else {})
        self.select_audio()
        self._command = SocketCommand.LISTEN

        return True

    def play(self, filename: str) -> bool:
        if self._command is not None:
            return False
        
        self.send_command(SocketCommand.PLAY, {"filename":filename})
        
        return True
       
    @property
    def is_recording(self) -> bool:
        return self._command == SocketCommand.RECORD

    def record(self, filename: str, seconds: float = 5) -> bool:
        if self._command is not None:
            return False
        
        self.send_command(SocketCommand.RECORD, {"filename":filename, "seconds":seconds})
        self.select_audio()
        self._command = SocketCommand.RECORD

        return True

    def stop(self):
        self.send_command(SocketCommand.STOP)

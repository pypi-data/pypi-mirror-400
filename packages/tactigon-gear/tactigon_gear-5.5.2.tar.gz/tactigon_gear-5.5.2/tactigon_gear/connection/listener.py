import selectors
import logging
import socket
from threading import Thread, Event

from typing import Dict, Tuple

from ..models.socket import SocketCommand
from ..middleware.packet_manager import PacketManager

class Listener(Thread):
    _listener: socket.socket
    _stop_event: Event

    _connected: bool = False

    def __init__(self, url: str, port: int):
        Thread.__init__(self)
        self._stop_event = Event()
        self._address = (url, port)
        self._logger = logging.getLogger(Listener.__name__)
        self._packet_manager = PacketManager(self._logger)

        self._selector = selectors.DefaultSelector()
        self._clients: Dict[socket.socket, Tuple[str, int]] = {}

    def run(self):
        self._logger.debug("Started!")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self._listener:
            self._listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._listener.bind(self._address)
            self._listener.listen()
            self._listener.setblocking(False)
            self._selector.register(self._listener, selectors.EVENT_READ)
            self._logger.debug("Listener created on %s", self._address)

            try:
                while not self._stop_event.is_set():
                    events = self._selector.select(timeout=0.1)
                    for key, mask in events:
                        sock: socket.socket = key.fileobj #type: ignore
                        if sock is self._listener:
                            conn, addr = self._listener.accept()
                            conn.setblocking(False)
                            self._selector.register(conn, selectors.EVENT_READ)
                            self._clients[conn] = addr
                            self._logger.debug("Connected client %s", addr)
                        else:
                            try:
                                packet_size_bytes = self._packet_manager.recv_bytes(sock, 4)
                                if not packet_size_bytes:
                                    raise ConnectionError("Client disconnected")
                                bufsize = int.from_bytes(packet_size_bytes, "big")
                                packet_body = self._packet_manager.recv_bytes(sock, bufsize)
                                command, payload = self._packet_manager.unpack_command(packet_body)
                                self._logger.debug("Got command %s data %s", command, payload)
                                self.task(command, payload)
                            except ConnectionError:
                                addr = self._clients.pop(sock, ("Unknown", 0))
                                self._logger.debug("Client %s disconnected", addr)
                                self.task(SocketCommand.DISCONNECTED, {})
                                self._selector.unregister(sock)
                                sock.close()
                            except Exception as e:
                                self._logger.error(e)

            except Exception as e:
                self._logger.error(e)
            finally:
                for conn in list(self._clients.keys()):
                    try:
                        self._selector.unregister(conn)
                        conn.close()
                    except Exception:
                        pass
                try:
                    self._selector.unregister(self._listener)
                except Exception:
                    pass
                self._logger.debug("Stopped!")
        
    def task(self, command: SocketCommand, payload: dict):
        pass

    def send(self, command: SocketCommand, payload: dict | list[bytes]):
        buff = self._packet_manager.pack_command(command, payload)
        for client in self._clients:
            try:
                client.sendall(buff)
            except Exception as e:
                self._clients.pop(client)
                self._logger.error("Cannot send data. %s", e)        

    def join(self, timeout: float | None = None):
        self._logger.debug("Called stop...")
        self._stop_event.set()
        Thread.join(self, timeout)
        self._logger.debug("Joined!")



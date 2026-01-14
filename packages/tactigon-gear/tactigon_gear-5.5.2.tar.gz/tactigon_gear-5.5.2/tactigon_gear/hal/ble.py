import logging
import struct
import math
import asyncio
import time

from bleak import BleakClient
from threading import Thread, Event, Lock
from queue import Queue
from multiprocessing.connection import _ConnectionBase

from ..models.ble import BLECommand, BLECommandMask, BLECommandWord, BLESelector, BLECommands
from ..models.tskin import Hand, Angle, Acceleration, Touch, Gyro
from ..models.touch import TouchConfig, OneFingerGesture, TwoFingerGesture

from ..utils import AdvancedQueue
from ..middleware.adpcm_engine import ADPCMEngine

class Ble(Thread):
    TICK: float = 0.02
    _RECONNECT_TIMEOUT: float = 0.1
    STATUS_UUID: str =          "bea5760d-503d-4920-b000-101e7306b012"
    SENSORS_UUID: str =         "bea5760d-503d-4920-b000-101e7306b005"
    TOUCHPAD_UUID: str =        "bea5760d-503d-4920-b000-101e7306b009"
    TOUCH_CONFIG_UUID: str =    "bea5760d-503d-4920-b000-101e7306b011"

    AUDIO_DATA_UUID: str =      "08000000-0001-11e1-ac36-0002a5d5c51b"
    AUDIO_SYNC_UUID: str =      "40000000-0001-11e1-ac36-0002a5d5c51b"

    TERMINAL_UUID: str =        "00000001-000e-11e1-ac36-0002a5d5c51b"
    CONFIG_UUID: str =          "00000002-000f-11e1-ac36-0002a5d5c51b"

    address: str
    hand: Hand
    touch_config: TouchConfig
    debug: bool

    _stop_event: Event
    _client_connected: bool = False
    selector: BLESelector
    _sensor_tx: _ConnectionBase | None = None
    _angle_tx: _ConnectionBase | None = None
    _audio_tx: _ConnectionBase | None = None
    _update: Lock
    _update_touch: Lock
    _update_selector: Lock
    _sleep: Event
    _charging: Event
    _calibrated_sensorfusion: Event
    _calibrated_compass: Event

    _fw_version: str | None = None
    _angle: Angle | None = None
    _acceleration: Acceleration | None = None
    _gyro: Gyro | None = None
    _battery: float = 0
    _touch: Touch | None = None

    _writes: AdvancedQueue
    _reads: Queue
    _ble_logger: logging.Logger

    adpcm_engine: ADPCMEngine

    def __init__(self, address: str, hand: Hand, touch_config: TouchConfig | None = None, debug: bool = False):
        Thread.__init__(self)
        self._ble_logger = logging.getLogger(Ble.__name__)
        self.address = address
        self.hand = hand
        
        if touch_config:
            self.touch_config = touch_config
        else:
            self.touch_config = TouchConfig.Default()

        self.debug = debug

        self._sleep = Event()
        self._charging = Event()
        self._calibrated_sensorfusion = Event()
        self._calibrated_compass = Event()
        self._stop_event = Event()
        self._update = Lock()
        self._update_touch = Lock()
        self._update_selector = Lock()
        self.selector = BLESelector.SENSORS
        self.adpcm_engine = ADPCMEngine()

        self._writes = AdvancedQueue()
        self._reads = Queue()

        self.update_touch(self.touch_config)
        self._calibrated_sensorfusion.set()
        self._calibrated_compass.set()

    @staticmethod
    def gravity_comp(hand: Hand, accX: float, accY: float, accZ: float, gyroX: float, gyroY: float, gyroZ: float, roll: float, pitch: float, yaw: float):
        """gravity compensation"""
        G_CONST = 9.81
        ANG_TO_RAD = math.pi / 180
        ACC_RATIO = 1000
        VEL_RATIO = 30

        if hand == Hand.LEFT:
            accX = -accX / ACC_RATIO
            accY = -accY / ACC_RATIO
            accZ = -accZ / ACC_RATIO

            gyroX = -gyroX / VEL_RATIO
            gyroY = -gyroY / VEL_RATIO
            gyroZ = -gyroZ / VEL_RATIO

            _pitch = roll * ANG_TO_RAD
            _roll = pitch * ANG_TO_RAD

        else:
            accX = accX / ACC_RATIO
            accY = accY / ACC_RATIO
            accZ = -accZ / ACC_RATIO

            gyroX = gyroX / VEL_RATIO
            gyroY = gyroY / VEL_RATIO
            gyroZ = -gyroZ / VEL_RATIO

            _pitch = -roll * ANG_TO_RAD
            _roll = -pitch * ANG_TO_RAD

        if accZ == 0:
            beta = math.pi / 2
        else:
            beta = math.atan(
                math.sqrt(math.pow(accX, 2) + math.pow(accY, 2)) / accZ
            )

        accX = accX - G_CONST * math.sin(_roll)
        accY = accY + G_CONST * math.sin(_pitch)
        accZ = accZ - G_CONST * math.cos(beta)

        return accX, accY, accZ, gyroX, gyroY, gyroZ, roll, pitch, yaw

    @property
    def firmware_version(self) -> str | None:
        return self._fw_version

    @property
    def connected(self) -> bool:
        return self._client_connected
    
    @property
    def angle(self) -> Angle | None:
        if self.sleep:
            return None
        
        with self._update:
            angle = self._angle
        return angle
    
    @property
    def acceleration(self) -> Acceleration | None:
        if self.sleep:
            return None
        
        with self._update:
            acc = self._acceleration
        return acc

    @property
    def gyro(self) -> Gyro | None:
        if self.sleep:
            return None
        
        with self._update:
            gyro = self._gyro
        return gyro
    
    @property
    def touch(self) -> Touch | None:
        if self.sleep:
            return None
        
        with self._update_touch:
            touch = self._touch
            self._touch = None
        return touch
    
    @property
    def sleep(self) -> bool:
        return self._sleep.is_set()
        
    @property
    def battery(self) -> float | None:
        if self.sleep:
            return None
        
        return self._battery

    @property
    def calibrated(self) -> bool:
        return self._calibrated_compass.is_set() and self._calibrated_sensorfusion.is_set()

    def on_terminal(self, char, data: bytearray):
        print("TERMINAL", data)

    def on_config(self, char, data: bytearray):
        _tick = int.from_bytes(data[0:2], 'little')
        command = BLECommandWord(data[6])
        payload = int.from_bytes(data[7:], 'little')
        _mask = int.from_bytes(data[2:6], 'big')
        mask = BLECommandMask(bytes([_mask >> 24 & 0xFF, _mask >> 16 & 0xFF, _mask >> 8 & 0xFF, _mask & 0xFF]))

        if mask == BLECommandMask.SENSORFUSION:
            if command == BLECommandWord.STATUS:
                if payload == 100:
                    self._calibrated_sensorfusion.set()
                else:
                    self._calibrated_sensorfusion.clear()
        elif mask == BLECommandMask.ECOMPASS:
            if command == BLECommandWord.STATUS:
                if payload == 100:
                    self._calibrated_compass.set()
                else:
                    self._calibrated_compass.clear()

        self._ble_logger.debug("Config %i %s %s %s", _tick, mask, command, payload)

    def handle_status(self, char, data: bytearray):
        fw_major, fw_minor, fw_patch, fw_dev, sleep_armed = struct.unpack("cccc?", data[0:5])
        self._fw_version = f"{fw_major.decode()}.{fw_minor.decode()}.{fw_patch.decode()}.{fw_dev.decode()}"
        
        if sleep_armed:
            self._sleep.set()
        else:
            self._sleep.clear()

        self._ble_logger.debug("FW version: %s, sleep %s", self._fw_version, self.sleep)
        
    def handle_audio_sync(self, char, data: bytearray):
        pass

    def handle_audio(self, char, data: bytearray):
        if self._audio_tx:
            self._audio_tx.send_bytes(self.adpcm_engine.extract_data(data))

    def handle_sensors(self, char, data:bytearray):       
        accX, accY, accZ, gyroX, gyroY, gyroZ, roll, pitch, yaw, battery = struct.unpack("hhhhhhhhhh", data)
        accX, accY, accZ, gyroX, gyroY, gyroZ, roll, pitch, yaw = self.gravity_comp(self.hand, accX, accY, accZ, gyroX, gyroY, gyroZ, roll, pitch, yaw)

        with self._update:
            self._angle = Angle(roll, pitch, yaw)
            self._acceleration = Acceleration(accX, accY, accZ)
            self._gyro = Gyro(gyroX, gyroY, gyroZ)
            self._battery = battery/1000

        if self.debug:
            self._ble_logger.debug("Angle: %f,%f,%f",roll, pitch, yaw)
            self._ble_logger.debug("Acceleration: %f,%f,%f",accX, accY, accZ)
            self._ble_logger.debug("Gyro: %f,%f,%f",gyroX, gyroY, gyroZ)
            self._ble_logger.debug("Battery: %f", battery/1000)

        if self._sensor_tx:
            self._sensor_tx.send([accX, accY, accZ, gyroX, gyroY, gyroZ])

        if self._angle_tx:
            self._angle_tx.send([roll, pitch, yaw])

    def handle_touchpad(self, char, data: bytearray):
        with self._update_touch:
            one_finger = OneFingerGesture(int.from_bytes(data[0:1], "big"))
            two_finger = TwoFingerGesture(int.from_bytes(data[1:2], "big"))
            if one_finger is not OneFingerGesture.NONE or two_finger is not TwoFingerGesture.NONE:
                self._touch = Touch(
                    one_finger,
                    two_finger,
                    float(struct.unpack("h", data[2:4])[0]),
                    float(struct.unpack("h", data[4:6])[0])
                )

    def start(self):
        self._ble_logger.debug("BLE starting on address %s", self.address)
        Thread.start(self)

    def join(self, timeout: float | None = None):
        self._ble_logger.debug("Stopping BLE on address %s", self.address)
        self._stop_event.set()
        Thread.join(self, timeout)

    def run(self):
        asyncio.run(self.task())

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *attr):
        self.join()

    async def task(self):
        running_selector: BLESelector | None = None

        while not self._stop_event.is_set():
            self._client_connected = False
            
            try:
                running_selector = None

                async with BleakClient(self.address, disconnected_callback=self.on_disconnect) as client:
                    self._ble_logger.debug("%s connected", client)

                    await client.start_notify(self.TERMINAL_UUID, self.on_terminal)
                    await client.start_notify(self.CONFIG_UUID, self.on_config)
                    await client.start_notify(self.STATUS_UUID, self.handle_status)
                    await client.start_notify(self.TOUCHPAD_UUID, self.handle_touchpad)

                    self._client_connected = True

                    while self.connected:
                        if self._stop_event.is_set():
                            await client.disconnect()
                            break

                        if not self.sleep:
                            while True:
                                try:
                                    cmd: BLECommand = self._writes.get_nowait()
                                except:
                                    break

                                if cmd.command == BLECommands.WRITE and cmd.payload:
                                    await client.write_gatt_char(cmd.characteristic, cmd.payload)
                                elif cmd.command == BLECommands.READ:
                                    data = await client.read_gatt_char(cmd.characteristic)
                                    if data:
                                        self._reads.put(data)
                            
                        if running_selector != self.selector:
                            with self._update_selector:
                                if running_selector == BLESelector.SENSORS:
                                    await client.stop_notify(self.SENSORS_UUID)

                                    self._update.acquire()
                                    self._angle = None
                                    self._acceleration = None
                                    self._gyro = None
                                    self._update.release()
                                    self._ble_logger.debug("Stopped notification on sensors (%s)", self.SENSORS_UUID)
                                elif running_selector == BLESelector.AUDIO:
                                    await client.stop_notify(self.AUDIO_DATA_UUID)
                                    await client.stop_notify(self.AUDIO_SYNC_UUID)
                                    self._ble_logger.debug("Stopped notification on AUDIO (%s)", self.AUDIO_DATA_UUID)

                                running_selector = self.selector

                                if running_selector == BLESelector.SENSORS:
                                    await client.start_notify(self.SENSORS_UUID, self.handle_sensors)

                                    self._ble_logger.debug("Started notification on sensors (%s)", self.SENSORS_UUID)
                                elif running_selector == BLESelector.AUDIO:
                                    await client.start_notify(self.AUDIO_SYNC_UUID, self.handle_audio_sync) 
                                    await client.start_notify(self.AUDIO_DATA_UUID, self.handle_audio)

                                    self._ble_logger.debug("Started notification on AUDIO (%s)", self.AUDIO_DATA_UUID)

                        await asyncio.sleep(self._RECONNECT_TIMEOUT)
            
            except Exception as e:
                self._ble_logger.error("BLE error: %s", e)
                await asyncio.sleep(self._RECONNECT_TIMEOUT)

    def on_disconnect(self, client: BleakClient):
        self._ble_logger.debug("Client %s disconnected", client)
        self._client_connected = False

    def set_touch(self, config: TouchConfig, timeout: float = 5) -> bool:
        cfg1, cfg2, save = config.toBytes()

        ref1 = self._writes.put(BLECommand(BLECommands.WRITE, self.TOUCH_CONFIG_UUID, cfg1))
        ref2 = self._writes.put(BLECommand(BLECommands.WRITE, self.TOUCH_CONFIG_UUID, cfg2))
        refsave = self._writes.put(BLECommand(BLECommands.WRITE, self.TOUCH_CONFIG_UUID, save))

        _t = 0
        while _t < timeout:
            if self._writes.check(ref1) and self._writes.check(ref2) and self._writes.check(refsave):
                return True
            
            _t += self._RECONNECT_TIMEOUT
            time.sleep(self._RECONNECT_TIMEOUT)
            
        return False

    def get_touch(self, timeout: float = 5) -> tuple[bytes, bytes] | None:
        self._writes.put(BLECommand(BLECommands.READ, self.TOUCH_CONFIG_UUID))
        self._writes.put(BLECommand(BLECommands.READ, self.TOUCH_CONFIG_UUID))

        cfg1 = None
        cfg2 = None

        _t = 0
        while _t < timeout:
            try:
                resp: bytes = self._reads.get_nowait()
                if cfg1 == None:
                    cfg1 = resp
                else:
                    cfg2 = resp
            except:
                pass

            if cfg1 and cfg2:
                return cfg1, cfg2

            _t += self._RECONNECT_TIMEOUT
            time.sleep(self._RECONNECT_TIMEOUT)
            
        return None
    
    def update_touch(self, touch_config: TouchConfig, timeout: float = 5) -> bool:
        if self.set_touch(touch_config, timeout):
            res = self.get_touch(timeout)
            return self.touch_config.update(*res) if res else False

        return False
    
    def set_touch_sensitivity(self, sensitivity: int = 2, timeout: float = 5):
        self.touch_config.set_sensitivity(sensitivity)
        return self.set_touch(self.touch_config, timeout)

    def calibrate(self, timeout: float = 5) -> bool:
        cmd = BLECommandMask.SENSORFUSION.value + bytes(BLECommandWord.START.value) + b'\x00'
        ret = self._writes.put(BLECommand(BLECommands.WRITE, self.CONFIG_UUID, cmd))

        _t = 0
        while _t < timeout:
            if self._writes.check(ret):
                return True
            
            _t += self._RECONNECT_TIMEOUT
            time.sleep(self._RECONNECT_TIMEOUT)
            
        return False

    def select_sensors(self):
        self._update_selector.acquire()
        self.selector = BLESelector.SENSORS
        self._update_selector.release()

    def select_audio(self):
        self._update_selector.acquire()
        self.selector = BLESelector.AUDIO
        self._update_selector.release()

    def connect(self):
        self.start()

    def disconnect(self):
        self.join()

    def terminate(self):
        self.join()
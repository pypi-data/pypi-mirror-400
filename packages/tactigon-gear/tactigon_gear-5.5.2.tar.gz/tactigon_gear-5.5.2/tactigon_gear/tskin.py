import logging
from multiprocessing import Pipe

from .hal.ble import Ble
from .middleware.tactigon_gesture import TactigonGesture
from .models.tskin import TSkinConfig, TSkinState
from .models.gesture import Gesture

class TSkin(Ble):
    _tgesture: TactigonGesture | None = None
    _gesture: Gesture | None = None
    _logger: logging.Logger

    config: TSkinConfig
    def __init__(self, config: TSkinConfig, debug: bool = False):
        Ble.__init__(self, config.address, config.hand, config.touch_config)
        self._logger = logging.getLogger(TSkin.__name__)
        self.config = config

        if debug:
            logging.basicConfig(level=logging.DEBUG)

        if self.config.gesture_config:
            _sensor_rx, self._sensor_tx = Pipe(duplex=False)

            self._tgesture = TactigonGesture(
                self.config.gesture_config,
                _sensor_rx,
                logging.getLogger(),
            )

    @property
    def gesture(self) -> Gesture | None:
        if not self._tgesture:
            return None
        
        if self._gesture:
            g = self._gesture
            self._gesture = None
        else:
            g = self._tgesture.gesture()
        
        return g
    
    @property
    def gesture_preserve(self) -> Gesture | None:
        if not self._tgesture:
            return None
        
        if not self._gesture:
            self._gesture = self._tgesture.gesture()
            
        return self._gesture
    
    @property
    def state(self) -> TSkinState:
        return TSkinState(
            self.connected,
            self.sleep,
            self.battery,
            self.selector,
            self.touch,
            self.angle,
            self.gesture,
        )
    
    @property
    def state_preserve_gesture(self) -> TSkinState:
        return TSkinState(
            self.connected,
            self.sleep,
            self.battery,
            self.selector,
            self.touch,
            self.angle,
            self.gesture_preserve,
        )
    
    def __str__(self):
        return "TSkin(name='{0}', address='{1}', gesture={2})".format(self.config.name, self.config.address, self.config.gesture_config)

    def start(self):
        if self._tgesture:
            self._tgesture.start()
        Ble.start(self)

    def join(self, timeout: float | None = None):
        if self._tgesture:
            self._tgesture.terminate()
        Ble.join(self, timeout)
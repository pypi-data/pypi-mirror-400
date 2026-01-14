import setup_path
import time
import logging
from datetime import datetime

from tactigon_gear.tskin import TSkin
from tactigon_gear.models.tskin import Hand, TSkinConfig
from tactigon_gear.models.touch import OneFingerGesture, TwoFingerGesture
from tactigon_gear.models.ble import BLESelector

# C0:83:3F:39:21:57
# 296A6374-C160-2914-7A19-A8B8861DC309

logging.basicConfig(
    filename="log.log", 
    level=logging.DEBUG
)
# logging.getLogger("bleak").setLevel(logging.INFO)



def test():
    last_update = datetime.now()
    audio_sec = 5
    tskin_cfg = TSkinConfig(
        "C0:83:3F:39:21:57",
        Hand.RIGHT
    )

    with TSkin(tskin_cfg, debug=True) as tskin:
        i = 0

        while True:
            if not tskin.connected:
                print("Connecting..")
                while not tskin.connected:
                    time.sleep(tskin.TICK)

                print("Connected!")

            if i > 5:
                break

            state = tskin.state

            if state.selector == BLESelector.AUDIO:
                if (datetime.now()-last_update).total_seconds() > audio_sec:
                    tskin.select_sensors()

            if state.sleep:
                print("Device in sleep...")
                lll = 0
                while tskin.sleep:
                    lll += 1
                    time.sleep(tskin.TICK)

                print(lll * tskin.TICK)
                continue

            if state.touch:
                if state.touch.one_finger == OneFingerGesture.SINGLE_TAP:
                    last_update = datetime.now()
                    tskin.select_audio()
                elif state.touch.one_finger == OneFingerGesture.TAP_AND_HOLD:
                    i += 1

            print(tskin.acceleration, tskin.battery)

            time.sleep(tskin.TICK)

if __name__ == "__main__":
    test()
import time
import datetime
from os import path
from src.tactigon_gear.tskin import TSkin
from src.tactigon_gear.models.tskin import TSkinConfig, Hand
from src.tactigon_gear.models.gesture import GestureConfig
from src.tactigon_gear.models.touch import OneFingerGesture

# C0:83:4B:32:4E:36
# BE5BDEB7-72CC-4221-A44D-103795E74335

def test():
    model_folder = path.join(path.abspath("."), "data", "models", "MODEL_01_R")

    gmodel = GestureConfig(
        path.join(model_folder, "model.pickle"), 
        path.join(model_folder, "encoder.pickle"),
        "test",
        datetime.datetime.now()
    )

    tskin = TSkin(TSkinConfig("C0:83:4F:34:28:38", Hand.RIGHT, "TEST", None, gmodel), True)
    tskin.start()

    print("connecting tskin", tskin)

    while not tskin.connected:
        pass

    i = 0

    while True:
        if not tskin.connected:
            print("Connecting...")
            time.sleep(0.2)
            continue

        if i > 5:
            break

        t = tskin.touch
        g = tskin.gesture

        if g:
            print(g)

        # print(tskin.sleep, tskin.gesture, tskin.acceleration, tskin.gyro, tskin.angle)

        if t and t.one_finger == OneFingerGesture.TAP_AND_HOLD:
            i += 1

        time.sleep(tskin.TICK)

    print("exit")

    tskin.terminate()


if __name__ == "__main__":
    test()
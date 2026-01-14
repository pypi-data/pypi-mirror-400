import time
from src.tactigon_gear.tskin import TSkin
from src.tactigon_gear.models.tskin import TSkinConfig, Hand, Acceleration, Gyro, Angle
from src.tactigon_gear.models.gesture import GestureConfig
from src.tactigon_gear.models.touch import OneFingerGesture
from src.tactigon_gear.hal.ble import Ble

# C0:83:4B:32:4E:36
# BE5BDEB7-72CC-4221-A44D-103795E74335

def test():
    # model_folder = path.join(path.abspath("."), "data", "models", "MODEL_01_R")

    gmodel = None

    with TSkin(TSkinConfig("C0:83:4F:34:28:38", Hand.RIGHT, "TEST", None, gmodel), True) as tskin:
        print("connecting tskin", tskin)

        while not tskin.connected:
            time.sleep(1)

        while True:

            if not tskin.connected:
                print("Disconnected...")
                time.sleep(2)
                continue

            if tskin.sleep:
                print("Sleeping...")
                time.sleep(2)
                continue

            if not tskin.calibrated:
                print("Calibrating... Move around")
                time.sleep(1)
                continue

            acc = tskin.acceleration
            gyro = tskin.gyro
            angle = tskin.angle

            if acc and gyro and angle:
                print(f"{round(angle.roll, 2)}\t{round(angle.pitch, 2)}\t{round(angle.yaw, 2)}\t{round(acc.x, 3)}\t{round(acc.y, 3)}\t{round(acc.z, 3)}\t{round(gyro.x, 3)}\t{round(gyro.y, 3)}\t{round(gyro.z, 3)}")

            time.sleep(tskin.TICK)

    print("exit")


if __name__ == "__main__":
    test()
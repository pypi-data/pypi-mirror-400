import time
import csv
from src.tactigon_gear.tskin import TSkin
from src.tactigon_gear.models.tskin import Hand, TSkinConfig
from src.tactigon_gear.models.touch import OneFingerGesture, TwoFingerGesture

# C0:83:4B:32:4E:36
# BE5BDEB7-72CC-4221-A44D-103795E74335

def test():
    tskin_cfg = TSkinConfig(
        "C0:83:22:30:55:58",
        Hand.RIGHT
    )

    tskin = TSkin(tskin_cfg, debug=True)
    tskin.start()

    i = 0

    with open("test_ble.csv", "w", newline='', encoding='utf-8') as test_file:
        test_writer = csv.writer(test_file)
        test_writer.writerow(["battery", "roll", "pitch", "yaw", "touch"])
    

        while True:
            if not tskin.connected:
                print("Connecting..")
                time.sleep(0.5)
                continue

            if i > 5:
                break

            batt = tskin.battery
            a = tskin.angle
            t = tskin.touch
            acc = tskin.acceleration
            gyro = tskin.gyro

            result = [str(batt)]
            result.extend([str(a.roll), str(a.pitch), str(a.yaw)] if a else ["","",""])
            result.extend([t.one_finger.name, t.two_finger.name, str(t.x_pos), str(t.y_pos)] if t else ["","","", ""])

            test_writer.writerow(result)

            print(batt, a, t)

            if t:
                if t.one_finger == OneFingerGesture.TAP_AND_HOLD:
                    i += 1

            time.sleep(0.01)

    tskin.terminate()

        


if __name__ == "__main__":
    test()
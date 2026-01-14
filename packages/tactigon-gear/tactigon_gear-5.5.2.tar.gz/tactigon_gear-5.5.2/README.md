# Tactigon Gear

![The tactigon team](https://avatars.githubusercontent.com/u/63020285?s=200&v=4)

This package enables the wearable device Tactigon Skin to connect to your python project using Bluetooth Low Energy.

## Architecture

Tactigon Gear environment has the following architecture:

Server is located on the cloud and it is manteined by Next Industries s.r.l.
Server has a web interface where you can handle your profile and your data (models and gestures)

Provided Tactigon Gear SDK is the implementation of Tactigon Gear environment client side

Tactigon Gear SDK is used for collecting new raw data, send the data to server,
ask server to train a model using the raw data, and download the model from server. 
Finally use the model for testing real-time gesture recognition.

![Tactigon Gear architecture definition](https://www.thetactigon.com/wp/wp-content/uploads/2023/11/Architecture_Tactigon_Gear.png "Tactigon Gear architecture definition")  

## Prerequisites
In order to use the Tactigon Gear SDK the following prerequisites needs to be observed:

* Python version: following versions has been used and tested. It is STRONGLY recommended to use these ones depending on platform.
  * Win10: 3.12.x
  * Linux: 3.12.x
  * Mac osx: 3.12.x
  * Raspberry: 3.12.x

## Installing

Install and update using pip:

`pip install tactigon-gear`

## A Simple Example

```python

import time
from tactigon_gear import TSkin, TSkinConfig, Hand, OneFingerGesture

def main():
    TSKIN_MAC = "change-me"
    tskin_cfg = TSkinConfig(TSKIN_MAC, Hand.RIGHT) # Hand.LEFT if the TSkin is wear on left hand.

    with TSkin(tskin_cfg) as tskin:
        i = 0

        while True:
            if not tskin.connected:
                print("Connecting..")
                time.sleep(0.5)
                continue

            if i > 5:
                break

            a = tskin.angle
            t = tskin.touch
            acc = tskin.acceleration
            gyro = tskin.gyro

            print(a, t, acc, gyro)

            if t and t.one_finger == OneFingerGesture.TAP_AND_HOLD:
                i += 1
            else:
                i = 0

            time.sleep(0.02)
        
if __name__ == "__main__":
    main()
```

## Links
- [Tactigon SOUL](https://github.com/TactigonTeam/Tactigon-Soul/wiki)
- [SDK](https://github.com/TactigonTeam/Tactigon-SDK)
- [Documentation](https://github.com/TactigonTeam/Tactigon-SDK/wiki)
- [Blog](https://www.thetactigon.com/blog/)
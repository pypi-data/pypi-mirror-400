import setup_path
import time
import logging

from tactigon_gear.tskin_socket import TSkinSocket
from tactigon_gear.models.tskin import TSkinConfig, Hand, OneFingerGesture, TwoFingerGesture
from tactigon_gear.models.socket import SocketConfig
from tactigon_gear.models.audio import TSpeechObject, TSpeech, HotWord

logging.basicConfig(
    # filename="log.log", 
    level=logging.DEBUG
)
logging.getLogger("bleak").setLevel(logging.WARNING)

def get_tspeechobj() -> TSpeechObject:
    return TSpeechObject(
        [
            TSpeech(
                [HotWord("pick"), HotWord("place")],
                TSpeechObject(
                    [
                        TSpeech(
                            [HotWord("position")],
                            TSpeechObject(
                                [
                                    TSpeech(
                                        [HotWord("star"), HotWord("square")]
                                    )
                                ]
                            )
                        )                     
                    ]
                )
            )
        ]
    )

def main():
    cfg = TSkinConfig(
        "C0:83:3F:39:21:57",
        Hand.RIGHT
    )

    socket_cfg = SocketConfig("localhost", 50006)

    print("Init...")

    with TSkinSocket(cfg, socket_cfg) as tskin:
        print(tskin)
        while not tskin.connected:
            time.sleep(1)

        print("connected!")

        while True:
            if not tskin.connected:
                print("Reconnecting..")
                time.sleep(1)

            t = tskin.touch
            text_so_far = tskin.text_so_far
            transcription = tskin.transcription

            if text_so_far:
                print("Text so far:", text_so_far)
            
            if transcription:
                print("Transcription:", transcription)

            if t:
                if t.one_finger == OneFingerGesture.SINGLE_TAP:
                    print("record", tskin.record("testing.wav", 10))
                elif t.two_finger == TwoFingerGesture.TWO_FINGER_TAP:
                    print("Listen", tskin._command, tskin.listen(get_tspeechobj()))
                elif t.one_finger == OneFingerGesture.TAP_AND_HOLD:
                    break


            time.sleep(tskin.TICK)

if __name__ == "__main__":
    main()
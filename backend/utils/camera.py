import logging

import cv2 as cv

logger = logging.getLogger(__name__)


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwds):
        DEVICE_INDEX = 0
        device = args[DEVICE_INDEX]
        if device not in cls._instances:
            cls._instances[device] = super(Singleton, cls).__call__(*args, **kwds)
        return cls._instances[device]


class Camera(metaclass=Singleton):
    def __init__(self, device):
        # カメラデバイスを開く
        self.cap = cv.VideoCapture(device)
        if not self.cap.isOpened():
            # 開けなかった場合はエラー処理
            logger.error("カメラを開けませんでした。device: %s", device)
            raise RuntimeError("カメラを開けませんでした。device: %s" % device)
        else:
            # 開けた場合はデバッグ情報を出力
            logger.debug("カメラを正常に開きました。device: %s", device)

    def read(self):
        ret, frame = self.cap.read()
        if not ret:
            logger.warning("カメラからフレームを読み取れませんでした。")
        return ret, frame

    def release(self):
        # カメラデバイスのリソース解放処理
        self.cap.release()
        logger.debug("カメラを正常に解放しました。")

    def __del__(self):
        if hasattr(self, "cap") and self.cap.isOpened():
            # カメラデバイスが開いている場合は解放する
            self.release()


def camera(process):
    def inner():
        DEVICE = 0
        DELAY = 1
        KEYCODE_ESC = 27
        camera = Camera(DEVICE)
        try:
            while camera.cap.isOpened():
                _, frame = camera.read()
                frame = process(frame)
                cv.imshow("frame", frame)
                logger.debug({"frame.shape": frame.shape})
                key = cv.waitKey(DELAY)
                if key == KEYCODE_ESC:
                    raise (KeyboardInterrupt)
        except KeyboardInterrupt as ex:
            logger.warning({"ex": ex})
        finally:
            del camera
            cv.destroyAllWindows()

    return inner


if __name__ == "__main__":
    import sys

    logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)

    @camera
    def process(frame):
        logger.debug({"action": "process"})
        return frame

    process()

import logging

import cv2 as cv
import numpy as np

from .model import Model

logger = logging.getLogger(__name__)


INDEX_CONF = 2
INDEX_XMIN = 3
INDEX_YMIN = 4
INDEX_XMAN = 5
INDEX_YMAX = 6
INDEX_X = 1
INDEX_Y = 0
BLUE = (255, 0, 0)


class FaceDetector(Model):
    def __init__(self, ie_core, model_path, device_name="CPU", num_requests=0):
        super(FaceDetector, self).__init__(
            ie_core=ie_core,
            model_path=model_path,
            device_name=device_name,
            num_requests=num_requests,
        )

    def prepare_data(self, input, frame, confidence=0.5):
        data_array = []
        for data in np.squeeze(input):
            conf = data[INDEX_CONF]

            # フレームからはみ出す座標を避けるため、xmin/yminは0未満にならないようにします
            xmin = max(0, int(data[INDEX_XMIN] * frame.shape[INDEX_X]))
            ymin = max(0, int(data[INDEX_YMIN] * frame.shape[INDEX_Y]))

            # フレーム内に収まるよう、xmax/ymaxをframeの幅/高さの範囲内に制限します
            xmax = min(
                int(data[INDEX_XMAN] * frame.shape[INDEX_X]), frame.shape[INDEX_X]
            )
            ymax = min(
                int(data[INDEX_YMAX] * frame.shape[INDEX_Y]), frame.shape[INDEX_Y]
            )
            if conf > confidence:
                area = (xmax - xmin) * (ymax - ymin)
                data = {
                    "xmin": xmin,
                    "ymin": ymin,
                    "xmax": xmax,
                    "ymax": ymax,
                    "area": area,
                }
                data_array.append(data)

                # 検出されたオブジェクトを面積の大きい順にソートし、最も大きいオブジェクトから処理するようにします
                data_array.sort(key=lambda face: face["area"], reverse=True)
        logger.debug(
            {
                "action": "prepare_data",
                "input.shape": input.shape,
                "data_array": data_array,
            }
        )
        return data_array

    def draw(self, data_array, frame):
        dest = frame.copy()
        for i, data in enumerate(data_array):
            cv.rectangle(
                dest,
                (int(data["xmin"]), int(data["ymin"])),
                (int(data["xmax"]), int(data["ymax"])),
                color=BLUE,
                thickness=3,
            )
            logger.debug(
                {
                    "action": "draw",
                    "i": i,
                    "dest.shape": dest.shape,
                }
            )
        return dest

    def crop(self, data_array, frame):
        cropped_frames = []
        for i, data in enumerate(data_array):
            xmin = data["xmin"]
            ymin = data["ymin"]
            xmax = data["xmax"]
            ymax = data["ymax"]
            cropped_frame = frame[ymin:ymax, xmin:xmax]
            cropped_frames.append(cropped_frame)
            logger.debug(
                {"action": "crop", "i": i, "cropped_frame.shape": cropped_frame.shape}
            )
        return cropped_frames

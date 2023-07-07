import logging

import cv2 as cv
import numpy as np

from .model import Model

logger = logging.getLogger(__name__)


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
        index_conf = 2
        index_xmin = 3
        index_ymin = 4
        index_xman = 5
        index_ymax = 6
        index_x = 1
        index_y = 0
        for data in np.squeeze(input):
            conf = data[index_conf]

            # フレームからはみ出す座標を避けるため、xmin/yminは0未満にならないようにします
            xmin = max(0, int(data[index_xmin] * frame.shape[index_x]))
            ymin = max(0, int(data[index_ymin] * frame.shape[index_y]))

            # フレーム内に収まるよう、xmax/ymaxをframeの幅/高さの範囲内に制限します
            xmax = min(
                int(data[index_xman] * frame.shape[index_x]), frame.shape[index_x]
            )
            ymax = min(
                int(data[index_ymax] * frame.shape[index_y]), frame.shape[index_y]
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
        blue = (255, 0, 0)
        for i, data in enumerate(data_array):
            cv.rectangle(
                dest,
                (int(data["xmin"]), int(data["ymin"])),
                (int(data["xmax"]), int(data["ymax"])),
                color=blue,
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

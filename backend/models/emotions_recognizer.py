import logging

import cv2 as cv
import numpy as np

from .model import Model

logger = logging.getLogger(__name__)


NEUTRAL_INDEX = 0
SMILE_INDEX = 1
COLOR_PICKER = [
    (255, 0, 0),
    (0, 255, 255),
    (0, 255, 0),
    (255, 0, 255),
    (0, 0, 255),
]


class EmotionsRecognizer(Model):
    def __init__(self, ie_core, model_path, device_name="CPU", num_requests=0):
        super(EmotionsRecognizer, self).__init__(
            ie_core=ie_core,
            model_path=model_path,
            device_name=device_name,
            num_requests=num_requests,
        )

    def score(self, infer_result):
        emotions_score = np.squeeze(infer_result)
        return emotions_score

    def draw(self, xmin, ymin, xmax, ymax, emotions_score, frame, smile_mode=False):
        dest = frame.copy()
        emotion = np.argmax(emotions_score)
        if emotion == 1:
            color = COLOR_PICKER[SMILE_INDEX]
        elif smile_mode:
            color = COLOR_PICKER[NEUTRAL_INDEX]
        else:
            color = COLOR_PICKER[emotion]
        cv.rectangle(
            dest,
            (int(xmin), int(ymin)),
            (int(xmax), int(ymax)),
            color=color,
            thickness=3,
        )
        logger.debug(
            {
                "action": "draw",
                "dest.shape": dest.shape,
            }
        )
        return dest

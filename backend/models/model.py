import logging

import cv2 as cv
import numpy as np

logger = logging.getLogger(__name__)


class Model(object):
    def __init__(self, ie_core, model_path, device_name="CPU", num_requests=0):
        net = ie_core.read_network(model_path + ".xml", model_path + ".bin")

        self.exec_net = ie_core.load_network(
            network=net, device_name=device_name, num_requests=num_requests
        )

        # 入力名・出力名・入力サイズ・出力サイズを設定
        self.input_name = next(iter(net.input_info))
        self.output_name = next(iter(net.outputs))
        self.input_size = net.input_info[self.input_name].input_data.shape
        self.output_size = (
            self.exec_net.requests[0].output_blobs[self.output_name].buffer.shape
        )

    def prepare_frame(self, frame):
        # 入力サイズにリサイズし、画像のチャンネルを先頭に配置，4次元配列に変換
        _, _, h, w = self.input_size
        input_frame = cv.resize(frame, (h, w)).transpose((2, 0, 1))[np.newaxis]

        logger.debug(
            {
                "action": "prepare_frame",
                "input_size": (h, w),
                "input_frame.shape": input_frame.shape,
            }
        )

        return input_frame

    def infer(self, data):
        input_data = {self.input_name: data}

        infer_result = self.exec_net.infer(input_data)[self.output_name]

        logger.debug(
            {
                "action": "infer",
                "input_data.shape": input_data[self.input_name].shape,
                "infer_result.shape": infer_result.shape,
            }
        )

        return infer_result

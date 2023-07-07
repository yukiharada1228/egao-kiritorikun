import logging
import subprocess
import sys
from pathlib import Path

from openvino.inference_engine import IECore

from models import FaceDetector
from utils.camera import camera

# ロギングの設定
logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)
PROJECT_ROOT = Path(__file__).resolve().parent
MODEL_PATH = {}
FACE_DETECTION_MODEL = "face-detection-retail-0005"
MODELS = [FACE_DETECTION_MODEL]
ie_core = IECore()
for model in MODELS:
    cmd = f"omz_downloader --name {model}"
    model_dir = PROJECT_ROOT / "intel" / model
    model_path = str(model_dir / f"FP32/{model}")
    if not model_dir.exists():
        subprocess.call(cmd.split(" "), cwd=str(PROJECT_ROOT))
    MODEL_PATH[model] = model_path
face_detector = FaceDetector(ie_core, MODEL_PATH[FACE_DETECTION_MODEL])


@camera
def process(frame):
    input_frame = face_detector.prepare_frame(frame)
    infer_result = face_detector.infer(input_frame)
    data_array = face_detector.prepare_data(infer_result, frame)
    cropped_frames = face_detector.crop(data_array, frame)
    dest = cropped_frames[0] if len(cropped_frames) else frame
    return dest


process()

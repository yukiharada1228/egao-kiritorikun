import logging
import subprocess
import sys
from pathlib import Path

from openvino.inference_engine import IECore

from models import EmotionsRecognizer, FaceDetector
from utils.camera import camera

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)

SMILE_INDEX = 1
PROJECT_ROOT = Path(__file__).resolve().parent
MODEL_PATH = {}
FACE_DETECTION_MODEL = "face-detection-retail-0005"
EMOTIONS_RECOGNITION_MODEL = "emotions-recognition-retail-0003"
MODELS = [FACE_DETECTION_MODEL, EMOTIONS_RECOGNITION_MODEL]
ie_core = IECore()
for model in MODELS:
    cmd = f"omz_downloader --name {model}"
    model_dir = PROJECT_ROOT / "intel" / model
    model_path = str(model_dir / f"FP32/{model}")
    if not model_dir.exists():
        subprocess.call(cmd.split(" "), cwd=str(PROJECT_ROOT))
    MODEL_PATH[model] = model_path
face_detector = FaceDetector(ie_core, MODEL_PATH[FACE_DETECTION_MODEL])
emotions_recognizer = EmotionsRecognizer(
    ie_core, MODEL_PATH[EMOTIONS_RECOGNITION_MODEL]
)

best_smile_score = 0


@camera
def process(frame):
    global best_smile_score
    input_frame = face_detector.prepare_frame(frame)
    infer_result = face_detector.infer(input_frame)
    data_array = face_detector.prepare_data(infer_result, frame)
    cropped_frames = face_detector.crop(data_array, frame)
    dest = frame.copy()
    for i, cropped_frame in enumerate(cropped_frames):
        data = data_array[i]
        input_frame = emotions_recognizer.prepare_frame(cropped_frame)
        infer_result = emotions_recognizer.infer(input_frame)
        emotions_score = emotions_recognizer.score(infer_result)
        smile_score = emotions_score[SMILE_INDEX]
        is_best = best_smile_score < smile_score
        best_smile_score = max(best_smile_score, smile_score)
        if is_best:
            logger.info({"is_best": is_best, "smile_score": smile_score})
        dest = emotions_recognizer.draw(
            data["xmin"], data["ymin"], data["xmax"], data["ymax"], emotions_score, dest
        )
    return dest


process()

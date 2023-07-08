import logging
import subprocess
import sys
import tempfile
from pathlib import Path

import cv2
import uvicorn
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from openvino.inference_engine import IECore
from starlette.responses import FileResponse

from models import EmotionsRecognizer, FaceDetector

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

app = FastAPI()


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    # 一時ファイルとして動画保存
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
        tmp.write(await file.read())
        input_filename = tmp.name

    # 動画の読み込みと加工
    cap = cv2.VideoCapture(input_filename)
    best_smile_score = 0
    dest = None
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        # 笑顔検出処理
        input_frame = face_detector.prepare_frame(frame)
        infer_result = face_detector.infer(input_frame)
        data_array = face_detector.prepare_data(infer_result, frame)
        cropped_frames = face_detector.crop(data_array, frame)
        for cropped_frame in cropped_frames:
            input_frame = emotions_recognizer.prepare_frame(cropped_frame)
            infer_result = emotions_recognizer.infer(input_frame)
            emotions_score = emotions_recognizer.score(infer_result)
            smile_score = emotions_score[SMILE_INDEX]
            is_best = best_smile_score < smile_score
            best_smile_score = max(best_smile_score, smile_score)
            if is_best:
                dest = frame.copy()
    cap.release()

    if dest is None:
        error_message = "顔が検出されませんでした。"
        return JSONResponse(status_code=400, content={"error": error_message})

    # 加工された最後のフレームを画像ファイルとして保存
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
        output_filename = tmp.name
        cv2.imwrite(output_filename, dest)

    # 最後のフレームの画像ファイルをレスポンスとして返す
    return FileResponse(output_filename, media_type="image/jpeg")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

import tempfile

import cv2
import numpy as np
import uvicorn
from fastapi import FastAPI, File, UploadFile
from starlette.responses import FileResponse

app = FastAPI()


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    # 一時ファイルとして動画保存
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
        tmp.write(await file.read())
        input_filename = tmp.name

    # 動画の読み込みと加工
    cap = cv2.VideoCapture(input_filename)
    last_frame = None
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        # ここでフレームを加工する処理を行う
        gray_img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        last_frame = gray_img

    cap.release()

    # 加工された最後のフレームを画像ファイルとして保存
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
        output_filename = tmp.name
        cv2.imwrite(output_filename, last_frame)

    # 最後のフレームの画像ファイルをレスポンスとして返す
    return FileResponse(output_filename, media_type="image/jpeg")


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

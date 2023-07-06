import tempfile

import cv2
import uvicorn
from fastapi import FastAPI, File, UploadFile

app = FastAPI()


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile() as tmp:
        tmp.write(await file.read())
        filename = tmp.name
        cap = cv2.VideoCapture(filename)
        _, frame = cap.read()
        return {
            "height": frame.shape[0],
            "width": frame.shape[1],
            "channels": frame.shape[2],
        }


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

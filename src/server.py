from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse, StreamingResponse
import cv2
import asyncio
import uvicorn
import os
import numpy as np

# Create dummy classes to avoid crashing if dependencies are missing during analysis
class DummyStream:
    def __init__(self, *args, **kwargs): pass
    def start(self): pass
    def stop(self): pass
    def read(self): return True, None
    def restart(self): pass

class DummyDetector:
    def __init__(self, *args, **kwargs): pass
    def predict(self, frame): return frame

try:
    from src.core import StreamHandler
    from src.inference.detector import Detector
    from src.config import settings
except ImportError:
    class settings:
        STREAM_URL = 0
        MODEL_PATH = "models/yolo11n.pt"
    StreamHandler = DummyStream
    Detector = DummyDetector

app = FastAPI()

# Initialize components
camera = StreamHandler(settings.STREAM_URL)
detector = Detector(model_path=settings.MODEL_PATH)

def generate_frames():
    try:
        camera.start()
        while True:
            ret, frame = camera.read()
            if not ret or frame is None:
                # If no frame, yield a black placeholder
                frame = np.zeros((640, 640, 3), dtype=np.uint8)
                cv2.putText(frame, "Waiting for Stream...", (150, 320), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
            # Predict and get annotated frame
            annotated_frame = detector.predict(frame)
            
            # Encode as JPEG
            _, buffer = cv2.imencode('.jpg', annotated_frame)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
    except Exception as e:
        print(f"Error in stream: {e}")
    finally:
        camera.stop()

@app.get("/video_feed")
async def video_feed():
    return StreamingResponse(generate_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

@app.get("/", response_class=HTMLResponse)
async def get_index():
    template_path = os.path.join(os.path.dirname(__file__), "web_template.html")
    if os.path.exists(template_path):
        with open(template_path, "r") as f:
            return f.read()
    return "<h1>Web template not found</h1>"

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

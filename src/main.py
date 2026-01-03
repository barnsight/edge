from core.camera import StreamHandler
import time
import cv2

from core.config import settings
from core.logger import logger

if __name__ == "__main__":
  with StreamHandler(
    settings.STREAM_URL,
    width=settings.FRAME_WIDTH,
    height=settings.FRAME_HEIGHT
  ) as camera:

    start_time = time.time()

    restart_attempts = 0

    try:
      while True:
        ret, frame = camera.read()
        if not ret:
          if time.time() - start_time > settings.FRAME_TIMEOUT:
            logger.error("[x] Stream unhealthy - attempting restart.")   
          
            camera.restart()
            restart_attempts += 1
            if restart_attempts >= settings.MAX_RESTARTS:
              logger.critical("[-] Stream failed too many times.")
              break
          
          time.sleep(0.05)
          continue
        
        start_time = time.time()

        rotated_frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
        frame = cv2.resize(rotated_frame, (settings.FRAME_WIDTH, settings.FRAME_HEIGHT))

      # Remove it later, because it's an edge device, so it doesn't need to use WINDOWS | Install opencv-headless
        cv2.imshow("Camera", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
          break
      
      camera.stop()
      cv2.destroyAllWindows()
  
    except cv2.error as e:
      logger.error("[x] An error occured while proccessing frames.", e)
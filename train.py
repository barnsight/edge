from ultralytics import YOLO

class Train:
  def __init__(self):
    self.model = YOLO("yolo11n.pt")

  def __call__(self):
    results = self.model.train(data="coco8.yaml", epochs=100, imgsz=640)
    return results
  
if __name__ == "__main__":
  train = Train()
  train()


from ultralytics import YOLO

if __name__ == "__main__":
    # Load a model
    # model = YOLO("yolo-wsq.yaml")  # build a new model from YAML
    model = YOLO("yolo11n.pt")  # load a pretrained model (recommended for training)
    # model = YOLO("yolo-wsq.yaml").load(
    #     "yolo11n.pt"
    # )  # build from YAML and transfer weights

    # Train the model
    results = model.train(data="yolo-accident.yaml", workers=1, epochs=100, imgsz=640)

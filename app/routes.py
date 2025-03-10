from flask import Blueprint, request, jsonify, send_from_directory
import os
from config import Config
from werkzeug.utils import secure_filename
from ultralytics import YOLO, solutions
from moviepy import VideoFileClip
import shutil
import cv2

import requests

model = YOLO("buou-best.pt")
accident_model = YOLO("accident-best.pt")

bp = Blueprint("main", __name__)

# UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"txt", "pdf", "png", "jpg", "jpeg", "gif", "mp4"}


# 检查文件扩展名是否允许
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route("/")
def home():
    return {"code": 200, "message": "Hello, World!"}


def getToal(predictor):
    r = predictor.results[0]
    print(r[0])


# 文件上传
@bp.route("/upload", methods=["POST"])
def upload():
    catchFlag = False
    if "file" not in request.files:
        return jsonify({"code": 400, "message": "No file part"})

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"code": 400, "message": "No selected file"})

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(Config.UPLOAD_FOLDER, filename)
        # file.save(os.path.join(Config.UPLOAD_FOLDER, filename))
        file.save(file_path)
        source = "uploads/" + filename
        # 图片文件
        if filename.split(".")[-1] in ["png", "jpg", "jpeg"]:
            # 回调
            # model.add_callback("on_predict_postprocess_end", getToal)
            results = model([source])
            for result in results:
                # result.save_txt("predict.txt")
                # 具体结果
                summary = result.summary()
                # print(result.to_csv())
                try:
                    boxes = result.boxes
                    if boxes.is_track:
                        track_ids = boxes.id
                        print(f"Track IDs: {track_ids}")
                except Exception as e:
                    pass

                result.save(filename=Config.PREDICT_FOLDER + "/" + filename)
            file_url = request.host_url + Config.PREDICT_FOLDER + "/" + filename
            return jsonify(
                {
                    "code": 200,
                    "message": "Upload Success!",
                    "file_path": file_url,
                    "summary": summary,
                }
            )

        # 视频文件
        else:

            results = model(source, save=True, save_frames=True)

            for index, result in enumerate(results):
                print(index, result.verbose())
                if result.verbose() != "(no detections)" and catchFlag == False:
                    catchFlag = True
                    result.save(filename=Config.PREDICT_FOLDER + "/catch-pic.jpg")

            if os.path.exists(
                Config.PREDICT_FOLDER + "/" + filename.split(".")[0] + ".avi"
            ):
                os.remove(Config.PREDICT_FOLDER + "/" + filename.split(".")[0] + ".avi")

            shutil.move(
                results[0].save_dir + "/" + filename.split(".")[0] + ".avi",
                Config.PREDICT_FOLDER,
            )
            convert_avi_to_mp4(
                Config.PREDICT_FOLDER + "/" + filename.split(".")[0] + ".avi",
                Config.PREDICT_FOLDER + "/" + filename.split(".")[0] + ".mp4",
            )
            file_url = (
                request.host_url
                + Config.PREDICT_FOLDER
                + "/"
                + filename.split(".")[0]
                + ".mp4"
            )
            catchFlag = False
            return jsonify(
                {
                    "code": 200,
                    "message": "Upload Success!",
                    "file_path": file_url,
                    "catch_file": request.host_url
                    + Config.PREDICT_FOLDER
                    + "/catch-pic.jpg",
                }
            )

    return jsonify({"code": 400, "message": "File type not allowed"})


# 车流量
@bp.route("/upload2", methods=["POST"])
def upload2():
    if "file" not in request.files:
        return jsonify({"code": 400, "message": "No file part"})

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"code": 400, "message": "No selected file"})

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(Config.UPLOAD_FOLDER, filename)
        file.save(file_path)
        source = "uploads/" + filename

        # results = model(source, save=True)

        count_objects_in_region(
            source,
            Config.PREDICT_FOLDER + "/" + filename.split(".")[0] + ".avi",
            "yolo11n.pt",
        )

        # if os.path.exists(
        #     Config.PREDICT_FOLDER + "/" + filename.split(".")[0] + ".avi"
        # ):
        #     os.remove(Config.PREDICT_FOLDER + "/" + filename.split(".")[0] + ".avi")

        # shutil.move(
        #     results[0].save_dir + "/" + filename.split(".")[0] + ".avi",
        #     Config.PREDICT_FOLDER,
        # )
        convert_avi_to_mp4(
            Config.PREDICT_FOLDER + "/" + filename.split(".")[0] + ".avi",
            Config.PREDICT_FOLDER + "/" + filename.split(".")[0] + "_result.mp4",
        )
        file_url = (
            request.host_url
            + Config.PREDICT_FOLDER
            + "/"
            + filename.split(".")[0]
            + "_result.mp4"
        )

        return jsonify(
            {
                "code": 200,
                "message": "Upload Success!",
                "file_path": file_url,
            }
        )

    return jsonify({"code": 400, "message": "File type not allowed"})


# 交通事故
@bp.route("/upload3", methods=["POST"])
def upload3():
    if "file" not in request.files:
        return jsonify({"code": 400, "message": "No file part"})

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"code": 400, "message": "No selected file"})

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(Config.UPLOAD_FOLDER, filename)
        # file.save(os.path.join(Config.UPLOAD_FOLDER, filename))
        file.save(file_path)
        source = "uploads/" + filename

        results = accident_model(source, save=True, save_frames=True)

        for result in results:
            result.save("crop")
            print("日志" + result.verbose())

        if os.path.exists(
            Config.PREDICT_FOLDER + "/" + filename.split(".")[0] + ".avi"
        ):
            os.remove(Config.PREDICT_FOLDER + "/" + filename.split(".")[0] + ".avi")
        shutil.move(
            results[0].save_dir + "/" + filename.split(".")[0] + ".avi",
            Config.PREDICT_FOLDER,
        )
        convert_avi_to_mp4(
            Config.PREDICT_FOLDER + "/" + filename.split(".")[0] + ".avi",
            Config.PREDICT_FOLDER + "/" + filename.split(".")[0] + ".mp4",
        )
        file_url = (
            request.host_url
            + Config.PREDICT_FOLDER
            + "/"
            + filename.split(".")[0]
            + ".mp4"
        )

        return jsonify(
            {
                "code": 200,
                "message": "Upload Success!",
                "file_path": file_url,
            }
        )

    return jsonify({"code": 400, "message": "File type not allowed"})


def count_objects_in_region(video_path, output_video_path, model_path):
    """Count objects in a specific region within a video."""
    cap = cv2.VideoCapture(video_path)
    assert cap.isOpened(), "Error reading video file"
    w, h, fps = (
        int(cap.get(x))
        for x in (cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT, cv2.CAP_PROP_FPS)
    )
    video_writer = cv2.VideoWriter(
        output_video_path, cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h)
    )

    region_points = [(20, 200), (1080, 200)]
    # region_points = [(20, 200), (1080, 200), (1080, 150), (20, 150)]
    counter = solutions.ObjectCounter(
        show=False, region=region_points, model=model_path
    )

    while cap.isOpened():
        success, im0 = cap.read()
        if not success:
            print(
                "Video frame is empty or video processing has been successfully completed."
            )
            break
        im0 = counter.count(im0)
        video_writer.write(im0)

    cap.release()
    video_writer.release()
    cv2.destroyAllWindows()


def convert_avi_to_mp4(input_file, output_file):
    video = VideoFileClip(input_file)
    video.write_videofile(output_file, codec="libx264")
    video.close()


@bp.route("/download/<name>")
def download_file(name):
    return send_from_directory("./" + Config.UPLOAD_FOLDER, name)


bp.add_url_rule("/uploads/<name>", endpoint="download_file", build_only=True)

# 存放图片的文件夹的路径
# IMAGE_FOLDER = r"F:\work\innovate\flask\predict"
IMAGE_FOLDER = r"E:\work\flask\predict"


@bp.route("/predict/<filename>")
def serve_image(filename):
    # 检查文件是否存在以及是否是安全的文件名（防止路径遍历攻击）
    file_path = os.path.join(IMAGE_FOLDER, filename)
    if ".." in filename or not os.path.isfile(file_path):
        return "Error: File not found or invalid filename", 404
    # 返回图片文件
    return send_from_directory(IMAGE_FOLDER, filename)

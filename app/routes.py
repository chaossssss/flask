from flask import Blueprint, request, jsonify, send_from_directory
import os
from config import Config
from werkzeug.utils import secure_filename

bp = Blueprint("main", __name__)

# UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"txt", "pdf", "png", "jpg", "jpeg", "gif"}


# 检查文件扩展名是否允许
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route("/")
def home():
    return {"code": 200, "message": "Hello, World!"}


# 文件上传
@bp.route("/upload", methods=["POST"])
def upload():
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
        file_url = request.host_url + "uploads/" + filename
        return jsonify(
            {"code": 200, "message": "Upload Success!", "file_path": file_url}
        )

    return jsonify({"code": 400, "message": "File type not allowed"})


@bp.route("/download/<name>")
def download_file(name):
    return send_from_directory("./" + Config.UPLOAD_FOLDER, name)


bp.add_url_rule("/uploads/<name>", endpoint="download_file", build_only=True)

# 存放图片的文件夹的路径
IMAGE_FOLDER = r"E:\work\flask\uploads"


@bp.route("/uploads/<filename>")
def serve_image(filename):
    # 检查文件是否存在以及是否是安全的文件名（防止路径遍历攻击）
    file_path = os.path.join(IMAGE_FOLDER, filename)
    if ".." in filename or not os.path.isfile(file_path):
        return "Error: File not found or invalid filename", 404
    # 返回图片文件
    return send_from_directory(IMAGE_FOLDER, filename)

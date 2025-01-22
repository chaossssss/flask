from flask import Blueprint, request, jsonify
import os

from werkzeug.utils import secure_filename

bp = Blueprint("main", __name__)

UPLOAD_FOLDER = "uploads"
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
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        return jsonify({"code": 200, "message": "Upload Success!"})

    return jsonify({"code": 400, "message": "File type not allowed"})

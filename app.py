import os
import uuid
import subprocess
import shutil
from pathlib import Path

from flask import Flask, request, send_file, jsonify
from flask_cors import CORS

BASE_DIR = Path(__file__).resolve().parent
WORK_DIR = Path("/tmp")

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 400 * 1024 * 1024  # 400MB
CORS(app)

ALLOWED_QUALITIES = {
    "screen": "/screen",
    "ebook": "/ebook",
    "printer": "/printer",
    "prepress": "/prepress",
    "default": "/default",
}


def run_ghostscript(input_path: Path, output_path: Path, quality: str) -> None:
    preset = ALLOWED_QUALITIES.get(quality, "/ebook")

    gs_path = shutil.which("gs") or "/opt/homebrew/bin/gs"

    cmd = [
        gs_path,
        "-sDEVICE=pdfwrite",
        "-dCompatibilityLevel=1.4",
        f"-dPDFSETTINGS={preset}",
        "-dNOPAUSE",
        "-dQUIET",
        "-dBATCH",
        f"-sOutputFile={output_path}",
        str(input_path),
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "Ghostscript 压缩失败")


@app.route("/health", methods=["GET"])
def health():
    return {"ok": True}


@app.route("/compress", methods=["POST"])
def compress():
    if "pdf" not in request.files:
        return jsonify(error="未找到上传文件"), 400

    file = request.files["pdf"]
    if file.filename == "":
        return jsonify(error="请选择 PDF 文件"), 400

    if not file.filename.lower().endswith(".pdf"):
        return jsonify(error="仅支持 PDF 文件"), 400

    quality = request.form.get("quality", "ebook")

    file_id = uuid.uuid4().hex
    input_path = WORK_DIR / f"{file_id}.pdf"
    output_path = WORK_DIR / f"{file_id}_compressed.pdf"

    file.save(str(input_path))

    try:
        run_ghostscript(input_path, output_path, quality)
        return send_file(
            output_path,
            as_attachment=True,
            download_name="compressed.pdf",
            mimetype="application/pdf",
        )
    finally:
        if input_path.exists():
            input_path.unlink(missing_ok=True)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "10000"))
    app.run(host="0.0.0.0", port=port)

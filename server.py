import os
import json
from datetime import datetime

import requests
from flask import Flask, request, send_from_directory, jsonify, make_response

try:
    from flask_cors import CORS
except Exception:
    CORS = None

APP_PORT = int(os.environ.get("PORT", "5053"))
DIFY_API_KEY = os.environ.get("DIFY_API_KEY", "app-NqbWgMDFL11ifKnao2NoKidS")
DIFY_BASE = os.environ.get("DIFY_BASE", "https://api.dify.ai")
BASE_DIR = os.path.dirname(__file__)
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
DIST_DIR = os.path.join(BASE_DIR, "dist")
SERVE_DIST = os.environ.get("SERVE_DIST", "1") == "1"

app = Flask(__name__)
if CORS:
    CORS(app, resources={r"/*": {"origins": "*"}})

os.makedirs(UPLOAD_DIR, exist_ok=True)


def serve_static(filename):
    """Serve built assets from dist when available and enabled, otherwise dev files."""
    dist_path = os.path.join(DIST_DIR, filename)
    if SERVE_DIST and os.path.exists(dist_path):
        return send_from_directory(DIST_DIR, filename)
    return send_from_directory(BASE_DIR, filename)


def corsify(resp):
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Headers"] = "*"
    resp.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    return resp


@app.route("/")
def index():
    return serve_static("index.html")

@app.route("/about.html")
def about_page():
    return serve_static("about.html")

@app.route("/cbam.html")
def cbam_page():
    return serve_static("cbam.html")

@app.route("/faq.html")
def faq_page():
    return serve_static("faq.html")


@app.route("/app.js")
def app_js():
    return serve_static("app.js")


@app.route("/style.css")
def style_css():
    return serve_static("style.css")


@app.route("/image/<path:filename>")
def image_files(filename):
    dist_image_dir = os.path.join(DIST_DIR, "image")
    base_image_dir = os.path.join(BASE_DIR, "image")
    if SERVE_DIST and os.path.exists(os.path.join(dist_image_dir, filename)):
        return send_from_directory(dist_image_dir, filename)
    return send_from_directory(base_image_dir, filename)


@app.route("/api/health")
def health():
    return corsify(jsonify({"status": "ok", "time": datetime.utcnow().isoformat()}))


@app.route("/api/upload", methods=["POST", "OPTIONS"]) 
def upload_file():
    if request.method == "OPTIONS":
        return corsify(make_response("", 204))

    file = request.files.get("file")
    if not file:
        return corsify(jsonify({"error": "missing file field 'file'"})), 400

    # Save a copy locally for debug
    ts = int(datetime.utcnow().timestamp() * 1000)
    local_name = f"{ts}-{file.filename}"
    local_path = os.path.join(UPLOAD_DIR, local_name)
    file.save(local_path)

    files = {"file": (file.filename, open(local_path, "rb"), file.mimetype or "application/octet-stream")}
    headers = {"Authorization": f"Bearer {DIFY_API_KEY}"}
    try:
        r = requests.post(f"{DIFY_BASE}/v1/files/upload", headers=headers, files=files, timeout=60)
        r.raise_for_status()
    except requests.RequestException as e:
        return corsify(jsonify({"error": "upload_failed", "detail": str(e)})), 502

    data = r.json()
    return corsify(jsonify(data))


@app.route("/api/workflow", methods=["POST", "OPTIONS"]) 
def run_workflow():
    if request.method == "OPTIONS":
        return corsify(make_response("", 204))

    try:
        payload = request.get_json(force=True)
    except Exception:
        payload = None
    if not payload:
        return corsify(jsonify({"error": "invalid_json"})), 400

    source_url = payload.get("source_url") or payload.get("inputfile")
    user = payload.get("user") or "demo-user"
    if not source_url:
        return corsify(jsonify({"error": "missing source_url"})), 400

    headers = {"Authorization": f"Bearer {DIFY_API_KEY}", "Content-Type": "application/json"}
    body = {
        "inputs": {"inputfile": source_url},
        "response_mode": "blocking",
        "user": user,
    }

    try:
        r = requests.post(f"{DIFY_BASE}/v1/workflows/run", headers=headers, json=body, timeout=120)
        r.raise_for_status()
    except requests.RequestException as e:
        return corsify(jsonify({"error": "workflow_failed", "detail": str(e)})), 502

    return corsify(jsonify(r.json()))


if __name__ == "__main__":
    print(f"[cacbonsolution] starting at http://localhost:{APP_PORT}/")
    app.run(host="0.0.0.0", port=APP_PORT)
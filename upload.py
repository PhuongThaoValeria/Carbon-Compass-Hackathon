import os
from datetime import datetime
import requests
from flask import Flask, request, jsonify, make_response

app = Flask(__name__)

# Use /tmp for serverless writable storage (Vercel only allows /tmp)
UPLOAD_DIR = os.environ.get("UPLOAD_DIR", "/tmp/uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.route("/", methods=["POST", "OPTIONS"]) 
def upload():
    # Optional CORS preflight (not needed for same-origin on Vercel)
    if request.method == "OPTIONS":
        resp = make_response("", 204)
        resp.headers["Access-Control-Allow-Origin"] = "*"
        resp.headers["Access-Control-Allow-Headers"] = "*"
        resp.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
        return resp

    file = request.files.get("file")
    if not file:
        return jsonify({"error": "missing file field 'file'"}), 400

    dify_base = os.environ.get("DIFY_BASE", "https://api.dify.ai")
    dify_key = os.environ.get("DIFY_API_KEY")
    if not dify_key:
        return jsonify({"error": "missing DIFY_API_KEY"}), 500

    # Persist the uploaded file to /tmp to comply with serverless write constraints
    ts = int(datetime.utcnow().timestamp() * 1000)
    local_name = f"{ts}-{file.filename}"
    local_path = os.path.join(UPLOAD_DIR, local_name)
    try:
        file.save(local_path)
    except Exception as e:
        return jsonify({"error": "save_failed", "detail": str(e)}), 500

    headers = {"Authorization": f"Bearer {dify_key}"}

    # Stream from local temp file to Dify
    try:
        with open(local_path, "rb") as f:
            files = {
                "file": (
                    file.filename,
                    f,
                    file.mimetype or "application/octet-stream",
                )
            }
            r = requests.post(f"{dify_base}/v1/files/upload", headers=headers, files=files, timeout=60)
            r.raise_for_status()
    except requests.RequestException as e:
        return jsonify({"error": "upload_failed", "detail": str(e)}), 502
    finally:
        try:
            os.remove(local_path)
        except Exception:
            pass

    return jsonify(r.json())
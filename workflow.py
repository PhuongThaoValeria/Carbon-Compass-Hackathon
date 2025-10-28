import os
import requests
from flask import Flask, request, jsonify, make_response

app = Flask(__name__)


@app.route("/", methods=["POST", "OPTIONS"]) 
def workflow():
    # Optional CORS preflight (not needed for same-origin on Vercel)
    if request.method == "OPTIONS":
        resp = make_response("", 204)
        resp.headers["Access-Control-Allow-Origin"] = "*"
        resp.headers["Access-Control-Allow-Headers"] = "*"
        resp.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
        return resp

    try:
        payload = request.get_json(force=True)
    except Exception:
        payload = None
    if not payload:
        return jsonify({"error": "invalid_json"}), 400

    source_url = payload.get("source_url") or payload.get("inputfile")
    user = payload.get("user") or "demo-user"
    if not source_url:
        return jsonify({"error": "missing source_url"}), 400

    dify_base = os.environ.get("DIFY_BASE", "https://api.dify.ai")
    dify_key = os.environ.get("DIFY_API_KEY")
    if not dify_key:
        return jsonify({"error": "missing DIFY_API_KEY"}), 500

    headers = {"Authorization": f"Bearer {dify_key}", "Content-Type": "application/json"}
    body = {
        "inputs": {"inputfile": source_url},
        "response_mode": "blocking",
        "user": user,
    }

    try:
        r = requests.post(f"{dify_base}/v1/workflows/run", headers=headers, json=body, timeout=120)
        r.raise_for_status()
    except requests.RequestException as e:
        return jsonify({"error": "workflow_failed", "detail": str(e)}), 502

    return jsonify(r.json())
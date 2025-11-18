# api.py — ECG AI Backend API

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import pandas as pd
import json
import time

# === Import analyzer functions ===
from ecg_analyzer import analyze_ecg_signal, analyze_ecg_image, LABELS, WIN_LEN

# === Flask App Setup ===
app = Flask(__name__, static_folder=".")
CORS(app)
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# === Save JSON Results ===
def save_json_result(result_dict, prefix="ecg"):
    folder = "json_outputs"
    os.makedirs(folder, exist_ok=True)
    ts = time.strftime("%Y%m%d-%H%M%S")
    filename = f"{prefix}_{ts}.json"
    path = os.path.join(folder, filename)
    with open(path, "w") as f:
        json.dump(result_dict, f, indent=2)
    return path

# === Serve Main Frontend ===
@app.route("/")
def serve_index():
    return send_from_directory(".", "index.html")

@app.route("/<path:filename>")
def serve_static(filename):
    return send_from_directory(".", filename)

# === ECG Analyze Endpoint ===
@app.route("/predict", methods=["POST"])
def predict():
    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "Empty filename"}), 400

    try:
        filename = file.filename.lower()
        print(f"[📥] File received: {filename}")

        # --- CSV Input ---
        if filename.endswith(".csv"):
            df = pd.read_csv(file)
            if df.shape[1] == 0:
                return jsonify({"error": "CSV appears empty"}), 400
            signal = df.iloc[:, 0].values.astype("float32")
            result = analyze_ecg_signal(signal)

        # --- Image Input ---
        else:
            img_bytes = file.read()
            result = analyze_ecg_image(img_bytes)

        # --- Save Full Result to Disk ---
        json_path = save_json_result(result, prefix="ecg_reading")
        print(f"[📊] Saved JSON to: {json_path}")

        # --- Format Output for Frontend ---
        response = {
            "diagnosis": {
                "Heart Rate": result["heart_rate"],
                "Rhythm": result["rhythm"],
                "PR Interval": result["pr_interval"],
                "QRS Duration": result["qrs_duration"],
                "QT Interval": result["qt_interval"],
                "Assessment": result["assessment"]
            },
            "score": {
                "Confidence": result["confidence_score"],
                "Risk Level": result["risk_level"]
            },
            "doctors_notes": result["recommendation"]
        }

        return jsonify(response)

    except Exception as e:
        print(f"[❌] Error during processing: {str(e)}")
        return jsonify({"error": str(e)}), 500

# === Debug Info Endpoint ===
@app.route("/debug/info", methods=["GET"])
def debug_info():
    return jsonify({
        "label_classes": list(map(str, LABELS)),
        "cnn_input_length": int(WIN_LEN),
        "status": "ok"
    })

# === Run App ===
if __name__ == "__main__":
    app.run(debug=True, port=5000)

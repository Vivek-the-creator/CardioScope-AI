# ecg_analyzer.py
import os
import numpy as np
import cv2
import matplotlib
matplotlib.use('Agg')  # Use this backend to avoid GUI issues
import matplotlib.pyplot as plt
import uuid
import json
import neurokit2 as nk
import tensorflow as tf
from keras.saving import register_keras_serializable


@register_keras_serializable(package="legacy")
class LegacyLSTM(tf.keras.layers.LSTM):
    """Compat wrapper to ignore deprecated arguments from older checkpoints."""

    def __init__(self, *args, time_major=False, **kwargs):
        super().__init__(*args, **kwargs)


from tensorflow.keras.models import load_model
from skimage.filters import threshold_otsu
from scipy.signal import find_peaks, peak_widths, resample, butter, filtfilt
from scipy.ndimage import gaussian_filter1d
from imutils.perspective import four_point_transform

# ────────────────────────────────────────────────────────────────
# 1. SETUP
# ────────────────────────────────────────────────────────────────

MODEL_PATH = "ecg_model.h5"
LABELS_PATH = "label_classes.npy"
DEBUG_FOLDER = "trace_debug"
RESULTS_FOLDER = "json_outputs"

os.makedirs(DEBUG_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)

MODEL = load_model(
    MODEL_PATH,
    compile=False,
    safe_mode=False,
    custom_objects={"LSTM": LegacyLSTM}
)
LABELS = np.load(LABELS_PATH)
WIN_LEN = MODEL.input_shape[1]

# ────────────────────────────────────────────────────────────────
# 2. IMAGE PROCESSING
# ────────────────────────────────────────────────────────────────

def _deskew_and_crop(img):
    """Deskews and crops the ECG paper to a flattened, aligned image."""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if img.ndim == 3 else img
    edges = cv2.Canny(gray, 50, 150)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 200, minLineLength=150, maxLineGap=20)

    if lines is not None:
        x1, y1, x2, y2 = max(lines, key=lambda l: np.hypot(l[0][2]-l[0][0], l[0][3]-l[0][1]))[0]
        angle = np.degrees(np.arctan2(y2 - y1, x2 - x1))
        h, w = gray.shape[:2]
        M = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
        gray = cv2.warpAffine(gray, M, (w, h), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REPLICATE)

    _, bw = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
    cnts, _ = cv2.findContours(bw, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if cnts:
        c = max(cnts, key=cv2.contourArea)
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        if len(approx) == 4:
            gray = four_point_transform(gray, approx.reshape(4, 2))
    return gray

def _estimate_fs(gray):
    """Estimate sampling frequency using vertical and horizontal gridlines."""
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    bw = (blur < threshold_otsu(blur)).astype(int)
    col = bw.sum(axis=0)
    row = bw.sum(axis=1)
    vx, _ = find_peaks(col, prominence=col.max() * 0.4, distance=20)
    hy, _ = find_peaks(row, prominence=row.max() * 0.4, distance=20)

    if len(vx) > 1 and len(hy) > 1:
        px = (np.median(np.diff(vx)) + np.median(np.diff(hy))) / 2
        return int(px * 5)  # assume 5 mm per second at 25 mm/s
    return 250  # fallback to 250 Hz

def _extract_trace(gray):
    """Extracts the most prominent lead as signal trace from a grayscale ECG image."""
    fs = _estimate_fs(gray)
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    bw = (blur < threshold_otsu(blur)).astype(np.uint8) * 255
    h, w = bw.shape

    template = (255 - bw[h // 4, :]).astype(float)
    best_corr, best_row, best_trace = -np.inf, 0, None

    for r in range(0, h, 2):
        row = (255 - bw[r, :]).astype(float)
        corr = np.correlate(row, template, mode="valid")[0]
        if corr > best_corr:
            best_corr, best_row, best_trace = corr, r, row

    if best_corr < 1e5 or best_trace is None:
        variances = [(np.var((255 - bw[r, :]).astype(float)), r) for r in range(0, h, 2)]
        best_row = max(variances)[1]
        best_trace = (255 - bw[best_row, :]).astype(float)

    trace = (best_trace - best_trace.mean()) / (best_trace.std() + 1e-6)
    full = resample(trace, fs * 10)
    window = resample(full, WIN_LEN)
    return window, full, fs

# ────────────────────────────────────────────────────────────────
# 3. ANALYSIS
# ────────────────────────────────────────────────────────────────

def _cnn(window):
    probs = MODEL.predict(window.reshape(1, -1, 1), verbose=0)[0]
    idx = int(np.argmax(probs))
    return LABELS[idx], float(probs[idx] * 100)

def _hr_rr(sig, fs):
    try:
        clean = nk.ecg_clean(sig, sampling_rate=fs)
        peaks = nk.ecg_peaks(clean, sampling_rate=fs)[1]["ECG_R_Peaks"]
        if len(peaks) >= 2:
            rr = np.diff(peaks) / fs
            return int(round(60 / np.median(rr))), rr
    except:
        pass

    try:
        peaks, _ = find_peaks(sig, height=np.percentile(sig, 90), distance=0.25 * fs)
        if len(peaks) >= 2:
            rr = np.diff(peaks) / fs
            return int(round(60 / np.median(rr))), rr
    except:
        pass

    return 60, np.array([1.0])  # fallback heart rate

def _intervals(sig, fs):
    try:
        sig = nk.ecg_clean(sig, sampling_rate=fs)
        _, info = nk.ecg_peaks(sig, sampling_rate=fs)
        sig, w = nk.ecg_delineate(sig, info["ECG_R_Peaks"], sampling_rate=fs)
        pr = (w["ECG_P_Offsets"] - w["ECG_P_Onsets"]) / fs * 1000
        qrs = (w["ECG_S_Peaks"] - w["ECG_Q_Peaks"]) / fs * 1000
        qt = (w["ECG_T_Offsets"] - w["ECG_Q_Peaks"]) / fs * 1000
        return int(np.nanmedian(pr)), int(np.nanmedian(qrs)), int(np.nanmedian(qt))
    except:
        return 120, 80, 400  # fallback intervals

# ────────────────────────────────────────────────────────────────
# 4. DOCTOR NOTES GENERATOR
# ────────────────────────────────────────────────────────────────

def _doctor_notes(label, hr, rr_std):
    if label == "N" and hr < 120 and hr > 50:
        print(
            "This ECG trace appears to show normal sinus rhythm with no concerning anomalies. \nPlease continue regular cardiac screenings and maintain a balanced lifestyle."
        )
    if label == "N" and (hr < 50 or hr > 120):
        return (
            "Your heart rhythm seems regular, but the heart rate is outside the typical range. \nConsider following up with a physician to evaluate possible bradycardia or tachycardia."
        )
    if "AFib" in label or "Irregular" in label:
        return (
            "There are signs of an irregular heartbeat suggestive of atrial fibrillation or similar arrhythmia. \nPlease consult a cardiologist promptly for a full evaluation and possible treatment options."
        )
    return (
        "The model detected abnormalities that may need medical evaluation.\n"
        "Please seek a cardiologist's opinion and consider additional diagnostics."
    )

# ────────────────────────────────────────────────────────────────
# 5. FORMATTING AND OUTPUT
# ────────────────────────────────────────────────────────────────

def _format(hr, rr, label, conf, pr, qrs, qt):
    normal = label == "N"
    risk = "Low" if normal else "Moderate"
    if hr < 50 or hr > 120:
        risk = "High"
    if len(rr) >= 8 and np.std(rr) * 1000 > 120 and normal:
        label = "Possible AFib / Irregular"
        risk = "Moderate"

    return {
        "heart_rate": f"{hr} BPM",
        "rhythm": "Sinus Rhythm" if normal else label,
        "pr_interval": f"{pr} ms",
        "qrs_duration": f"{qrs} ms",
        "qt_interval": f"{qt} ms",
        "assessment": "Normal ECG" if normal else "Abnormal ECG",
        "recommendation": _doctor_notes(label, hr, rr),
        "confidence_score": f"{conf:.1f}%",
        "risk_level": risk
    }

# ────────────────────────────────────────────────────────────────
# 6. PUBLIC API
# ────────────────────────────────────────────────────────────────

def analyze_ecg_image(img_bytes):
    raw = cv2.imdecode(np.frombuffer(img_bytes, np.uint8), cv2.IMREAD_COLOR)
    gray = _deskew_and_crop(raw)
    win, full, fs = _extract_trace(gray)
    label, conf = _cnn(win)
    hr, rr = _hr_rr(full, fs)
    pr, qrs, qt = _intervals(full, fs)
    result = _format(hr, rr, label, conf, pr, qrs, qt)
    _save_result_json(result)
    return result

def analyze_ecg_signal(arr, fs=360):
    sig = (np.asarray(arr, float) - np.mean(arr)) / (np.std(arr) + 1e-6)
    win = resample(sig, WIN_LEN)
    label, conf = _cnn(win)
    hr, rr = _hr_rr(sig, fs)
    pr, qrs, qt = _intervals(sig, fs)
    result = _format(hr, rr, label, conf, pr, qrs, qt)
    _save_result_json(result)
    return result

def _save_result_json(data):
    fname = f"result_{uuid.uuid4().hex[:8]}.json"
    path = os.path.join(RESULTS_FOLDER, fname)
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
    return path

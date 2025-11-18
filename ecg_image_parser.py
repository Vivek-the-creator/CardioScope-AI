import cv2, numpy as np
from scipy.signal import resample

def _deskew(img):
    edges = cv2.Canny(img, 50, 150, apertureSize=3)
    lines = cv2.HoughLines(edges, 1, np.pi/180, 200)
    if lines is None:          # looks straight
        return img
    angle = np.median([l[0][1] for l in lines])
    rot = (angle - np.pi/2) * 180/np.pi      # deg offset from 90 °
    M = cv2.getRotationMatrix2D((img.shape[1]/2, img.shape[0]/2), rot, 1.0)
    return cv2.warpAffine(img, M, img.shape[::-1], flags=cv2.INTER_LINEAR,
                          borderMode=cv2.BORDER_REPLICATE)

def image_to_signal(img_bytes: bytes, out_len: int = 180) -> np.ndarray:
    raw = cv2.imdecode(np.frombuffer(img_bytes, np.uint8), cv2.IMREAD_GRAYSCALE)
    if raw is None:
        raise ValueError("Corrupted or unsupported image")
    img  = _deskew(raw)

    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    img   = clahe.apply(img)
    img   = cv2.medianBlur(img, 3)

    _, bw = cv2.threshold(img, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)
    grid  = cv2.morphologyEx(bw, cv2.MORPH_OPEN,
            cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3)))
    bw    = cv2.bitwise_and(bw, cv2.bitwise_not(grid))

    rowsum = bw.sum(axis=1)
    r = int(np.argmax(rowsum))
    band  = bw[max(0, r-40): r+40, :]            # pick fattest trace row
    trace = 255 - band.mean(axis=0)              # 0–255 ➜ waveform
    trace = (trace - trace.min()) / (trace.ptp() + 1e-6) - 0.5
    return resample(trace, out_len).astype(np.float32)

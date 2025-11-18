import os
import numpy as np
import pandas as pd

DATA_DIR = r"C:\Users\priya\My files\My Projects\Cardia Care - Internship\Ecg analysis - my role\Dataset organizer\data\converted"  # your CSV folder
WINDOW_SIZE = 180
OVERLAP = 90  # Set to 90 for 50% overlap

# Supported arrhythmia labels
LABELS = ["N", "L", "R", "A", "V"]  # normal, LBBB, RBBB, AFib, PVC

def extract_windows(signal, label, window_size):
    windows = []
    labels = []
    step = window_size - OVERLAP
    for i in range(0, len(signal) - window_size, step):
        segment = signal[i:i+window_size]
        segment = (segment - np.mean(segment)) / (np.std(segment) + 1e-6)
        windows.append(segment)
        labels.append(label)
    return windows, labels

def build_dataset():
    all_X = []
    all_y = []

    for file in os.listdir(DATA_DIR):
        if not file.endswith(".csv"):
            continue

        full_path = os.path.join(DATA_DIR, file)
        df = pd.read_csv(full_path)

        # Detect label from filename or column (adjust if needed)
        if "label" in df.columns:
            label = df['label'].iloc[0]
            signal = df.iloc[:, 0].values
        else:
            label = 'N'  # fallback
            signal = df.iloc[:, 0].values

        if label not in LABELS:
            continue

        X_win, y_win = extract_windows(signal, label, WINDOW_SIZE)
        all_X.extend(X_win)
        all_y.extend(y_win)

    X = np.array(all_X)
    y = np.array(all_y)

    print(f"✅ X shape: {X.shape}, y shape: {y.shape}")
    np.save("X_mitdb.npy", X)
    np.save("y_mitdb.npy", y)

if __name__ == "__main__":
    build_dataset()

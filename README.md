# ECG Analysis

Lightweight Flask service for running an ECG arrhythmia detector that can
ingest either raw numeric traces (`.csv`) or scanned ECG images. The backend
loads a pre-trained CNN/LSTM model (`ecg_model.h5`) to produce rhythm
classification, intervals, heart rate estimates, risk scoring, and a brief
recommendation summary. A bundled HTML/JS front-end (`index.html`, `script.js`,
`style.css`) consumes the `/predict` endpoint, but the API can also be called
directly.

> **Disclaimer:** This project is for research/education only and must not be
> relied on for medical decisions.

---

## Requirements

- Python 3.11+ (tested on 3.13.5)
- pip
- ~1.5 GB of disk space for model + datasets

Install Python dependencies:

```powershell
cd "C:\Users\Vivek\OneDrive\Desktop\ECG Analysis"
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

> TensorFlow 2.20.0, OpenCV, NeuroKit2, and other scientific packages are
> required; installation may take several minutes. If you already have GPU
> drivers/CUDA installed, TensorFlow will automatically use them.

---

## Running the API

```powershell
python app.py
```

The Flask dev server starts on `http://127.0.0.1:5000` with live reload
(`debug=True`). Open `index.html` in your browser (served automatically by
navigating to the root URL) or call the API manually.

### API Summary

| Method | Endpoint    | Body                                         | Description                          |
| ------ | ----------- | -------------------------------------------- | ------------------------------------ |
| POST   | `/predict`  | multipart form field named `file`; accepts `.csv` or image formats (`.png`, `.jpg`, `.jpeg`, `.bmp`) | Runs ECG analysis and returns structured JSON |
| GET    | `/debug/info` | none                                      | Returns model label information and window length |

Sample `curl` call:

```bash
curl -X POST http://127.0.0.1:5000/predict ^
  -H "Content-Type: multipart/form-data" ^
  -F "file=@sample_ecg.csv"
```

The response JSON includes `diagnosis`, `score`, and `doctors_notes` sections.
A copy of the full result is persisted under `json_outputs/`.

---

## Data & Assets

- `sample_ecg.csv` & `data/converted/*.csv` – numeric ECG traces
- `data/mitdb/` – MIT-BIH dataset copies (not required to run inference)
- `static/` & `trace_debug/` – debugging plots and assets generated during analysis
- `uploads/` – runtime uploads saved when using the UI

The analysis pipeline lives in `ecg_analyzer.py` and loads
`ecg_model.h5` plus `label_classes.npy`. If you retrain new models, update
those artefacts in place.

---

## Troubleshooting

- **TensorFlow protobuf warnings:** Running with newer protobuf runtimes than
  the model was exported with prints many warnings. They are harmless for
  inference. Keep dependencies pinned to `requirements.txt`.
- **`LegacyLSTM` loading error:** The repository includes a compatibility shim
  for old checkpoints. Do not remove the `LegacyLSTM` class unless you
  regenerate the model using modern Keras APIs.
- **Large dependency installs:** On Windows you may need to run the terminal as
  Administrator or use a virtual environment if global installs fail.
- **GPU drivers:** If the server logs mention missing AVX instructions, ignore
  them unless you need maximum performance; the CPU path works out-of-the-box.

---

## Development Notes

- Run formatting/linting manually as needed; no toolchain is enforced.
- Store new inference runs automatically via `save_json_result()` in `app.py`.
- Add unit tests or notebooks if you extend preprocessing or model logic.

Happy experimenting!


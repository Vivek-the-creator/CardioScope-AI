<div align="center">
  
  # 🫀 CardioScope-AI 🫀
</div>
<div align="center">

### AI-Powered ECG Analyzer System

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/downloads/)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.20.0-orange.svg)](https://www.tensorflow.org/)
[![Flask](https://img.shields.io/badge/Flask-Latest-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**⚠️DISCLAIMER: This project is intended for research and educational use only. The results may be approximate and should not be fully relied upon for medical decisions or clinical diagnosis.**

[Features](#-features) • [Demo](#-demo) • [Installation](#-installation) • [Usage](#-usage) • [API Reference](#-api-reference) • [Contributing](#-contributing)

[Sample Output](#-sample-output)

</div>

---

## 📋 Overview

ECG Analysis Platform is a **lightweight Flask-based web service** that leverages deep learning (CNN/LSTM) to analyze electrocardiogram data for arrhythmia detection. The system accepts both **raw numeric traces** (`.csv`) and **scanned ECG images**, providing comprehensive cardiac rhythm analysis.

### What It Does

- 🔍 **Rhythm Classification** - Identifies normal sinus rhythm and various arrhythmias
- 📏 **Interval Measurements** - PR, QRS, QT interval analysis
- ❤️ **Heart Rate Estimation** - Accurate BPM calculation
- ⚠️ **Risk Assessment** - Confidence scoring and risk stratification
- 📝 **Clinical Recommendations** - AI-generated doctor's notes and actionable insights

The platform includes a **modern web interface** for patient management, real-time visualization, and report generation, while also offering a **REST API** for programmatic access.

---

## ✨ Features

### Core Capabilities

- 🔍 **Multi-Format Input** - Supports CSV numeric traces and image formats (PNG, JPG, JPEG, BMP)
- 🧠 **Deep Learning Model** - Pre-trained CNN/LSTM architecture trained on MIT-BIH dataset
- 📊 **12-Lead ECG Support** - Comprehensive analysis of standard ECG leads (I, II, III, aVR, aVL, aVF, V1-V6)
- 📈 **Real-Time Visualization** - Interactive Chart.js plotting for waveform analysis
- 💾 **Patient Management** - LocalStorage-based patient records with full CRUD operations
- 📄 **Report Generation** - Structured JSON outputs with persistent storage in `json_outputs/`
- 🔌 **REST API** - Clean, documented API for integration with external systems

### Technical Features

- ⚡ **GPU Acceleration** - Automatic CUDA utilization when available
- 🔧 **Signal Processing** - NeuroKit2 integration for advanced preprocessing
- 🎯 **High Accuracy** - Trained on validated MIT-BIH arrhythmia database
- 🔒 **Secure File Handling** - Validated uploads with type and size checking
- 📱 **Responsive Design** - Works seamlessly on desktop and mobile browsers
- 🐛 **Debug Tools** - Built-in debugging endpoints and trace visualization

***

## 🎬 Demo

### Web Interface Features

1. **Patient Information Form** - Capture name, age, and gender
2. **Drag-and-Drop Upload** - Easy file upload with preview
3. **Live Analysis** - Real-time processing with AI feedback
4. **Interactive Charts** - Zoom, pan, and explore ECG waveforms
5. **Patient History** - Sidebar with saved patient records
6. **Export Options** - Download reports and analysis results

### Example

```json
{
  "diagnosis": {
    "Rhythm": "Normal Sinus Rhythm",
    "Classification": "Normal",
    "Heart_Rate_BPM": 72,
    "PR_Interval_ms": 160,
    "QRS_Duration_ms": 90,
    "QT_Interval_ms": 400
  },
  "score": {
    "Confidence": 0.95,
    "Risk_Level": "Low",
    "Model_Version": "1.0"
  },
  "doctors_notes": "Regular rhythm detected. All intervals within normal limits. No immediate concerns identified. Continue routine monitoring."
}
```

***


## 📊 Sample Output

<div align="center">

### Interface Screenshots

<table>
  <tr>
    <td><img src="https://github.com/user-attachments/assets/9a6a548a-285e-40ae-8cb9-fcf1a47f9163" alt="Patient Upload" width="500"/></td>
    <td><img src="https://github.com/user-attachments/assets/b03c454b-c00e-48e3-811d-c41c4c0bda2d" alt="Analysis Results" width="500"/></td>
    <td><img src="https://github.com/user-attachments/assets/d6fb00f3-b8d8-4739-962d-f6fc0fb1fc23" alt="ECG Chart View" width="500"/></td>
  </tr>
  <tr>
    <td align="center"><b>1. Landing Page</b></td>
    <td align="center"><b>2. Analysis Results</b></td>
    <td align="center"><b>3. ECG Chart View</b></td>
  </tr>
</table>

</div>


***



## 🚀 Installation

### Prerequisites

- **Python 3.11+** (tested on 3.13.5)
- **pip** package manager
- **~1.5 GB** disk space for model and dependencies
- *Optional:* CUDA-capable GPU with drivers for accelerated inference

### Quick Start

#### Step 1: Clone Repository

```bash
git clone https://github.com/Vivek-the-creator/ECG-Analyser.git
cd ECG-Analyser
```

#### Step 2: Install Dependencies

```powershell
# Upgrade pip
python -m pip install --upgrade pip

# Install all requirements
python -m pip install -r requirements.txt
```

> **Note:** Installation may take several minutes. TensorFlow 2.20.0, OpenCV, NeuroKit2, and other scientific packages will be downloaded (~1.5 GB total).

#### Step 3: Verify Installation

```bash
python -c "import tensorflow as tf; print(f'TensorFlow {tf.__version__} installed successfully')"
```

### Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

***

## 💻 Usage

### Starting the Server

```powershell
python app.py
```

The Flask development server starts at **`http://127.0.0.1:5000`** with live reload enabled (`debug=True`).

```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

### Web Interface Workflow

1. **Navigate** to `http://127.0.0.1:5000` in your browser
2. **Enter Patient Details:**
   - Name (required)
   - Age (required)
   - Gender (required)
3. **Upload ECG File:**
   - Drag-and-drop or click "Browse"
   - Supports `.csv` (numeric traces) or images (`.png`, `.jpg`, `.jpeg`, `.bmp`)
4. **View Results:**
   - Diagnosis with rhythm classification
   - Risk score and confidence level
   - Doctor's notes and recommendations
   - Interactive waveform chart (CSV files only)
5. **Manage Records:**
   - Save patient data to browser storage
   - Load previous records from sidebar
   - Update existing patient information
   - Delete old records

### Command-Line API Usage

#### Analyze CSV File

```bash
curl -X POST http://127.0.0.1:5000/predict \
  -H "Content-Type: multipart/form-data" \
  -F "file=@sample_ecg.csv"
```

#### Analyze ECG Image

```bash
curl -X POST http://127.0.0.1:5000/predict \
  -F "file=@ecg_scan.png"
```

#### Get Model Information

```bash
curl http://127.0.0.1:5000/debug/info
```

***

## 📡 API Reference

### Endpoints

#### `POST /predict`

Analyzes uploaded ECG data and returns classification results.

**Request:**
- **Method:** `POST`
- **Content-Type:** `multipart/form-data`
- **Body:** File field named `file`
- **Accepted Formats:** `.csv`, `.png`, `.jpg`, `.jpeg`, `.bmp`

**Response:** `200 OK`
```json
{
  "diagnosis": {
    "Rhythm": "string",
    "Classification": "string",
    "Heart_Rate_BPM": "number"
  },
  "score": {
    "Confidence": "number (0-1)",
    "Risk_Level": "string (Low/Medium/High)"
  },
  "doctors_notes": "string"
}
```

**Example:**
```bash
curl -X POST http://127.0.0.1:5000/predict ^
  -H "Content-Type: multipart/form-data" ^
  -F "file=@sample_ecg.csv"
```

#### `GET /debug/info`

Returns model metadata and configuration.

**Request:**
- **Method:** `GET`
- **Body:** None

**Response:** `200 OK`
```json
{
  "model_version": "1.0",
  "label_classes": ["Normal", "Atrial Fibrillation", ...],
  "window_length": 1000,
  "sampling_rate": 360
}
```
***

## 📂 Project Structure

```
ECG-Analyser/
├── app.py                    # Flask server and API routes
├── ecg_analyzer.py           # Core analysis pipeline
├── ecg_model.h5              # Pre-trained CNN/LSTM model
├── label_classes.npy         # Model output labels
├── requirements.txt          # Python dependencies
├── README.md                 # This file
│
├── index.html                # Web UI entry point
├── script.js                 # Frontend logic and API calls
├── style.css                 # UI styling
│
├── sample_ecg.csv            # Example ECG data
│
├── data/
│   ├── mitdb/                # MIT-BIH dataset (optional)
│   └── converted/            # Additional CSV traces
│
├── static/                   # Static assets for UI
├── trace_debug/              # Debug plots (runtime generated)
├── uploads/                  # Uploaded files (runtime generated)
└── json_outputs/             # Analysis results (runtime generated)
```

***

## 📊 Data & Assets

### Input Data

- **`sample_ecg.csv`** - Example 12-lead ECG trace for testing
- **`data/converted/*.csv`** - Additional numeric ECG traces
- **`data/mitdb/`** - MIT-BIH Arrhythmia Database copies (not required for inference)

### CSV Format

```csv
time,I,II,III,aVR,aVL,aVF,V1,V2,V3,V4,V5,V6
0.000,-0.145,-0.145,0.000,0.145,0.000,-0.145,0.145,0.145,0.145,0.145,0.145,0.145
0.003,-0.150,-0.150,0.000,0.150,0.000,-0.150,0.150,0.150,0.150,0.150,0.150,0.150
...
```

### Model Files

- **`ecg_model.h5`** - TensorFlow/Keras model (CNN/LSTM architecture)
- **`label_classes.npy`** - NumPy array of output class labels

### Runtime Directories

- **`uploads/`** - Temporary storage for uploaded files
- **`json_outputs/`** - Persistent JSON results for each analysis
- **`trace_debug/`** - Debug plots and visualization artifacts
- **`static/`** - Additional static assets

***

## 🔧 Troubleshooting

### Common Issues

#### TensorFlow Protobuf Warnings

**Symptom:** Many protobuf-related warnings during model loading

**Solution:** These are harmless for inference. Keep dependencies pinned to `requirements.txt` versions. Suppress warnings:

```python
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
```

#### `LegacyLSTM` Loading Error

**Symptom:** Error loading model due to missing `LegacyLSTM` layer

**Solution:** The repository includes a compatibility shim for old checkpoints. Do **not** remove the `LegacyLSTM` class from `ecg_analyzer.py` unless you regenerate the model with modern Keras APIs.

#### Large Dependency Install Failures

**Symptom:** Pip fails to install TensorFlow or other large packages

**Solution:**
- Run terminal as Administrator (Windows)
- Use a virtual environment
- Ensure sufficient disk space (~2 GB free)
- Try: `pip install --no-cache-dir -r requirements.txt`

#### GPU/CUDA Issues

**Symptom:** Warnings about missing AVX instructions or CUDA libraries

**Solution:**
- CPU inference works out-of-the-box (ignore warnings)
- For GPU acceleration, install CUDA toolkit matching TensorFlow version
- Check: `python -c "import tensorflow as tf; print(tf.config.list_physical_devices('GPU'))"`

#### Port Already in Use

**Symptom:** `Address already in use` error on port 5000

**Solution:**
- Change port in `app.py`: `app.run(debug=True, port=5001)`
- Or kill existing process using port 5000

***

## 🛠️ Development

### Code Structure

- **`app.py`** - Flask routes, file handling, JSON persistence via `save_json_result()`
- **`ecg_analyzer.py`** - Preprocessing, model inference, signal processing with NeuroKit2
- **`script.js`** - Frontend logic: file uploads, Chart.js plotting, localStorage for patients
- **`index.html`** - UI layout with forms, sidebar, chart canvas
- **`style.css`** - Responsive styling for all UI components

### Extending the Project

#### Retrain the Model

1. Prepare new training data in `data/` directory
2. Train using TensorFlow/Keras
3. Save as `ecg_model.h5` and update `label_classes.npy`
4. Test with `sample_ecg.csv`

#### Add New Features

- **Unit Tests:** Create `tests/` directory with pytest
- **Notebooks:** Add Jupyter notebooks for data exploration
- **Linting:** Use `black` and `flake8` for code formatting
- **CI/CD:** Set up GitHub Actions for automated testing

### Best Practices

- Run formatting/linting manually as needed (no enforced toolchain)
- Store new inference runs automatically via `save_json_result()`
- Add unit tests if extending preprocessing or model logic
- Document new endpoints in this README

***

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

### How to Contribute

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/AmazingFeature`)
3. **Commit** your changes (`git commit -m 'Add some AmazingFeature'`)
4. **Push** to the branch (`git push origin feature/AmazingFeature`)
5. **Open** a Pull Request

### Contribution Guidelines

- Follow existing code style and structure
- Add tests for new features
- Update documentation (README, docstrings)
- Ensure all tests pass before submitting PR
- Use descriptive commit messages

### Areas for Improvement

- [ ] Add comprehensive unit tests
- [ ] Implement PDF export for reports
- [ ] Support for additional ECG formats (HL7, DICOM)
- [ ] Multi-language support for UI
- [ ] Real-time streaming ECG analysis
- [ ] Integration with hospital systems (FHIR)
- [ ] Mobile app (React Native/Flutter)
- [ ] Docker containerization
- [ ] Cloud deployment guide (AWS, Azure, GCP)

***

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2025 Vivek-the-creator

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction...
```

***

## 🙏 Acknowledgments

- **MIT-BIH Arrhythmia Database** - Training data source ([PhysioNet](https://physionet.org/))
- **TensorFlow Team** - Deep learning framework
- **NeuroKit2** - ECG signal processing toolkit
- **Flask** - Web framework
- **Chart.js** - Interactive visualization library
- **OpenCV** - Image processing capabilities

### Research Citations

If you use this project in your research, please cite:

```bibtex
@software{ecg_analyser_2025,
  author = {Vivek},
  title = {ECG Analysis Platform: AI-Powered Arrhythmia Detection},
  year = {2025},
  url = {https://github.com/Vivek-the-creator/ECG-Analyser}
}
```

***

## 📞 Contact & Support

- **GitHub Issues:** [Report bugs or request features](https://github.com/Vivek-the-creator/ECG-Analyser/issues)
- **Discussions:** [Ask questions and share ideas](https://github.com/Vivek-the-creator/ECG-Analyser/discussions)
- **Email:** [Contact the maintainer](mailto:vivek@example.com)

***

## 🔮 Roadmap

### Version 1.1 (Q1 2026)
- [ ] PDF report export
- [ ] Docker support
- [ ] Improved mobile UI
- [ ] Additional arrhythmia classes

### Version 2.0 (Q2 2026)
- [ ] Real-time streaming analysis
- [ ] Multi-user authentication
- [ ] Cloud deployment
- [ ] Integration APIs for EHR systems

---

## ⚡ Quick Reference

| Task | Command |
|------|---------|
| Start server | `python app.py` |
| Install dependencies | `pip install -r requirements.txt` |
| Test API | `curl -X POST http://127.0.0.1:5000/predict -F "file=@sample_ecg.csv"` |
| Check model info | `curl http://127.0.0.1:5000/debug/info` |
| Access web UI | Open `http://127.0.0.1:5000` |

***

<div align="center">


**Made with ❤️ by Team MeshMinds**

[⬆ Back to Top](#cardioscope-ai)


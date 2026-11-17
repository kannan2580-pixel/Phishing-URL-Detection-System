# PHISHING URL DETECTION SYSTEM

whether a web URL is **Legitimate** or **Phishing** based on lexical and structural features.

---

## 🌟 Key Features

- **16-Feature Extraction Engine:** Extracts structural URL features safely without visiting remote servers.
- **Machine Learning Classifier:** Pre-trained **Random Forest Classifier** with 100% tesct accuracy.
- **Risk Level Meter Gauge:** Displays probability-based risk percentage (0% to 100%).
- **Interactive Flask Web App:** Modern, glassmorphic UI with quick test samples and scan history.
- **SQLite Database Persistence:** Audit logging for scan histories and usage statistics.
- **Automated Test Suite:** Pytest integration and unit test coverage.
- **Publication-Quality Academic PDF Report:** Generated automatically as `Phishing_URL_Detection_Project_Report.pdf`.

---

## 📁 Project Structure

```text
e:\PHISHING URL DETECTION SYSTEM\
├── app\
│   ├── __init__.py
│   ├── feature_extractor.py          # 16-Feature Extraction Engine
│   ├── database.py                   # SQLite Management & Storage
│   ├── routes.py                     # Flask REST API & Web Routes
│   ├── models\                       # Saved ML Model & Metrics JSON
│   │   ├── phishing_model.pkl
│   │   ├── feature_names.pkl
│   │   ├── scaler.pkl
│   │   └── metrics.json
│   ├── templates\                    # HTML5 Templates
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── history.html
│   │   └── metrics.html
│   └── static\                       # CSS, JS, and Images
│       ├── css\style.css
│       ├── js\main.js
│       └── images\                   # Screenshot & Diagram PNGs
├── dataset\
│   ├── generate_dataset.py           # Dataset Generator
│   └── phishing_urls.csv             # 2,000 Sample Dataset
├── tests\                            # Pytest Test Suite
│   ├── test_extractor.py
│   └── test_app.py
├── train_model.py                    # ML Model Pipeline Script
├── generate_diagrams.py              # Architecture & Workflow Diagram Generator
├── capture_screenshots.py            # Screenshot Capturing Tool
├── generate_pdf.py                   # Academic Report PDF Generator
├── run.py                            # Flask Application Entrypoint
├── requirements.txt                  # Python Package Dependencies
├── README.md                         # Documentation
├── VIVA_QUESTIONS.md                 # Student Viva & Module Guide
└── Phishing_URL_Detection_Project_Report.pdf # FINAL GENERATED ACADEMIC REPORT
```

---

## 🚀 Quick Start Guide

### 1. Prerequisites
Ensure Python 3.9+ is installed on your system.

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Train Model & Generate Dataset
```bash
python train_model.py
```

### 4. Generate Visual Diagrams & Screenshots
```bash
python generate_diagrams.py
python capture_screenshots.py
```

### 5. Run Web Application
```bash
python run.py
```
Open your browser and navigate to: `http://127.0.0.1:5000`

---

## 🧪 Running Automated Tests

Run the full pytest suite to verify feature extraction and Flask routes:
```bash
python -m pytest tests/
```

---

## 📄 Generating Final PDF Report

To re-generate the academic PDF report:
```bash
python generate_pdf.py
```
The report will be created at: `e:\PHISHING URL DETECTION SYSTEM\Phishing_URL_Detection_Project_Report.pdf`

---

## 🎓 Viva Voce & Academic Defense

Refer to [`VIVA_QUESTIONS.md`](VIVA_QUESTIONS.md) for simple module breakdowns and frequently asked viva questions with answers.

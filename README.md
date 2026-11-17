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
Phishing-URL-Detection-System/
│
├── app/
│   ├── __init__.py
│   ├── content_analyzer.py
│   ├── feature_extractor.py
│   ├── database.py
│   ├── routes.py
│   │
│   ├── models/
│   │   ├── phishing_model.pkl
│   │   ├── feature_names.pkl
│   │   ├── scaler.pkl
│   │   └── metrics.json
│   │
│   ├── templates/
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── history.html
│   │   └── metrics.html
│   │
│   └── static/
│       ├── css/
│       │   └── style.css
│       ├── js/
│       │   └── main.js
│       └── images/
│
├── dataset/
│   ├── generate_dataset.py
│   └── phishing_urls.csv
│
├── tests/
│   ├── test_app.py
│   ├── test_content_analyzer.py
│   └── test_extractor.py
│
├── train_model.py
├── run.py
├── requirements.txt
├── .gitignore
└── README.md
```
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

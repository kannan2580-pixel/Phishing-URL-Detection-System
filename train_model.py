"""
Machine Learning Training and Evaluation Pipeline.
Trains Random Forest, Decision Tree, and Logistic Regression models on extracted URL features,
evaluates performance metrics, generates visualization artifacts, and saves the best model.
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for generating PNG plots
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report
)

from app.feature_extractor import FeatureExtractor
from dataset.generate_dataset import generate_dataset, CSV_PATH

BASE_DIR = os.path.dirname(__file__)
MODELS_DIR = os.path.join(BASE_DIR, 'app', 'models')
STATIC_IMG_DIR = os.path.join(BASE_DIR, 'app', 'static', 'images')

os.makedirs(MODELS_DIR, exist_ok=True)
os.makedirs(STATIC_IMG_DIR, exist_ok=True)


def train_and_evaluate():
    # Step 1: Ensure Dataset Exists
    if not os.path.exists(CSV_PATH):
        print("Dataset not found. Generating dataset...")
        generate_dataset()

    print(f"Loading dataset from {CSV_PATH}...")
    df = pd.read_csv(CSV_PATH)
    print(f"Dataset contains {len(df)} URLs.")

    # Step 2: Feature Extraction
    print("Extracting URL features...")
    features_list = []
    for url in df['url']:
        feats = FeatureExtractor.extract_features(url)
        features_list.append(feats)

    X = pd.DataFrame(features_list)
    y = df['label']
    feature_names = list(X.columns)

    # Step 3: Train / Test Split (80% Train, 20% Test)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    # Scale features for algorithms that require scaling
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Step 4: Model Exploration & Comparison
    print("Training ML Models...")

    models = {
        'Random Forest': RandomForestClassifier(n_estimators=100, max_depth=12, random_state=42),
        'Decision Tree': DecisionTreeClassifier(max_depth=10, random_state=42),
        'Logistic Regression': LogisticRegression(max_iter=1000, random_state=42)
    }

    comparison_results = {}
    trained_models = {}

    for name, model in models.items():
        if name == 'Logistic Regression':
            model.fit(X_train_scaled, y_train)
            preds = model.predict(X_test_scaled)
        else:
            model.fit(X_train, y_train)
            preds = model.predict(X_test)

        acc = accuracy_score(y_test, preds)
        prec = precision_score(y_test, preds, zero_division=0)
        rec = recall_score(y_test, preds, zero_division=0)
        f1 = f1_score(y_test, preds, zero_division=0)

        comparison_results[name] = {
            'accuracy': float(round(acc, 4)),
            'precision': float(round(prec, 4)),
            'recall': float(round(rec, 4)),
            'f1_score': float(round(f1, 4))
        }
        trained_models[name] = (model, preds)

        print(f"[{name}] Accuracy: {acc:.4f}, Precision: {prec:.4f}, Recall: {rec:.4f}, F1: {f1:.4f}")

    # Select Best Model (Random Forest)
    best_model_name = 'Random Forest'
    best_model, best_preds = trained_models[best_model_name]

    # Calculate actual detailed performance metrics for Best Model
    acc = accuracy_score(y_test, best_preds)
    prec = precision_score(y_test, best_preds)
    rec = recall_score(y_test, best_preds)
    f1 = f1_score(y_test, best_preds)
    cm = confusion_matrix(y_test, best_preds)
    tn, fp, fn, tp = cm.ravel()

    # Calculate Feature Importances
    importances = best_model.feature_importances_
    feat_imp = sorted(zip(feature_names, importances), key=lambda x: x[1], reverse=True)
    feat_imp_dict = {k: float(round(v, 4)) for k, v in feat_imp}

    metrics_payload = {
        'model_name': best_model_name,
        'dataset_size': len(df),
        'train_size': len(X_train),
        'test_size': len(X_test),
        'accuracy': float(round(acc, 4)),
        'precision': float(round(prec, 4)),
        'recall': float(round(rec, 4)),
        'f1_score': float(round(f1, 4)),
        'confusion_matrix': {
            'tn': int(tn),
            'fp': int(fp),
            'fn': int(fn),
            'tp': int(tp)
        },
        'feature_importances': feat_imp_dict,
        'model_comparison': comparison_results
    }

    # Step 5: Save Model, Scaler, and Feature Names
    joblib.dump(best_model, os.path.join(MODELS_DIR, 'phishing_model.pkl'))
    joblib.dump(feature_names, os.path.join(MODELS_DIR, 'feature_names.pkl'))
    joblib.dump(scaler, os.path.join(MODELS_DIR, 'scaler.pkl'))

    with open(os.path.join(MODELS_DIR, 'metrics.json'), 'w') as f:
        json.dump(metrics_payload, f, indent=4)

    print("\nBest Model Saved Successfully.")

    # Step 6: Generate Visualizations (Confusion Matrix & Feature Importances)
    plt.figure(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Legitimate', 'Phishing'], yticklabels=['Legitimate', 'Phishing'])
    plt.title(f'Confusion Matrix - {best_model_name}', fontsize=12, fontweight='bold', pad=10)
    plt.xlabel('Predicted Label', fontweight='bold')
    plt.ylabel('True Label', fontweight='bold')
    plt.tight_layout()
    cm_path = os.path.join(STATIC_IMG_DIR, 'confusion_matrix.png')
    plt.savefig(cm_path, dpi=300)
    plt.close()

    # Feature Importance plot
    plt.figure(figsize=(9, 5))
    top_feats = feat_imp[:10]
    names, vals = zip(*top_feats)
    plt.barh(range(len(names)), vals, color='#3b82f6')
    plt.yticks(range(len(names)), names)
    plt.gca().invert_yaxis()
    plt.title('Top 10 Feature Importances (Random Forest)', fontsize=12, fontweight='bold')
    plt.xlabel('Relative Importance Score', fontweight='bold')
    plt.tight_layout()
    fi_path = os.path.join(STATIC_IMG_DIR, 'feature_importance.png')
    plt.savefig(fi_path, dpi=300)
    plt.close()

    print(f"Generated plots:\n - {cm_path}\n - {fi_path}")
    return metrics_payload

if __name__ == '__main__':
    train_and_evaluate()

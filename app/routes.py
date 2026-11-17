"""
Flask Application Routes and API Endpoints for Phishing URL Detection System.
Combines Random Forest ML URL feature analysis with Website Content Inspection & SSRF protections.
"""

import os
import json
import joblib
import pandas as pd
from flask import Blueprint, render_template, request, jsonify, redirect, url_for

from app.feature_extractor import FeatureExtractor
from app.content_analyzer import WebsiteContentAnalyzer
from app.database import save_analysis, get_history, get_stats, init_db

main_bp = Blueprint('main', __name__, template_folder='templates')

MODELS_DIR = os.path.join(os.path.dirname(__file__), 'models')
MODEL_PATH = os.path.join(MODELS_DIR, 'phishing_model.pkl')
FEATURE_NAMES_PATH = os.path.join(MODELS_DIR, 'feature_names.pkl')
METRICS_PATH = os.path.join(MODELS_DIR, 'metrics.json')

# Global variables for model and feature names
model = None
feature_names = None


def load_ml_model():
    """Loads the trained Random Forest model and feature names from disk."""
    global model, feature_names
    if os.path.exists(MODEL_PATH) and os.path.exists(FEATURE_NAMES_PATH):
        try:
            model = joblib.load(MODEL_PATH)
            feature_names = joblib.load(FEATURE_NAMES_PATH)
            print("ML model and feature names loaded successfully.")
        except Exception as e:
            print(f"Error loading ML model: {e}")
            model = None
            feature_names = None
    else:
        print("ML model file not found. Please run train_model.py first.")


# Initialize DB and Load Model on module import
init_db()
load_ml_model()


@main_bp.app_context_processor
def inject_global_context():
    """Injects default statistics into all template contexts automatically."""
    try:
        stats = get_stats()
    except Exception:
        stats = {
            'total_scans': 0,
            'phishing_count': 0,
            'legitimate_count': 0,
            'average_risk_score': 0.0
        }
    return dict(stats=stats)


@main_bp.route('/')
def index():
    """Home Page / URL Analyzer Interface."""
    stats = get_stats()
    return render_template('index.html', stats=stats)


@main_bp.route('/analyze', methods=['POST'])
def analyze():
    """
    Handles URL Analysis request.
    1. Validates URL format.
    2. Extracts 16 URL lexical/structural features & predicts ML risk.
    3. Safely fetches website HTML content (with anti-SSRF & timeout constraints).
    4. Evaluates hybrid risk level (LOW, MEDIUM, HIGH, UNKNOWN/UNVERIFIED).
    5. Stores audit log in SQLite and returns JSON / HTML response.
    """
    global model, feature_names

    # Reload model if missing
    if model is None or feature_names is None:
        load_ml_model()

    # Extract URL from JSON request or Form data
    if request.is_json:
        data = request.get_json()
        raw_url = data.get('url', '').strip() if data else ''
    else:
        raw_url = request.form.get('url', '').strip()

    # Security & Input Validation
    if not raw_url:
        return jsonify({
            'status': 'error',
            'message': 'Please enter a URL to analyze.'
        }), 400

    if not FeatureExtractor.is_valid_url(raw_url):
        return jsonify({
            'status': 'error',
            'message': 'Invalid URL format. Please provide a valid web address or domain (e.g., https://example.com).'
        }), 400

    # Step 1: Extract URL Lexical Features
    features_dict = FeatureExtractor.extract_features(raw_url)

    # Step 2: Perform Machine Learning URL Prediction
    if model is not None and feature_names is not None:
        try:
            df_features = pd.DataFrame([features_dict])[feature_names]
            pred_code = model.predict(df_features)[0]

            if hasattr(model, 'predict_proba'):
                probabilities = model.predict_proba(df_features)[0]
                url_risk_score = float(probabilities[1]) * 100.0
            else:
                url_risk_score = 100.0 if pred_code == 1 else 0.0

            ml_prediction = "Phishing" if pred_code == 1 else "Legitimate"

        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': f'ML Prediction computation failed: {str(e)}'
            }), 500
    else:
        # Fallback estimation if model file is uninitialized
        suspicious_score = (
            features_dict['has_ip'] * 40 +
            features_dict['has_shortener'] * 30 +
            (1 if features_dict['suspicious_keyword_count'] > 0 else 0) * 20 +
            (1 if features_dict['dot_count'] > 3 else 0) * 10
        )
        url_risk_score = min(100.0, float(suspicious_score))
        ml_prediction = "Phishing" if url_risk_score >= 50.0 else "Legitimate"

    url_risk_score_rounded = round(url_risk_score, 2)

    # Step 3: Safely Fetch and Inspect Website Content
    fetch_result = WebsiteContentAnalyzer.fetch_website_content(raw_url)
    content_analysis = WebsiteContentAnalyzer.analyze_html_content(raw_url, fetch_result)

    # Step 4: Hybrid Risk Evaluation
    evaluation = WebsiteContentAnalyzer.evaluate_hybrid_risk(
        raw_url=raw_url,
        ml_risk_score=url_risk_score_rounded,
        ml_prediction=ml_prediction,
        content_analysis=content_analysis
    )

    final_prediction = evaluation['prediction_label']
    final_risk_score = evaluation['combined_risk_score']
    outcome_level = evaluation['outcome_level']
    reasons = evaluation['reasons']

    # Step 5: Save to SQLite Database
    record_id = save_analysis(
        url=raw_url,
        prediction=final_prediction,
        risk_score=final_risk_score,
        features=features_dict,
        outcome_level=outcome_level,
        content_analysis=content_analysis,
        reasons=reasons
    )

    response_payload = {
        'status': 'success',
        'id': record_id,
        'url': raw_url,
        'prediction': final_prediction,
        'outcome_level': outcome_level,
        'risk_score': final_risk_score,
        'url_risk_score': url_risk_score_rounded,
        'content_risk_score': evaluation.get('content_risk_score'),
        'is_phishing': (final_prediction in ('Phishing', 'Suspicious')),
        'summary_text': evaluation['summary_text'],
        'reasons': reasons,
        'features': features_dict,
        'content_analysis': content_analysis
    }

    if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify(response_payload)
    else:
        stats = get_stats()
        return render_template('index.html', result=response_payload, stats=stats)


@main_bp.route('/history')
def history():
    """Analysis History Page displaying past analyzed URLs."""
    records = get_history(limit=100)
    stats = get_stats()
    return render_template('history.html', history=records, stats=stats)


@main_bp.route('/metrics')
def metrics():
    """ML Performance Metrics & Visualizations Page."""
    metrics_data = None
    if os.path.exists(METRICS_PATH):
        with open(METRICS_PATH, 'r') as f:
            metrics_data = json.load(f)
    return render_template('metrics.html', metrics=metrics_data)


@main_bp.route('/api/stats')
def api_stats():
    """JSON endpoint for application statistics."""
    return jsonify(get_stats())


@main_bp.route('/api/history')
def api_history():
    """JSON endpoint for analysis history."""
    limit = request.args.get('limit', 50, type=int)
    return jsonify(get_history(limit=limit))


@main_bp.app_errorhandler(404)
def page_not_found(e):
    return render_template('index.html', error="Page not found (404).", stats=get_stats()), 404


@main_bp.app_errorhandler(500)
def internal_server_error(e):
    return render_template('index.html', error="Internal server error (500).", stats=get_stats()), 500

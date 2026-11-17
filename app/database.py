"""
SQLite Database Management Module for Phishing URL Detection System.
Handles table initialization, saving analysis results, and retrieving analysis history.
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

DB_PATH = os.path.join(os.path.dirname(__file__), 'phishing_detector.db')


def get_db_connection():
    """Establishes and returns a SQLite database connection with row factory."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initializes the database schema if tables do not exist and migrates new columns."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analysis_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            prediction TEXT NOT NULL,
            risk_score REAL NOT NULL,
            features_json TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            outcome_level TEXT DEFAULT 'UNKNOWN',
            content_json TEXT DEFAULT '{}',
            reasons_json TEXT DEFAULT '[]'
        )
    ''')

    # Migrations for existing tables
    cursor.execute("PRAGMA table_info(analysis_history)")
    columns = [row['name'] for row in cursor.fetchall()]

    if 'outcome_level' not in columns:
        cursor.execute("ALTER TABLE analysis_history ADD COLUMN outcome_level TEXT DEFAULT 'UNKNOWN'")
    if 'content_json' not in columns:
        cursor.execute("ALTER TABLE analysis_history ADD COLUMN content_json TEXT DEFAULT '{}'")
    if 'reasons_json' not in columns:
        cursor.execute("ALTER TABLE analysis_history ADD COLUMN reasons_json TEXT DEFAULT '[]'")

    conn.commit()
    conn.close()


def save_analysis(
    url: str,
    prediction: str,
    risk_score: float,
    features: Dict[str, Any],
    outcome_level: str = "UNKNOWN",
    content_analysis: Optional[Dict[str, Any]] = None,
    reasons: Optional[List[str]] = None
) -> int:
    """
    Saves an analysis record into the database.
    Returns the newly inserted record ID.
    """
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()

    features_str = json.dumps(features or {})
    content_str = json.dumps(content_analysis or {})
    reasons_str = json.dumps(reasons or [])
    created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    cursor.execute('''
        INSERT INTO analysis_history (url, prediction, risk_score, features_json, outcome_level, content_json, reasons_json, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (url, prediction, risk_score, features_str, outcome_level, content_str, reasons_str, created_at))

    record_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return record_id


def get_history(limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
    """Retrieves list of past analyzed URLs."""
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT id, url, prediction, risk_score, features_json, outcome_level, content_json, reasons_json, created_at
        FROM analysis_history
        ORDER BY id DESC
        LIMIT ? OFFSET ?
    ''', (limit, offset))

    rows = cursor.fetchall()
    conn.close()

    history = []
    for row in rows:
        history.append({
            'id': row['id'],
            'url': row['url'],
            'prediction': row['prediction'],
            'risk_score': row['risk_score'],
            'outcome_level': row['outcome_level'] if 'outcome_level' in row.keys() and row['outcome_level'] else ('HIGH' if row['prediction'] == 'Phishing' else 'LOW'),
            'features': json.loads(row['features_json']) if row['features_json'] else {},
            'content_analysis': json.loads(row['content_json']) if 'content_json' in row.keys() and row['content_json'] else {},
            'reasons': json.loads(row['reasons_json']) if 'reasons_json' in row.keys() and row['reasons_json'] else [],
            'created_at': row['created_at']
        })
    return history


def get_stats() -> Dict[str, Any]:
    """Retrieves aggregate usage statistics for the dashboard."""
    init_db()
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) as total FROM analysis_history')
    total = cursor.fetchone()['total']

    cursor.execute("SELECT COUNT(*) as phishing FROM analysis_history WHERE prediction = 'Phishing'")
    phishing = cursor.fetchone()['phishing']

    cursor.execute("SELECT COUNT(*) as legitimate FROM analysis_history WHERE prediction = 'Legitimate'")
    legitimate = cursor.fetchone()['legitimate']

    cursor.execute('SELECT AVG(risk_score) as avg_risk FROM analysis_history')
    avg_risk_row = cursor.fetchone()
    avg_risk = round(avg_risk_row['avg_risk'] or 0.0, 2)

    conn.close()

    return {
        'total_scans': total,
        'phishing_count': phishing,
        'legitimate_count': legitimate,
        'average_risk_score': avg_risk
    }

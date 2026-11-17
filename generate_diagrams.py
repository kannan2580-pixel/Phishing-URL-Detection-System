"""
Diagram Generation Script for Phishing URL Detection System.
Generates System Architecture, Workflow, Abstract Visual, DFD, Use Case,
Activity, Sequence, ER, and ML Pipeline Diagrams as PNG images.
"""

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches

STATIC_IMG_DIR = os.path.join(os.path.dirname(__file__), 'app', 'static', 'images')
os.makedirs(STATIC_IMG_DIR, exist_ok=True)


def generate_architecture_diagram():
    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.axis('off')
    fig.patch.set_facecolor('#0f172a')
    ax.set_facecolor('#0f172a')

    boxes = [
        ("User / Client\n(Browser UI)", 0.05, 0.4, 0.22, 0.22, '#3b82f6'),
        ("Flask Web Server\n(REST API / Routes)", 0.36, 0.4, 0.24, 0.22, '#06b6d4'),
        ("Feature Extractor\n(16 Lexical Features)", 0.68, 0.68, 0.26, 0.22, '#8b5cf6'),
        ("Random Forest Model\n(Scikit-Learn ML)", 0.68, 0.4, 0.26, 0.22, '#10b981'),
        ("SQLite Database\n(Scan History & Stats)", 0.68, 0.12, 0.26, 0.22, '#f59e0b')
    ]

    for title, x, y, w, h, color in boxes:
        rect = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.03", ec=color, fc='#1e293b', lw=2.5)
        ax.add_patch(rect)
        ax.text(x + w/2, y + h/2, title, color='#f8fafc', fontsize=10, fontweight='bold', ha='center', va='center', multialignment='center')

    arrows = [
        ((0.27, 0.51), (0.36, 0.51), "HTTP Request"),
        ((0.60, 0.51), (0.68, 0.79), "Raw URL"),
        ((0.60, 0.51), (0.68, 0.51), "Features Vector"),
        ((0.60, 0.51), (0.68, 0.23), "Store Record")
    ]

    for (x1, y1), (x2, y2), label in arrows:
        ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="->", color="#94a3b8", lw=2, mutation_scale=15))

    plt.title("PHISHING URL DETECTION SYSTEM — SYSTEM ARCHITECTURE", color='#f8fafc', fontsize=13, fontweight='bold', pad=15)
    plt.tight_layout()
    path = os.path.join(STATIC_IMG_DIR, 'system_architecture.png')
    plt.savefig(path, dpi=300, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    print(f"Architecture diagram saved to {path}")


def generate_workflow_diagram():
    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.axis('off')
    fig.patch.set_facecolor('#0f172a')
    ax.set_facecolor('#0f172a')

    steps = [
        "1. Input URL\n(Form Entry)",
        "2. Security Validation\n(Format & Bounds)",
        "3. Feature Extraction\n(16 Lexical Attributes)",
        "4. ML Prediction\n(Random Forest Classifier)",
        "5. Risk Score & DB Log\n(SQLite + UI Output)"
    ]

    x_positions = [0.04 + i * 0.188 for i in range(5)]
    y_pos = 0.38
    w, h = 0.155, 0.24

    for i, (title, x) in enumerate(zip(steps, x_positions)):
        rect = patches.FancyBboxPatch((x, y_pos), w, h, boxstyle="round,pad=0.02", ec='#3b82f6', fc='#1e293b', lw=2)
        ax.add_patch(rect)
        ax.text(x + w/2, y_pos + h/2, title, color='#f8fafc', fontsize=8.5, fontweight='bold', ha='center', va='center', multialignment='center')

        if i < 4:
            ax.annotate('', xy=(x_positions[i+1], y_pos + h/2), xytext=(x + w, y_pos + h/2),
                        arrowprops=dict(arrowstyle="->", color="#06b6d4", lw=2, mutation_scale=12))

    plt.title("PHISHING URL DETECTION SYSTEM — EXECUTION WORKFLOW", color='#f8fafc', fontsize=13, fontweight='bold', pad=15)
    plt.tight_layout()
    path = os.path.join(STATIC_IMG_DIR, 'system_workflow.png')
    plt.savefig(path, dpi=300, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    print(f"Workflow diagram saved to {path}")


def generate_abstract_visual():
    fig, ax = plt.subplots(figsize=(9, 3.2))
    ax.axis('off')
    fig.patch.set_facecolor('#0f172a')
    ax.set_facecolor('#0f172a')

    # Legitimate URL Box (Left)
    rect1 = patches.FancyBboxPatch((0.03, 0.12), 0.44, 0.76, transform=ax.transAxes, boxstyle="round,pad=0.02", fc='#064e3b', ec='#10b981', lw=2)
    ax.add_patch(rect1)
    ax.text(0.25, 0.76, "LEGITIMATE URL CHARACTERISTICS", transform=ax.transAxes, color='#34d399', fontsize=9.5, fontweight='bold', ha='center')
    legit_traits = "• Valid Domain & SSL (HTTPS)\n• Standard Path Structure & Length\n• Absence of IP / URL Shortener\n• Clean Lexical Attributes"
    ax.text(0.06, 0.40, legit_traits, transform=ax.transAxes, color='#e2e8f0', fontsize=8.5, va='center', multialignment='left')

    # Phishing URL Box (Right)
    rect2 = patches.FancyBboxPatch((0.53, 0.12), 0.44, 0.76, transform=ax.transAxes, boxstyle="round,pad=0.02", fc='#450a0a', ec='#ef4444', lw=2)
    ax.add_patch(rect2)
    ax.text(0.75, 0.76, "PHISHING URL ANOMALIES", transform=ax.transAxes, color='#fca5a5', fontsize=9.5, fontweight='bold', ha='center')
    phish_traits = "• Typosquatting / Hyphenated Domain\n• Raw IP Address & Shortened Redirection\n• Excessive Subdomains & Dots (.)\n• Deceptive Keywords (login, verify, bank)"
    ax.text(0.56, 0.40, phish_traits, transform=ax.transAxes, color='#e2e8f0', fontsize=8.5, va='center', multialignment='left')

    plt.tight_layout()
    path = os.path.join(STATIC_IMG_DIR, 'abstract_visual.png')
    plt.savefig(path, dpi=300, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    print(f"Abstract visual diagram saved to {path}")


def generate_dfd_diagram():
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.axis('off')
    fig.patch.set_facecolor('#0f172a')
    ax.set_facecolor('#0f172a')

    # External Entity (User)
    ax.add_patch(patches.Rectangle((0.04, 0.38), 0.18, 0.24, fc='#1e293b', ec='#3b82f6', lw=2))
    ax.text(0.13, 0.50, "User / Browser\n(External Entity)", color='#f8fafc', fontsize=9, fontweight='bold', ha='center', va='center')

    # Processes
    proc1 = patches.Circle((0.40, 0.50), 0.11, fc='#1e293b', ec='#06b6d4', lw=2)
    ax.add_patch(proc1)
    ax.text(0.40, 0.50, "1.0 Validate &\nExtract Features", color='#f8fafc', fontsize=8.5, fontweight='bold', ha='center', va='center')

    proc2 = patches.Circle((0.68, 0.50), 0.11, fc='#1e293b', ec='#10b981', lw=2)
    ax.add_patch(proc2)
    ax.text(0.68, 0.50, "2.0 Predict ML\nClassification", color='#f8fafc', fontsize=8.5, fontweight='bold', ha='center', va='center')

    # Data Store (SQLite)
    ax.add_patch(patches.Rectangle((0.45, 0.08), 0.36, 0.18, fc='#1e293b', ec='#f59e0b', lw=2))
    ax.text(0.63, 0.17, "D1: SQLite Database\n(analysis_history table)", color='#f8fafc', fontsize=9, fontweight='bold', ha='center', va='center')

    # Data Flow Arrows
    ax.annotate('', xy=(0.29, 0.50), xytext=(0.22, 0.50), arrowprops=dict(arrowstyle="->", color="#94a3b8", lw=2))
    ax.text(0.255, 0.53, "Input URL", color='#94a3b8', fontsize=8, ha='center')

    ax.annotate('', xy=(0.57, 0.50), xytext=(0.51, 0.50), arrowprops=dict(arrowstyle="->", color="#94a3b8", lw=2))
    ax.text(0.54, 0.53, "Features Vector", color='#94a3b8', fontsize=8, ha='center')

    ax.annotate('', xy=(0.63, 0.26), xytext=(0.68, 0.39), arrowprops=dict(arrowstyle="->", color="#94a3b8", lw=2))
    ax.text(0.68, 0.30, "Log Result", color='#94a3b8', fontsize=8, ha='center')

    plt.title("DATA FLOW DIAGRAM (DFD LEVEL 1) — PHISHING URL DETECTION", color='#f8fafc', fontsize=12, fontweight='bold', pad=15)
    plt.tight_layout()
    path = os.path.join(STATIC_IMG_DIR, 'dfd_diagram.png')
    plt.savefig(path, dpi=300, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    print(f"DFD diagram saved to {path}")


def generate_use_case_diagram():
    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.axis('off')
    fig.patch.set_facecolor('#0f172a')
    ax.set_facecolor('#0f172a')

    # System Boundary Box
    sys_box = patches.FancyBboxPatch((0.25, 0.08), 0.68, 0.84, boxstyle="round,pad=0.02", fc='#1e293b', ec='#334155', lw=2)
    ax.add_patch(sys_box)
    ax.text(0.59, 0.88, "Phishing URL Detection System Boundary", color='#94a3b8', fontsize=10, fontweight='bold', ha='center')

    # Actor (User) Stick Figure representation
    ax.add_patch(patches.Circle((0.10, 0.60), 0.04, fc='#3b82f6', ec='#ffffff'))
    ax.plot([0.10, 0.10], [0.46, 0.56], color='#3b82f6', lw=3)
    ax.plot([0.05, 0.15], [0.52, 0.52], color='#3b82f6', lw=3)
    ax.plot([0.10, 0.06], [0.46, 0.36], color='#3b82f6', lw=3)
    ax.plot([0.10, 0.14], [0.46, 0.36], color='#3b82f6', lw=3)
    ax.text(0.10, 0.28, "End User /\nSecurity Analyst", color='#f8fafc', fontsize=9, fontweight='bold', ha='center')

    # Use Cases (Ovals)
    use_cases = [
        ("UC-01: Submit URL for Scan", 0.59, 0.74),
        ("UC-02: Extract Lexical Features", 0.59, 0.58),
        ("UC-03: Predict ML Classification", 0.59, 0.42),
        ("UC-04: View Scan History Logs", 0.59, 0.26),
        ("UC-05: Inspect Model Metrics", 0.59, 0.12)
    ]

    for title, x, y in use_cases:
        ellipse = patches.Ellipse((x, y), 0.34, 0.10, fc='#0f172a', ec='#06b6d4', lw=2)
        ax.add_patch(ellipse)
        ax.text(x, y, title, color='#f8fafc', fontsize=8.5, fontweight='bold', ha='center', va='center')
        ax.plot([0.14, x - 0.17], [0.50, y], color='#64748b', lw=1.5, linestyle='--')

    plt.title("USE CASE DIAGRAM — PHISHING URL DETECTION SYSTEM", color='#f8fafc', fontsize=12, fontweight='bold', pad=15)
    plt.tight_layout()
    path = os.path.join(STATIC_IMG_DIR, 'use_case_diagram.png')
    plt.savefig(path, dpi=300, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    print(f"Use case diagram saved to {path}")


def generate_activity_diagram():
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.axis('off')
    fig.patch.set_facecolor('#0f172a')
    ax.set_facecolor('#0f172a')

    # Start Node
    ax.add_patch(patches.Circle((0.50, 0.92), 0.025, fc='#10b981', ec='#ffffff'))
    ax.text(0.50, 0.96, "Start", color='#f8fafc', fontsize=8.5, fontweight='bold', ha='center')

    activities = [
        ("1. Enter URL string", 0.50, 0.80, 'rect'),
        ("2. Is URL valid?", 0.50, 0.65, 'diamond'),
        ("3. Extract 16 Features", 0.50, 0.48, 'rect'),
        ("4. ML Model Prediction", 0.50, 0.32, 'rect'),
        ("5. Log SQLite & Display UI", 0.50, 0.16, 'rect')
    ]

    for text, x, y, shape in activities:
        if shape == 'rect':
            box = patches.FancyBboxPatch((x - 0.16, y - 0.04), 0.32, 0.08, boxstyle="round,pad=0.01", fc='#1e293b', ec='#3b82f6', lw=2)
            ax.add_patch(box)
        elif shape == 'diamond':
            poly = patches.Polygon([[x, y + 0.05], [x + 0.14, y], [x, y - 0.05], [x - 0.14, y]], fc='#1e293b', ec='#f59e0b', lw=2)
            ax.add_patch(poly)
        ax.text(x, y, text, color='#f8fafc', fontsize=8.5, fontweight='bold', ha='center', va='center')

    # End Node
    ax.add_patch(patches.Circle((0.50, 0.04), 0.025, fc='#ef4444', ec='#ffffff'))
    ax.add_patch(patches.Circle((0.50, 0.04), 0.015, fc='#ffffff'))

    # Connectors
    lines = [(0.92, 0.84), (0.76, 0.70), (0.60, 0.52), (0.44, 0.36), (0.28, 0.20), (0.12, 0.065)]
    for y1, y2 in lines:
        ax.annotate('', xy=(0.50, y2), xytext=(0.50, y1), arrowprops=dict(arrowstyle="->", color="#94a3b8", lw=2))

    plt.title("ACTIVITY DIAGRAM — SYSTEM PROCESSING FLOW", color='#f8fafc', fontsize=12, fontweight='bold', pad=15)
    plt.tight_layout()
    path = os.path.join(STATIC_IMG_DIR, 'activity_diagram.png')
    plt.savefig(path, dpi=300, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    print(f"Activity diagram saved to {path}")


def generate_sequence_diagram():
    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.axis('off')
    fig.patch.set_facecolor('#0f172a')
    ax.set_facecolor('#0f172a')

    lifelines = [
        ("User Browser", 0.10),
        ("Flask Routes", 0.35),
        ("Feature Extractor", 0.60),
        ("ML Model", 0.80),
        ("SQLite DB", 0.94)
    ]

    for name, x in lifelines:
        box = patches.FancyBboxPatch((x - 0.08, 0.84), 0.16, 0.10, boxstyle="round,pad=0.01", fc='#1e293b', ec='#3b82f6', lw=1.5)
        ax.add_patch(box)
        ax.text(x, 0.89, name, color='#f8fafc', fontsize=8.5, fontweight='bold', ha='center', va='center')
        ax.plot([x, x], [0.10, 0.84], color='#475569', linestyle='--', lw=1.5)

    seq_calls = [
        (0.10, 0.35, 0.74, "POST /analyze (url)", "#06b6d4"),
        (0.35, 0.60, 0.60, "extract_features(url)", "#8b5cf6"),
        (0.60, 0.35, 0.48, "features_dict", "#8b5cf6"),
        (0.35, 0.80, 0.36, "model.predict(features)", "#10b981"),
        (0.80, 0.35, 0.26, "prediction, risk_score", "#10b981"),
        (0.35, 0.94, 0.18, "save_analysis()", "#f59e0b"),
        (0.35, 0.10, 0.12, "JSON Response (result)", "#3b82f6")
    ]

    for x1, x2, y, msg, col in seq_calls:
        ax.annotate('', xy=(x2, y), xytext=(x1, y), arrowprops=dict(arrowstyle="->", color=col, lw=2))
        ax.text((x1 + x2)/2, y + 0.02, msg, color='#e2e8f0', fontsize=7.5, ha='center')

    plt.title("SEQUENCE DIAGRAM — RUNTIME COMPONENT INTERACTION", color='#f8fafc', fontsize=12, fontweight='bold', pad=15)
    plt.tight_layout()
    path = os.path.join(STATIC_IMG_DIR, 'sequence_diagram.png')
    plt.savefig(path, dpi=300, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    print(f"Sequence diagram saved to {path}")


def generate_er_diagram():
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.axis('off')
    fig.patch.set_facecolor('#0f172a')
    ax.set_facecolor('#0f172a')

    # Entity Box
    ent_box = patches.FancyBboxPatch((0.25, 0.65), 0.50, 0.22, boxstyle="round,pad=0.02", fc='#1e293b', ec='#3b82f6', lw=2.5)
    ax.add_patch(ent_box)
    ax.text(0.50, 0.76, "ENTITY: analysis_history\n(SQLite Database Table)", color='#f8fafc', fontsize=11, fontweight='bold', ha='center', va='center')

    # Attributes (Ovals)
    attrs = [
        ("PK: id\n(INTEGER)", 0.10, 0.30),
        ("url\n(TEXT)", 0.26, 0.30),
        ("prediction\n(TEXT)", 0.42, 0.30),
        ("risk_score\n(REAL)", 0.58, 0.30),
        ("features_json\n(TEXT)", 0.74, 0.30),
        ("created_at\n(TIMESTAMP)", 0.90, 0.30)
    ]

    for name, x, y in attrs:
        ellipse = patches.Ellipse((x, y), 0.14, 0.16, fc='#0f172a', ec='#06b6d4', lw=1.5)
        ax.add_patch(ellipse)
        ax.text(x, y, name, color='#f8fafc', fontsize=7.5, fontweight='bold', ha='center', va='center')
        ax.plot([0.50, x], [0.65, y + 0.08], color='#64748b', lw=1.5)

    plt.title("ENTITY-RELATIONSHIP (ER) DIAGRAM — DATABASE SCHEMA", color='#f8fafc', fontsize=12, fontweight='bold', pad=15)
    plt.tight_layout()
    path = os.path.join(STATIC_IMG_DIR, 'er_diagram.png')
    plt.savefig(path, dpi=300, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    print(f"ER diagram saved to {path}")


def generate_ml_pipeline_diagram():
    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.axis('off')
    fig.patch.set_facecolor('#0f172a')
    ax.set_facecolor('#0f172a')

    p_steps = [
        ("1. Dataset (2000 URLs)", 0.08, '#3b82f6'),
        ("2. Feature Extraction (16 Feats)", 0.29, '#8b5cf6'),
        ("3. StandardScaler Normalization", 0.50, '#06b6d4'),
        ("4. Random Forest Classifier", 0.71, '#10b981'),
        ("5. Output Prediction & Score", 0.92, '#f59e0b')
    ]

    for title, x, col in p_steps:
        rect = patches.FancyBboxPatch((x - 0.09, 0.35), 0.17, 0.30, boxstyle="round,pad=0.02", fc='#1e293b', ec=col, lw=2)
        ax.add_patch(rect)
        ax.text(x, 0.50, title, color='#f8fafc', fontsize=8, fontweight='bold', ha='center', va='center', multialignment='center')

    for i in range(4):
        x1 = p_steps[i][1] + 0.085
        x2 = p_steps[i+1][1] - 0.095
        ax.annotate('', xy=(x2, 0.50), xytext=(x1, 0.50), arrowprops=dict(arrowstyle="->", color="#94a3b8", lw=2))

    plt.title("MACHINE LEARNING PIPELINE & TRAINING ARCHITECTURE", color='#f8fafc', fontsize=12, fontweight='bold', pad=15)
    plt.tight_layout()
    path = os.path.join(STATIC_IMG_DIR, 'ml_pipeline_diagram.png')
    plt.savefig(path, dpi=300, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    print(f"ML Pipeline diagram saved to {path}")


if __name__ == '__main__':
    generate_architecture_diagram()
    generate_workflow_diagram()
    generate_abstract_visual()
    generate_dfd_diagram()
    generate_use_case_diagram()
    generate_activity_diagram()
    generate_sequence_diagram()
    generate_er_diagram()
    generate_ml_pipeline_diagram()

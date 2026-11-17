/* Main Interactive JavaScript for Phishing URL & Content Detection System */

document.addEventListener('DOMContentLoaded', () => {
    const urlForm = document.getElementById('urlForm');
    const urlInput = document.getElementById('urlInput');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const resultCard = document.getElementById('resultCard');
    const errorMessage = document.getElementById('errorMessage');

    // Handle Form Submit
    if (urlForm) {
        urlForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const url = urlInput.value.strip ? urlInput.value.strip() : urlInput.value.trim();

            if (!url) {
                showError('Please enter a URL to analyze.');
                return;
            }

            hideError();
            setLoading(true);

            try {
                const response = await fetch('/analyze', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    body: JSON.stringify({ url: url })
                });

                const data = await response.json();

                if (response.ok && data.status === 'success') {
                    displayResult(data);
                } else {
                    showError(data.message || 'An error occurred during analysis.');
                }
            } catch (err) {
                showError('Failed to connect to the server. Please ensure Flask app is running.');
            } finally {
                setLoading(false);
            }
        });
    }

    // Set sample URL helper
    window.setSampleUrl = (sampleUrl) => {
        if (urlInput) {
            urlInput.value = sampleUrl;
            urlInput.focus();
        }
    };
});

function setLoading(isLoading) {
    const analyzeBtn = document.getElementById('analyzeBtn');
    if (!analyzeBtn) return;
    if (isLoading) {
        analyzeBtn.disabled = true;
        analyzeBtn.innerHTML = '<span class="loading-spinner"></span> Analyzing URL & Content...';
    } else {
        analyzeBtn.disabled = false;
        analyzeBtn.innerHTML = '🔍 Analyze URL & Content';
    }
}

function showError(msg) {
    const errorMessage = document.getElementById('errorMessage');
    if (errorMessage) {
        errorMessage.textContent = msg;
        errorMessage.style.display = 'block';
    }
}

function hideError() {
    const errorMessage = document.getElementById('errorMessage');
    if (errorMessage) {
        errorMessage.style.display = 'none';
    }
}

function displayResult(data) {
    const resultCard = document.getElementById('resultCard');
    const verdictBadge = document.getElementById('verdictBadge');
    const analyzedUrlText = document.getElementById('analyzedUrlText');
    const riskScoreVal = document.getElementById('riskScoreVal');
    const urlScoreVal = document.getElementById('urlScoreVal');
    const contentScoreVal = document.getElementById('contentScoreVal');
    const progressBarFill = document.getElementById('progressBarFill');
    const summaryText = document.getElementById('summaryText');
    const reasonsList = document.getElementById('reasonsList');
    const featuresContainer = document.getElementById('featuresContainer');
    const contentAnalysisGrid = document.getElementById('contentAnalysisGrid');

    if (!resultCard) return;

    const outcome = data.outcome_level || 'UNKNOWN';

    let outcomeClass = 'legitimate';
    let outcomeText = '✅ LOW RISK (LEGITIMATE)';
    let fillClass = 'fill-safe';

    if (outcome === 'HIGH') {
        outcomeClass = 'phishing';
        outcomeText = '🚨 HIGH RISK (PHISHING)';
        fillClass = 'fill-danger';
    } else if (outcome === 'MEDIUM') {
        outcomeClass = 'suspicious';
        outcomeText = '⚠️ MEDIUM RISK (SUSPICIOUS)';
        fillClass = 'fill-warning';
    } else if (outcome === 'UNKNOWN / UNVERIFIED') {
        outcomeClass = 'unverified';
        outcomeText = '❓ UNKNOWN / UNVERIFIED';
        fillClass = 'fill-neutral';
    }

    // Reset classes and badges
    resultCard.className = `result-card show ${outcomeClass}`;
    verdictBadge.className = `verdict-badge ${outcomeClass}`;
    verdictBadge.textContent = outcomeText;

    analyzedUrlText.textContent = data.url;
    riskScoreVal.textContent = (data.risk_score !== undefined ? data.risk_score : 0) + '%';
    if (urlScoreVal) urlScoreVal.textContent = (data.url_risk_score !== undefined ? data.url_risk_score : 0) + '%';
    if (contentScoreVal) {
        contentScoreVal.textContent = data.content_risk_score !== null && data.content_risk_score !== undefined 
            ? data.content_risk_score + '%' 
            : 'Unreachable';
    }

    // Update Progress Bar
    progressBarFill.style.width = (data.risk_score || 0) + '%';
    progressBarFill.className = `progress-bar-fill ${fillClass}`;

    // Executive Summary & Reasons
    if (summaryText) summaryText.textContent = data.summary_text || '';
    if (reasonsList && data.reasons) {
        reasonsList.innerHTML = '';
        data.reasons.forEach(r => {
            const li = document.createElement('li');
            li.textContent = r;
            reasonsList.appendChild(li);
        });
    }

    // HTML Content Analysis Grid
    if (contentAnalysisGrid && data.content_analysis) {
        const c = data.content_analysis;
        contentAnalysisGrid.innerHTML = `
            <div class="feature-box">
                <div class="feature-title">Content Status</div>
                <div class="feature-value" style="font-size: 1rem;">
                    ${c.content_retrieved ? '<span style="color: var(--success-green);">Fetched (200 OK)</span>' : '<span style="color: var(--warning-amber);">Content Unreachable</span>'}
                </div>
            </div>
            <div class="feature-box">
                <div class="feature-title">Page Title</div>
                <div class="feature-value" style="font-size: 0.95rem; word-break: break-word;">
                    ${c.title ? c.title : '(No Title Tag)'}
                </div>
            </div>
            <div class="feature-box">
                <div class="feature-title">Password Input Fields</div>
                <div class="feature-value" style="color: ${c.has_password_input ? 'var(--danger-red)' : 'var(--success-green)'};">
                    ${c.password_input_count || 0} Detected
                </div>
            </div>
            <div class="feature-box">
                <div class="feature-title">Total HTML Forms</div>
                <div class="feature-value">${c.form_count || 0}</div>
            </div>
            <div class="feature-box">
                <div class="feature-title">External Form Actions</div>
                <div class="feature-value" style="color: ${c.external_form_actions && c.external_form_actions.length > 0 ? 'var(--danger-red)' : 'var(--success-green)'};">
                    ${c.external_form_actions ? c.external_form_actions.length : 'None'}
                </div>
            </div>
            <div class="feature-box">
                <div class="feature-title">Brand Verification</div>
                <div class="feature-value" style="font-size: 0.95rem;">
                    ${c.brand_mismatch 
                        ? `<span style="color: var(--danger-red);">⚠️ Impersonation ('${c.brand_detected}')</span>`
                        : (c.brand_detected ? `<span style="color: var(--success-green);">✅ Verified ('${c.brand_detected}')</span>` : 'No Brand Mentioned')}
                </div>
            </div>
        `;
    }

    // Display URL Lexical Features
    if (featuresContainer && data.features) {
        featuresContainer.innerHTML = '';
        const feats = data.features;
        const displayLabels = {
            'url_length': 'URL Length',
            'dot_count': 'Dot Count (.)',
            'hyphen_count': 'Hyphen Count (-)',
            'at_count': '@ Symbol Count',
            'slash_count': 'Slash Count (/)',
            'digit_count': 'Digit Count',
            'is_https': 'HTTPS Secure',
            'has_ip': 'Raw IP Address',
            'has_shortener': 'URL Shortener',
            'subdomain_count': 'Subdomains',
            'suspicious_keyword_count': 'Suspicious Keywords',
            'url_depth': 'URL Path Depth'
        };

        for (const [key, label] of Object.entries(displayLabels)) {
            if (key in feats) {
                let val = feats[key];
                if (key === 'is_https' || key === 'has_ip' || key === 'has_shortener') {
                    val = val === 1 ? 'YES' : 'NO';
                }

                const box = document.createElement('div');
                box.className = 'feature-box';
                box.innerHTML = `
                    <div class="feature-title">${label}</div>
                    <div class="feature-value">${val}</div>
                `;
                featuresContainer.appendChild(box);
            }
        }
    }
}

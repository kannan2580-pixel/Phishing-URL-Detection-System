"""
Website Content Analyzer and Security Protection Module for Phishing Detection System.
Provides safe HTTP/HTTPS web fetching, anti-SSRF protections, HTML content inspection,
brand impersonation detection, and calibrated hybrid risk assessment.
"""

import re
import socket
import urllib.parse
import ipaddress
from typing import Dict, Any, List, Tuple, Optional
import requests
from bs4 import BeautifulSoup


class SSRFProtectionError(Exception):
    """Custom exception raised when a target URL violates SSRF security rules."""
    pass


class WebsiteContentAnalyzer:
    """Safely fetches and analyzes website HTML content to evaluate phishing risk."""

    # Maximum response size: 1.5 MB
    MAX_RESPONSE_SIZE = 1_572_864

    # Request timeouts (seconds)
    CONNECT_TIMEOUT = 2.5
    READ_TIMEOUT = 3.0
    TOTAL_TIMEOUT = 4.0

    # Max redirects
    MAX_REDIRECTS = 3

    # User-Agent header
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

    # Known popular brands and their legitimate official domain patterns
    KNOWN_BRANDS = {
        'paypal': ['paypal.com', 'paypal.me'],
        'apple': ['apple.com', 'icloud.com'],
        'microsoft': ['microsoft.com', 'live.com', 'office.com', 'outlook.com', 'msn.com', 'windows.com'],
        'google': ['google.com', 'youtube.com', 'gmail.com', 'google.co.in', 'google.org'],
        'amazon': ['amazon.com', 'amazon.co.uk', 'aws.amazon.com', 'media-amazon.com'],
        'chase': ['chase.com'],
        'wellsfargo': ['wellsfargo.com'],
        'bankofamerica': ['bankofamerica.com', 'bofa.com'],
        'netflix': ['netflix.com'],
        'facebook': ['facebook.com', 'fb.com', 'meta.com'],
        'instagram': ['instagram.com'],
        'twitter': ['twitter.com', 'x.com'],
        'linkedin': ['linkedin.com']
    }

    # Internal / Private IP networks to block (IPv4 and IPv6)
    BLOCKED_NETWORKS = [
        ipaddress.ip_network('0.0.0.0/8'),
        ipaddress.ip_network('10.0.0.0/8'),
        ipaddress.ip_network('100.64.0.0/10'),
        ipaddress.ip_network('127.0.0.0/8'),
        ipaddress.ip_network('169.254.0.0/16'),
        ipaddress.ip_network('172.16.0.0/12'),
        ipaddress.ip_network('192.0.0.0/24'),
        ipaddress.ip_network('192.0.2.0/24'),
        ipaddress.ip_network('192.168.0.0/16'),
        ipaddress.ip_network('198.18.0.0/15'),
        ipaddress.ip_network('198.51.100.0/24'),
        ipaddress.ip_network('203.0.113.0/24'),
        ipaddress.ip_network('224.0.0.0/4'),
        ipaddress.ip_network('240.0.0.0/4'),
        ipaddress.ip_network('255.255.255.255/32'),
        # IPv6
        ipaddress.ip_network('::/128'),
        ipaddress.ip_network('::1/128'),
        ipaddress.ip_network('fc00::/7'),
        ipaddress.ip_network('fe80::/10')
    ]

    # Blocked hostnames / metadata endpoints
    BLOCKED_HOSTNAMES = {
        'localhost', 'localhost.localdomain', 'local',
        'metadata.google.internal', '169.254.169.254', 'instance-data'
    }

    @classmethod
    def validate_url_security(cls, target_url: str) -> Tuple[str, str]:
        """
        Validates URL scheme, hostname, and resolves DNS to ensure target is public.
        Raises SSRFProtectionError if target URL violates security policies.
        Returns tuple of (validated_url, resolved_ip).
        """
        if not target_url or not isinstance(target_url, str):
            raise SSRFProtectionError("Invalid or empty URL provided.")

        target_url = target_url.strip()

        # Add scheme if missing
        if not target_url.startswith(('http://', 'https://')):
            target_url = 'http://' + target_url

        try:
            parsed = urllib.parse.urlparse(target_url)
        except Exception as e:
            raise SSRFProtectionError(f"URL parsing error: {str(e)}")

        scheme = parsed.scheme.lower()
        if scheme not in ('http', 'https'):
            raise SSRFProtectionError(f"Unsupported scheme '{scheme}'. Only http and https are allowed.")

        hostname = parsed.hostname
        if not hostname:
            raise SSRFProtectionError("Invalid URL: missing hostname.")

        hostname_lower = hostname.lower()

        # Check blocked hostnames
        if hostname_lower in cls.BLOCKED_HOSTNAMES or hostname_lower.endswith(('.local', '.internal', '.lan', '.home')):
            raise SSRFProtectionError(f"Access to internal hostname '{hostname}' is blocked for security.")

        # If hostname is a literal IP address
        try:
            ip_obj = ipaddress.ip_address(hostname)
            cls._check_ip_address(ip_obj)
            return target_url, str(ip_obj)
        except ValueError:
            # Not a literal IP, proceed to DNS resolution
            pass

        # Perform DNS resolution
        try:
            addr_info = socket.getaddrinfo(hostname, None, socket.AF_UNSPEC, socket.SOCK_STREAM)
            if not addr_info:
                raise SSRFProtectionError(f"DNS resolution failed for domain '{hostname}'.")

            resolved_ips = list({info[4][0] for info in addr_info})
            for ip_str in resolved_ips:
                ip_obj = ipaddress.ip_address(ip_str)
                cls._check_ip_address(ip_obj)

            primary_ip = resolved_ips[0]
            return target_url, primary_ip

        except socket.gaierror:
            raise SSRFProtectionError(f"Domain name '{hostname}' could not be resolved in DNS.")
        except SSRFProtectionError:
            raise
        except Exception as e:
            raise SSRFProtectionError(f"Security validation failed: {str(e)}")

    @classmethod
    def _check_ip_address(cls, ip_obj: ipaddress.IPv4Address | ipaddress.IPv6Address) -> None:
        """Verifies if an IP address is public and non-restricted."""
        if ip_obj.is_loopback:
            raise SSRFProtectionError(f"Blocked: Target resolves to loopback IP {ip_obj}.")
        if ip_obj.is_private:
            raise SSRFProtectionError(f"Blocked: Target resolves to private IP {ip_obj}.")
        if ip_obj.is_link_local:
            raise SSRFProtectionError(f"Blocked: Target resolves to link-local IP {ip_obj}.")
        if ip_obj.is_multicast:
            raise SSRFProtectionError(f"Blocked: Target resolves to multicast IP {ip_obj}.")
        if ip_obj.is_reserved:
            raise SSRFProtectionError(f"Blocked: Target resolves to reserved IP {ip_obj}.")
        if ip_obj.is_unspecified:
            raise SSRFProtectionError(f"Blocked: Target resolves to unspecified IP {ip_obj}.")

        for net in cls.BLOCKED_NETWORKS:
            if ip_obj in net:
                raise SSRFProtectionError(f"Blocked: Target IP {ip_obj} falls within restricted network range {net}.")

    @classmethod
    def fetch_website_content(cls, target_url: str) -> Dict[str, Any]:
        """
        Safely fetches web content for the target URL adhering to SSRF,
        timeout, redirect, and response size constraints.
        Returns a structured fetch result dictionary.
        """
        current_url = target_url
        redirect_history = []

        for redirect_count in range(cls.MAX_REDIRECTS + 1):
            try:
                validated_url, resolved_ip = cls.validate_url_security(current_url)
            except SSRFProtectionError as spe:
                return {
                    'status': 'blocked_ssrf',
                    'success': False,
                    'final_url': current_url,
                    'error_message': str(spe),
                    'html_content': '',
                    'redirect_history': redirect_history
                }

            headers = {
                'User-Agent': cls.USER_AGENT,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
                'Connection': 'close'
            }

            try:
                # Use streaming request to enforce size limits
                response = requests.get(
                    validated_url,
                    headers=headers,
                    timeout=(cls.CONNECT_TIMEOUT, cls.READ_TIMEOUT),
                    allow_redirects=False,
                    stream=True
                )

                # Handle HTTP redirects manually to validate redirect target
                if response.is_redirect or response.status_code in (301, 302, 303, 307, 308):
                    location = response.headers.get('Location')
                    if not location:
                        break
                    
                    next_url = urllib.parse.urljoin(validated_url, location)
                    redirect_history.append((response.status_code, next_url))
                    current_url = next_url
                    response.close()
                    continue

                if response.status_code != 200:
                    return {
                        'status': f'http_error_{response.status_code}',
                        'success': False,
                        'final_url': validated_url,
                        'status_code': response.status_code,
                        'error_message': f"Server returned HTTP status {response.status_code}.",
                        'html_content': '',
                        'redirect_history': redirect_history
                    }

                # Read body content up to MAX_RESPONSE_SIZE
                content_bytes = bytearray()
                for chunk in response.iter_content(chunk_size=8192):
                    content_bytes.extend(chunk)
                    if len(content_bytes) >= cls.MAX_RESPONSE_SIZE:
                        break
                response.close()

                # Attempt decoding
                encoding = response.encoding or 'utf-8'
                try:
                    html_str = content_bytes.decode(encoding, errors='replace')
                except Exception:
                    html_str = content_bytes.decode('utf-8', errors='replace')

                return {
                    'status': 'fetched',
                    'success': True,
                    'final_url': validated_url,
                    'status_code': 200,
                    'error_message': '',
                    'html_content': html_str,
                    'redirect_history': redirect_history
                }

            except requests.exceptions.Timeout:
                return {
                    'status': 'timeout',
                    'success': False,
                    'final_url': current_url,
                    'error_message': f"Website connection or response timed out ({cls.TOTAL_TIMEOUT}s max limit).",
                    'html_content': '',
                    'redirect_history': redirect_history
                }
            except requests.exceptions.SSLError as ssle:
                return {
                    'status': 'ssl_error',
                    'success': False,
                    'final_url': current_url,
                    'error_message': f"SSL certificate validation error: {str(ssle).split(':')[-1].strip()}",
                    'html_content': '',
                    'redirect_history': redirect_history
                }
            except requests.exceptions.RequestException as re_err:
                return {
                    'status': 'connection_failed',
                    'success': False,
                    'final_url': current_url,
                    'error_message': f"Unable to establish connection: {str(re_err).split(':')[-1].strip()}",
                    'html_content': '',
                    'redirect_history': redirect_history
                }

        return {
            'status': 'too_many_redirects',
            'success': False,
            'final_url': current_url,
            'error_message': f"Exceeded maximum allowed HTTP redirects ({cls.MAX_REDIRECTS}).",
            'html_content': '',
            'redirect_history': redirect_history
        }

    @classmethod
    def _is_same_base_domain(cls, d1: str, d2: str) -> bool:
        """Helper to determine if two domain strings share the same apex domain."""
        if not d1 or not d2:
            return True
        d1 = d1.lower().replace('www.', '')
        d2 = d2.lower().replace('www.', '')
        if d1 == d2 or d1.endswith('.' + d2) or d2.endswith('.' + d1):
            return True
        parts1 = d1.split('.')
        parts2 = d2.split('.')
        if len(parts1) >= 2 and len(parts2) >= 2:
            return parts1[-2:] == parts2[-2:]
        return False

    @classmethod
    def analyze_html_content(cls, raw_url: str, fetch_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parses fetched HTML content to extract safety indicators, forms,
        password inputs, external destinations, and brand impersonation evidence.
        """
        if not fetch_result.get('success') or not fetch_result.get('html_content'):
            return {
                'content_retrieved': False,
                'status': fetch_result.get('status', 'fetch_failed'),
                'status_message': fetch_result.get('error_message', 'Website content could not be retrieved.'),
                'title': '',
                'form_count': 0,
                'password_input_count': 0,
                'has_password_input': False,
                'external_form_actions': [],
                'http_form_actions': [],
                'iframe_count': 0,
                'hidden_iframe_count': 0,
                'meta_refresh_detected': False,
                'is_js_rendered': False,
                'brand_detected': None,
                'brand_mismatch': False,
                'text_snippet': '',
                'reasons': [f"Website Content Analysis: {fetch_result.get('error_message', 'Content fetch failed.')}"]
            }

        html_text = fetch_result['html_content']
        parsed_target_url = urllib.parse.urlparse(raw_url if raw_url.startswith(('http://', 'https://')) else 'http://' + raw_url)
        target_domain = parsed_target_url.netloc.lower().split(':')[0].replace('www.', '')

        soup = BeautifulSoup(html_text, 'html.parser')

        # 1. Page Title
        title_tag = soup.find('title')
        title_str = title_tag.get_text().strip() if title_tag else ""

        # 2. Forms & Inputs Analysis
        forms = soup.find_all('form')
        form_count = len(forms)

        password_inputs = soup.find_all('input', attrs={'type': lambda t: t and t.lower() == 'password'})
        password_input_count = len(password_inputs)
        has_password_input = password_input_count > 0

        external_form_actions = []
        http_form_actions = []

        for form in forms:
            action = form.get('action', '').strip()
            if action:
                try:
                    action_url = urllib.parse.urljoin(fetch_result['final_url'], action)
                    parsed_action = urllib.parse.urlparse(action_url)
                    action_domain = parsed_action.netloc.lower().split(':')[0].replace('www.', '')

                    # Check external form destination
                    if action_domain and not cls._is_same_base_domain(target_domain, action_domain):
                        # Check if action_domain is an official domain for the same brand
                        is_official_action = False
                        for brand, official_domains in cls.KNOWN_BRANDS.items():
                            if any(target_domain == od or target_domain.endswith('.' + od) for od in official_domains):
                                if any(action_domain == od or action_domain.endswith('.' + od) for od in official_domains):
                                    is_official_action = True
                                    break
                        if not is_official_action:
                            external_form_actions.append(action_url)

                    # Check HTTP form destination on HTTPS site
                    if parsed_action.scheme.lower() == 'http' and parsed_target_url.scheme.lower() == 'https':
                        http_form_actions.append(action_url)
                except Exception:
                    pass

        # 3. Iframe Analysis
        iframes = soup.find_all('iframe')
        iframe_count = len(iframes)
        hidden_iframe_count = 0

        for iframe in iframes:
            style = iframe.get('style', '').lower()
            width = str(iframe.get('width', '')).strip()
            height = str(iframe.get('height', '')).strip()
            if 'display:none' in style or 'visibility:hidden' in style or width in ('0', '1') or height in ('0', '1'):
                hidden_iframe_count += 1

        # 4. Meta Refresh Analysis
        meta_refresh = soup.find('meta', attrs={'http-equiv': lambda h: h and h.lower() == 'refresh'})
        meta_refresh_detected = meta_refresh is not None

        # 5. Visible Text & JS Rendering Check
        visible_text = soup.get_text(separator=' ', strip=True)
        text_snippet = visible_text[:250] + ("..." if len(visible_text) > 250 else "")

        js_keywords = ["javascript is required", "enable javascript", "js disabled", "loading app"]
        is_js_rendered = len(visible_text) < 150 and any(kw in visible_text.lower() for kw in js_keywords)

        # 6. Brand Impersonation Check (Targeted Title, Headings, and Login Forms)
        headings_text = " ".join([h.get_text().strip() for h in soup.find_all(['h1', 'h2', 'h3'])])
        prominent_text = (title_str + " " + headings_text).lower()

        brand_detected = None
        brand_mismatch = False

        for brand, official_domains in cls.KNOWN_BRANDS.items():
            brand_in_prominent = (brand in title_str.lower()) or (brand in target_domain) or (brand in headings_text.lower())
            brand_in_login_form = has_password_input and (brand in visible_text[:800].lower())

            if brand_in_prominent or brand_in_login_form:
                is_official = any(target_domain == od or target_domain.endswith('.' + od) for od in official_domains)
                brand_detected = brand.capitalize()
                if not is_official:
                    brand_mismatch = True
                    break

        # Build list of evidence reasons
        reasons = []
        if title_str:
            reasons.append(f"Page Title: '{title_str[:60]}'")
        else:
            reasons.append("Page Title: (No title tag specified)")

        if brand_mismatch:
            reasons.append(f"CRITICAL: Brand '{brand_detected}' keywords found in prominent page elements, but domain '{target_domain}' is NOT an official brand domain!")
        elif brand_detected:
            reasons.append(f"Verified Brand: Target domain matches official '{brand_detected}' domain infrastructure.")

        if has_password_input:
            reasons.append(f"Credential Risk: Page contains {password_input_count} password input field(s) for user authentication.")

        if external_form_actions:
            reasons.append(f"Form Destination Mismatch: Form submits data to external domain '{external_form_actions[0]}'.")

        if http_form_actions:
            reasons.append(f"Insecure Form Action: HTTPS website submits credentials over unencrypted HTTP endpoint '{http_form_actions[0]}'.")

        if hidden_iframe_count > 0:
            reasons.append(f"Obfuscation Indicator: Detected {hidden_iframe_count} hidden <iframe> element(s).")

        if is_js_rendered:
            reasons.append("Rendering Limitation: Page relies heavily on client-side JavaScript execution.")

        return {
            'content_retrieved': True,
            'status': 'fetched',
            'status_message': 'Website content retrieved and analyzed successfully.',
            'title': title_str,
            'form_count': form_count,
            'password_input_count': password_input_count,
            'has_password_input': has_password_input,
            'external_form_actions': external_form_actions,
            'http_form_actions': http_form_actions,
            'iframe_count': iframe_count,
            'hidden_iframe_count': hidden_iframe_count,
            'meta_refresh_detected': meta_refresh_detected,
            'is_js_rendered': is_js_rendered,
            'brand_detected': brand_detected,
            'brand_mismatch': brand_mismatch,
            'text_snippet': text_snippet,
            'reasons': reasons
        }

    @classmethod
    def evaluate_hybrid_risk(cls, raw_url: str, ml_risk_score: float, ml_prediction: str, content_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Combines machine learning URL predictions with HTML content indicators
        to produce a calibrated overall risk score, outcome level (LOW, MEDIUM, HIGH, UNKNOWN/UNVERIFIED),
        and transparent list of evidence reasons.
        """
        reasons = []
        content_retrieved = content_analysis.get('content_retrieved', False)

        # 1. Start with ML URL risk score
        url_score = float(ml_risk_score)
        reasons.append(f"ML URL Feature Model Risk Score: {url_score:.2f}% ({ml_prediction})")

        if not content_retrieved:
            # Content could not be retrieved (inaccessible / timeout / blocked)
            fetch_msg = content_analysis.get('status_message', 'Website content unavailable.')
            reasons.append(f"Content Status: {fetch_msg}")

            if url_score >= 60.0:
                final_score = url_score
                outcome_level = "HIGH"
                prediction_label = "Phishing"
                summary = "High risk indicated by lexical URL analysis (Website content was unreachable)."
            elif url_score >= 40.0:
                final_score = url_score
                outcome_level = "MEDIUM"
                prediction_label = "Phishing" if url_score >= 50 else "Legitimate"
                summary = "Moderate suspicion from URL structure (Website content was unreachable)."
            else:
                final_score = url_score
                outcome_level = "UNKNOWN / UNVERIFIED"
                prediction_label = "Unverified"
                summary = "Content unreachable; URL features show low risk, but full safety cannot be guaranteed without content verification."

            return {
                'outcome_level': outcome_level,
                'prediction_label': prediction_label,
                'combined_risk_score': round(final_score, 2),
                'url_risk_score': round(url_score, 2),
                'content_risk_score': None,
                'content_retrieved': False,
                'summary_text': summary,
                'reasons': reasons,
                'content_analysis': content_analysis
            }

        # 2. Compute Content Risk Score
        content_score = 10.0  # baseline for reachable page

        if content_analysis.get('brand_mismatch'):
            content_score += 55.0
        elif content_analysis.get('brand_detected'):
            content_score -= 10.0

        if content_analysis.get('has_password_input'):
            content_score += 20.0

        if content_analysis.get('external_form_actions'):
            content_score += 30.0

        if content_analysis.get('http_form_actions'):
            content_score += 35.0

        if content_analysis.get('hidden_iframe_count', 0) > 0:
            content_score += 20.0

        if content_analysis.get('meta_refresh_detected'):
            content_score += 15.0

        content_score = max(0.0, min(100.0, content_score))

        # Add content reasons
        for r in content_analysis.get('reasons', []):
            reasons.append(r)

        # 3. Combine URL Score and Content Score (Weighted 55% ML URL + 45% Content)
        combined_score = (0.55 * url_score) + (0.45 * content_score)

        # Critical Overrides
        if content_analysis.get('brand_mismatch') or content_analysis.get('http_form_actions'):
            combined_score = max(combined_score, 85.0)
        elif content_analysis.get('has_password_input') and content_analysis.get('external_form_actions'):
            combined_score = max(combined_score, 75.0)

        combined_score = round(max(0.0, min(100.0, combined_score)), 2)

        # Determine Outcome Level
        if combined_score >= 70.0:
            outcome_level = "HIGH"
            prediction_label = "Phishing"
            summary = "High risk of phishing detected based on URL characteristics and website content evidence."
        elif combined_score >= 40.0:
            outcome_level = "MEDIUM"
            prediction_label = "Phishing" if combined_score >= 50.0 else "Suspicious"
            summary = "Moderate phishing risk or suspicious content indicators detected."
        else:
            outcome_level = "LOW"
            prediction_label = "Legitimate"
            summary = "Low risk detected. URL structure and web content appear legitimate."

        return {
            'outcome_level': outcome_level,
            'prediction_label': prediction_label,
            'combined_risk_score': combined_score,
            'url_risk_score': round(url_score, 2),
            'content_risk_score': round(content_score, 2),
            'content_retrieved': True,
            'summary_text': summary,
            'reasons': reasons,
            'content_analysis': content_analysis
        }

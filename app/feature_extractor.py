"""
URL Feature Extractor Module for Phishing Detection System.
Extracts lexical, structural, and security features from input URLs safely
without performing external HTTP requests or executing code.
"""

import re
import urllib.parse
from typing import Dict, Any, List


class FeatureExtractor:
    """Extracts machine learning features from a given URL string."""

    # Common URL shorteners
    SHORTENERS = {
        'bit.ly', 'goo.gl', 'tinyurl.com', 'ow.ly', 't.co', 'is.gd',
        'buff.ly', 'adf.ly', 'bit.do', 'cutt.ly', 'rb.gy', 'v.gd',
        'tiny.cc', 'shorturl.at', 'qr.ae', 'tr.im'
    }

    # Suspicious keywords frequently found in phishing target URLs
    SUSPICIOUS_KEYWORDS = [
        'login', 'signin', 'verify', 'verification', 'update', 'account',
        'banking', 'secure', 'security', 'webscr', 'cmd', 'paypal', 'ebay',
        'amazon', 'apple', 'microsoft', 'google', 'admin', 'password',
        'confirm', 'service', 'validation', 'billing', 'support', 'token',
        'auth', 'credential', 'recovery', 'wallet'
    ]

    @staticmethod
    def is_valid_url(url: str) -> bool:
        """Validates if the provided string has basic URL structure."""
        if not url or not isinstance(url, str):
            return False
        url = url.strip()
        if len(url) < 3 or len(url) > 2048:
            return False
        # Basic check for scheme or domain structure
        regex = re.compile(
            r'^(?:http|https)://'  # http:// or https://
            r'|(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}'  # or domain without scheme
            r'|^(?:[0-9]{1,3}\.){3}[0-9]{1,3}'  # or IP address
        , re.IGNORECASE)
        return bool(regex.search(url))

    @classmethod
    def extract_features(cls, raw_url: str) -> Dict[str, Any]:
        """
        Extracts 16 numeric features from the given URL.
        Returns a dictionary mapping feature names to numeric values.
        """
        if not raw_url or not isinstance(raw_url, str):
            raw_url = ""

        raw_url = raw_url.strip()

        # Normalize URL by adding scheme if missing for proper parsing
        parsing_url = raw_url
        if not parsing_url.startswith(('http://', 'https://')):
            parsing_url = 'http://' + parsing_url

        try:
            parsed = urllib.parse.urlparse(parsing_url)
            netloc = parsed.netloc.lower()
            path = parsed.path.lower()
            query = parsed.query.lower()
        except Exception:
            netloc = ""
            path = ""
            query = ""

        # Extract hostname/domain without port
        hostname = netloc.split(':')[0] if ':' in netloc else netloc

        # Feature 1: URL Length
        url_length = len(raw_url)

        # Feature 2: Dot count
        dot_count = raw_url.count('.')

        # Feature 3: Hyphen count
        hyphen_count = raw_url.count('-')

        # Feature 4: At (@) symbol count
        at_count = raw_url.count('@')

        # Feature 5: Question mark (?) count
        question_count = raw_url.count('?')

        # Feature 6: Equals (=) symbol count
        equal_count = raw_url.count('=')

        # Feature 7: Slash (/) count
        slash_count = raw_url.count('/')

        # Feature 8: Digit count
        digit_count = sum(c.isdigit() for c in raw_url)

        # Feature 9: Letter count
        letter_count = sum(c.isalpha() for c in raw_url)

        # Feature 10: HTTPS usage (1 if scheme is https, 0 otherwise)
        is_https = 1 if raw_url.lower().startswith('https://') else 0

        # Feature 11: Raw IP address presence
        ip_pattern = r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$'
        has_ip = 1 if re.match(ip_pattern, hostname) else 0

        # Feature 12: URL Shortener usage
        has_shortener = 1 if hostname in cls.SHORTENERS else 0

        # Feature 13: Subdomain count
        # Remove www. if present to count actual subdomains
        clean_hostname = hostname.replace('www.', '')
        parts = clean_hostname.split('.')
        # Domain typically has domain.tld (2 parts), subdomains add more
        subdomain_count = max(0, len(parts) - 2) if len(parts) >= 2 else 0

        # Feature 14: Suspicious keyword count in full URL
        url_lower = raw_url.lower()
        suspicious_keyword_count = sum(
            1 for kw in cls.SUSPICIOUS_KEYWORDS if kw in url_lower
        )

        # Feature 15: Prefix/Suffix in domain (hyphen in domain name)
        prefix_suffix_domain = 1 if '-' in hostname else 0

        # Feature 16: URL Path Depth
        path_segments = [p for p in path.split('/') if p]
        url_depth = len(path_segments)

        return {
            'url_length': url_length,
            'dot_count': dot_count,
            'hyphen_count': hyphen_count,
            'at_count': at_count,
            'question_count': question_count,
            'equal_count': equal_count,
            'slash_count': slash_count,
            'digit_count': digit_count,
            'letter_count': letter_count,
            'is_https': is_https,
            'has_ip': has_ip,
            'has_shortener': has_shortener,
            'subdomain_count': subdomain_count,
            'suspicious_keyword_count': suspicious_keyword_count,
            'prefix_suffix_domain': prefix_suffix_domain,
            'url_depth': url_depth
        }

    @classmethod
    def get_feature_names(cls) -> List[str]:
        """Returns the list of feature names in strict order."""
        return [
            'url_length',
            'dot_count',
            'hyphen_count',
            'at_count',
            'question_count',
            'equal_count',
            'slash_count',
            'digit_count',
            'letter_count',
            'is_https',
            'has_ip',
            'has_shortener',
            'subdomain_count',
            'suspicious_keyword_count',
            'prefix_suffix_domain',
            'url_depth'
        ]

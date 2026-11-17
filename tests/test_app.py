"""
Integration Tests for Flask Web Application Routes and Database Operations.
"""

import unittest
import json
from run import app
from app.database import init_db, get_db_connection


class TestFlaskApplication(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()
        init_db()

    def test_home_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Phishing URL Detection System', response.data)

    def test_analyze_legitimate_url(self):
        payload = {'url': 'https://www.google.com/search?q=python'}
        response = self.client.post(
            '/analyze',
            data=json.dumps(payload),
            content_type='application/json',
            headers={'X-Requested-With': 'XMLHttpRequest'}
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['prediction'], 'Legitimate')

    def test_analyze_phishing_url(self):
        payload = {'url': 'http://192.168.1.45/paypal/webscr?cmd=_login-run'}
        response = self.client.post(
            '/analyze',
            data=json.dumps(payload),
            content_type='application/json',
            headers={'X-Requested-With': 'XMLHttpRequest'}
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['prediction'], 'Phishing')

    def test_analyze_empty_input(self):
        payload = {'url': ''}
        response = self.client.post(
            '/analyze',
            data=json.dumps(payload),
            content_type='application/json',
            headers={'X-Requested-With': 'XMLHttpRequest'}
        )
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'error')

    def test_analyze_invalid_url(self):
        payload = {'url': 'invalid_url_text_without_domain'}
        response = self.client.post(
            '/analyze',
            data=json.dumps(payload),
            content_type='application/json',
            headers={'X-Requested-With': 'XMLHttpRequest'}
        )
        self.assertEqual(response.status_code, 400)

    def test_history_page(self):
        response = self.client.get('/history')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Analysis Scan History', response.data)

    def test_metrics_page(self):
        response = self.client.get('/metrics')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Machine Learning Model Performance', response.data)

    def test_api_stats(self):
        response = self.client.get('/api/stats')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('total_scans', data)


if __name__ == '__main__':
    unittest.main()

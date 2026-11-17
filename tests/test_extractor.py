"""
Unit Tests for URL Feature Extraction Module.
"""

import unittest
from app.feature_extractor import FeatureExtractor


class TestFeatureExtractor(unittest.TestCase):

    def test_valid_url_checking(self):
        self.assertTrue(FeatureExtractor.is_valid_url("https://www.google.com"))
        self.assertTrue(FeatureExtractor.is_valid_url("http://192.168.1.1/login"))
        self.assertTrue(FeatureExtractor.is_valid_url("example.com"))
        self.assertFalse(FeatureExtractor.is_valid_url(""))
        self.assertFalse(FeatureExtractor.is_valid_url("   "))
        self.assertFalse(FeatureExtractor.is_valid_url(None))

    def test_https_feature(self):
        feats_https = FeatureExtractor.extract_features("https://www.bank.com")
        self.assertEqual(feats_https['is_https'], 1)

        feats_http = FeatureExtractor.extract_features("http://www.bank.com")
        self.assertEqual(feats_http['is_https'], 0)

    def test_ip_address_feature(self):
        feats_ip = FeatureExtractor.extract_features("http://192.168.1.5/login.html")
        self.assertEqual(feats_ip['has_ip'], 1)

        feats_domain = FeatureExtractor.extract_features("http://www.google.com")
        self.assertEqual(feats_domain['has_ip'], 0)

    def test_shortener_feature(self):
        feats_short = FeatureExtractor.extract_features("http://bit.ly/3x821")
        self.assertEqual(feats_short['has_shortener'], 1)

        feats_normal = FeatureExtractor.extract_features("https://www.python.org")
        self.assertEqual(feats_normal['has_shortener'], 0)

    def test_suspicious_keywords(self):
        url = "http://verify-bank-account-login.com/update/secure"
        feats = FeatureExtractor.extract_features(url)
        self.assertGreater(feats['suspicious_keyword_count'], 0)

    def test_feature_counts(self):
        feats = FeatureExtractor.extract_features("https://www.example.com/path/to/page?id=10#section")
        self.assertEqual(len(feats), 16)
        self.assertEqual(feats['dot_count'], 2)
        self.assertEqual(feats['slash_count'], 5)


if __name__ == '__main__':
    unittest.main()

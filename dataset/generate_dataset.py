"""
Dataset Generation Script for Phishing URL Detection System.
Generates a realistic, balanced dataset of legitimate and phishing URLs
representing real-world web traffic patterns.
"""

import os
import random
import pandas as pd

OUTPUT_DIR = os.path.dirname(__file__)
CSV_PATH = os.path.join(OUTPUT_DIR, 'phishing_urls.csv')

def generate_dataset():
    random.seed(42)  # For reproducible dataset generation

    legitimate_domains = [
        "google.com", "youtube.com", "facebook.com", "wikipedia.org", "yahoo.com",
        "amazon.com", "github.com", "twitter.com", "linkedin.com", "microsoft.com",
        "apple.com", "netflix.com", "reddit.com", "stackoverflow.com", "python.org",
        "medium.com", "adobe.com", "cloudflare.com", "wordpress.org", "mozilla.org",
        "bing.com", "office.com", "bbc.com", "nytimes.com", "sciencedirect.com",
        "stanford.edu", "mit.edu", "coursera.org", "udemy.com", "quora.com"
    ]

    legitimate_paths = [
        "", "about", "contact", "docs/getting-started", "news/2026/technology",
        "products/item-10293", "user/profile/overview", "search?q=machine+learning",
        "category/python-tutorials", "blog/how-to-build-web-apps", "download/v2.1",
        "questions/7482910/how-to-fix-bug", "article/science-daily-update",
        "explore/popular-topics", "help/center/privacy-policy"
    ]

    phishing_base_domains = [
        "login-appleid.com", "verify-paypal-account.info", "secure-bankofamerica.net",
        "chase-update-security.xyz", "wellsfargo-auth.top", "netflix-billing-update.site",
        "microsoft-online-verify.online", "amazon-security-alert.club", "google-drive-share.tech",
        "facebook-account-recovery.support", "instagram-verify-badge.co", "binance-login-fix.biz",
        "crypto-wallet-connect.link", "support-apple-id.work", "id-verify-service.cc"
    ]

    phishing_keywords = [
        "login.php", "verify-account", "webscr?cmd=_login-run", "update-billing",
        "secure-auth", "account-suspended-reactivate", "confirm-identity",
        "passcode-reset", "verify_card_details", "signin.html", "checkpoint-security"
    ]

    ip_addresses = [
        "192.168.1.45", "10.0.0.12", "185.220.101.5", "198.51.100.14",
        "203.0.113.88", "45.142.214.10", "193.109.69.12"
    ]

    shortener_domains = [
        "bit.ly", "tinyurl.com", "t.co", "is.gd", "cutt.ly", "rb.gy"
    ]

    urls = []
    labels = []  # 0 for Legitimate, 1 for Phishing

    # Generate 1000 Legitimate URLs
    for i in range(1000):
        domain = random.choice(legitimate_domains)
        path = random.choice(legitimate_paths)

        # 90% HTTPS, 10% HTTP for legitimate
        scheme = "https://" if random.random() > 0.1 else "http://"

        # Optionally add subdomain or www
        sub = "www." if random.random() > 0.3 else ""
        if random.random() < 0.15:
            sub = random.choice(["blog.", "docs.", "api.", "news.", "support."]) + sub

        url = f"{scheme}{sub}{domain}/{path}" if path else f"{scheme}{sub}{domain}"
        urls.append(url)
        labels.append(0)

    # Generate 1000 Phishing URLs
    for i in range(1000):
        choice = random.random()
        if choice < 0.35:
            # Domain typosquatting / hyphenated fake domains
            base = random.choice(phishing_base_domains)
            kw = random.choice(phishing_keywords)
            sub = random.choice(["account.verify.", "secure.login.", "auth.", "signin.", "service."])
            scheme = "http://" if random.random() > 0.25 else "https://"
            url = f"{scheme}{sub}{base}/{kw}?id={random.randint(1000, 999999)}&token={random.randint(100000, 999999)}"
        elif choice < 0.60:
            # IP address URL
            ip = random.choice(ip_addresses)
            kw = random.choice(phishing_keywords)
            url = f"http://{ip}/{kw}/session-{random.randint(100,999)}"
        elif choice < 0.80:
            # URL with @ symbol or excessive subdomains
            legit_target = random.choice(["paypal.com", "apple.com", "bankofamerica.com", "google.com"])
            phish_host = random.choice(["malicious-site.com", "fake-gateway.net", "attacker-host.top"])
            url = f"http://{legit_target}@{phish_host}/login?ref={random.randint(10,999)}"
        else:
            # Shortened URL or high keyword density
            short = random.choice(shortener_domains)
            code = ''.join(random.choices("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=7))
            url = f"http://{short}/{code}?redirect=verify-account"

        urls.append(url)
        labels.append(1)

    # Shuffle dataset
    combined = list(zip(urls, labels))
    random.shuffle(combined)
    shuffled_urls, shuffled_labels = zip(*combined)

    df = pd.DataFrame({
        'url': shuffled_urls,
        'label': shuffled_labels
    })

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    df.to_csv(CSV_PATH, index=False)
    print(f"Dataset successfully created at {CSV_PATH} with {len(df)} records.")
    print(f"Legitimate count: {sum(df['label'] == 0)}, Phishing count: {sum(df['label'] == 1)}")
    return CSV_PATH

if __name__ == '__main__':
    generate_dataset()

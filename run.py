"""
Application Entrypoint for Phishing URL Detection System.
"""

from app import create_app

app = create_app()

if __name__ == '__main__':
    print("Starting Phishing URL Detection System Web Application...")
    app.run(host='127.0.0.1', port=5000, debug=True)


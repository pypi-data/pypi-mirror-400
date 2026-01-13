from flaskapptest.core.flask_detector import FlaskAppDetector
from pathlib import Path


def test_detects_flask_app(tmp_path: Path):
    file = tmp_path / "app.py"
    file.write_text("""
from flask import Flask
app = Flask(__name__)
""")

    detector = FlaskAppDetector([file])
    apps = detector.detect()

    assert len(apps) == 1
    assert apps[0]["app_name"] == "app"

from flaskapptest.core.endpoint_extractor import EndpointExtractor
from pathlib import Path


def test_extracts_flask_route(tmp_path: Path):
    file = tmp_path / "app.py"
    file.write_text("""
from flask import Flask
app = Flask(__name__)

@app.route("/users", methods=["POST"])
def create_user():
    pass
""")

    extractor = EndpointExtractor([
        {"app_name": "app", "file_path": file}
    ])

    endpoints = extractor.extract()

    assert len(endpoints) == 1
    assert endpoints[0]["path"] == "/users"
    assert endpoints[0]["methods"] == ["POST"]

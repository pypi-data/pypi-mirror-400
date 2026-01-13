# flaskapptest/core/flask_detector.py

import ast
from pathlib import Path
from typing import List, Dict


class FlaskAppDetector:
    """
    Detects Flask app instances using AST analysis.
    """

    def __init__(self, python_files: List[Path]) -> None:
        self.python_files = python_files

    def detect(self) -> List[Dict]:
        """
        Detect Flask app instances like:
            app = Flask(__name__)
        """
        detected_apps: List[Dict] = []

        for file_path in self.python_files:
            try:
                tree = ast.parse(file_path.read_text(encoding="utf-8"))
            except Exception:
                # Skip unreadable or invalid files
                continue

            for node in ast.walk(tree):
                if self._is_flask_app_assignment(node):
                    detected_apps.append(
                        {
                            "app_name": node.targets[0].id,
                            "file_path": file_path,
                        }
                    )

        return detected_apps

    def _is_flask_app_assignment(self, node: ast.AST) -> bool:
        """
        Checks if node matches:
            variable = Flask(...)
        """
        if not isinstance(node, ast.Assign):
            return False

        if len(node.targets) != 1:
            return False

        target = node.targets[0]
        value = node.value

        if not isinstance(target, ast.Name):
            return False

        if not isinstance(value, ast.Call):
            return False

        if isinstance(value.func, ast.Name) and value.func.id == "Flask":
            return True

        return False

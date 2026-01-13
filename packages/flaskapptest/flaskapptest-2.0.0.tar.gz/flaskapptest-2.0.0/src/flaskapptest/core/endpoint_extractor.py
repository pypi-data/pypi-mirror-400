# flaskapptest/core/endpoint_extractor.py

import ast
from pathlib import Path
from typing import List, Dict


class EndpointExtractor:
    """
    Extracts Flask routes from detected Flask app files.
    """

    def __init__(self, flask_apps: List[Dict]) -> None:
        self.flask_apps = flask_apps

    def extract(self) -> List[Dict]:
        """
        Extracts endpoints from Flask app files.
        """
        endpoints: List[Dict] = []

        for app in self.flask_apps:
            file_path: Path = app["file_path"]
            app_name: str = app["app_name"]

            try:
                tree = ast.parse(file_path.read_text(encoding="utf-8"))
            except Exception:
                continue

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    endpoint = self._extract_from_function(node, app_name, file_path)
                    if endpoint:
                        endpoints.append(endpoint)

        return endpoints

    def _extract_from_function(
        self,
        node: ast.FunctionDef,
        app_name: str,
        file_path: Path,
    ) -> Dict | None:
        """
        Extracts route info from a function definition.
        """
        for decorator in node.decorator_list:
            if not isinstance(decorator, ast.Call):
                continue

            if not isinstance(decorator.func, ast.Attribute):
                continue

            if not isinstance(decorator.func.value, ast.Name):
                continue

            if decorator.func.value.id != app_name:
                continue

            if decorator.func.attr != "route":
                continue

            path = self._get_route_path(decorator)
            methods = self._get_http_methods(decorator)

            return {
                "path": path,
                "methods": methods,
                "function": node.name,
                "file_path": str(file_path),
            }

        return None

    def _get_route_path(self, decorator: ast.Call) -> str:
        if decorator.args and isinstance(decorator.args[0], ast.Constant):
            return decorator.args[0].value
        return "/"

    def _get_http_methods(self, decorator: ast.Call) -> List[str]:
        for keyword in decorator.keywords:
            if keyword.arg == "methods" and isinstance(keyword.value, ast.List):
                return [
                    elt.value
                    for elt in keyword.value.elts
                    if isinstance(elt, ast.Constant)
                ]
        return ["GET"]

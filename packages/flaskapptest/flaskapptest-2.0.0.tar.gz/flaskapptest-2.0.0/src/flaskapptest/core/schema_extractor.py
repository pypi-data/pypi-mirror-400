# flaskapptest/core/schema_extractor.py

import ast
from typing import Dict, List


class SchemaExtractor:
    """
    Extracts input schema information from endpoint functions.
    """

    def extract(self, endpoint: Dict) -> Dict:
        """
        Extracts path params, query params, and body params.
        """
        path_params = self._extract_path_params(endpoint["path"])
        body_params = self._extract_body_params(endpoint)

        return {
            "path_params": path_params,
            "query_params": [],  # can be expanded later
            "body_params": body_params,
        }

    def _extract_path_params(self, path: str) -> List[str]:
        """
        Extracts Flask-style path params: /user/<id>
        """
        params = []
        parts = path.split("/")
        for part in parts:
            if part.startswith("<") and part.endswith(">"):
                params.append(part[1:-1])
        return params

    def _extract_body_params(self, endpoint: Dict) -> List[str]:
        """
        Extracts function arguments as body params (heuristic).
        """
        try:
            tree = ast.parse(open(endpoint["file_path"], encoding="utf-8").read())
        except Exception:
            return []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == endpoint["function"]:
                return [
                    arg.arg
                    for arg in node.args.args
                    if arg.arg not in ("self",)
                ]

        return []

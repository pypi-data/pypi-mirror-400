# flaskapptest/core/payload_generator.py

from typing import Dict


class PayloadGenerator:
    """
    Generates structured payload templates for endpoints.
    """

    def generate(self, schema: Dict) -> Dict:
        return {
            "path": self._build_empty(schema.get("path_params", [])),
            "query": self._build_empty(schema.get("query_params", [])),
            "body": self._build_empty(schema.get("body_params", [])),
        }

    def _build_empty(self, fields: list) -> Dict:
        """
        Creates empty dict for structured input.
        """
        return {field: None for field in fields}

# flaskapptest/core/test_generator.py

from typing import Dict, List
from flaskapptest.core.schema_extractor import SchemaExtractor
from flaskapptest.core.payload_generator import PayloadGenerator


class TestGenerator:
    """
    Generates executable test cases from extracted endpoints.
    """

    def __init__(self) -> None:
        self.schema_extractor = SchemaExtractor()
        self.payload_generator = PayloadGenerator()

    def generate(self, endpoints: List[Dict]) -> List[Dict]:
        test_cases: List[Dict] = []

        for endpoint in endpoints:
            schema = self.schema_extractor.extract(endpoint)
            payload = self.payload_generator.generate(schema)

            for method in endpoint["methods"]:
                test_cases.append(
                    {
                        "name": f"{method} {endpoint['path']}",
                        "method": method,
                        "path": endpoint["path"],
                        "schema": schema,
                        "payload": payload,
                        "expected_status": self._default_expected_status(method),
                    }
                )

        return test_cases

    def _default_expected_status(self, method: str) -> List[int]:
        if method == "POST":
            return [200, 201]
        if method in ("PUT", "PATCH"):
            return [200]
        if method == "DELETE":
            return [200, 204]
        return [200]

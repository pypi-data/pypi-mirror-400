# flaskapptest/core/test_runner.py

from typing import Dict, List
from flaskapptest.core.request_executor import RequestExecutor
from flaskapptest.core.validators import ResponseValidator


class TestRunner:
    """
    Executes generated test cases.
    """

    def __init__(self, base_url: str, headers: Dict | None = None) -> None:
        self.executor = RequestExecutor(base_url)
        self.validator = ResponseValidator()
        self.headers = headers or {}

    def run(self, test_cases: List[Dict]) -> List[Dict]:
        results: List[Dict] = []

        for test in test_cases:
            response = self.executor.execute(
                method=test["method"],
                path=test["path"],
                payload=test["payload"],
                headers=self.headers,
            )

            validation = self.validator.validate(
                response=response,
                expected_status=test["expected_status"],
            )

            results.append(
                {
                    "test_name": test["name"],
                    "passed": validation["passed"],
                    "errors": validation["errors"],
                    "response": response,
                }
            )

        return results

# flaskapptest/core/validators.py

from typing import Dict, List


class ResponseValidator:
    """
    Validates HTTP responses.
    """

    def validate(
        self,
        response: Dict,
        expected_status: List[int] | None = None,
    ) -> Dict:

        errors = []

        if response.get("status_code") is None:
            errors.append("Request failed to execute")

        if expected_status and response.get("status_code") not in expected_status:
            errors.append(
                f"Unexpected status code: {response.get('status_code')}"
            )

        return {
            "passed": len(errors) == 0,
            "errors": errors,
        }

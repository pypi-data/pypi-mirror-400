# flaskapptest/core/reporting.py

import json
from typing import List, Dict


class ReportGenerator:
    """
    Generates reports from test results.
    """

    def summary(self, results: List[Dict]) -> Dict:
        total = len(results)
        passed = sum(1 for r in results if r["passed"])
        failed = total - passed

        return {
            "total": total,
            "passed": passed,
            "failed": failed,
        }

    def to_json(self, results: List[Dict]) -> str:
        return json.dumps(
            {
                "summary": self.summary(results),
                "results": results,
            },
            indent=2,
        )

    def to_cli(self, results: List[Dict]) -> str:
        lines = []
        summary = self.summary(results)

        lines.append("=== Flask API Test Report ===")
        lines.append(f"Total tests : {summary['total']}")
        lines.append(f"Passed      : {summary['passed']}")
        lines.append(f"Failed      : {summary['failed']}")
        lines.append("")

        for result in results:
            status = "PASS" if result["passed"] else "FAIL"
            lines.append(f"[{status}] {result['test_name']}")

            if result["errors"]:
                for err in result["errors"]:
                    lines.append(f"   - {err}")

        return "\n".join(lines)

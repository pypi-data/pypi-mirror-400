import sys
from typing import Dict, Optional, List

from flaskapptest.cli.batch_runner import BatchRunner

DEFAULT_FLASK_BASE_URL = "http://127.0.0.1:5000"


class CIRunner:
    """
    CI/CD runner.

    Purpose:
    - Execute all tests non-interactively
    - Fail pipeline on any test failure
    - Produce deterministic exit codes

    Exit codes:
    - 0 → All tests passed
    - 1 → Test failures detected
    - 2 → Configuration / runtime error
    """

    def __init__(
        self,
        project_path: str,
        base_url: Optional[str] = None,
        fail_fast: bool = True,
    ) -> None:
        self.project_path = project_path
        self.base_url = base_url or DEFAULT_FLASK_BASE_URL
        self.fail_fast = fail_fast

    # ---------- Public API ----------

    def run(self) -> None:
        print(f"\n🔹 Running CI/CD tests on project: {self.project_path}")
        print(f"🌐 Base URL in use: {self.base_url}")

        try:
            results = self._execute()
        except Exception as exc:
            print("\n❌ CI execution failed")
            print(str(exc))
            sys.exit(2)

        summary = self._summarize(results)

        if summary["failed"] > 0:
            print("\n🚨 CI FAILED")
            self._print_failures(results)
            sys.exit(1)

        print("\n✅ CI PASSED: All tests successful")
        sys.exit(0)

    # ---------- Internals ----------

    def _execute(self) -> List[Dict]:
        """
        Executes all tests using the BatchRunner.

        Returns:
        List of test execution results.
        """
        runner = BatchRunner(
            project_path=self.project_path,
            base_url=self.base_url,
            fail_fast=self.fail_fast,
        )
        return runner.run()

    def _summarize(self, results: List[Dict]) -> Dict:
        total = len(results)
        passed = sum(1 for r in results if r.get("passed"))
        failed = total - passed

        print("\n📊 CI Test Summary")
        print(f"Total Tests : {total}")
        print(f"Passed      : {passed}")
        print(f"Failed      : {failed}")

        return {
            "total": total,
            "passed": passed,
            "failed": failed,
        }

    def _print_failures(self, results: List[Dict]) -> None:
        print("\n❌ Failed Tests:")
        for result in results:
            if not result.get("passed"):
                print(f"- {result.get('test_name')}")
                for err in result.get("errors", []):
                    print(f"    • {err}")

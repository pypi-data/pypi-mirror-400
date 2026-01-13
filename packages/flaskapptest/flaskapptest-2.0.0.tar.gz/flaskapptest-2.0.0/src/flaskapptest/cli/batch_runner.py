from typing import List, Dict, Optional

from flaskapptest.core.project_scanner import ProjectScanner
from flaskapptest.core.flask_detector import FlaskAppDetector
from flaskapptest.core.endpoint_extractor import EndpointExtractor
from flaskapptest.core.test_generator import TestGenerator
from flaskapptest.core.test_runner import TestRunner

DEFAULT_FLASK_BASE_URL = "http://127.0.0.1:5000"


class BatchRunner:
    """
    Executes all detected Flask endpoints automatically.
    """

    def __init__(
        self,
        project_path: str,
        base_url: Optional[str] = None,
        fail_fast: bool = False,
    ) -> None:
        self.project_path = project_path
        self.base_url = base_url or DEFAULT_FLASK_BASE_URL
        self.fail_fast = fail_fast

        self.scanner = ProjectScanner(project_path)
        self.test_generator = TestGenerator()
        self.test_runner = TestRunner(base_url=self.base_url)

    # ---------- Public API ----------

    def run(self) -> List[Dict]:
        print(f"\n🔹 Running batch tests on project: {self.project_path}")
        print(f"🌐 Base URL: {self.base_url}")

        python_files = self.scanner.scan()
        if not python_files:
            raise RuntimeError("❌ No Python files found")

        detector = FlaskAppDetector(python_files)
        flask_apps = detector.detect()
        if not flask_apps:
            raise RuntimeError("❌ No Flask app detected")

        extractor = EndpointExtractor(flask_apps)
        endpoints = extractor.extract()
        if not endpoints:
            raise RuntimeError("❌ No Flask endpoints found")

        test_cases = self.test_generator.generate(endpoints)

        results = []
        for test in test_cases:
            test_result = self.test_runner.run([test])[0]
            results.append(test_result)

            if self.fail_fast and not test_result["passed"]:
                print("\n⚠️ Fail-fast enabled, stopping execution")
                break

        self._print_summary(results)
        return results

    # ---------- Output ----------

    def _print_summary(self, results: List[Dict]) -> None:
        total = len(results)
        passed = sum(1 for r in results if r["passed"])
        failed = total - passed

        print("\n📊 Batch Test Summary")
        print(f"Total Tests : {total}")
        print(f"Passed      : {passed}")
        print(f"Failed      : {failed}")

        if failed:
            print("\n❌ Failed Tests:")
            for r in results:
                if not r["passed"]:
                    print(f"- {r['test_name']}")

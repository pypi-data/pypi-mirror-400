from typing import List, Dict, Optional

from flaskapptest.core.project_scanner import ProjectScanner
from flaskapptest.core.flask_detector import FlaskAppDetector
from flaskapptest.core.endpoint_extractor import EndpointExtractor
from flaskapptest.core.schema_extractor import SchemaExtractor
from flaskapptest.core.payload_generator import PayloadGenerator
from flaskapptest.core.request_executor import RequestExecutor
from flaskapptest.core.validators import ResponseValidator


DEFAULT_FLASK_BASE_URL = "http://127.0.0.1:5000"


class ManualRunner:
    """
    Interactive CLI runner for manually testing detected Flask endpoints.
    """

    def __init__(self, project_path: str, base_url: Optional[str] = None):
        self.project_path = project_path
        self.base_url = base_url or DEFAULT_FLASK_BASE_URL

        self.scanner = ProjectScanner(project_path)

        # Stateless helpers
        self.schema_extractor = SchemaExtractor()
        self.payload_generator = PayloadGenerator()
        self.validator = ResponseValidator()

    # ---------- Public API ----------

    def run(self) -> None:
        print("\n🔍 Scanning project...")
        python_files = self.scanner.scan()

        if not python_files:
            print("❌ No Python files found")
            return

        detector = FlaskAppDetector(python_files)
        flask_apps = detector.detect()

        if not flask_apps:
            print("❌ No Flask application detected")
            return

        endpoint_extractor = EndpointExtractor(flask_apps)
        endpoints = endpoint_extractor.extract()

        if not endpoints:
            print("❌ No Flask endpoints found")
            return

        print("\n✅ Flask project detected")
        print(f"🌐 Base URL: {self.base_url}")

        self._interactive_loop(endpoints)

    # ---------- Interactive Loop ----------

    def _interactive_loop(self, endpoints: List[Dict]) -> None:
        while True:
            self._print_endpoint_list(endpoints)

            choice = input("\nSelect endpoint number (or 'exit'): ").strip()
            if choice.lower() == "exit":
                print("\n👋 Exiting manual mode")
                break

            if not choice.isdigit() or not (1 <= int(choice) <= len(endpoints)):
                print("⚠️ Invalid selection")
                continue

            endpoint = endpoints[int(choice) - 1]

            method = self._select_method(endpoint)
            payload = self._collect_payload(endpoint)

            confirm = input("\nSend request now? (y/n): ").strip().lower()
            if confirm != "y":
                print("⏭ Request skipped")
                continue

            self._execute_request(endpoint, method, payload)

    # ---------- Execution ----------

    def _execute_request(self, endpoint: Dict, method: str, payload: Dict) -> None:
        executor = RequestExecutor(self.base_url)

        response = executor.execute(
            method=method,
            path=endpoint["path"],
            payload=payload,
        )

        validation = self.validator.validate(
            response=response,
            expected_status=None,  # manual mode = flexible
        )

        self._print_response(response, validation)

    # ---------- Helpers ----------

    def _print_endpoint_list(self, endpoints: List[Dict]) -> None:
        print("\n📌 Detected Endpoints:")
        for idx, ep in enumerate(endpoints, start=1):
            methods = ", ".join(ep["methods"])
            print(f"{idx}. [{methods}] {ep['path']}")

    def _select_method(self, endpoint: Dict) -> str:
        methods = endpoint.get("methods", ["GET"])

        if len(methods) == 1:
            return methods[0]

        print("\nAvailable methods:")
        for idx, method in enumerate(methods, start=1):
            print(f"{idx}. {method}")

        while True:
            choice = input("Select HTTP method: ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(methods):
                return methods[int(choice) - 1]
            print("⚠️ Invalid method selection")

    def _collect_payload(self, endpoint: Dict) -> Dict:
        """
        Collects payload input from user using extracted schema.
        """
        schema = self.schema_extractor.extract(endpoint)
        template = self.payload_generator.generate(schema)

        payload = {
            "path": {},
            "query": {},
            "body": {},
        }

        print("\n📝 Enter request data (press Enter to skip a field):")

        for section, fields in template.items():
            if not fields:
                continue

            print(f"\n{section.upper()} PARAMETERS:")
            for key, default in fields.items():
                value = input(f"{section}.{key} [{default}]: ").strip()
                if value:
                    payload[section][key] = value

        return payload

    def _print_response(self, response: Dict, validation: Dict) -> None:
        print("\n📬 RESPONSE")
        print(f"Status: {response.get('status_code')}")

        if not validation["passed"]:
            print("❌ Validation failed:")
            for err in validation["errors"]:
                print(f" - {err}")
        else:
            print("✅ Request executed successfully")

        print("\nBody:")
        print(response.get("body"))

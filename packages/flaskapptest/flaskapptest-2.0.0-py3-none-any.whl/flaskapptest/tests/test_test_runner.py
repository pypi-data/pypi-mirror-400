from flaskapptest.core.test_runner import TestRunner
from unittest.mock import patch


@patch("flaskapptest.core.request_executor.RequestExecutor.execute")
def test_test_runner(mock_execute):
    mock_execute.return_value = {"status_code": 200}

    runner = TestRunner("http://localhost")
    results = runner.run([
        {
            "name": "GET /test",
            "method": "GET",
            "path": "/test",
            "payload": {"path": {}, "query": {}, "body": {}},
            "expected_status": [200],
        }
    ])

    assert results[0]["passed"] is True

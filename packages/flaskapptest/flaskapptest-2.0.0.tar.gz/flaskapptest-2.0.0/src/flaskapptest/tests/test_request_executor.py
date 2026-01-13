import requests
from flaskapptest.core.request_executor import RequestExecutor
from unittest.mock import patch


@patch("requests.request")
def test_request_execution(mock_request):
    mock_response = requests.Response()
    mock_response.status_code = 200
    mock_response._content = b'{"ok": true}'
    mock_request.return_value = mock_response

    executor = RequestExecutor("http://localhost")
    response = executor.execute(
        method="GET",
        path="/test",
        payload={"path": {}, "query": {}, "body": {}}
    )

    assert response["status_code"] == 200
    assert response["body"]["ok"] is True

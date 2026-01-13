from flaskapptest.core.validators import ResponseValidator


def test_response_validation_pass():
    validator = ResponseValidator()
    result = validator.validate(
        response={"status_code": 200},
        expected_status=[200]
    )

    assert result["passed"] is True


def test_response_validation_fail():
    validator = ResponseValidator()
    result = validator.validate(
        response={"status_code": 500},
        expected_status=[200]
    )

    assert result["passed"] is False

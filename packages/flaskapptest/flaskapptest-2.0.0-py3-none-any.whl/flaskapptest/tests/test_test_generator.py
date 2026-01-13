from flaskapptest.core.test_generator import TestGenerator


def test_test_generation():
    endpoints = [
        {
            "path": "/users",
            "methods": ["GET"],
            "function": "get_users",
            "file_path": "app.py",
        }
    ]

    generator = TestGenerator()
    tests = generator.generate(endpoints)

    assert len(tests) == 1
    assert tests[0]["method"] == "GET"

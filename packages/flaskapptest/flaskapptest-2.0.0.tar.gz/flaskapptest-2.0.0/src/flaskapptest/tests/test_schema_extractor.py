from flaskapptest.core.schema_extractor import SchemaExtractor


def test_schema_extraction():
    endpoint = {
        "path": "/users/<id>",
        "function": "update_user",
        "file_path": __file__,
    }

    extractor = SchemaExtractor()
    schema = extractor.extract(endpoint)

    assert "id" in schema["path_params"]

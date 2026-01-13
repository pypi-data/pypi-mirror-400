from flaskapptest.core.payload_generator import PayloadGenerator


def test_payload_structure():
    schema = {
        "path_params": ["id"],
        "query_params": ["page"],
        "body_params": ["name", "email"],
    }

    generator = PayloadGenerator()
    payload = generator.generate(schema)

    assert payload["path"] == {"id": None}
    assert payload["body"] == {"name": None, "email": None}

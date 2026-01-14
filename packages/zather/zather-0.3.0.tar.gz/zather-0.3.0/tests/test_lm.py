from zather.lm import _responses_create_with_fallback


def test_responses_create_with_fallback_strips_unsupported_temperature() -> None:
    calls = {"n": 0}

    def create_fn(**kwargs):
        calls["n"] += 1
        if calls["n"] == 1:
            assert "temperature" in kwargs
            raise Exception("Unsupported parameter: 'temperature' is not supported with this model.")
        assert "temperature" not in kwargs
        return {"output_text": "ok"}

    resp = _responses_create_with_fallback(create_fn, {"model": "gpt-5-mini", "temperature": 0.2})
    assert resp["output_text"] == "ok"


def test_responses_create_with_fallback_raises_on_unknown_param() -> None:
    def create_fn(**kwargs):
        raise Exception("Unsupported parameter: 'weird' is not supported with this model.")

    try:
        _responses_create_with_fallback(create_fn, {"model": "x", "temperature": 0.2})
    except Exception as e:
        assert "Unsupported parameter" in str(e)
    else:
        raise AssertionError("Expected exception")

from zather.utils import redact_secrets


def test_redact_secrets_openai_style() -> None:
    text = "OPENAI_API_KEY=sk-abcdefghijklmnopqrstuvwxyz0123456789"
    out = redact_secrets(text)
    assert "REDACTED" in out
    assert "abcdefghijklmnopqrstuvwxyz" not in out


def test_redact_secrets_key_value_pairs() -> None:
    text = "wandb_api_key: abc123\nanthropic_api_key = def456"
    out = redact_secrets(text)
    assert "wandb_api_key" in out and "REDACTED" in out
    assert "anthropic_api_key" in out and "REDACTED" in out
    assert "abc123" not in out
    assert "def456" not in out

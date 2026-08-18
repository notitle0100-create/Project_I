from seoul_mens_daily_edit.core.logging import redact_sensitive_text


def test_redact_sensitive_text_hides_database_and_token_values() -> None:
    message = (
        "postgresql+psycopg://app:testing-password@localhost:5432/database "
        "token=testing-token Bearer testing-bearer"
    )

    redacted = redact_sensitive_text(message)

    assert "testing-password" not in redacted
    assert "testing-token" not in redacted
    assert "testing-bearer" not in redacted
    assert "postgresql+psycopg://app:***@localhost:5432/database" in redacted

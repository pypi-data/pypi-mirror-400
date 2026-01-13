import pytest
import respx
from httpx import Response

from kraken_sdk import KrakenClient, KrakenValidationError


@respx.mock
def test_validation_error() -> None:
    """Test that validation errors are properly raised and contain details."""
    respx.get("https://api.kraken.com/api/v1/jobs/invalid-id").mock(
        return_value=Response(
            422,
            json={
                "detail": [
                    {
                        "loc": ["path", "job_id"],
                        "msg": "value is not a valid uuid",
                        "type": "type_error.uuid",
                    }
                ]
            },
        )
    )

    client = KrakenClient(base_url="https://api.kraken.com")

    with pytest.raises(KrakenValidationError) as excinfo:
        client.jobs.get("invalid-id")

    assert excinfo.value.status_code == 422
    assert excinfo.value.args[0] == "Validation error"
    # detail is the parsed JSON response
    assert isinstance(excinfo.value.detail, dict)
    assert "detail" in excinfo.value.detail
    assert excinfo.value.detail["detail"][0]["msg"] == "value is not a valid uuid"

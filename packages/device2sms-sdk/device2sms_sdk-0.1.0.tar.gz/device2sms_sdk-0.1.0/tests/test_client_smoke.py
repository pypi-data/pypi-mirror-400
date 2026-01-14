import os
import uuid
import pytest
from device2sms_sdk import Device2SmsClient


@pytest.mark.skipif(
    not os.getenv("DEVICE2SMS_API_KEY"),
    reason="DEVICE2SMS_API_KEY not set",
)
def test_send_sms_smoke():
    client = Device2SmsClient(
        base_url=os.getenv(
            "DEVICE2SMS_BASE_URL",
            "https://api.device2sms.com",
        ),
        api_key=os.getenv("DEVICE2SMS_API_KEY"),
    )

    message = f"Device2SMS Python SDK smoke test {uuid.uuid4()}"
    idem_key = f"smoke-{uuid.uuid4()}"

    res = client.send_sms(
        to="+353872157760",
        message=message,
        idempotency_key=idem_key,
    )

    assert isinstance(res, dict)
    assert "job_id" in res
    assert isinstance(res["job_id"], str)

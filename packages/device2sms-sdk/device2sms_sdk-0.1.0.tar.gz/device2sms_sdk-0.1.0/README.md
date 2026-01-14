# Device2SMS Python SDK (End-to-End Encrypted SMS)

The official **Python SDK** for **Device2SMS**.

This SDK allows you to send SMS messages through your paired Android devices using
**end-to-end encryption (E2EE)** powered by **Google Tink**.  
Message content is encrypted **before it leaves your application** and is only
decrypted on the paired Android device.

---

## 🚀 Features

- 🔐 End-to-end encrypted SMS (E2EE)
- 📱 Uses your own Android devices to send SMS
- 🔑 Simple API-key authentication
- ♻️ Idempotent message sending
- 🧩 No key management required by the user
- 🐍 Pythonic API with minimal dependencies

---

## 📦 Requirements

- **Python 3.11 or newer**
- A **Device2SMS account**
- At least one **paired Android device**
- An **API key** created in the Device2SMS dashboard

---

## 📥 Installation

### From PyPI (recommended)

```bash
pip install device2sms-sdk
```

### Local development install

```bash
cd sdk/python
python -m venv .venv
.venv\Scripts\activate
pip install -e .
```
# Linux / macOS
source .venv/bin/activate

# Windows
.venv\Scripts\activate

---

## 🔑 Authentication

Create an API key in the Device2SMS dashboard and store it securely:

```bash
export DEVICE2SMS_API_KEY="your_api_key_here"
```

---

## ✉️ Sending an SMS (E2EE)

```python
from device2sms_sdk import Device2SmsClient

client = Device2SmsClient(
    base_url="https://api.device2sms.com",
    api_key="YOUR_API_KEY",
)

result = client.send_sms(
    to="+000000000000",
    message="Hello from Device2SMS!",
    idempotency_key="order-123"
)

print(result)
```

### Response example

```json
{
  "job_id": "f1d1b4e6-3c9a-4d6a-8b9e-1c8a9e2d1234",
  "status": "queued"
}
```

---

## 🔐 How End-to-End Encryption Works

1. The SDK calls `/v1/sms/prepare`.
2. The backend selects an online device and returns its **public encryption key**.
3. The SDK encrypts the message locally using **Google Tink**.
4. Only ciphertext is sent to the backend.
5. The Android device decrypts the message and sends the SMS.

At no point does Device2SMS store or log plaintext message content.

---

## 🧪 Idempotency

To safely retry requests, pass an `idempotency_key`:

```python
client.send_sms(
    to="+000000000000",
    message="Hello again",
    idempotency_key="order-123"
)
```

Repeated requests with the same key will **not** send duplicate messages.

---

## ⚠️ System Messages

Verification and test messages may be sent without E2EE for operational reasons.
All **user-initiated SMS messages sent via the SDK are always end-to-end encrypted**.

---

## 🧯 Error Handling

All SDK errors raise `Device2SmsError`:

```python
from device2sms_sdk import Device2SmsClient, Device2SmsError

try:
    client.send_sms(...)
except Device2SmsError as e:
    print("SMS failed:", e)
```

---

## 📚 Documentation & Support

- Dashboard: https://device2sms.com  
- API reference: https://docs.device2sms.com  
- Support: support@device2sms.com  

---

## 🛡 Security Model Summary

| Component             | Access to plaintext |
|----------------------|---------------------|
| Your application     | ✅ Yes              |
| Device2SMS backend   | ❌ No               |
| Android device       | ✅ Yes              |
| Database / logs      | ❌ No               |
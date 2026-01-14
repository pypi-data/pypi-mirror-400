import base64
import hashlib
from dataclasses import dataclass
from typing import Optional, Dict, Any

import requests

from tink import hybrid, cleartext_keyset_handle, BinaryKeysetReader


@dataclass(frozen=True)
class PrepareResponse:
    device_id: str
    device_public_key: str  # base64(binary keyset)
    key_version: int
    prepare_token: str
    expires_at: str


class Device2SmsError(RuntimeError):
    pass


class Device2SmsClient:
    """
    Device2SMS Python SDK (E2EE).
    Uses Google Tink (official Python implementation).
    """

    def __init__(self, base_url: str, api_key: str, timeout: int = 15):
        if not base_url:
            raise ValueError("base_url is required")
        if not api_key:
            raise ValueError("api_key is required")

        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout

        # One-time Tink init
        hybrid.register()

    def _headers(self, idempotency_key: Optional[str] = None) -> Dict[str, str]:
        h = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json",
        }
        if idempotency_key:
            h["Idempotency-Key"] = idempotency_key
        return h

    @staticmethod
    def _aad(to: str) -> bytes:
        # Must match backend + Android decryption AAD
        return f"sms:{to}".encode("utf-8")

    @staticmethod
    def _message_hash(plaintext: str) -> str:
        return hashlib.sha256(plaintext.encode("utf-8")).hexdigest()

    @staticmethod
    def _encrypt_with_public_keyset(
        device_public_key_b64: str,
        plaintext: str,
        aad: bytes,
    ) -> str:
        keyset_bytes = base64.b64decode(device_public_key_b64)

        reader = BinaryKeysetReader(keyset_bytes)
        handle = cleartext_keyset_handle.read(reader)  # public keyset only

        encryptor = handle.primitive(hybrid.HybridEncrypt)
        ciphertext = encryptor.encrypt(
            plaintext.encode("utf-8"),
            aad,
        )

        return base64.b64encode(ciphertext).decode("utf-8")

    def prepare(self) -> PrepareResponse:
        try:
            r = requests.post(
                f"{self.base_url}/v1/sms/prepare",
                headers=self._headers(),
                json={},
                timeout=self.timeout,
            )
            r.raise_for_status()
            data = r.json()
        except requests.RequestException as e:
            raise Device2SmsError(f"prepare failed: {e}") from e
        except ValueError as e:
            raise Device2SmsError("prepare failed: invalid json response") from e

        return PrepareResponse(
            device_id=data["device_id"],
            device_public_key=data["device_public_key"],
            key_version=int(data["key_version"]),
            prepare_token=data["prepare_token"],
            expires_at=data["expires_at"],
        )

    def send_sms(
        self,
        to: str,
        message: str,
        idempotency_key: Optional[str] = None,
    ) -> Dict[str, Any]:
        if not to:
            raise ValueError("to is required")
        if not message:
            raise ValueError("message is required")

        prep = self.prepare()
        aad = self._aad(to)

        ciphertext_b64 = self._encrypt_with_public_keyset(
            prep.device_public_key,
            message,
            aad,
        )

        payload = {
            "to": to,
            "ciphertext": ciphertext_b64,
            "aad": aad.decode("utf-8"),
            "enc_device_id": prep.device_id,
            "enc_key_version": prep.key_version,
            "prepare_token": prep.prepare_token,
            "message_hash": self._message_hash(message),
        }

        try:
            r = requests.post(
                f"{self.base_url}/v1/sms/enqueue-e2ee",
                headers=self._headers(idempotency_key),
                json=payload,
                timeout=self.timeout,
            )
            r.raise_for_status()
            return r.json()
        except requests.RequestException as e:
            raise Device2SmsError(f"enqueue failed: {e}") from e
        except ValueError as e:
            raise Device2SmsError("enqueue failed: invalid json response") from e

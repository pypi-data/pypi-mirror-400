
from typing import Any, Dict, Mapping, Optional, Union, List
import json
import base64

import httpx
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec, utils
from cryptography.hazmat.primitives.asymmetric.ec import EllipticCurvePublicKey
from cryptography.hazmat.primitives import serialization

from miropay_payment_sdk.interface import ICancelPaymentResponse, ICancelPaymentResponseBody, ICreatePayment, ICreatePaymentResponse, ICreatePaymentResponseBody, IPaymentDetailsResponse, IPaymentDetailsResponseBody

from .auth import Auth
from .constant import API_BASE_URL


class PaymentClient:
    upstream_version: int = 1
    __http_client: httpx.AsyncClient
    __authenticator: Auth
    base_url: str
    is_test: bool = True

    def __init__(self, api_key: str, api_secret: str, base_url: Optional[str] = None) -> None:
        # `api_key` is the private key, `api_secret` is the secret used as passphrase / indicator
        self.__authenticator = Auth(api_key, api_secret)
        self.is_test = self.check_is_test(api_secret)
        self.base_url = self.__trim_base_url(base_url) if base_url else API_BASE_URL

        # async httpx client with sensible defaults
        self.__http_client = httpx.AsyncClient(timeout=10.0)

        # cache for public keys
        self.public_keys: List[Dict[str, Any]] = []

    # ------------------------------- Basic Methods ------------------------------ #
    async def __call(self, path: str, method: str, request_body: Optional[Union[str, Any]] = None) -> Dict[str, Any]:
        v = f"/v{self.upstream_version}"
        relative_url = f"{v}/payment/rest/{'test' if self.is_test else 'live'}{path}"
        versioned_url = f"{self.base_url}{relative_url}"
        signature = self.__authenticator.make_signature(method.upper(), relative_url)

        headers = {
            "x-signature": signature,
            "x-id": self.__authenticator.key_id,
            "Content-Type": "application/json",
        }

        try:
            if request_body is None:
                resp = await self.__http_client.request(method.upper(), versioned_url, headers=headers)
            else:
                # request_body is expected to be a JSON string or bytes
                resp = await self.__http_client.request(method.upper(), versioned_url, content=request_body, headers=headers)

            try:
                json_body = resp.json()
            except Exception:
                # If response is empty or not JSON, preserve text
                json_body = resp.text

            if resp.status_code < 200 or resp.status_code > 209:
                raise httpx.HTTPStatusError(f"Unexpected status: {resp.status_code}", request=resp.request, response=resp)

            return {"body": json_body, "headers": dict(resp.headers), "statusCode": resp.status_code}
        except Exception:
            raise

    # Trim base url
    def __trim_base_url(self, host_name: Optional[str]) -> str:
        _https = "https://"
        _http = "http://"

        if not host_name:
            return self.base_url

        if not host_name.startswith(_https):
            if host_name.startswith(_http):
                host_name = host_name.replace("http://", _https)
            else:
                host_name = f"{_https}{host_name}"

        if host_name.endswith("/"):
            return host_name[:-1]
        return host_name

    def check_is_test(self, secret: str) -> bool:
        return "test" in (secret or "")

    async def get_public_keys(self) -> Dict[str, Any]:
        return await self.__call("/get-public-keys", "GET", None)

    # ======================== Public Methods =======================
    async def get_payment_by_reference_code(self, reference_code: str) -> IPaymentDetailsResponse:
        resp = await self.__call(f"/status/{reference_code}", "GET", None)

        return IPaymentDetailsResponse(
            body=IPaymentDetailsResponseBody(**resp["body"]),
            headers=resp["headers"],
            statusCode=resp["statusCode"],
        )

    async def create_payment(self, payload: ICreatePayment) -> ICreatePaymentResponse:
        resp = await self.__call("/create", "POST", json.dumps(payload.to_dict()))

        return ICreatePaymentResponse(
            body=ICreatePaymentResponseBody(**resp["body"]),
            headers=resp["headers"],
            statusCode=resp["statusCode"],
        )
    
    async def cancel_payment(self, reference_code: str) -> ICancelPaymentResponse:
        resp = await self.__call(f"/cancel/{reference_code}", "PATCH", None)

        return ICancelPaymentResponse(
            body=ICancelPaymentResponseBody(**resp["body"]),
            headers=resp["headers"],
            statusCode=resp["statusCode"],
        )

    async def verify(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        # ensure public keys cached
        if not self.public_keys:
            resp = await self.get_public_keys()
            self.public_keys = resp.get("body") or []

        key_id = payload.get("keyId") if isinstance(payload, dict) else getattr(payload, "keyId", None)
        target_key = next((k for k in self.public_keys if k.get("id") == key_id), None)

        if not target_key:
            resp = await self.get_public_keys()
            self.public_keys = resp.get("body") or []
            target_key = next((k for k in self.public_keys if k.get("id") == key_id), None)
            if not target_key:
                raise RuntimeError("Internal server error: public key not found")

        content = payload.get("content") if isinstance(payload, dict) else getattr(payload, "content", None)
        if not content:
            raise RuntimeError("Internal server error: empty content")

        def _b64url_decode(input_str: str) -> bytes:
            rem = len(input_str) % 4
            if rem:
                input_str += "=" * (4 - rem)
            return base64.urlsafe_b64decode(input_str.encode("ascii"))

        # content is expected to be a JWS compact serialization: header.payload.signature
        try:
            parts = content.split(".")
            if len(parts) != 3:
                raise RuntimeError("Invalid token format")

            header_b64, payload_b64, sig_b64 = parts
            signed_data = f"{header_b64}.{payload_b64}".encode("ascii")
            sig_raw = _b64url_decode(sig_b64)

            pub_key_pem = target_key.get("key")
            if not pub_key_pem:
                raise RuntimeError("Public key missing")

            public_key = serialization.load_pem_public_key(pub_key_pem.encode("utf-8"))

            # Only Elliptic Curve public keys are supported for ES signatures in this implementation
            if not isinstance(public_key, EllipticCurvePublicKey):
                raise RuntimeError("Unsupported public key type for ES signature verification")

            # Convert raw signature (r||s) to DER for cryptography verify
            key_size_bytes = (public_key.curve.key_size + 7) // 8
            if len(sig_raw) != 2 * key_size_bytes:
                raise RuntimeError("Invalid signature length for ES algorithm")

            r = int.from_bytes(sig_raw[:key_size_bytes], "big")
            s = int.from_bytes(sig_raw[key_size_bytes:], "big")
            der_sig = utils.encode_dss_signature(r, s)

            # Verify signature (raises on failure)
            public_key.verify(der_sig, signed_data, ec.ECDSA(hashes.SHA512()))

            # Decode payload
            payload_json = json.loads(_b64url_decode(payload_b64).decode("utf-8"))

        except Exception:
            raise

        return {"body": payload_json, "headers": {}, "status_code": 200}


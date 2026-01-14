import base64
from typing import Optional, Any

try:
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric import padding
    from cryptography.hazmat.primitives import serialization
except Exception :
    # Defer import error until signing is used so lightweight usage doesn't require cryptography
    hashes: Any = None
    padding: Any = None
    serialization: Any = None 


class Auth:
    def __init__(self, private_key_pem: str, key_id: str, ):
        # private_key_pem: PEM string (multi-line or single-line)
        # key_id: string to use in x-id header
        self._private_key = private_key_pem
        self._key_id = key_id
        

    def get_private_key(self) -> str:
        return self._private_key

    def get_key_id(self) -> str:
        return self._key_id

    @property
    def key_id(self) -> str:
        return self._key_id

    @key_id.setter
    def key_id(self, value: str) -> None:
        self._key_id = value

    def make_signature(self, method: str, relative_url: str) -> str:
        """
        Create a base64 signature of the raw string: "{method} || {key_id} || {relative_url}".
        This expects the private key to be a PEM-encoded string and will attempt to
        load it with the instance passphrase as the passphrase if present.
        Supports RSA, Ed25519, Ed448, and EC keys.
        """
        if serialization is None:
            raise RuntimeError(
                "The 'cryptography' package is required to create signatures. Install it with: pip install cryptography"
            )

        raw_sign = f"{method} || {self._key_id} || {relative_url}"
        data = raw_sign.encode("utf-8")


        # Fix common PEM header typos (e.g., missing dash)
        pem = self._private_key


        try:
            private_key_obj: Any = serialization.load_pem_private_key(
                pem.encode("utf-8"),password=None
            )
        except Exception as exc:
            raise RuntimeError(f"Failed to load private key: {exc}")

        # Sign depending on key type
        try:
            from cryptography.hazmat.primitives.asymmetric import rsa, ec, ed25519, ed448
            if hasattr(private_key_obj, 'sign'):
                # Ed25519/Ed448: sign(data)
                if private_key_obj.__class__.__name__ in ("Ed25519PrivateKey", "Ed448PrivateKey"):
                    signature = private_key_obj.sign(data)
                # RSA: sign(data, padding, hash)
                elif isinstance(private_key_obj, rsa.RSAPrivateKey):
                    signature = private_key_obj.sign(
                        data, padding.PKCS1v15(), hashes.SHA256()
                    )
                # EC: sign(data, ec.ECDSA)
                elif isinstance(private_key_obj, ec.EllipticCurvePrivateKey):
                    signature = private_key_obj.sign(
                        data, ec.ECDSA(hashes.SHA256())
                    )
                else:
                    raise RuntimeError(f"Unsupported private key type: {type(private_key_obj)}")
            else:
                raise RuntimeError("Private key object does not support signing")
        except Exception as exc:
            raise RuntimeError(f"Failed to sign data: {exc}")

        return base64.b64encode(signature).decode("ascii")
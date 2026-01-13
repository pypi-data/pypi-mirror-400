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
    def __init__(self, private_key: str, secret: str):
        self._private_key = private_key
        self._secret = secret

    def get_private_key(self) -> str:
        return self._private_key

    def get_secret(self) -> str:
        return self._secret

    @property
    def secret(self) -> str:
        return self._secret

    @secret.setter
    def secret(self, value: str) -> None:
        self._secret = value

    @property
    def encrypted_pv_key(self) -> str:
        return self._private_key

    @encrypted_pv_key.setter
    def encrypted_pv_key(self, value: str) -> None:
        self._private_key = value

    @property
    def key_id(self) -> str:
        return self._secret

    def make_signature(self, method: str, relative_url: str) -> str:
        """Create a base64 signature of the raw string: "{method} || {secret} || {relative_url}".

        This expects the private key to be a PEM-encoded string and will attempt to
        load it with the instance `secret` as the passphrase if present.
        Uses RSA+SHA256 (PKCS1v15) for signing.
        """
        if serialization is None:
            raise RuntimeError(
                "The 'cryptography' package is required to create signatures. Install it with: pip install cryptography"
            )

        raw_sign = f"{method} || {self._secret} || {relative_url}"
        data = raw_sign.encode("utf-8")

        password: Optional[bytes] = self._secret.encode("utf-8") if self._secret else None

        try:
            private_key_obj: Any = serialization.load_pem_private_key(
                self._private_key.encode("utf-8"), password=password
            )
        except Exception as exc:
            raise RuntimeError(f"Failed to load private key: {exc}")

        try:
            signature = private_key_obj.sign(
                data, padding.PKCS1v15(), hashes.SHA256()
            )
        except Exception as exc:
            raise RuntimeError(f"Failed to sign data: {exc}")

        return base64.b64encode(signature).decode("ascii")
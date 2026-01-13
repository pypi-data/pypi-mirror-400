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

        def _try_load(pem_bytes: bytes) -> Any:
            try:
                return serialization.load_pem_private_key(pem_bytes, password=password)
            except Exception:
                return None

        pk_source = self._private_key or ""

        # Try raw
        private_key_obj: Any = _try_load(pk_source.encode("utf-8"))

        # Try replacing escaped newlines ("\\n") with real newlines
        if private_key_obj is None and "\\n" in pk_source:
            fixed = pk_source.replace("\\n", "\n")
            private_key_obj = _try_load(fixed.encode("utf-8"))

        # Try replacing literal '\n' sequences (e.g., from some env injection)
        if private_key_obj is None and "\\r" in pk_source:
            fixed = pk_source.replace("\\r", "\r").replace("\\n", "\n")
            private_key_obj = _try_load(fixed.encode("utf-8"))

        # If the key appears to be base64 without PEM headers, try wrapping with PEM markers
        if private_key_obj is None and "BEGIN" not in pk_source:
            candidate = pk_source.strip()
            # remove any whitespace and linebreaks then re-wrap
            no_ws = "".join(candidate.split())
            wrapped = "-----BEGIN PRIVATE KEY-----\n"
            # split into 64-char lines per PEM convention
            for i in range(0, len(no_ws), 64):
                wrapped += no_ws[i : i + 64] + "\n"
            wrapped += "-----END PRIVATE KEY-----\n"
            private_key_obj = _try_load(wrapped.encode("utf-8"))

        if private_key_obj is None:
            # Provide a helpful error message linking to cryptography FAQ and include common fixes
            msg = (
                "Failed to load private key: Unable to load PEM file or key material. "
                "Common causes: key missing PEM headers, escaped newlines (\\n) not converted, or malformed base64 framing. "
                "Try passing a proper PEM string (with '-----BEGIN ...-----'), or replace literal '\\n' with actual newlines. "
                "See https://cryptography.io/en/latest/faq/#why-can-t-i-import-my-pem-file for details."
            )
            raise RuntimeError(msg)

        try:
            signature = private_key_obj.sign(
                data, padding.PKCS1v15(), hashes.SHA256()
            )
        except Exception as exc:
            raise RuntimeError(f"Failed to sign data: {exc}")

        return base64.b64encode(signature).decode("ascii")

import os
import json
import base64
from pathlib import Path
from datetime import datetime
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.exceptions import InvalidSignature

# Embedded Public Key (Generated offline)
PUBLIC_KEY_PEM = b"""
-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAqwxr6awYpdUvQUF/pgLW
53/yot416/7hMz9EQrp20ghCB4mVStYhqsfUdVaaqL1nmTsgZ3ypC0x9N1qydUdq
qA+txkGDME4Wrwemv4FDRBgsvpXBemY0h2vv5m3uB+tMUXcb/hQsmEz6fuvDM16B
xXfr5MME5Hhm8YN3Brca+wHze1k/lo3b0en7ZNdF7TqCcYQx+0VIvZD6daQxGiGV
uoLRFp4EGYP6GXl70h6PP+PvjSuHH2Mqy3Lo8Xt1Hl6MhQchCioJ/IDcqwTZjtn4
FkPwAWDRtsqFblu8Zq2E9Yr+Hnkhct2KkE8ZaHj4eHnU42C8BbGgS/hhpPuO2P0o
wQIDAQAB
-----END PUBLIC KEY-----
"""

class LicenseManager:
    def __init__(self):
        self.license_dir = Path.home() / ".terminal_tutor"
        self.license_file = self.license_dir / "license"
        self._ensure_license_dir()
        self._public_key = self._load_public_key()

    def _ensure_license_dir(self):
        """Ensure the license directory exists."""
        self.license_dir.mkdir(parents=True, exist_ok=True)

    def _load_public_key(self):
        """Load the embedded public key."""
        return serialization.load_pem_public_key(PUBLIC_KEY_PEM)

    def verify_key_string(self, key_string):
        """
        Verify a license key string.
        Format: TT-<base64_payload>.<base64_signature>
        """
        if not key_string.startswith("TT-"):
            return None

        try:
            # Strip prefix
            content = key_string[3:]
            parts = content.split(".")
            if len(parts) != 2:
                return None
            
            payload_b64 = parts[0]
            signature_b64 = parts[1]

            payload_bytes = base64.urlsafe_b64decode(payload_b64 + "==")
            signature_bytes = base64.urlsafe_b64decode(signature_b64 + "==")

            # verify signature
            self._public_key.verify(
                signature_bytes,
                payload_bytes,
                padding.PKCS1v15(),
                hashes.SHA256()
            )

            # If we get here, signature is valid
            return json.loads(payload_bytes)
        except (ValueError, InvalidSignature, json.JSONDecodeError):
            return None
        except Exception as e:
            # Catch-all for other crypto errors
            return None

    def activate(self, key_string):
        """Validate and save a license key."""
        data = self.verify_key_string(key_string)
        if not data:
            return False, "Invalid license key signature."

        # Check expiry if present
        if "expiry" in data:
            expiry_date = datetime.strptime(data["expiry"], "%Y-%m-%d")
            if datetime.now() > expiry_date:
                return False, f"License expired on {data['expiry']}"

        # Save to file
        try:
            with open(self.license_file, "w") as f:
                f.write(key_string)
            return True, "License activated successfully!"
        except Exception as e:
            return False, f"Failed to save license: {str(e)}"

    def get_current_license_status(self):
        """
        Check the currently installed license.
        Returns: status_string, details_dict (or None)
        """
        if not self.license_file.exists():
            return "MISSING", None

        try:
            content = self.license_file.read_text().strip()
            data = self.verify_key_string(content)
            if data:
                return "VALID", data
            else:
                return "INVALID", None
        except Exception:
            return "ERROR", None

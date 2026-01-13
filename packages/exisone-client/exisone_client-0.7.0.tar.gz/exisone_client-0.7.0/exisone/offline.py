"""Offline license validation using RSA signature verification."""

import json
import struct
from datetime import datetime
from typing import Optional, Tuple

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

from .models import OfflineKeyPayload, OfflineValidationResult


# Crockford Base32 alphabet (excludes I, L, O, U to avoid confusion)
_BASE32_ALPHABET = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"

# Minimum length to detect offline keys (online keys are typically 19 chars like XXXX-XXXX-XXXX-XXXX)
OFFLINE_KEY_MIN_LENGTH = 50


def is_offline_key(key: str) -> bool:
    """Check if a key appears to be an offline activation code based on length."""
    clean = key.replace("-", "").replace(" ", "")
    return len(clean) >= OFFLINE_KEY_MIN_LENGTH


def validate_offline(
    offline_code: str,
    hardware_id: str,
    public_key_pem: str
) -> OfflineValidationResult:
    """
    Validate an offline activation code locally without server connection.

    Args:
        offline_code: The offline activation code (Base32 with dashes)
        hardware_id: The hardware ID to validate against
        public_key_pem: RSA public key in PEM format

    Returns:
        OfflineValidationResult with validation details
    """
    if not public_key_pem:
        return OfflineValidationResult(
            is_valid=False,
            error_message="Offline validation not configured. Set offline_public_key in options."
        )

    if not offline_code:
        return OfflineValidationResult(
            is_valid=False,
            error_message="Offline code is required"
        )

    if not hardware_id:
        return OfflineValidationResult(
            is_valid=False,
            error_message="Hardware ID is required"
        )

    try:
        is_valid, payload = _parse_offline_activation_code(public_key_pem, offline_code)

        if not is_valid or payload is None:
            return OfflineValidationResult(
                is_valid=False,
                error_message="Invalid or tampered offline activation code"
            )

        # Check hardware ID match (case-insensitive)
        if payload.hardware_id.upper() != hardware_id.upper():
            return OfflineValidationResult(
                is_valid=False,
                error_message="Hardware ID mismatch. This code is bound to a different machine.",
                hardware_mismatch=True,
                product_name=payload.product_name,
                expiration_date=payload.expiration_date
            )

        # Check expiration against local machine time
        now = datetime.utcnow()
        if payload.expiration_date < now:
            return OfflineValidationResult(
                is_valid=False,
                error_message="License has expired",
                is_expired=True,
                product_name=payload.product_name,
                product_id=payload.product_id,
                expiration_date=payload.expiration_date,
                email=payload.email,
                features=payload.features,
                version=payload.version
            )

        return OfflineValidationResult(
            is_valid=True,
            product_name=payload.product_name,
            product_id=payload.product_id,
            expiration_date=payload.expiration_date,
            email=payload.email,
            features=payload.features,
            version=payload.version
        )

    except Exception as e:
        return OfflineValidationResult(
            is_valid=False,
            error_message=f"Error validating offline code: {str(e)}"
        )


def _parse_offline_activation_code(
    public_key_pem: str,
    offline_code: str
) -> Tuple[bool, Optional[OfflineKeyPayload]]:
    """Parse and verify an offline activation code."""
    try:
        # Remove dashes and whitespace, convert to uppercase
        clean_code = offline_code.replace("-", "").replace(" ", "").upper()

        # Decode from Base32
        combined = _from_base32(clean_code)
        if len(combined) < 4:
            return False, None

        # Extract payload length (2 bytes, little-endian)
        payload_length = struct.unpack("<H", combined[:2])[0]
        if len(combined) < 2 + payload_length + 1:
            return False, None

        # Extract payload and signature
        payload_bytes = combined[2:2 + payload_length]
        signature = combined[2 + payload_length:]

        # Verify signature
        if not _verify_rsa_signature(public_key_pem, payload_bytes, signature):
            return False, None

        # Deserialize payload
        payload_json = payload_bytes.decode("utf-8")
        payload_dict = json.loads(payload_json)

        # Parse expiration date
        exp_str = payload_dict.get("expirationDate", "")
        if exp_str:
            # Handle ISO format with or without timezone
            exp_str = exp_str.replace("Z", "+00:00")
            if "+" in exp_str or exp_str.endswith("Z"):
                expiration_date = datetime.fromisoformat(exp_str.replace("+00:00", ""))
            else:
                expiration_date = datetime.fromisoformat(exp_str)
        else:
            expiration_date = datetime.min

        payload = OfflineKeyPayload(
            product_id=payload_dict.get("productId", 0),
            product_name=payload_dict.get("productName", ""),
            hardware_id=payload_dict.get("hardwareId", ""),
            expiration_date=expiration_date,
            email=payload_dict.get("email", ""),
            features=payload_dict.get("features", []),
            tenant_id=payload_dict.get("tenantId", 0),
            version=payload_dict.get("version", "")
        )

        return True, payload

    except Exception:
        return False, None


def _verify_rsa_signature(public_key_pem: str, data: bytes, signature: bytes) -> bool:
    """Verify RSA-SHA256 signature using PKCS#1 v1.5 padding."""
    try:
        public_key = serialization.load_pem_public_key(public_key_pem.encode("utf-8"))

        if not isinstance(public_key, rsa.RSAPublicKey):
            return False

        public_key.verify(
            signature,
            data,
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        return True
    except Exception:
        return False


def _from_base32(encoded: str) -> bytes:
    """Decode Crockford Base32 encoded string to bytes."""
    if not encoded:
        return b""

    # Build reverse lookup
    lookup = {char: idx for idx, char in enumerate(_BASE32_ALPHABET)}

    result = bytearray()
    buffer = 0
    bits_left = 0

    for char in encoded:
        val = lookup.get(char, -1)
        if val < 0:
            continue  # Skip invalid chars

        buffer = (buffer << 5) | val
        bits_left += 5

        if bits_left >= 8:
            bits_left -= 8
            result.append((buffer >> bits_left) & 0xFF)

    return bytes(result)

"""
CryptoEngine™ - Secure Encryption & Signing Toolkit
Copyright (c) 2025
Harshana Chathuranga / Bitrate Solutions (Pvt) Ltd.
Licensed under the MIT License — see LICENSE for details.
CryptoEngine™ name is trademarked — see TRADEMARK.md.
"""
import base64
import json

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_ssh_public_key
from cryptography.exceptions import InvalidSignature


SIG_VERSION = 1
SIG_ALGO = "rsa-pss"
SIG_HASH = "sha256"


class SignatureError(Exception):
    """Custom exception for signature operations."""
    pass


def sign_detached_rsa(private_key_pem: str, password: str | None, data: bytes) -> str:
    """
    Create a detached RSA-PSS signature over `data`.

    Returns a JSON string like:
    {
        "version": 1,
        "algo": "rsa-pss",
        "hash": "sha256",
        "signature": "BASE64..."
    }
    """
    try:
        key = load_pem_private_key(
            private_key_pem.encode("utf-8"),
            password.encode("utf-8") if password else None,
        )
    except Exception as e:
        raise SignatureError(f"Failed to load private key: {e}") from e

    try:
        signature = key.sign(
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH,
            ),
            hashes.SHA256(),
        )
    except Exception as e:
        raise SignatureError(f"Signing failed: {e}") from e

    sig_json = {
        "version": SIG_VERSION,
        "algo": SIG_ALGO,
        "hash": SIG_HASH,
        "signature": base64.b64encode(signature).decode("ascii"),
    }
    return json.dumps(sig_json, indent=2)


def verify_detached_rsa(public_key_ssh: str, data: bytes, signature_json: str) -> bool:
    """
    Verify a detached RSA-PSS signature over `data`.

    Returns True if valid, False if invalid.
    Raises SignatureError on format / key issues.
    """
    try:
        sig_obj = json.loads(signature_json)
    except Exception as e:
        raise SignatureError(f"Signature is not valid JSON: {e}") from e

    try:
        algo = sig_obj.get("algo")
        hname = sig_obj.get("hash")
        sig_b64 = sig_obj.get("signature")
        if algo != SIG_ALGO or hname != SIG_HASH or not sig_b64:
            raise SignatureError("Unsupported or missing signature parameters.")
        signature = base64.b64decode(sig_b64)
    except SignatureError:
        raise
    except Exception as e:
        raise SignatureError(f"Invalid signature structure: {e}") from e

    try:
        pub = load_ssh_public_key(public_key_ssh.encode("utf-8"))
    except Exception as e:
        raise SignatureError(f"Failed to load public key: {e}") from e

    try:
        pub.verify(
            signature,
            data,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH,
            ),
            hashes.SHA256(),
        )
        return True
    except InvalidSignature:
        return False
    except Exception as e:
        raise SignatureError(f"Verification failed: {e}") from e
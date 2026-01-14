"""
CryptoEngine™ - Secure Encryption & Signing Toolkit
Copyright (c) 2025
Harshana Chathuranga / Bitrate Solutions (Pvt) Ltd.
Licensed under the MIT License — see LICENSE for details.
CryptoEngine™ name is trademarked — see TRADEMARK.md.
"""
import hashlib
import base64

SUPPORTED_HASHES = {
    "SHA-256": "sha256",
    "SHA-512": "sha512",
    "SHA-1": "sha1",
    "MD5": "md5",
}


def compute_hash(data: bytes, algo_name: str) -> dict[str, str]:
    """
    Compute hash of data with the given algorithm display name.

    Returns:
        {
          "algo": <canonical name>,
          "hex":  <hex digest>,
          "b64":  <base64 digest>
        }
    """
    algo_key = SUPPORTED_HASHES.get(algo_name)
    if not algo_key:
        raise ValueError(f"Unsupported hash algorithm: {algo_name}")

    h = hashlib.new(algo_key)
    h.update(data)
    digest = h.digest()

    return {
        "algo": algo_key,
        "hex": h.hexdigest(),
        "b64": base64.b64encode(digest).decode("ascii"),
    }
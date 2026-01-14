"""
CryptoEngine™ - Secure Encryption & Signing Toolkit
Copyright (c) 2025
Harshana Chathuranga / Bitrate Solutions (Pvt) Ltd.
Licensed under the MIT License — see LICENSE for details.
CryptoEngine™ name is trademarked — see TRADEMARK.md.
"""
import os
import json
import base64
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


def load_rsa_public_key_from_ssh(ssh_pub_str: str):
    """Load an RSA public key from an OpenSSH 'ssh-rsa AAAA...' string."""
    ssh_pub_bytes = ssh_pub_str.encode("utf-8")
    return serialization.load_ssh_public_key(ssh_pub_bytes)


def load_rsa_private_key_from_any_format(key_str: str, password: str | None = None):
    """
    Load RSA private key from either:
    - OpenSSH format (BEGIN OPENSSH PRIVATE KEY)
    - PEM PKCS#1 / PKCS#8
    """
    key_bytes = key_str.encode("utf-8")
    password_bytes = password.encode("utf-8") if password else None

    # Try OpenSSH
    try:
        return serialization.load_ssh_private_key(key_bytes, password=password_bytes)
    except Exception:
        pass

    # Fallback to PEM
    return serialization.load_pem_private_key(key_bytes, password=password_bytes)


def encrypt_with_rsa_aes(ssh_public_key_str: str, plaintext: bytes) -> str:
    """
    Hybrid encryption:
    - Generate random AES-256 key
    - Encrypt plaintext with AES-256-GCM
    - Encrypt AES key with RSA-OAEP
    - Return JSON string (base64 fields)
    """
    public_key = load_rsa_public_key_from_ssh(ssh_public_key_str)

    aes_key = AESGCM.generate_key(bit_length=256)
    aesgcm = AESGCM(aes_key)
    nonce = os.urandom(12)  # 96-bit nonce

    ciphertext = aesgcm.encrypt(nonce, plaintext, associated_data=None)

    encrypted_key = public_key.encrypt(
        aes_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )

    blob = {
        "v": 1,
        "alg": "rsa-oaep+aes-256-gcm",
        "ek": base64.b64encode(encrypted_key).decode("ascii"),
        "nonce": base64.b64encode(nonce).decode("ascii"),
        "ct": base64.b64encode(ciphertext).decode("ascii"),
    }
    return json.dumps(blob, indent=2)


def decrypt_with_rsa_aes(private_key_pem_str: str, encrypted_json: str,
                         password: str | None = None) -> bytes:
    """Decrypt JSON blob produced by encrypt_with_rsa_aes."""
    blob = json.loads(encrypted_json)
    if blob.get("v") != 1 or blob.get("alg") != "rsa-oaep+aes-256-gcm":
        raise ValueError("Unsupported version or algorithm")

    encrypted_key = base64.b64decode(blob["ek"])
    nonce = base64.b64decode(blob["nonce"])
    ciphertext = base64.b64decode(blob["ct"])

    private_key = load_rsa_private_key_from_any_format(private_key_pem_str, password)

    aes_key = private_key.decrypt(
        encrypted_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )

    aesgcm = AESGCM(aes_key)
    plaintext = aesgcm.decrypt(nonce, ciphertext, associated_data=None)
    return plaintext

def generate_rsa_ssh_keypair(key_size: int = 4096, passphrase: str | None = None) -> tuple[str, str]:
    """
    Generate an RSA key pair.

    Returns:
        (private_key_pem_str, public_key_ssh_str)
    """
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=key_size,
    )

    if passphrase:
        enc_alg = serialization.BestAvailableEncryption(passphrase.encode("utf-8"))
    else:
        enc_alg = serialization.NoEncryption()

    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=enc_alg,
    ).decode("utf-8")

    public_ssh = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.OpenSSH,
        format=serialization.PublicFormat.OpenSSH,
    ).decode("utf-8")

    return private_pem, public_ssh
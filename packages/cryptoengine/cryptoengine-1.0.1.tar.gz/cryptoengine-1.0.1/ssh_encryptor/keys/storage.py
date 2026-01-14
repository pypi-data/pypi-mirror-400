"""
CryptoEngine™ - Secure Encryption & Signing Toolkit
Copyright (c) 2025
Harshana Chathuranga / Bitrate Solutions (Pvt) Ltd.
Licensed under the MIT License — see LICENSE for details.
CryptoEngine™ name is trademarked — see TRADEMARK.md.
"""
import os
import json

CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".ssh_encryptor_keys.json")


def load_config():
    if not os.path.isfile(CONFIG_PATH):
        return {"public_keys": [], "private_keys": []}
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        if "public_keys" not in data:
            data["public_keys"] = []
        if "private_keys" not in data:
            data["private_keys"] = []
        return data
    except Exception:
        return {"public_keys": [], "private_keys": []}


def save_config(cfg):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)
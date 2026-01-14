"""
CryptoEngine™ - Secure Encryption & Signing Toolkit
Copyright (c) 2025
Harshana Chathuranga / Bitrate Solutions (Pvt) Ltd.
Licensed under the MIT License — see LICENSE for details.
CryptoEngine™ name is trademarked — see TRADEMARK.md.
"""
import os
import uuid
from PyQt6 import QtWidgets

from ssh_encryptor.crypto.rsa_hybrid import generate_rsa_ssh_keypair
from ssh_encryptor.keys.storage import save_config
from ssh_encryptor.ui.dialogs import (
    PublicKeyDialog,
    PrivateKeyDialog,
    GenerateKeypairDialog,
)


class KeysTab(QtWidgets.QWidget):
    def __init__(self, parent=None, main_window=None):
        super().__init__(parent)
        self.main = main_window

        self._build_ui()
        self.refresh_key_lists()

    # ---------- UI ----------

    def _build_ui(self):
        layout = QtWidgets.QHBoxLayout(self)

        # Public keys column
        pub_col = QtWidgets.QVBoxLayout()
        pub_label = QtWidgets.QLabel("Public keys")
        self.public_keys_list = QtWidgets.QListWidget()

        pub_btn_row = QtWidgets.QHBoxLayout()
        self.pub_add_btn = QtWidgets.QPushButton("Add")
        self.pub_edit_btn = QtWidgets.QPushButton("Edit")
        self.pub_del_btn = QtWidgets.QPushButton("Delete")

        self.pub_add_btn.clicked.connect(self.add_public_key)
        self.pub_edit_btn.clicked.connect(self.edit_public_key)
        self.pub_del_btn.clicked.connect(self.delete_public_key)

        pub_btn_row.addWidget(self.pub_add_btn)
        pub_btn_row.addWidget(self.pub_edit_btn)
        pub_btn_row.addWidget(self.pub_del_btn)

        pub_col.addWidget(pub_label)
        pub_col.addWidget(self.public_keys_list)
        pub_col.addLayout(pub_btn_row)

        # Private keys column
        priv_col = QtWidgets.QVBoxLayout()
        priv_label = QtWidgets.QLabel("Private keys")
        self.private_keys_list = QtWidgets.QListWidget()

        priv_btn_row = QtWidgets.QHBoxLayout()
        self.priv_add_btn = QtWidgets.QPushButton("Add")
        self.priv_edit_btn = QtWidgets.QPushButton("Edit")
        self.priv_del_btn = QtWidgets.QPushButton("Delete")
        self.priv_gen_btn = QtWidgets.QPushButton("Generate key pair")

        self.priv_add_btn.clicked.connect(self.add_private_key)
        self.priv_edit_btn.clicked.connect(self.edit_private_key)
        self.priv_del_btn.clicked.connect(self.delete_private_key)
        self.priv_gen_btn.clicked.connect(self.generate_key_pair)

        priv_btn_row.addWidget(self.priv_add_btn)
        priv_btn_row.addWidget(self.priv_edit_btn)
        priv_btn_row.addWidget(self.priv_del_btn)
        priv_btn_row.addWidget(self.priv_gen_btn)

        priv_col.addWidget(priv_label)
        priv_col.addWidget(self.private_keys_list)
        priv_col.addLayout(priv_btn_row)

        layout.addLayout(pub_col)
        layout.addLayout(priv_col)

    # ---------- Refresh lists ----------

    def refresh_key_lists(self):
        """Refresh list widgets from main.config."""
        if not self.main:
            return
        cfg = self.main.config

        # Public keys
        self.public_keys_list.clear()
        for k in cfg.get("public_keys", []):
            item = QtWidgets.QListWidgetItem(k["name"])
            item.setData(256, k["id"])
            self.public_keys_list.addItem(item)

        # Private keys
        self.private_keys_list.clear()
        for k in cfg.get("private_keys", []):
            label = f"{k['name']} ({k['path']})"
            item = QtWidgets.QListWidgetItem(label)
            item.setData(256, k["id"])
            self.private_keys_list.addItem(item)

    # ---------- Public key actions ----------

    def add_public_key(self):
        if not self.main:
            return
        dlg = PublicKeyDialog(self)
        if dlg.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            name, data = dlg.get_values()
            entry = {"id": uuid.uuid4().hex, "name": name, "data": data}
            self.main.config.setdefault("public_keys", []).append(entry)
            save_config(self.main.config)
            self.main.refresh_keys_everywhere()
            self.main.show_toast("Public key added.", level="success")

    def edit_public_key(self):
        if not self.main:
            return
        item = self.public_keys_list.currentItem()
        if not item:
            return
        key_id = item.data(256)
        pk = next(
            (k for k in self.main.config.get("public_keys", []) if k["id"] == key_id),
            None,
        )
        if not pk:
            return
        dlg = PublicKeyDialog(self, name=pk["name"], data=pk["data"])
        if dlg.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            name, data = dlg.get_values()
            pk["name"] = name
            pk["data"] = data
            save_config(self.main.config)
            self.main.refresh_keys_everywhere()
            self.main.show_toast("Public key updated.", level="success")

    def delete_public_key(self):
        if not self.main:
            return
        item = self.public_keys_list.currentItem()
        if not item:
            return
        key_id = item.data(256)
        res = QtWidgets.QMessageBox.question(
            self,
            "Confirm delete",
            "Delete selected public key?",
        )
        if res != QtWidgets.QMessageBox.StandardButton.Yes:
            return
        self.main.config["public_keys"] = [
            k for k in self.main.config.get("public_keys", []) if k["id"] != key_id
        ]
        save_config(self.main.config)
        self.main.refresh_keys_everywhere()
        self.main.show_toast("Public key deleted.", level="info")

    # ---------- Private key actions ----------

    def add_private_key(self):
        if not self.main:
            return
        dlg = PrivateKeyDialog(self)
        if dlg.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            name, path = dlg.get_values()
            entry = {"id": uuid.uuid4().hex, "name": name, "path": path}
            self.main.config.setdefault("private_keys", []).append(entry)
            save_config(self.main.config)
            self.main.refresh_keys_everywhere()
            self.main.show_toast("Private key added.", level="success")

    def edit_private_key(self):
        if not self.main:
            return
        item = self.private_keys_list.currentItem()
        if not item:
            return
        key_id = item.data(256)
        pk = next(
            (k for k in self.main.config.get("private_keys", []) if k["id"] == key_id),
            None,
        )
        if not pk:
            return
        dlg = PrivateKeyDialog(self, name=pk["name"], path=pk["path"])
        if dlg.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            name, path = dlg.get_values()
            pk["name"] = name
            pk["path"] = path
            save_config(self.main.config)
            self.main.refresh_keys_everywhere()
            self.main.show_toast("Private key updated.", level="success")

    def delete_private_key(self):
        if not self.main:
            return
        item = self.private_keys_list.currentItem()
        if not item:
            return
        key_id = item.data(256)
        res = QtWidgets.QMessageBox.question(
            self,
            "Confirm delete",
            "Delete selected private key?",
        )
        if res != QtWidgets.QMessageBox.StandardButton.Yes:
            return
        self.main.config["private_keys"] = [
            k for k in self.main.config.get("private_keys", []) if k["id"] != key_id
        ]
        save_config(self.main.config)
        self.main.refresh_keys_everywhere()
        self.main.show_toast("Private key deleted.", level="info")

    def generate_key_pair(self):
        if not self.main:
            return
        dlg = GenerateKeypairDialog(self)
        if dlg.exec() != QtWidgets.QDialog.DialogCode.Accepted:
            return

        vals = dlg.get_values()
        name = vals["name"]
        key_size = vals["key_size"]
        path = vals["path"]
        passphrase = vals["passphrase"] or None

        # Generate keys
        try:
            priv_pem, pub_ssh = generate_rsa_ssh_keypair(
                key_size=key_size,
                passphrase=passphrase,
            )
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self,
                "Error",
                f"Failed to generate key pair:\n{e}",
            )
            return

        # Derive public key path (same + ".pub")
        pub_path = path + ".pub"

        # Write files
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
        except Exception:
            # ignore if no directory part
            pass

        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(priv_pem)
            with open(pub_path, "w", encoding="utf-8") as f:
                f.write(pub_ssh)
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self,
                "Error",
                f"Failed to save keys to disk:\n{e}",
            )
            return

        # Register in key manager:
        priv_entry = {"id": uuid.uuid4().hex, "name": name, "path": path}
        pub_entry = {"id": uuid.uuid4().hex, "name": name + " (pub)", "data": pub_ssh}
        self.main.config.setdefault("private_keys", []).append(priv_entry)
        self.main.config.setdefault("public_keys", []).append(pub_entry)
        save_config(self.main.config)
        self.main.refresh_keys_everywhere()

        self.main.show_toast(
            f"Key pair created.\nPrivate: {path}\nPublic: {pub_path}",
            level="success",
            duration_ms=5000,
        )
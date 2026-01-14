"""
CryptoEngine™ - Secure Encryption & Signing Toolkit
Copyright (c) 2025
Harshana Chathuranga / Bitrate Solutions (Pvt) Ltd.
Licensed under the MIT License — see LICENSE for details.
CryptoEngine™ name is trademarked — see TRADEMARK.md.
"""
import os
from PyQt6 import QtWidgets

from ssh_encryptor.crypto.rsa_hybrid import encrypt_with_rsa_aes
from ssh_encryptor.crypto.sign_utils import sign_detached_rsa, SignatureError


class EncryptTab(QtWidgets.QWidget):
    def __init__(self, parent=None, main_window=None):
        super().__init__(parent)
        self.main = main_window  # reference to MainWindow

        self.last_encrypted_json: str | None = None
        self.last_signature_json: str | None = None

        self._build_ui()
        self.refresh_public_keys()
        self.refresh_private_keys()

    # ---------- UI ----------

    def _build_ui(self):
        layout = QtWidgets.QVBoxLayout(self)

        # Public key selection row (for encryption)
        pub_row = QtWidgets.QHBoxLayout()
        self.public_key_combo = QtWidgets.QComboBox()
        self.public_key_combo.currentIndexChanged.connect(
            self.handle_public_combo_change
        )
        pub_row.addWidget(QtWidgets.QLabel("Saved public key:"))
        pub_row.addWidget(self.public_key_combo)
        pub_row.addStretch()

        self.pub_key_edit = QtWidgets.QPlainTextEdit()
        self.pub_key_edit.setPlaceholderText(
            "Paste or auto-load recipient RSA SSH PUBLIC key (ssh-rsa AAAA...)"
        )

        # Plaintext mode (Text / File)
        pt_mode_row = QtWidgets.QHBoxLayout()
        self.plaintext_mode_text = QtWidgets.QRadioButton("Text")
        self.plaintext_mode_file = QtWidgets.QRadioButton("File")
        self.plaintext_mode_text.setChecked(True)
        self.plaintext_mode_text.toggled.connect(self.update_plaintext_mode)
        pt_mode_row.addWidget(QtWidgets.QLabel("Plaintext input:"))
        pt_mode_row.addWidget(self.plaintext_mode_text)
        pt_mode_row.addWidget(self.plaintext_mode_file)
        pt_mode_row.addStretch()

        # Text input
        self.plaintext_edit = QtWidgets.QPlainTextEdit()
        self.plaintext_edit.setPlaceholderText("Type or paste plaintext message here")

        # File input
        pt_file_row = QtWidgets.QHBoxLayout()
        self.plaintext_file_path_edit = QtWidgets.QLineEdit()
        self.plaintext_file_path_edit.setPlaceholderText("Select file to encrypt")
        self.browse_plaintext_button = QtWidgets.QPushButton("Browse…")
        self.browse_plaintext_button.clicked.connect(self.browse_plaintext_file)
        pt_file_row.addWidget(self.plaintext_file_path_edit)
        pt_file_row.addWidget(self.browse_plaintext_button)

        # Buttons for encryption
        self.encrypt_button = QtWidgets.QPushButton("Encrypt")
        self.encrypt_button.clicked.connect(self.handle_encrypt)

        self.copy_encrypted_button = QtWidgets.QPushButton("Copy")
        self.copy_encrypted_button.clicked.connect(self.copy_encrypted_to_clipboard)

        self.save_encrypted_button = QtWidgets.QPushButton("Save")
        self.save_encrypted_button.clicked.connect(self.save_encrypted_to_file)

        top_btn_row = QtWidgets.QHBoxLayout()
        top_btn_row.addWidget(self.encrypt_button)
        top_btn_row.addStretch()

        encrypted_btn_row = QtWidgets.QHBoxLayout()
        encrypted_btn_row.addStretch()
        encrypted_btn_row.addWidget(self.copy_encrypted_button)
        encrypted_btn_row.addSpacing(10)
        encrypted_btn_row.addWidget(self.save_encrypted_button)

        # Encrypted JSON output
        self.encrypted_output = QtWidgets.QPlainTextEdit()
        self.encrypted_output.setPlaceholderText("Encrypted JSON will appear here")
        self.encrypted_output.setReadOnly(True)

        # --- Signature section (for encrypted JSON) ---

        # Saved private key combo (autofills path)
        sign_priv_sel_row = QtWidgets.QHBoxLayout()
        self.sign_private_key_combo = QtWidgets.QComboBox()
        self.sign_private_key_combo.currentIndexChanged.connect(
            self.handle_sign_private_combo_change
        )
        sign_priv_sel_row.addWidget(QtWidgets.QLabel("Saved private key:"))
        sign_priv_sel_row.addWidget(self.sign_private_key_combo)
        sign_priv_sel_row.addStretch()

        # Private key file path + browse (for signing)
        sign_priv_row = QtWidgets.QHBoxLayout()
        self.sign_priv_path_edit = QtWidgets.QLineEdit()
        self.sign_priv_path_edit.setPlaceholderText(
            "Select RSA private key file for signing (e.g. ~/.ssh/id_rsa)"
        )
        self.sign_browse_priv_btn = QtWidgets.QPushButton("Browse…")
        self.sign_browse_priv_btn.clicked.connect(self.browse_sign_private_key)
        sign_priv_row.addWidget(self.sign_priv_path_edit)
        sign_priv_row.addWidget(self.sign_browse_priv_btn)

        # Buttons: Sign / Copy / Save
        self.sign_encrypted_button = QtWidgets.QPushButton("Sign")
        self.sign_encrypted_button.clicked.connect(self.handle_sign_encrypted)

        self.copy_signature_button = QtWidgets.QPushButton("Copy signature")
        self.copy_signature_button.clicked.connect(self.copy_signature)

        self.save_signature_button = QtWidgets.QPushButton("Save signature")
        self.save_signature_button.clicked.connect(self.save_signature)

        sig_btn_row = QtWidgets.QHBoxLayout()
        sig_btn_row.addWidget(self.sign_encrypted_button)
        sig_btn_row.addStretch()
        sig_btn_row.addWidget(self.copy_signature_button)
        sig_btn_row.addSpacing(10)
        sig_btn_row.addWidget(self.save_signature_button)

        self.signature_output = QtWidgets.QPlainTextEdit()
        self.signature_output.setReadOnly(True)
        self.signature_output.setPlaceholderText("Signature JSON will appear here")

        # Assemble layout
        layout.addLayout(pub_row)
        layout.addWidget(QtWidgets.QLabel("Public key (editable)"))
        layout.addWidget(self.pub_key_edit)
        layout.addLayout(pt_mode_row)
        layout.addWidget(self.plaintext_edit)
        layout.addLayout(pt_file_row)
        layout.addLayout(top_btn_row)

        layout.addWidget(QtWidgets.QLabel("Encrypted JSON"))
        layout.addWidget(self.encrypted_output)
        layout.addLayout(encrypted_btn_row)

        layout.addSpacing(12)
        layout.addWidget(QtWidgets.QLabel("Signature JSON (over encrypted JSON)"))
        layout.addLayout(sign_priv_sel_row)
        layout.addLayout(sign_priv_row)
        layout.addLayout(sig_btn_row)
        layout.addWidget(self.signature_output)

        self.update_plaintext_mode()

    # ---------- Key refresh from MainWindow ----------

    def refresh_public_keys(self):
        """Reload public keys from main_window.config into the combo."""
        self.public_key_combo.blockSignals(True)
        self.public_key_combo.clear()
        self.public_key_combo.addItem("Manual entry", userData=None)

        if self.main:
            for k in self.main.config.get("public_keys", []):
                self.public_key_combo.addItem(k["name"], userData=k["id"])

        self.public_key_combo.blockSignals(False)

    def refresh_private_keys(self):
        """Reload private keys (for signing) from main_window.config into combo."""
        self.sign_private_key_combo.blockSignals(True)
        self.sign_private_key_combo.clear()
        self.sign_private_key_combo.addItem("Manual entry", userData=None)

        if self.main:
            for k in self.main.config.get("private_keys", []):
                self.sign_private_key_combo.addItem(k["name"], userData=k["id"])

        self.sign_private_key_combo.blockSignals(False)

    # ---------- Mode toggle ----------

    def update_plaintext_mode(self):
        is_text = self.plaintext_mode_text.isChecked()
        self.plaintext_edit.setEnabled(is_text)
        self.plaintext_file_path_edit.setEnabled(not is_text)
        self.browse_plaintext_button.setEnabled(not is_text)

    # ---------- File dialogs ----------

    def browse_plaintext_file(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Select file to encrypt",
            os.path.expanduser("~"),
            "All Files (*)",
        )
        if file_path:
            self.plaintext_file_path_edit.setText(file_path)

    def browse_sign_private_key(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Select RSA private key file for signing",
            os.path.expanduser("~"),
            "All Files (*);;PEM/SSH Keys (*)",
        )
        if file_path:
            self.sign_priv_path_edit.setText(file_path)

    # ---------- Handlers ----------

    def handle_public_combo_change(self, index: int):
        if not self.main:
            return
        key_id = self.public_key_combo.itemData(index)
        if not key_id:
            return  # manual
        pk = next(
            (k for k in self.main.config.get("public_keys", []) if k["id"] == key_id),
            None,
        )
        if pk:
            self.pub_key_edit.setPlainText(pk["data"])

    def handle_sign_private_combo_change(self, index: int):
        """Autofill private key path when a saved key is selected."""
        if not self.main:
            return
        key_id = self.sign_private_key_combo.itemData(index)
        if not key_id:
            return  # manual
        pk = next(
            (k for k in self.main.config.get("private_keys", []) if k["id"] == key_id),
            None,
        )
        if pk:
            self.sign_priv_path_edit.setText(pk["path"])

    def handle_encrypt(self):
        if not self.main:
            return

        pub = self.pub_key_edit.toPlainText().strip()
        if not pub:
            self.main.show_toast("Public key is required.", level="warning")
            return

        # Plaintext source
        if self.plaintext_mode_text.isChecked():
            pt_text = self.plaintext_edit.toPlainText()
            if not pt_text:
                self.main.show_toast("Plaintext text is empty.", level="warning")
                return
            plaintext_bytes = pt_text.encode("utf-8")
        else:
            path = self.plaintext_file_path_edit.text().strip()
            if not path:
                self.main.show_toast("Please select a file to encrypt.", level="warning")
                return
            if not os.path.isfile(path):
                self.main.show_toast(f"File not found: {path}", level="warning")
                return
            try:
                with open(path, "rb") as f:
                    plaintext_bytes = f.read()
            except Exception as e:
                QtWidgets.QMessageBox.critical(
                    self, "Error", f"Could not read file:\n{e}"
                )
                return

        try:
            enc = encrypt_with_rsa_aes(pub, plaintext_bytes)
            self.last_encrypted_json = enc
            self.encrypted_output.setPlainText(enc)

            # reset old signature (ciphertext changed)
            self.last_signature_json = None
            self.signature_output.clear()

            self.main.show_toast("Encryption completed.", level="success")
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "Error", f"Encryption failed:\n{e}"
            )

    # ---------- Sign encrypted JSON ----------

    def handle_sign_encrypted(self):
        if not self.main:
            return

        if not self.last_encrypted_json:
            self.main.show_toast(
                "No encrypted JSON available. Encrypt something first.",
                level="warning",
            )
            return

        key_path = self.sign_priv_path_edit.text().strip()
        if not key_path:
            self.main.show_toast(
                "Private key file is required for signing.",
                level="warning",
            )
            return
        if not os.path.isfile(key_path):
            self.main.show_toast(
                f"Private key file not found: {key_path}", level="warning"
            )
            return

        # Ask for password (optional)
        pwd, ok = QtWidgets.QInputDialog.getText(
            self,
            "Private key password",
            "Password (leave empty if none):",
            QtWidgets.QLineEdit.EchoMode.Password,
        )
        if not ok:
            return
        if pwd == "":
            pwd = None

        # Load private key
        try:
            with open(key_path, "r", encoding="utf-8") as f:
                priv_pem = f.read()
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "Error", f"Could not read private key file:\n{e}"
            )
            return

        data = self.last_encrypted_json.encode("utf-8")

        try:
            sig_json = sign_detached_rsa(priv_pem, pwd, data)
        except SignatureError as e:
            QtWidgets.QMessageBox.critical(self, "Error", str(e))
            return

        self.last_signature_json = sig_json
        self.signature_output.setPlainText(sig_json)

        self.main.show_toast("Signature created over encrypted JSON.", level="success")

    def copy_signature(self):
        if not self.last_signature_json:
            if self.main:
                self.main.show_toast(
                    "No signature available. Create one first.",
                    level="warning",
                )
            return
        QtWidgets.QApplication.clipboard().setText(self.last_signature_json)
        if self.main:
            self.main.show_toast("Signature JSON copied.", level="success")

    def save_signature(self):
        if not self.last_signature_json:
            if self.main:
                self.main.show_toast(
                    "No signature available. Create one first.",
                    level="warning",
                )
            return

        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Save signature JSON",
            os.path.expanduser("~"),
            "JSON Files (*.json);;All Files (*)",
        )
        if not file_path:
            return

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(self.last_signature_json)
            if self.main:
                self.main.show_toast("Signature saved.", level="success")
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "Error", f"Could not save signature:\n{e}"
            )

    # ---------- Save / Copy encrypted ----------

    def save_encrypted_to_file(self):
        if not self.last_encrypted_json:
            if self.main:
                self.main.show_toast(
                    "No encrypted data available. Encrypt something first.",
                    level="warning",
                )
            return

        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Save encrypted JSON",
            os.path.expanduser("~"),
            "JSON Files (*.json);;All Files (*)",
        )
        if not file_path:
            return

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(self.last_encrypted_json)
            if self.main:
                self.main.show_toast("Encrypted JSON saved.", level="success")
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "Error", f"Could not save encrypted file:\n{e}"
            )

    def copy_encrypted_to_clipboard(self):
        if not self.last_encrypted_json:
            if self.main:
                self.main.show_toast(
                    "No encrypted data available. Encrypt something first.",
                    level="warning",
                )
            return

        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.setText(self.last_encrypted_json)

        if self.main:
            self.main.show_toast(
                "Encrypted JSON copied to clipboard.",
                level="success",
            )
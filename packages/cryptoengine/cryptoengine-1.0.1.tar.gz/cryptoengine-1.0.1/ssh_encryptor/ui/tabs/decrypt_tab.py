"""
CryptoEngine™ - Secure Encryption & Signing Toolkit
Copyright (c) 2025
Harshana Chathuranga / Bitrate Solutions (Pvt) Ltd.
Licensed under the MIT License — see LICENSE for details.
CryptoEngine™ name is trademarked — see TRADEMARK.md.
"""
import os
from PyQt6 import QtWidgets

from ssh_encryptor.crypto.rsa_hybrid import decrypt_with_rsa_aes


class DecryptTab(QtWidgets.QWidget):
    def __init__(self, parent=None, main_window=None):
        super().__init__(parent)
        self.main = main_window
        self.last_decrypted_bytes = None

        self._build_ui()
        self.refresh_private_keys()
        self.update_encrypted_mode()

    # ---------- UI ----------

    def _build_ui(self):
        layout = QtWidgets.QVBoxLayout(self)

        # Private key selection row
        priv_sel_row = QtWidgets.QHBoxLayout()
        self.private_key_combo = QtWidgets.QComboBox()
        self.private_key_combo.currentIndexChanged.connect(
            self.handle_private_combo_change
        )
        priv_sel_row.addWidget(QtWidgets.QLabel("Saved private key:"))
        priv_sel_row.addWidget(self.private_key_combo)
        priv_sel_row.addStretch()

        # Private key file row
        priv_row = QtWidgets.QHBoxLayout()
        self.priv_key_path_edit = QtWidgets.QLineEdit()
        self.priv_key_path_edit.setPlaceholderText(
            "Select RSA private key file (e.g. ~/.ssh/id_rsa)"
        )
        self.browse_priv_button = QtWidgets.QPushButton("Browse…")
        self.browse_priv_button.clicked.connect(self.browse_private_key_file)
        priv_row.addWidget(self.priv_key_path_edit)
        priv_row.addWidget(self.browse_priv_button)

        self.priv_password = QtWidgets.QLineEdit()
        self.priv_password.setPlaceholderText(
            "Private key password (leave empty if none)"
        )
        self.priv_password.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)

        # Encrypted input mode (Text / File)
        enc_mode_row = QtWidgets.QHBoxLayout()
        self.enc_mode_text = QtWidgets.QRadioButton("Text")
        self.enc_mode_file = QtWidgets.QRadioButton("File")
        self.enc_mode_text.setChecked(True)
        self.enc_mode_text.toggled.connect(self.update_encrypted_mode)
        enc_mode_row.addWidget(QtWidgets.QLabel("Encrypted input:"))
        enc_mode_row.addWidget(self.enc_mode_text)
        enc_mode_row.addWidget(self.enc_mode_file)
        enc_mode_row.addStretch()

        # Encrypted text area
        self.encrypted_input = QtWidgets.QPlainTextEdit()
        self.encrypted_input.setPlaceholderText("Paste encrypted JSON here")

        # Encrypted file picker
        enc_file_row = QtWidgets.QHBoxLayout()
        self.encrypted_file_path_edit = QtWidgets.QLineEdit()
        self.encrypted_file_path_edit.setPlaceholderText("Select encrypted JSON file")
        self.browse_encrypted_button = QtWidgets.QPushButton("Browse…")
        self.browse_encrypted_button.clicked.connect(self.browse_encrypted_file)
        enc_file_row.addWidget(self.encrypted_file_path_edit)
        enc_file_row.addWidget(self.browse_encrypted_button)

        # Buttons
        self.decrypt_button = QtWidgets.QPushButton("Decrypt")
        self.decrypt_button.clicked.connect(self.handle_decrypt)

        self.copy_decrypted_button = QtWidgets.QPushButton("Copy")
        self.copy_decrypted_button.clicked.connect(self.copy_decrypted_to_clipboard)

        self.save_decrypted_button = QtWidgets.QPushButton("Save")
        self.save_decrypted_button.clicked.connect(self.save_decrypted_to_file)

        top_btn_row = QtWidgets.QHBoxLayout()
        top_btn_row.addWidget(self.decrypt_button)
        top_btn_row.addStretch()

        bottom_btn_row = QtWidgets.QHBoxLayout()
        bottom_btn_row.addStretch()
        bottom_btn_row.addWidget(self.copy_decrypted_button)
        bottom_btn_row.addSpacing(10)
        bottom_btn_row.addWidget(self.save_decrypted_button)

        # Output
        self.decrypted_output = QtWidgets.QPlainTextEdit()
        self.decrypted_output.setPlaceholderText(
            "Decrypted plaintext will appear here (if UTF-8 text)"
        )
        self.decrypted_output.setReadOnly(True)

        layout.addLayout(priv_sel_row)
        layout.addWidget(QtWidgets.QLabel("Private key file"))
        layout.addLayout(priv_row)
        layout.addWidget(self.priv_password)
        layout.addLayout(enc_mode_row)
        layout.addWidget(self.encrypted_input)
        layout.addLayout(enc_file_row)
        layout.addLayout(top_btn_row)
        layout.addWidget(QtWidgets.QLabel("Decrypted plaintext (if any)"))
        layout.addWidget(self.decrypted_output)
        layout.addLayout(bottom_btn_row)

    # ---------- Key combo refresh ----------

    def refresh_private_keys(self):
        self.private_key_combo.blockSignals(True)
        self.private_key_combo.clear()
        self.private_key_combo.addItem("Manual entry", userData=None)

        if not self.main:
            self.private_key_combo.blockSignals(False)
            return

        for k in self.main.config.get("private_keys", []):
            self.private_key_combo.addItem(k["name"], userData=k["id"])

        self.private_key_combo.blockSignals(False)

    # ---------- Mode toggle ----------

    def update_encrypted_mode(self):
        is_text = self.enc_mode_text.isChecked()
        self.encrypted_input.setEnabled(is_text)
        self.encrypted_file_path_edit.setEnabled(not is_text)
        self.browse_encrypted_button.setEnabled(not is_text)

    # ---------- File dialogs ----------

    def browse_private_key_file(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Select RSA private key file",
            os.path.expanduser("~"),
            "All Files (*);;PEM/SSH Keys (*)",
        )
        if file_path:
            self.priv_key_path_edit.setText(file_path)

    def browse_encrypted_file(self):
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Select encrypted JSON file",
            os.path.expanduser("~"),
            "JSON Files (*.json);;All Files (*)",
        )
        if file_path:
            self.encrypted_file_path_edit.setText(file_path)

    # ---------- Handlers ----------

    def handle_private_combo_change(self, index: int):
        if not self.main:
            return
        key_id = self.private_key_combo.itemData(index)
        if not key_id:
            return  # manual
        pk = next(
            (k for k in self.main.config.get("private_keys", []) if k["id"] == key_id),
            None,
        )
        if pk:
            self.priv_key_path_edit.setText(pk["path"])

    def handle_decrypt(self):
        if not self.main:
            return

        key_path = self.priv_key_path_edit.text().strip()
        pwd = self.priv_password.text() or None

        if not key_path:
            self.main.show_toast("Private key file is required.", level="warning")
            return
        if not os.path.isfile(key_path):
            self.main.show_toast(
                f"Private key file not found: {key_path}", level="warning"
            )
            return

        try:
            with open(key_path, "r", encoding="utf-8") as f:
                priv_key_pem_str = f.read()
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "Error", f"Could not read private key file:\n{e}"
            )
            return

        # Encrypted JSON source
        if self.enc_mode_text.isChecked():
            enc = self.encrypted_input.toPlainText().strip()
            if not enc:
                self.main.show_toast(
                    "Encrypted JSON text is empty.", level="warning"
                )
                return
        else:
            path = self.encrypted_file_path_edit.text().strip()
            if not path:
                self.main.show_toast(
                    "Please select an encrypted JSON file.", level="warning"
                )
                return
            if not os.path.isfile(path):
                self.main.show_toast(f"File not found: {path}", level="warning")
                return
            try:
                with open(path, "r", encoding="utf-8") as f:
                    enc = f.read()
            except Exception as e:
                QtWidgets.QMessageBox.critical(
                    self, "Error", f"Could not read encrypted file:\n{e}"
                )
                return

        try:
            pt_bytes = decrypt_with_rsa_aes(priv_key_pem_str, enc, pwd)
            self.last_decrypted_bytes = pt_bytes

            try:
                text = pt_bytes.decode("utf-8")
                self.decrypted_output.setPlainText(text)
            except UnicodeDecodeError:
                self.decrypted_output.setPlainText(
                    "[Decrypted data is not valid UTF-8 text]\n"
                    "Use 'Save decrypted to file…' to save it."
                )

            self.main.show_toast("Decryption completed.", level="success")
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "Error", f"Decryption failed:\n{e}"
            )

    def save_decrypted_to_file(self):
        if self.last_decrypted_bytes is None:
            if self.main:
                self.main.show_toast(
                    "No decrypted data available. Decrypt something first.",
                    level="warning",
                )
            return

        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Save decrypted data",
            os.path.expanduser("~"),
            "All Files (*)",
        )
        if not file_path:
            return

        try:
            with open(file_path, "wb") as f:
                f.write(self.last_decrypted_bytes)
            if self.main:
                self.main.show_toast("Decrypted data saved.", level="success")
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "Error", f"Could not save decrypted file:\n{e}"
            )

    def copy_decrypted_to_clipboard(self):
        if self.last_decrypted_bytes is None:
            if self.main:
                self.main.show_toast(
                    "No decrypted data available. Decrypt something first.",
                    level="warning",
                )
            return

        try:
            text = self.last_decrypted_bytes.decode("utf-8")
        except UnicodeDecodeError:
            if self.main:
                self.main.show_toast(
                    "Decrypted data is binary and cannot be copied as text. Save to a file instead.",
                    level="warning",
                )
            return

        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.setText(text)

        if self.main:
            self.main.show_toast(
                "Decrypted text copied to clipboard.",
                level="success",
            )
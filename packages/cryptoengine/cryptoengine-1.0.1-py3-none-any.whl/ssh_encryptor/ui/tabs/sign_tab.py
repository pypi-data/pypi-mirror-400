"""
CryptoEngine™ - Secure Encryption & Signing Toolkit
Copyright (c) 2025
Harshana Chathuranga / Bitrate Solutions (Pvt) Ltd.
Licensed under the MIT License — see LICENSE for details.
CryptoEngine™ name is trademarked — see TRADEMARK.md.
"""
import os
from PyQt6 import QtWidgets, QtCore

from ssh_encryptor.crypto.sign_utils import (
    sign_detached_rsa,
    verify_detached_rsa,
    SignatureError,
)


class SignTab(QtWidgets.QWidget):
    def __init__(self, parent=None, main_window=None):
        super().__init__(parent)
        self.main = main_window

        self.last_signature_json = None

        self._build_ui()
        self.refresh_key_combos()

    # ---------- UI ----------

    def _build_ui(self):
        main_layout = QtWidgets.QHBoxLayout(self)

        # Left: SIGN
        sign_group = QtWidgets.QGroupBox("Sign")
        sign_layout = QtWidgets.QVBoxLayout(sign_group)

        # Private key selection
        priv_sel_row = QtWidgets.QHBoxLayout()
        self.sign_private_key_combo = QtWidgets.QComboBox()
        self.sign_private_key_combo.currentIndexChanged.connect(
            self.handle_sign_private_combo_change 
        )
        priv_sel_row.addWidget(QtWidgets.QLabel("Saved private key:"))
        priv_sel_row.addWidget(self.sign_private_key_combo)
        priv_sel_row.addStretch()

        # Private key file
        priv_row = QtWidgets.QHBoxLayout()
        self.sign_priv_path_edit = QtWidgets.QLineEdit()
        self.sign_priv_path_edit.setPlaceholderText(
            "Select RSA private key file (e.g. ~/.ssh/id_rsa)"
        )
        self.sign_browse_priv_btn = QtWidgets.QPushButton("Browse…")
        self.sign_browse_priv_btn.clicked.connect(self.browse_sign_private_key)
        priv_row.addWidget(self.sign_priv_path_edit)
        priv_row.addWidget(self.sign_browse_priv_btn)

        self.sign_priv_password = QtWidgets.QLineEdit()
        self.sign_priv_password.setPlaceholderText(
            "Private key password (leave empty if none)"
        )
        self.sign_priv_password.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)

        # Data input mode (text/file)
        data_mode_row = QtWidgets.QHBoxLayout()
        self.sign_mode_text = QtWidgets.QRadioButton("Text")
        self.sign_mode_file = QtWidgets.QRadioButton("File")
        self.sign_mode_text.setChecked(True)
        self.sign_mode_text.toggled.connect(self.update_sign_input_mode)
        data_mode_row.addWidget(QtWidgets.QLabel("Data to sign:"))
        data_mode_row.addWidget(self.sign_mode_text)
        data_mode_row.addWidget(self.sign_mode_file)
        data_mode_row.addStretch()

        # Text area
        self.sign_text_edit = QtWidgets.QPlainTextEdit()
        self.sign_text_edit.setPlaceholderText("Type or paste text to sign")

        # File row
        sign_file_row = QtWidgets.QHBoxLayout()
        self.sign_file_path_edit = QtWidgets.QLineEdit()
        self.sign_file_path_edit.setPlaceholderText("Select file to sign")
        self.sign_browse_file_btn = QtWidgets.QPushButton("Browse…")
        self.sign_browse_file_btn.clicked.connect(self.browse_sign_file)
        sign_file_row.addWidget(self.sign_file_path_edit)
        sign_file_row.addWidget(self.sign_browse_file_btn)

        # Buttons
        self.sign_button = QtWidgets.QPushButton("Sign")
        self.sign_button.clicked.connect(self.handle_sign)

        self.sign_copy_btn = QtWidgets.QPushButton("Copy signature")
        self.sign_copy_btn.clicked.connect(self.copy_signature)

        self.sign_save_btn = QtWidgets.QPushButton("Save signature")
        self.sign_save_btn.clicked.connect(self.save_signature)

        sign_btn_row = QtWidgets.QHBoxLayout()
        sign_btn_row.addWidget(self.sign_button)
        sign_btn_row.addStretch()
        sign_btn_row.addWidget(self.sign_copy_btn)
        sign_btn_row.addSpacing(10)
        sign_btn_row.addWidget(self.sign_save_btn)

        # Signature output
        self.sign_output = QtWidgets.QPlainTextEdit()
        self.sign_output.setReadOnly(True)
        self.sign_output.setPlaceholderText("Signature JSON will appear here")

        sign_layout.addLayout(priv_sel_row)
        sign_layout.addWidget(QtWidgets.QLabel("Private key file"))
        sign_layout.addLayout(priv_row)
        sign_layout.addWidget(self.sign_priv_password)
        sign_layout.addLayout(data_mode_row)
        sign_layout.addWidget(self.sign_text_edit)
        sign_layout.addLayout(sign_file_row)
        sign_layout.addLayout(sign_btn_row)
        sign_layout.addWidget(QtWidgets.QLabel("Signature JSON"))
        sign_layout.addWidget(self.sign_output)

        # Right: VERIFY
        verify_group = QtWidgets.QGroupBox("Verify")
        verify_layout = QtWidgets.QVBoxLayout(verify_group)

        # Public key selection
        pub_sel_row = QtWidgets.QHBoxLayout()
        self.verify_public_key_combo = QtWidgets.QComboBox()
        self.verify_public_key_combo.currentIndexChanged.connect(
            self.handle_verify_public_combo_change
        )
        pub_sel_row.addWidget(QtWidgets.QLabel("Saved public key:"))
        pub_sel_row.addWidget(self.verify_public_key_combo)
        pub_sel_row.addStretch()

        self.verify_pub_key_edit = QtWidgets.QPlainTextEdit()
        self.verify_pub_key_edit.setPlaceholderText(
            "Paste or auto-load RSA SSH PUBLIC key (ssh-rsa AAAA...)"
        )

        # Data input mode (text/file)
        vdata_mode_row = QtWidgets.QHBoxLayout()
        self.verify_data_mode_text = QtWidgets.QRadioButton("Text")
        self.verify_data_mode_file = QtWidgets.QRadioButton("File")
        self.verify_data_mode_text.setChecked(True)
        self.verify_data_mode_text.toggled.connect(self.update_verify_data_mode)
        vdata_mode_row.addWidget(QtWidgets.QLabel("Signed data:"))
        vdata_mode_row.addWidget(self.verify_data_mode_text)
        vdata_mode_row.addWidget(self.verify_data_mode_file)
        vdata_mode_row.addStretch()

        self.verify_data_text = QtWidgets.QPlainTextEdit()
        self.verify_data_text.setPlaceholderText("Type or paste the signed text")

        vdata_file_row = QtWidgets.QHBoxLayout()
        self.verify_data_file_path = QtWidgets.QLineEdit()
        self.verify_data_file_path.setPlaceholderText("Select signed data file")
        self.verify_browse_data_btn = QtWidgets.QPushButton("Browse…")
        self.verify_browse_data_btn.clicked.connect(self.browse_verify_data_file)
        vdata_file_row.addWidget(self.verify_data_file_path)
        vdata_file_row.addWidget(self.verify_browse_data_btn)

        # Signature input mode (text/file)
        vsig_mode_row = QtWidgets.QHBoxLayout()
        self.verify_sig_mode_text = QtWidgets.QRadioButton("Text")
        self.verify_sig_mode_file = QtWidgets.QRadioButton("File")
        self.verify_sig_mode_text.setChecked(True)
        self.verify_sig_mode_text.toggled.connect(self.update_verify_sig_mode)
        vsig_mode_row.addWidget(QtWidgets.QLabel("Signature JSON:"))
        vsig_mode_row.addWidget(self.verify_sig_mode_text)
        vsig_mode_row.addWidget(self.verify_sig_mode_file)
        vsig_mode_row.addStretch()

        self.verify_sig_text = QtWidgets.QPlainTextEdit()
        self.verify_sig_text.setPlaceholderText("Paste signature JSON here")

        vsig_file_row = QtWidgets.QHBoxLayout()
        self.verify_sig_file_path = QtWidgets.QLineEdit()
        self.verify_sig_file_path.setPlaceholderText("Select signature JSON file")
        self.verify_browse_sig_btn = QtWidgets.QPushButton("Browse…")
        self.verify_browse_sig_btn.clicked.connect(self.browse_verify_sig_file)
        vsig_file_row.addWidget(self.verify_sig_file_path)
        vsig_file_row.addWidget(self.verify_browse_sig_btn)

        # Verify button + status
        self.verify_button = QtWidgets.QPushButton("Verify")
        self.verify_button.clicked.connect(self.handle_verify)

        self.verify_status_label = QtWidgets.QLabel("Status: Not verified yet")
        self.verify_status_label.setStyleSheet("color: #cccccc;")

        verify_btn_row = QtWidgets.QHBoxLayout()
        verify_btn_row.addWidget(self.verify_button)
        verify_btn_row.addStretch()
        verify_btn_row.addWidget(self.verify_status_label)

        verify_layout.addLayout(pub_sel_row)
        verify_layout.addWidget(QtWidgets.QLabel("Public key (editable)"))
        verify_layout.addWidget(self.verify_pub_key_edit)
        verify_layout.addLayout(vdata_mode_row)
        verify_layout.addWidget(self.verify_data_text)
        verify_layout.addLayout(vdata_file_row)
        verify_layout.addLayout(vsig_mode_row)
        verify_layout.addWidget(self.verify_sig_text)
        verify_layout.addLayout(vsig_file_row)
        verify_layout.addLayout(verify_btn_row)

        main_layout.addWidget(sign_group, stretch=1)
        main_layout.addWidget(verify_group, stretch=1)

        self.update_sign_input_mode()
        self.update_verify_data_mode()
        self.update_verify_sig_mode()

    # ---------- Key combo refresh ----------

    def refresh_key_combos(self):
        if not self.main:
            return
        cfg = self.main.config

        # Signing: private keys
        self.sign_private_key_combo.blockSignals(True)
        self.sign_private_key_combo.clear()
        self.sign_private_key_combo.addItem("Manual entry", userData=None)
        for k in cfg.get("private_keys", []):
            self.sign_private_key_combo.addItem(k["name"], userData=k["id"])
        self.sign_private_key_combo.blockSignals(False)

        # Verify: public keys
        self.verify_public_key_combo.blockSignals(True)
        self.verify_public_key_combo.clear()
        self.verify_public_key_combo.addItem("Manual entry", userData=None)
        for k in cfg.get("public_keys", []):
            self.verify_public_key_combo.addItem(k["name"], userData=k["id"])
        self.verify_public_key_combo.blockSignals(False)

    # ---------- Mode toggles ----------

    def update_sign_input_mode(self):
        is_text = self.sign_mode_text.isChecked()
        self.sign_text_edit.setEnabled(is_text)
        self.sign_file_path_edit.setEnabled(not is_text)
        self.sign_browse_file_btn.setEnabled(not is_text)

    def update_verify_data_mode(self):
        is_text = self.verify_data_mode_text.isChecked()
        self.verify_data_text.setEnabled(is_text)
        self.verify_data_file_path.setEnabled(not is_text)
        self.verify_browse_data_btn.setEnabled(not is_text)

    def update_verify_sig_mode(self):
        is_text = self.verify_sig_mode_text.isChecked()
        self.verify_sig_text.setEnabled(is_text)
        self.verify_sig_file_path.setEnabled(not is_text)
        self.verify_browse_sig_btn.setEnabled(not is_text)

    # ---------- File dialogs ----------

    def browse_sign_private_key(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Select RSA private key file",
            os.path.expanduser("~"),
            "All Files (*);;PEM/SSH Keys (*)",
        )
        if path:
            self.sign_priv_path_edit.setText(path)

    def browse_sign_file(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Select file to sign",
            os.path.expanduser("~"),
            "All Files (*)",
        )
        if path:
            self.sign_file_path_edit.setText(path)

    def browse_verify_data_file(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Select signed data file",
            os.path.expanduser("~"),
            "All Files (*)",
        )
        if path:
            self.verify_data_file_path.setText(path)

    def browse_verify_sig_file(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Select signature JSON file",
            os.path.expanduser("~"),
            "JSON Files (*.json);;All Files (*)",
        )
        if path:
            self.verify_sig_file_path.setText(path)

    # ---------- Combo change ----------

    def handle_verify_public_combo_change(self, index: int):
        if not self.main:
            return
        key_id = self.verify_public_key_combo.itemData(index)
        if not key_id:
            return  # manual
        pk = next(
            (k for k in self.main.config.get("public_keys", []) if k["id"] == key_id),
            None,
        )
        if pk:
            self.verify_pub_key_edit.setPlainText(pk["data"])

    def handle_sign_private_combo_change(self, index: int):
        """
        When user selects a saved private key in the Sign panel,
        auto-fill the private key file path textbox.
        """
        if not self.main:
            return

        key_id = self.sign_private_key_combo.itemData(index)
        if not key_id:
            return  # "Manual entry"

        pk = next(
            (k for k in self.main.config.get("private_keys", [])
             if k["id"] == key_id),
            None,
        )
        if pk:
            self.sign_priv_path_edit.setText(pk["path"])
    # ---------- Sign logic ----------

    def handle_sign(self):
        if not self.main:
            return

        # Private key file
        key_path = self.sign_priv_path_edit.text().strip()
        pwd = self.sign_priv_password.text() or None

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
                priv_pem = f.read()
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "Error", f"Could not read private key file:\n{e}"
            )
            return

        # Data
        if self.sign_mode_text.isChecked():
            text = self.sign_text_edit.toPlainText()
            if not text:
                self.main.show_toast("No text to sign.", level="warning")
                return
            data = text.encode("utf-8")
        else:
            path = self.sign_file_path_edit.text().strip()
            if not path:
                self.main.show_toast("Please select a file to sign.", level="warning")
                return
            if not os.path.isfile(path):
                self.main.show_toast(f"File not found: {path}", level="warning")
                return
            try:
                with open(path, "rb") as f:
                    data = f.read()
            except Exception as e:
                QtWidgets.QMessageBox.critical(
                    self, "Error", f"Could not read file:\n{e}"
                )
                return

        # Sign
        try:
            sig_json = sign_detached_rsa(priv_pem, pwd, data)
        except SignatureError as e:
            QtWidgets.QMessageBox.critical(self, "Error", str(e))
            return

        self.last_signature_json = sig_json
        self.sign_output.setPlainText(sig_json)
        self.main.show_toast("Signature created.", level="success")

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

        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Save signature JSON",
            os.path.expanduser("~"),
            "JSON Files (*.json);;All Files (*)",
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.last_signature_json)
            if self.main:
                self.main.show_toast("Signature saved.", level="success")
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "Error", f"Could not save signature:\n{e}"
            )

    # ---------- Verify logic ----------

    def handle_verify(self):
        if not self.main:
            return

        # Public key
        pub = self.verify_pub_key_edit.toPlainText().strip()
        if not pub:
            self.main.show_toast("Public key is required.", level="warning")
            return

        # Data
        if self.verify_data_mode_text.isChecked():
            text = self.verify_data_text.toPlainText()
            if not text:
                self.main.show_toast("Signed data text is empty.", level="warning")
                return
            data = text.encode("utf-8")
        else:
            path = self.verify_data_file_path.text().strip()
            if not path:
                self.main.show_toast(
                    "Please select the signed data file.", level="warning"
                )
                return
            if not os.path.isfile(path):
                self.main.show_toast(f"File not found: {path}", level="warning")
                return
            try:
                with open(path, "rb") as f:
                    data = f.read()
            except Exception as e:
                QtWidgets.QMessageBox.critical(
                    self, "Error", f"Could not read data file:\n{e}"
                )
                return

        # Signature
        if self.verify_sig_mode_text.isChecked():
            sig_json = self.verify_sig_text.toPlainText().strip()
            if not sig_json:
                self.main.show_toast("Signature JSON text is empty.", level="warning")
                return
        else:
            path = self.verify_sig_file_path.text().strip()
            if not path:
                self.main.show_toast(
                    "Please select a signature JSON file.", level="warning"
                )
                return
            if not os.path.isfile(path):
                self.main.show_toast(f"File not found: {path}", level="warning")
                return
            try:
                with open(path, "r", encoding="utf-8") as f:
                    sig_json = f.read()
            except Exception as e:
                QtWidgets.QMessageBox.critical(
                    self, "Error", f"Could not read signature file:\n{e}"
                )
                return

        # Verify
        try:
            ok = verify_detached_rsa(pub, data, sig_json)
        except SignatureError as e:
            QtWidgets.QMessageBox.critical(self, "Error", str(e))
            self._set_status("Error", color="#ff5555")
            return

        if ok:
            self._set_status("VALID", color="#1b5e20")
            self.main.show_toast("Signature is VALID.", level="success")
        else:
            self._set_status("INVALID", color="#b71c1c")
            self.main.show_toast("Signature is INVALID.", level="error")

    def _set_status(self, text: str, color: str):
        self.verify_status_label.setText(f"Status: {text}")
        self.verify_status_label.setStyleSheet(f"color: {color};")
"""
CryptoEngine™ - Secure Encryption & Signing Toolkit
Copyright (c) 2025
Harshana Chathuranga / Bitrate Solutions (Pvt) Ltd.
Licensed under the MIT License — see LICENSE for details.
CryptoEngine™ name is trademarked — see TRADEMARK.md.
"""
import os
from PyQt6 import QtWidgets

from ssh_encryptor.crypto.hash_utils import SUPPORTED_HASHES, compute_hash


class HashingTab(QtWidgets.QWidget):
    def __init__(self, parent=None, main_window=None):
        super().__init__(parent)
        self.main = main_window

        self._build_ui()
        self.update_hash_input_mode()

    # ---------- UI ----------

    def _build_ui(self):
        layout = QtWidgets.QVBoxLayout(self)

        # Algorithm row
        algo_row = QtWidgets.QHBoxLayout()
        self.hash_algo_combo = QtWidgets.QComboBox()
        for display_name in SUPPORTED_HASHES.keys():
            self.hash_algo_combo.addItem(display_name)
        self.hash_algo_combo.setCurrentText("SHA-256")

        algo_row.addWidget(QtWidgets.QLabel("Algorithm:"))
        algo_row.addWidget(self.hash_algo_combo)
        algo_row.addStretch()

        # Input mode
        mode_row = QtWidgets.QHBoxLayout()
        self.hash_mode_text = QtWidgets.QRadioButton("Text")
        self.hash_mode_file = QtWidgets.QRadioButton("File")
        self.hash_mode_text.setChecked(True)
        self.hash_mode_text.toggled.connect(self.update_hash_input_mode)
        mode_row.addWidget(QtWidgets.QLabel("Input:"))
        mode_row.addWidget(self.hash_mode_text)
        mode_row.addWidget(self.hash_mode_file)
        mode_row.addStretch()

        # Text input
        self.hash_text_edit = QtWidgets.QPlainTextEdit()
        self.hash_text_edit.setPlaceholderText("Type or paste text to hash")

        # File input row
        file_row = QtWidgets.QHBoxLayout()
        self.hash_file_path_edit = QtWidgets.QLineEdit()
        self.hash_file_path_edit.setPlaceholderText("Select file to hash")
        self.hash_browse_button = QtWidgets.QPushButton("Browse…")
        self.hash_browse_button.clicked.connect(self.browse_hash_file)
        file_row.addWidget(self.hash_file_path_edit)
        file_row.addWidget(self.hash_browse_button)

        # Hash button
        self.hash_button = QtWidgets.QPushButton("Hash")
        self.hash_button.clicked.connect(self.handle_hash)

        # Outputs
        self.hash_hex_edit = QtWidgets.QLineEdit()
        self.hash_hex_edit.setReadOnly(True)
        self.hash_hex_edit.setPlaceholderText("Hex digest")

        self.hash_b64_edit = QtWidgets.QLineEdit()
        self.hash_b64_edit.setReadOnly(True)
        self.hash_b64_edit.setPlaceholderText("Base64 digest")

        # Copy buttons (right-aligned)
        hex_btn_row = QtWidgets.QHBoxLayout()
        self.hash_copy_hex_btn = QtWidgets.QPushButton("Copy hex")
        self.hash_copy_hex_btn.clicked.connect(self.copy_hash_hex)
        hex_btn_row.addStretch()
        hex_btn_row.addWidget(self.hash_copy_hex_btn)

        b64_btn_row = QtWidgets.QHBoxLayout()
        self.hash_copy_b64_btn = QtWidgets.QPushButton("Copy base64")
        self.hash_copy_b64_btn.clicked.connect(self.copy_hash_b64)
        b64_btn_row.addStretch()
        b64_btn_row.addWidget(self.hash_copy_b64_btn)

        # Assemble layout
        layout.addLayout(algo_row)
        layout.addLayout(mode_row)
        layout.addWidget(self.hash_text_edit)
        layout.addLayout(file_row)
        layout.addWidget(self.hash_button)
        layout.addWidget(QtWidgets.QLabel("Hex digest"))
        layout.addWidget(self.hash_hex_edit)
        layout.addLayout(hex_btn_row)
        layout.addWidget(QtWidgets.QLabel("Base64 digest"))
        layout.addWidget(self.hash_b64_edit)
        layout.addLayout(b64_btn_row)

    # ---------- Mode toggle ----------

    def update_hash_input_mode(self):
        is_text = self.hash_mode_text.isChecked()
        self.hash_text_edit.setEnabled(is_text)
        self.hash_file_path_edit.setEnabled(not is_text)
        self.hash_browse_button.setEnabled(not is_text)

    # ---------- File dialog ----------

    def browse_hash_file(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Select file to hash",
            os.path.expanduser("~"),
            "All Files (*)",
        )
        if path:
            self.hash_file_path_edit.setText(path)

    # ---------- Hashing ----------

    def handle_hash(self):
        algo_display = self.hash_algo_combo.currentText()

        # Get data
        if self.hash_mode_text.isChecked():
            text = self.hash_text_edit.toPlainText()
            if not text:
                if self.main:
                    self.main.show_toast("Input text is empty.", level="warning")
                return
            data = text.encode("utf-8")
        else:
            path = self.hash_file_path_edit.text().strip()
            if not path:
                if self.main:
                    self.main.show_toast("Please select a file to hash.", level="warning")
                return
            if not os.path.isfile(path):
                if self.main:
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

        try:
            result = compute_hash(data, algo_display)
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "Error", f"Hashing failed:\n{e}"
            )
            return

        self.hash_hex_edit.setText(result["hex"])
        self.hash_b64_edit.setText(result["b64"])
        if self.main:
            self.main.show_toast("Hash computed.", level="success")

    def copy_hash_hex(self):
        text = self.hash_hex_edit.text().strip()
        if not text:
            if self.main:
                self.main.show_toast("Hex digest is empty.", level="warning")
            return
        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.setText(text)
        if self.main:
            self.main.show_toast("Hex digest copied.", level="success")

    def copy_hash_b64(self):
        text = self.hash_b64_edit.text().strip()
        if not text:
            if self.main:
                self.main.show_toast("Base64 digest is empty.", level="warning")
            return
        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.setText(text)
        if self.main:
            self.main.show_toast("Base64 digest copied.", level="success")
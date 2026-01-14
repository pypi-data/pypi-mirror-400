"""
CryptoEngine™ - Secure Encryption & Signing Toolkit
Copyright (c) 2025
Harshana Chathuranga / Bitrate Solutions (Pvt) Ltd.
Licensed under the MIT License — see LICENSE for details.
CryptoEngine™ name is trademarked — see TRADEMARK.md.
"""
from PyQt6 import QtWidgets
import os


class PublicKeyDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, name="", data=""):
        super().__init__(parent)
        self.setWindowTitle("Public Key")
        self.resize(600, 400)

        layout = QtWidgets.QVBoxLayout(self)

        self.name_edit = QtWidgets.QLineEdit()
        self.name_edit.setPlaceholderText("Key name (e.g. 'Production server')")
        self.name_edit.setText(name)

        self.data_edit = QtWidgets.QPlainTextEdit()
        self.data_edit.setPlaceholderText("Paste ssh-rsa PUBLIC key line here")
        self.data_edit.setPlainText(data)

        load_btn = QtWidgets.QPushButton("Load from file…")
        load_btn.clicked.connect(self.load_from_file)

        btn_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Ok |
            QtWidgets.QDialogButtonBox.StandardButton.Cancel
        )
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)

        layout.addWidget(QtWidgets.QLabel("Name"))
        layout.addWidget(self.name_edit)
        layout.addWidget(QtWidgets.QLabel("Public key data"))
        layout.addWidget(self.data_edit)
        layout.addWidget(load_btn)
        layout.addWidget(btn_box)

    def load_from_file(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Select public key file",
            os.path.expanduser("~"),
            "All Files (*)",
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                self.data_edit.setPlainText(f.read().strip())
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"Could not read file:\n{e}")

    def get_values(self):
        return self.name_edit.text().strip(), self.data_edit.toPlainText().strip()

    def accept(self):
        name, data = self.get_values()
        if not name or not data:
            QtWidgets.QMessageBox.warning(
                self, "Missing data", "Name and public key are required."
            )
            return
        super().accept()


class PrivateKeyDialog(QtWidgets.QDialog):
    def __init__(self, parent=None, name="", path=""):
        super().__init__(parent)
        self.setWindowTitle("Private Key")
        self.resize(600, 150)

        layout = QtWidgets.QVBoxLayout(self)

        self.name_edit = QtWidgets.QLineEdit()
        self.name_edit.setPlaceholderText("Key name (e.g. 'My laptop key')")
        self.name_edit.setText(name)

        row = QtWidgets.QHBoxLayout()
        self.path_edit = QtWidgets.QLineEdit()
        self.path_edit.setPlaceholderText(
            "Path to private key file (e.g. ~/.ssh/id_rsa)"
        )
        self.path_edit.setText(path)
        browse_btn = QtWidgets.QPushButton("Browse…")
        browse_btn.clicked.connect(self.browse_file)

        row.addWidget(self.path_edit)
        row.addWidget(browse_btn)

        btn_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Ok |
            QtWidgets.QDialogButtonBox.StandardButton.Cancel
        )
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)

        layout.addWidget(QtWidgets.QLabel("Name"))
        layout.addWidget(self.name_edit)
        layout.addWidget(QtWidgets.QLabel("Private key file"))
        layout.addLayout(row)
        layout.addWidget(btn_box)

    def browse_file(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Select private key file",
            os.path.expanduser("~"),
            "All Files (*)",
        )
        if path:
            self.path_edit.setText(path)

    def get_values(self):
        return self.name_edit.text().strip(), self.path_edit.text().strip()

    def accept(self):
        name, path = self.get_values()
        if not name or not path:
            QtWidgets.QMessageBox.warning(
                self, "Missing data", "Name and private key file are required."
            )
            return
        super().accept()


class GenerateKeypairDialog(QtWidgets.QDialog):
    """
    Dialog to collect parameters for keypair generation.
    - key name
    - key size
    - optional passphrase
    - target private-key file path
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Generate RSA SSH Key Pair")
        self.resize(600, 250)

        layout = QtWidgets.QVBoxLayout(self)

        # Name
        self.name_edit = QtWidgets.QLineEdit()
        self.name_edit.setPlaceholderText("Key name (e.g. 'New RSA key')")

        # Key size
        size_row = QtWidgets.QHBoxLayout()
        self.size_combo = QtWidgets.QComboBox()
        for size in (2048, 3072, 4096):
            self.size_combo.addItem(str(size), userData=size)
        self.size_combo.setCurrentIndex(2)  # 4096 by default
        size_row.addWidget(QtWidgets.QLabel("Key size:"))
        size_row.addWidget(self.size_combo)
        size_row.addStretch()

        # Passphrase
        self.passphrase_edit = QtWidgets.QLineEdit()
        self.passphrase_edit.setPlaceholderText("Passphrase for private key (optional)")
        self.passphrase_edit.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)

        self.passphrase_confirm_edit = QtWidgets.QLineEdit()
        self.passphrase_confirm_edit.setPlaceholderText("Confirm passphrase")
        self.passphrase_confirm_edit.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)

        # Private key file path
        path_row = QtWidgets.QHBoxLayout()
        self.path_edit = QtWidgets.QLineEdit()
        self.path_edit.setPlaceholderText("Save private key as (e.g. ~/.ssh/id_rsa_cryptoengine)")
        browse_btn = QtWidgets.QPushButton("Browse…")
        browse_btn.clicked.connect(self.browse_file)
        path_row.addWidget(self.path_edit)
        path_row.addWidget(browse_btn)

        # Buttons
        btn_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Ok |
            QtWidgets.QDialogButtonBox.StandardButton.Cancel
        )
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)

        layout.addWidget(QtWidgets.QLabel("Key name"))
        layout.addWidget(self.name_edit)
        layout.addLayout(size_row)
        layout.addWidget(QtWidgets.QLabel("Private key passphrase (optional)"))
        layout.addWidget(self.passphrase_edit)
        layout.addWidget(self.passphrase_confirm_edit)
        layout.addWidget(QtWidgets.QLabel("Private key file path"))
        layout.addLayout(path_row)
        layout.addWidget(btn_box)

    def browse_file(self):
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Save private key as",
            os.path.expanduser("~/.ssh"),
            "All Files (*)",
        )
        if path:
            self.path_edit.setText(path)

    def get_values(self):
        name = self.name_edit.text().strip()
        idx = self.size_combo.currentIndex()
        key_size = self.size_combo.itemData(idx)
        path = self.path_edit.text().strip()
        passphrase = self.passphrase_edit.text()
        passphrase_confirm = self.passphrase_confirm_edit.text()
        return {
            "name": name,
            "key_size": key_size,
            "path": path,
            "passphrase": passphrase,
            "passphrase_confirm": passphrase_confirm,
        }

    def accept(self):
        vals = self.get_values()
        if not vals["name"]:
            QtWidgets.QMessageBox.warning(self, "Missing data", "Key name is required.")
            return
        if not vals["path"]:
            QtWidgets.QMessageBox.warning(
                self,
                "Missing data",
                "Please choose where to save the private key.",
            )
            return
        if vals["passphrase"] != vals["passphrase_confirm"]:
            QtWidgets.QMessageBox.warning(
                self,
                "Passphrases differ",
                "Passphrase and confirmation do not match.",
            )
            return
        super().accept()
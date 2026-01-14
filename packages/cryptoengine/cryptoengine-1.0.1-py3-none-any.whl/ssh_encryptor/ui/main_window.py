"""
CryptoEngine™ - Secure Encryption & Signing Toolkit
Copyright (c) 2025
Harshana Chathuranga / Bitrate Solutions (Pvt) Ltd.
Licensed under the MIT License — see LICENSE for details.
CryptoEngine™ name is trademarked — see TRADEMARK.md.
"""
import os

from PyQt6 import QtWidgets
from PyQt6.QtGui import QIcon

from ssh_encryptor.keys.storage import load_config
from ssh_encryptor.ui.toast import ToastNotification

from ssh_encryptor.ui.tabs.encrypt_tab import EncryptTab
from ssh_encryptor.ui.tabs.decrypt_tab import DecryptTab
from ssh_encryptor.ui.tabs.keys_tab import KeysTab
from ssh_encryptor.ui.tabs.hashing_tab import HashingTab
from ssh_encryptor.ui.tabs.sign_tab import SignTab
from ssh_encryptor.ui.tabs.about_tab import AboutTab


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        # Icon
        assets_path = os.path.join(os.path.dirname(__file__), "..", "assets")
        icon_path = os.path.join(assets_path, "icon.icns")
        if not os.path.exists(icon_path):
            icon_path = os.path.join(assets_path, "icon.png")
        self.setWindowIcon(QIcon(icon_path))

        self.setWindowTitle("CryptoEngine")
        self.resize(1000, 700)

        # Shared config
        self.config = load_config()

        # Central tab widget
        tabs = QtWidgets.QTabWidget()
        self.setCentralWidget(tabs)

        # Create tab widgets (each gets a reference back to this MainWindow)
        self.hashing_tab = HashingTab(parent=self, main_window=self)
        self.encrypt_tab = EncryptTab(parent=self, main_window=self)
        self.decrypt_tab = DecryptTab(parent=self, main_window=self)
        self.sign_tab = SignTab(parent=self, main_window=self)
        self.keys_tab = KeysTab(parent=self, main_window=self)
        self.about_tab = AboutTab(parent=self, main_window=self)


        tabs.addTab(self.hashing_tab, "Hashing")
        tabs.addTab(self.encrypt_tab, "Encrypt")
        tabs.addTab(self.decrypt_tab, "Decrypt")
        tabs.addTab(self.sign_tab, "Signature Verify")
        tabs.addTab(self.keys_tab, "Key Manager")
        tabs.addTab(self.about_tab, "About")

        # Initial population of key lists/combos
        self.refresh_keys_everywhere()

    # ---------- Toast helper ----------

    def show_toast(self, message: str, level: str = "info", duration_ms: int = 3000):
        """
        Show a non-blocking toast notification.
        level: "info", "success", "warning", "error"
        """
        ToastNotification(self, message, level=level, duration_ms=duration_ms)

    # ---------- Cross-tab key refresh ----------

    def refresh_keys_everywhere(self):
        """
        Called whenever config['public_keys'] or ['private_keys'] changes.
        Keeps key manager + encrypt/decrypt combos in sync.
        """
        self.keys_tab.refresh_key_lists()
        self.encrypt_tab.refresh_public_keys()
        self.encrypt_tab.refresh_private_keys()
        self.decrypt_tab.refresh_private_keys()
        self.sign_tab.refresh_key_combos()
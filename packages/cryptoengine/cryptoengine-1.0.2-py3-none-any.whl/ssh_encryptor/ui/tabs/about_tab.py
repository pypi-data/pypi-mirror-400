"""
CryptoEngine™ - Secure Encryption & Signing Toolkit
Copyright (c) 2025
Harshana Chathuranga / Bitrate Solutions (Pvt) Ltd.
Licensed under the MIT License — see LICENSE for details.
CryptoEngine™ name is trademarked — see TRADEMARK.md.
"""
import os
from PyQt6 import QtWidgets, QtGui, QtCore


class AboutTab(QtWidgets.QWidget):
    def __init__(self, parent=None, main_window=None):
        super().__init__(parent)
        self.main = main_window
        self._build_ui()

    def _build_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)

        #
        # --- APP ICON (top) ---
        #
        icon_path = os.path.join(
            os.path.dirname(__file__),
            "..", "..", "assets", "icon.png"
        )
        self.app_icon_label = QtWidgets.QLabel()
        if os.path.exists(icon_path):
            pix = QtGui.QPixmap(icon_path)
            pix = pix.scaled(
                140, 140,
                QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                QtCore.Qt.TransformationMode.SmoothTransformation
            )
            self.app_icon_label.setPixmap(pix)
        else:
            self.app_icon_label.setText("[icon.png missing]")
        self.app_icon_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.app_icon_label.setStyleSheet("margin-top: 16px")

        #
        # --- TEXT HEADER ---
        #
        title = QtWidgets.QLabel("CryptoEngine")
        title.setStyleSheet("font-size: 22px; font-weight: bold;")
        title.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        subtitle = QtWidgets.QLabel("Secure encryption, signing & verification")
        subtitle.setStyleSheet("font-size: 14px; color: #cccccc;")
        subtitle.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        # Description
        desc = QtWidgets.QLabel(
            "CryptoEngine enhances secure sharing of sensitive information across networks.\n"
            "Recommended for Students, Developers, Security Professionals, and Cybersecurity Enthusiasts.\n\n"
            "Features include:\n"
            "• RSA Hybrid Encryption (AES + SSH keys)\n"
            "• Decryption using stored or manual keys\n"
            "• Detached digital signatures + verification\n"
            "• File & text hashing (SHA, MD5, etc)\n"
            "• SSH keypair generator + key manager\n"
        )
        desc.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        desc.setWordWrap(True)

        # Descrption sub
        desc_sub = QtWidgets.QLabel(
            "Keep your secrets safe with CryptoEngine.\n"
        )
        desc_sub.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        desc_sub.setStyleSheet("font-size: 14px; color: #cccccc;")
        desc_sub.setWordWrap(True)

        #
        # Divider line
        #
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        line.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)

        #
        # --- VERSION ---
        #
        version = QtWidgets.QLabel(f"Version 1.0.2")
        version.setStyleSheet("font-size: 12px; color: #cccccc;")
        version.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        #
        # --- DEVELOPER SECTION ---
        #
        author_label = QtWidgets.QLabel("Developed by:")
        author_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        author_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        name_label = QtWidgets.QLabel("@wmhchathuranga")
        name_label.setStyleSheet("font-size: 14px; margin-bottom: 8px;")
        name_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        bio_label = QtWidgets.QLabel("Director of Bitrate Solutions (Pvt) Ltd.")
        bio_label.setStyleSheet("font-size: 14px; margin-bottom: 8px;")
        bio_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        #
        # ---- YOUR PHOTO here ----
        #
        me_path = os.path.join(
            os.path.dirname(__file__),
            "..", "..", "assets", "me.jpeg"
        )
        self.me_img_label = QtWidgets.QLabel()
        if os.path.exists(me_path):
            mepix = QtGui.QPixmap(me_path)
            mepix = mepix.scaled(
                100, 100,
                QtCore.Qt.AspectRatioMode.KeepAspectRatio,
                QtCore.Qt.TransformationMode.SmoothTransformation
            )
            self.me_img_label.setPixmap(mepix)
        else:
            self.me_img_label.setText("[me.png missing]")
        self.me_img_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        #
        # Copy Email button
        #
        self.email_btn = QtWidgets.QPushButton("📧 Copy email")
        self.email_btn.setFixedWidth(160)
        self.email_btn.clicked.connect(self.copy_email)
        email_container = QtWidgets.QHBoxLayout()
        email_container.addStretch()
        email_container.addWidget(self.email_btn)
        email_container.addStretch()

        # License
        license_label = QtWidgets.QLabel("License: MIT (Free & Open Source)")
        license_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        license_label.setStyleSheet("font-size: 12px; color: #bbbbbb;")

        # Trademark
        trademark_label = QtWidgets.QLabel("CryptoEngine™ is a trademark of Bitrate Solutions (Pvt) Ltd.")
        trademark_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        trademark_label.setStyleSheet("font-size: 12px; color: #bbbbbb;")

        #
        # Add to layout
        #
        layout.addWidget(self.app_icon_label)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addSpacing(15)
        layout.addWidget(desc)
        layout.addWidget(desc_sub)
        layout.addSpacing(15)
        layout.addWidget(version)
        layout.addSpacing(15)
        layout.addWidget(line)
        layout.addWidget(author_label)
        layout.addWidget(self.me_img_label)
        layout.addWidget(name_label)
        layout.addWidget(bio_label)
        layout.addLayout(email_container)
        layout.addStretch()
        layout.addWidget(license_label)
        layout.addWidget(trademark_label)

    def copy_email(self):
        clipboard = QtWidgets.QApplication.clipboard()
        clipboard.setText("wmhchathuranga@bitrate.lk")
        QtWidgets.QToolTip.showText(QtGui.QCursor.pos(), "Email copied!")
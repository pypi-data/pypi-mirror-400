"""
CryptoEngine™ — Secure Encryption & Signing Toolkit
Copyright (c) 2025
Harshana Chathuranga / Bitrate Solutions (Pvt) Ltd

Licensed under the MIT License (see LICENSE).
CryptoEngine™ name and logo are trademarked (see TRADEMARK.md).
"""

# ssh_encryptor/ui/tabs/metadata_tab.py

import os
import json
import mimetypes
import datetime

from PyQt6 import QtWidgets, QtCore

# Optional EXIF support (only if Pillow is installed)
try:
    from PIL import Image, ExifTags  # type: ignore[attr-defined]
    _PIL_AVAILABLE = True
except Exception:  # pragma: no cover
    Image = None
    ExifTags = None
    _PIL_AVAILABLE = False

def _json_safe(value):
    """
    Convert EXIF / Pillow types into something json.dumps can handle.
    """
    # Already safe
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value

    # Sequences
    if isinstance(value, (list, tuple)):
        return [_json_safe(v) for v in value]

    # Dict-like
    if isinstance(value, dict):
        return {str(k): _json_safe(v) for k, v in value.items()}

    # Things like IFDRational (support __float__)
    try:
        return float(value)
    except Exception:
        # Fallback: string representation
        return str(value)

def _human_size(num_bytes: int) -> str:
    """Return human-readable size like 12.3 MB."""
    units = ["B", "KB", "MB", "GB", "TB"]
    size = float(num_bytes)
    for u in units:
        if size < 1024.0 or u == units[-1]:
            return f"{size:0.1f} {u}"
        size /= 1024.0
    return f"{num_bytes} B"


def extract_file_metadata(path: str) -> dict:
    """Collect generic file metadata + optional image EXIF."""
    st = os.stat(path)

    created = datetime.datetime.fromtimestamp(st.st_ctime).isoformat()
    modified = datetime.datetime.fromtimestamp(st.st_mtime).isoformat()
    mime, encoding = mimetypes.guess_type(path)

    info: dict = {
        "path": os.path.abspath(path),
        "name": os.path.basename(path),
        "size_bytes": st.st_size,
        "size_human": _human_size(st.st_size),
        "mime_type": mime,
        "encoding": encoding,
        "created": created,
        "modified": modified,
    }

    # Extra info for image files (if Pillow present)
    if _PIL_AVAILABLE and mime and mime.startswith("image/"):
        try:
            with Image.open(path) as img:
                info["image_width"], info["image_height"] = img.size
                exif_raw = img._getexif()
                if exif_raw:
                    exif = {}
                    for tag, value in exif_raw.items():
                        key = ExifTags.TAGS.get(tag, str(tag))
                        exif[key] = _json_safe(value)
                    info["exif"] = exif
        except Exception as e:  # don’t fail metadata completely
            info["exif_error"] = str(e)
    elif mime and mime.startswith("image/") and not _PIL_AVAILABLE:
        info["exif_note"] = "Install Pillow (PIL) to see EXIF metadata."

    return info


class MetadataTab(QtWidgets.QWidget):
    """
    Tab to inspect basic metadata of a selected file.
    """

    def __init__(self, parent=None, main_window=None):
        super().__init__(parent)
        self.main = main_window

        self.last_metadata_json: str | None = None

        self._build_ui()

    def _build_ui(self):
        layout = QtWidgets.QVBoxLayout(self)

        # File picker
        file_row = QtWidgets.QHBoxLayout()
        self.file_path_edit = QtWidgets.QLineEdit()
        self.file_path_edit.setPlaceholderText("Select file to inspect")
        browse_btn = QtWidgets.QPushButton("Browse…")
        browse_btn.clicked.connect(self.browse_file)
        file_row.addWidget(self.file_path_edit)
        file_row.addWidget(browse_btn)

        # Buttons
        self.analyze_btn = QtWidgets.QPushButton("Analyze")
        self.analyze_btn.clicked.connect(self.handle_analyze)

        self.copy_btn = QtWidgets.QPushButton("Copy JSON")
        self.copy_btn.clicked.connect(self.copy_metadata)

        self.save_btn = QtWidgets.QPushButton("Save JSON")
        self.save_btn.clicked.connect(self.save_metadata)

        btn_row = QtWidgets.QHBoxLayout()
        btn_row.addWidget(self.analyze_btn)
        btn_row.addStretch()
        btn_row.addWidget(self.copy_btn)
        btn_row.addSpacing(10)
        btn_row.addWidget(self.save_btn)

        # Output
        self.output_edit = QtWidgets.QPlainTextEdit()
        self.output_edit.setReadOnly(True)
        self.output_edit.setPlaceholderText("Metadata JSON will appear here")

        layout.addLayout(file_row)
        layout.addLayout(btn_row)
        layout.addWidget(QtWidgets.QLabel("File metadata (JSON)"))
        layout.addWidget(self.output_edit)

    # ---------- Actions ----------

    def browse_file(self):
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Select file to inspect",
            os.path.expanduser("~"),
            "All Files (*)",
        )
        if path:
            self.file_path_edit.setText(path)

    def handle_analyze(self):
        path = self.file_path_edit.text().strip()
        if not path:
            self._toast("Please select a file first.", "warning")
            return
        if not os.path.isfile(path):
            self._toast(f"File not found: {path}", "warning")
            return

        try:
            info = extract_file_metadata(path)
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "Error", f"Failed to read file metadata:\n{e}"
            )
            return

        self.last_metadata_json = json.dumps(info, indent=2, sort_keys=True)
        self.output_edit.setPlainText(self.last_metadata_json)
        self._toast("Metadata extracted.", "success")

    def copy_metadata(self):
        if not self.last_metadata_json:
            self._toast("No metadata available. Analyze a file first.", "warning")
            return
        QtWidgets.QApplication.clipboard().setText(self.last_metadata_json)
        self._toast("Metadata JSON copied to clipboard.", "success")

    def save_metadata(self):
        if not self.last_metadata_json:
            self._toast("No metadata available. Analyze a file first.", "warning")
            return

        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self,
            "Save metadata JSON",
            os.path.expanduser("~"),
            "JSON Files (*.json);;All Files (*)",
        )
        if not path:
            return

        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(self.last_metadata_json)
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self, "Error", f"Could not save metadata file:\n{e}"
            )
            return

        self._toast("Metadata JSON saved.", "success")

    # ---------- Helpers ----------

    def _toast(self, message: str, level: str = "info"):
        # Use main window toast if available
        if self.main and hasattr(self.main, "show_toast"):
            self.main.show_toast(message, level=level)
        else:
            # Fallback: simple message box
            if level in ("warning", "error"):
                QtWidgets.QMessageBox.warning(self, "Info", message)
            else:
                QtWidgets.QMessageBox.information(self, "Info", message)
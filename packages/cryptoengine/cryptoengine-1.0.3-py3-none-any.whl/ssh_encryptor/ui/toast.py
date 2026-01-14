"""
CryptoEngine™ - Secure Encryption & Signing Toolkit
Copyright (c) 2025
Harshana Chathuranga / Bitrate Solutions (Pvt) Ltd.
Licensed under the MIT License — see LICENSE for details.
CryptoEngine™ name is trademarked — see TRADEMARK.md.
"""
from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont


class ToastNotification(QtWidgets.QFrame):
    """
    In-window toast notification that appears in the top-right corner
    of the parent window and auto-hides after a short delay.
    Only one toast is shown at a time.
    """

    _current_toast = None  # class-level tracker

    def __init__(self, parent, message: str, level: str = "info", duration_ms: int = 3000):
        # Close any existing toast to avoid overlapping
        if ToastNotification._current_toast is not None:
            try:
                ToastNotification._current_toast.close()
            except Exception:
                pass

        super().__init__(parent)
        ToastNotification._current_toast = self

        # Allow background from stylesheet
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)

        label = QtWidgets.QLabel(message)
        # If you want NO wrapping, set this to False:
        # label.setWordWrap(False)
        label.setWordWrap(True)
        font = QFont()
        font.setPointSize(10)
        label.setFont(font)
        layout.addWidget(label)

        # Colors per level
        if level == "success":
            bg = "#1b5e20"
        elif level == "warning":
            bg = "#f9a825"
        elif level == "error":
            bg = "#b71c1c"
        else:  # info
            bg = "#263238"

        self.setStyleSheet(f"""
            QFrame {{
                background-color: {bg};
                color: white;
                border-radius: 6px;
            }}
            QLabel {{
                color: white;
            }}
        """)

        # Dynamic width: based on text, capped at ~60% of parent width
        max_width = 2000
        if parent is not None and parent.width() > 0:
            max_width = int(parent.width() * 0.6)
        label.setMaximumWidth(max_width)
        self.setMaximumWidth(max_width)

        # Let Qt recompute size now that max width is set
        self.adjustSize()

        # Position + stacking
        self._position_in_parent(parent)
        self.raise_()

        # Auto-close timer
        QTimer.singleShot(duration_ms, self.close)

        self.show()

    def _position_in_parent(self, parent: QtWidgets.QWidget):
        """
        Position the toast at top-right inside the parent widget.
        """
        if parent is None:
            return

        margin = 16
        pw = parent.width()
        ph = parent.height()
        # Guard against 0x0 during initial layout
        if pw <= 0 or ph <= 0:
            pw = parent.geometry().width()
            ph = parent.geometry().height()

        x = pw - self.width() - margin   # right aligned
        y = margin                       # top

        self.move(int(x), int(y))

    def close(self):
        """
        Ensure the class-level pointer is cleared when this toast closes.
        """
        if ToastNotification._current_toast is self:
            ToastNotification._current_toast = None
        super().close()
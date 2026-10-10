from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox, QFrame
)
from pathlib import Path

from auth import authenticate

BASE_DIR = Path(__file__).resolve().parent
ICON_PATH = BASE_DIR / "assets" / "icon.png"

STYLE = """
QMainWindow, QWidget { background: #101010; color: #e6e6e6; }
QLabel#brand { color: #99C2FF; font-size: 22px; font-weight: bold; background: transparent;}
QLabel#subtitle { color: #a0a0a0; background: transparent;}
QLineEdit {
    background: #0c0c0c; color: #eeeeee; border: 1px solid #383838;
    border-radius: 8px; padding: 11px; selection-background-color: #315d91;
}
QLineEdit:focus { border: 1px solid #99C2FF; }
QPushButton {
    background: #24476e; color: white; border: none; border-radius: 6px;
    padding: 11px; font-weight: bold;
}
QPushButton:hover { background: #315d91; }
QPushButton#secondary { background: transparent; color: #99C2FF; }
QPushButton#secondary:hover { background: #202020; }
QFrame#panel { background: #171717; border: 1px solid #303030; border-radius: 10px; }
"""


class LoginWindow(QMainWindow):
    authenticated = Signal(dict)
    register_requested = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Whale - Login")
        self.setMinimumSize(420, 385)
        self.resize(420, 385)
        if ICON_PATH.exists():
            self.setWindowIcon(QIcon(str(ICON_PATH)))
        self.setStyleSheet(STYLE)

        panel = QFrame()
        panel.setObjectName("panel")
        form = QVBoxLayout(panel)
        form.setContentsMargins(28, 28, 28, 28)
        form.setSpacing(14)

        brand = QLabel("WHALE")
        brand.setObjectName("brand")
        brand.setAlignment(Qt.AlignmentFlag.AlignCenter)
        brand.setFont(QFont("Consolas", 25, QFont.Weight.Bold))

        subtitle = QLabel("Sign in to your terminal")
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.identifier_input = QLineEdit()
        self.identifier_input.setPlaceholderText("Username atau email")
        self.identifier_input.setClearButtonEnabled(True)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.returnPressed.connect(self.do_login)

        login_button = QPushButton("LOGIN")
        login_button.clicked.connect(self.do_login)

        register_button = QPushButton("Belum punya akun? Register")
        register_button.setObjectName("secondary")
        register_button.clicked.connect(self.register_requested.emit)

        form.addWidget(brand)
        form.addWidget(subtitle)
        form.addSpacing(12)
        form.addWidget(self.identifier_input)
        form.addWidget(self.password_input)
        form.addWidget(login_button)
        form.addWidget(register_button)

        outer = QVBoxLayout()
        outer.addStretch()
        outer.addWidget(panel)
        outer.addStretch()
        outer.setContentsMargins(28, 24, 28, 24)

        central = QWidget()
        central.setLayout(outer)
        self.setCentralWidget(central)

    def do_login(self):
        identifier = self.identifier_input.text()
        password = self.password_input.text()
        try:
            user = authenticate(identifier, password)
        except Exception as error:
            QMessageBox.critical(self, "Database error", f"Tidak dapat membaca database.\n{error}")
            return

        if user is None:
            QMessageBox.warning(self, "Login gagal", "Username/email atau password salah.")
            self.password_input.clear()
            self.password_input.setFocus()
            return

        self.password_input.clear()
        self.authenticated.emit(user)

    def set_identifier(self, identifier: str):
        self.identifier_input.setText(identifier)
        self.password_input.clear()
        self.password_input.setFocus()

    def clear_password(self):
        self.password_input.clear()

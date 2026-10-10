from pathlib import Path

from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QFont, QIcon
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QFrame
)

from auth import register_user
from login_window import STYLE

BASE_DIR = Path(__file__).resolve().parent
ICON_PATH = BASE_DIR / "assets" / "icon.png"


class RegisterWindow(QMainWindow):
    back_requested = Signal()
    account_created = Signal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Whale - Register")
        self.setMinimumSize(440, 570)
        self.resize(470, 600)
        if ICON_PATH.exists():
            self.setWindowIcon(QIcon(str(ICON_PATH)))
        self.setStyleSheet(STYLE)

        panel = QFrame()
        panel.setObjectName("panel")
        form = QVBoxLayout(panel)
        form.setContentsMargins(28, 24, 28, 24)
        form.setSpacing(12)

        title = QLabel("CREATE ACCOUNT")
        title.setObjectName("brand")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Consolas", 19, QFont.Weight.Bold))

        subtitle = QLabel("Buat akun untuk menggunakan Whale")
        subtitle.setObjectName("subtitle")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username (3–24 karakter)")
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password (minimal 8 karakter)")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_input = QLineEdit()
        self.confirm_input.setPlaceholderText("Konfirmasi password")
        self.confirm_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_input.returnPressed.connect(self.do_register)

        create_button = QPushButton("BUAT AKUN")
        create_button.clicked.connect(self.do_register)
        back_button = QPushButton("Kembali ke Login")
        back_button.setObjectName("secondary")
        back_button.clicked.connect(self.back_requested.emit)

        note = QLabel("Username: huruf, angka, underscore.\nPassword: minimal 8 karakter, berisi huruf dan angka.")
        note.setObjectName("subtitle")
        note.setWordWrap(True)

        form.addWidget(title)
        form.addWidget(subtitle)
        form.addSpacing(6)
        form.addWidget(self.username_input)
        form.addWidget(self.email_input)
        form.addWidget(self.password_input)
        form.addWidget(self.confirm_input)
        form.addWidget(note)
        form.addWidget(create_button)
        form.addWidget(back_button)

        outer = QVBoxLayout()
        outer.addStretch()
        outer.addWidget(panel)
        outer.addStretch()
        outer.setContentsMargins(24, 20, 24, 20)

        central = QWidget()
        central.setLayout(outer)
        self.setCentralWidget(central)

    def do_register(self):
        username = self.username_input.text()
        email = self.email_input.text()
        password = self.password_input.text()
        confirm = self.confirm_input.text()

        success, message = register_user(username, email, password, confirm)
        if not success:
            QMessageBox.warning(self, "Register gagal", message)
            return

        QMessageBox.information(self, "Berhasil", message)
        self.account_created.emit(username.strip())

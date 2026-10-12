import sys
from pathlib import Path

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from database import initialize_database
from login_window import LoginWindow
from register_window import RegisterWindow
from terminal_window import TerminalWindow

BASE_DIR = Path(__file__).resolve().parent
ICON_PATH = BASE_DIR / "assets" / "icon.png"


class WhaleApplication:
    def __init__(self, app: QApplication):
        self.app = app
        initialize_database()

        self.login_window = LoginWindow()
        self.register_window = None
        self.terminal_window = None

        self.login_window.authenticated.connect(self.open_terminal)
        self.login_window.register_requested.connect(self.open_register)
        self.login_window.show()

    def open_register(self):
        self.login_window.hide()
        self.register_window = RegisterWindow()
        self.register_window.back_requested.connect(self.back_to_login)
        self.register_window.account_created.connect(self.registration_finished)
        self.register_window.show()

    def back_to_login(self):
        # Show the login window before closing the register window so Qt
        # does not interpret it as the last window being closed.
        self.login_window.show()
        if self.register_window:
            self.register_window.close()
            self.register_window = None

    def registration_finished(self, username: str):
        self.login_window.set_identifier(username)
        self.login_window.show()
        if self.register_window:
            self.register_window.close()
            self.register_window = None

    def open_terminal(self, user: dict):
        self.login_window.hide()
        self.terminal_window = TerminalWindow(user)
        self.terminal_window.logout_requested.connect(self.logout)
        self.terminal_window.show()

    def logout(self):
        if self.terminal_window:
            self.terminal_window.hide()
            self.terminal_window.deleteLater()
            self.terminal_window = None
        self.login_window.clear_password()
        self.login_window.show()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Whale")
    if ICON_PATH.exists():
        app.setWindowIcon(QIcon(str(ICON_PATH)))

    controller = WhaleApplication(app)  # Keep the controller alive for the app lifetime.
    sys.exit(app.exec())


if __name__ == "__main__":
    main()

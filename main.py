
import sys
import subprocess

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QPlainTextEdit,
    QLineEdit
)

from PySide6.QtGui import QFont, QTextCursor
from PySide6.QtCore import Qt

from PySide6.QtGui import QIcon
from pathlib import Path


class TerminalWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        icon_path = Path(__file__).parent / "assets" / "icon.png"
        self.setWindowIcon(QIcon(str(icon_path)))

        self.setWindowTitle("Whale")
        self.resize(780, 400)

        self.current_dir = ">"

        # Widget utama
        central = QWidget()
        layout = QVBoxLayout(central)

        # Area output terminal
        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)

        self.output.setStyleSheet("""
            QPlainTextEdit {
                background-color: #0c0c0c;
                color: #cccccc;
                border: none;
                padding: 12px;
            }
        """)

        # Input perintah
        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText("Ketik perintah...")
        self.command_input.setStyleSheet("""
            QLineEdit {
                background-color: #0c0c0c;
                color: #99C2FF;
                border: none;
                padding: 12px;
            }
        """)

        # Font terminal
        font = QFont("Consolas", 10)
        self.output.setFont(font)
        self.command_input.setFont(font)

        layout.addWidget(self.output)
        layout.addWidget(self.command_input)

        self.setCentralWidget(central)

        # Event saat Enter ditekan
        self.command_input.returnPressed.connect(
            self.execute_command
        )

        self.print_text("=====  MADE BY YEA =====\n")

        self.print_text("Ketik help untuk melihat perintah.\n")

        self.update_prompt()

    def print_text(self, text):
        self.output.appendPlainText(text)

    def update_prompt(self):
        self.command_input.setPlaceholderText(
            f"{self.current_dir}>"
        )

    def execute_command(self):
        command = self.command_input.text().strip()

        if not command:
            return

        self.print_text(f"{self.current_dir}> {command}")
        self.command_input.clear()

        if command.lower() == "help":
            self.print_text(
                "Perintah dasar:\n"
                "help     - Bantuan\n"
                "cls      - Bersihkan terminal\n"
                "dir      - Lihat isi folder\n"
                "ipconfig - Informasi jaringan\n"
                "exit     - Tutup aplikasi\n"
            )

        elif command.lower() == "cls":
            self.output.clear()

        elif command.lower() == "exit":
            self.close()

        else:
            try:
                result = subprocess.run(
                    command,
                    shell=True,
                    cwd=self.current_dir,
                    capture_output=True,
                    text=True,
                    errors="replace",
                    timeout=30
                )

                if result.stdout:
                    self.print_text(result.stdout.rstrip())

                if result.stderr:
                    self.print_text(result.stderr.rstrip())

            except subprocess.TimeoutExpired:
                self.print_text("Perintah melebihi batas waktu.")

            except Exception as error:
                self.print_text(f"Error: {error}")

        self.output.moveCursor(QTextCursor.MoveOperation.End)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = TerminalWindow()
    window.show()

    sys.exit(app.exec())

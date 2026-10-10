import os
import subprocess
from pathlib import Path

from PySide6.QtCore import Signal, Qt, QTimer, QTime
from PySide6.QtGui import QFont, QIcon, QTextCursor
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPlainTextEdit, QLineEdit, QLabel, QPushButton, QMessageBox
)

BASE_DIR = Path(__file__).resolve().parent
ICON_PATH = BASE_DIR / "assets" / "icon.png"


class TerminalWindow(QMainWindow):
    logout_requested = Signal()

    def __init__(self, user: dict):
        super().__init__()
        self.user = user
        self.current_dir = str(Path.cwd())

        self.setWindowTitle(f"Whale Terminal - {user['username']}")
        self.setMinimumSize(780, 385)
        self.resize(780, 385)
        if ICON_PATH.exists():
            self.setWindowIcon(QIcon(str(ICON_PATH)))

        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        top_bar = QWidget()
        top_bar.setStyleSheet("background-color: #171717;")
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(12, 6, 12, 6)

        user_label = QLabel(f"User: {user['username']}")
        user_label.setStyleSheet("color: #99C2FF;")
        
        self.clock_label = QLabel()
        self.clock_label.setStyleSheet("color: #aaaaaa; margin-right: 15px;")
        font_clock = QFont("Consolas", 10)
        self.clock_label.setFont(font_clock)

        logout_button = QPushButton("Logout")
        logout_button.setMaximumWidth(90)
        logout_button.setStyleSheet("""
            QPushButton { background: #333333; color: #eeeeee; border: none;
                          padding: 6px 12px; border-radius: 4px; }
            QPushButton:hover { background: #4a4a4a; }
        """)
        logout_button.clicked.connect(self.logout)
        
        top_layout.addWidget(user_label)
        top_layout.addStretch()
        top_layout.addWidget(self.clock_label) # TAMBAHAN: Pasang jam di top_bar sebelum tombol logout
        top_layout.addWidget(logout_button)

        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)
        self.output.setStyleSheet("""
            QPlainTextEdit {
                background-color: #0c0c0c; color: #cccccc;
                border: none; padding: 12px;
                selection-background-color: #315d91;
            }
        """)

        self.command_input = QLineEdit()
        self.command_input.setStyleSheet("""
            QLineEdit {
                background-color: #0c0c0c; color: #99C2FF;
                border: none; padding: 12px;
            }
        """)
        self.command_input.setPlaceholderText("Ketik perintah...")
        self.command_input.returnPressed.connect(self.execute_command)

        font = QFont("Consolas", 10)
        self.output.setFont(font)
        self.command_input.setFont(font)

        layout.addWidget(top_bar)
        layout.addWidget(self.output, 1)
        layout.addWidget(self.command_input)
        self.setCentralWidget(central)

        # TAMBAHAN: Konfigurasi QTimer untuk memperbarui jam setiap 1 detik
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_clock)
        self.timer.start(1000)
        self.update_clock() # Jalankan sekali di awal agar tidak kosong saat dibuka

        self.print_text("Ketik help untuk melihat perintah.")
        self.update_prompt()

    # TAMBAHAN: Fungsi untuk memperbarui teks jam berdasarkan waktu sistem
    def update_clock(self):
        current_time = QTime.currentTime().toString("HH:mm:ss")
        self.clock_label.setText(current_time)

    def print_text(self, text: str):
        self.output.appendPlainText(text)

    def update_prompt(self):
        self.command_input.setPlaceholderText(f"{self.current_dir}>")

    def execute_command(self):
        command = self.command_input.text().strip()
        if not command:
            return

        self.print_text(f"{self.current_dir}> {command}")
        self.command_input.clear()
        lowered = command.lower()

        if lowered == "help":
            self.print_text(
                "Perintah Whale:\n"
                "help      - Tampilkan bantuan\n"
                "cls       - Bersihkan terminal\n"
                "dir       - Lihat isi folder\n"
                "cd <path> - Pindah direktori\n"
                "ipconfig  - Informasi jaringan Windows\n"
                "logout    - Keluar dari akun Whale\n"
                "exit      - Tutup aplikasi Whale"
            )
        elif lowered in ("cls", "clear"):
            self.output.clear()
        elif lowered == "logout":
            self.logout()
        elif lowered == "exit":
            self.close()
        elif lowered == "cd" or lowered.startswith("cd "):
            self.change_directory(command[2:].strip())
        else:
            try:
                result = subprocess.run(
                    command,
                    shell=True,
                    cwd=self.current_dir,
                    capture_output=True,
                    text=True,
                    errors="replace",
                    timeout=30,
                )
                if result.stdout.strip():
                    self.print_text(result.stdout.rstrip())
                if result.stderr.strip():
                    self.print_text(result.stderr.rstrip())
                if result.returncode and not result.stdout.strip() and not result.stderr.strip():
                    self.print_text(f"Perintah selesai dengan kode {result.returncode}.")
            except subprocess.TimeoutExpired:
                self.print_text("Perintah melebihi batas waktu 30 detik.")
            except Exception as error:
                self.print_text(f"Error: {error}")

        self.output.moveCursor(QTextCursor.MoveOperation.End)
        self.update_prompt()

    def change_directory(self, target: str):
        target = target.strip().strip('"')
        if not target:
            self.print_text(self.current_dir)
            return
        if target == "~":
            target = str(Path.home())

        new_path = Path(target)
        if not new_path.is_absolute():
            new_path = Path(self.current_dir) / new_path

        try:
            resolved = new_path.resolve(strict=True)
            if not resolved.is_dir():
                self.print_text("Error: path bukan folder.")
                return
            self.current_dir = str(resolved)
        except FileNotFoundError:
            self.print_text("Error: folder tidak ditemukan.")
        except OSError as error:
            self.print_text(f"Error: {error}")

    def logout(self):
        self.logout_requested.emit()

    def closeEvent(self, event):
        event.accept()

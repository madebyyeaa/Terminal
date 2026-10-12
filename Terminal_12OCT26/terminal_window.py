import os
import subprocess
from pathlib import Path

from PySide6.QtCore import Signal, Qt, QTimer, QTime
from PySide6.QtGui import QFont, QIcon, QTextCursor
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPlainTextEdit, QLineEdit, QLabel, QPushButton, QMessageBox,
    QStackedWidget, QFileDialog, QInputDialog, QDialog, QFormLayout
)

try:
    import oracledb
    HAS_ORACLE = True
except ImportError:
    HAS_ORACLE = False

BASE_DIR = Path(__file__).resolve().parent
ICON_PATH = BASE_DIR / "assets" / "icon.png"


class OracleConnectDialog(QDialog):
    """Dialog Popup untuk Mengisi Akses & Monitoring Oracle Database"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Oracle Database Connection")
        self.setFixedSize(380, 280)
        self.setStyleSheet("""
            QDialog {
                background-color: #1E1F22;
                color: #FFFFFF;
                font-family: 'Segoe UI', sans-serif;
            }
            QLabel {
                color: #CCCCCC;
                font-size: 12px;
            }
            QLineEdit {
                background-color: #2B2D30;
                color: #99C2FF;
                border: 1px solid #3C3F41;
                border-radius: 4px;
                padding: 6px;
            }
            QPushButton {
                background-color: #3574F0;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #548BFF;
            }
        """)

        layout = QFormLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        self.host_input = QLineEdit("localhost")
        self.port_input = QLineEdit("1521")
        self.service_input = QLineEdit("ORCL")
        self.user_input = QLineEdit()
        self.pass_input = QLineEdit()
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)

        layout.addRow("Host / IP:", self.host_input)
        layout.addRow("Port:", self.port_input)
        layout.addRow("Service / SID:", self.service_input)
        layout.addRow("Username:", self.user_input)
        layout.addRow("Password:", self.pass_input)

        self.btn_connect = QPushButton("Connect & Monitor")
        self.btn_connect.clicked.connect(self.accept)
        layout.addRow(self.btn_connect)

    def get_credentials(self):
        return {
            "host": self.host_input.text().strip(),
            "port": self.port_input.text().strip(),
            "service": self.service_input.text().strip(),
            "user": self.user_input.text().strip(),
            "password": self.pass_input.text().strip()
        }


class TerminalWindow(QMainWindow):
    logout_requested = Signal()

    def __init__(self, user: dict):
        super().__init__()
        self.user = user
        self.current_dir = str(Path.cwd())

        self.setWindowTitle(f"Whale Terminal - {user['username']}")
        self.setMinimumSize(1140, 840)
        self.resize(1140, 840)
        if ICON_PATH.exists():
            self.setWindowIcon(QIcon(str(ICON_PATH)))

        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # TOP BAR
        top_bar = QWidget()
        top_bar.setStyleSheet("background-color: #171717;")
        top_layout = QHBoxLayout(top_bar)
        top_layout.setContentsMargins(12, 6, 12, 6)

        # ACCESS PROFILE BUTTON (Klik untuk kembali ke Terminal Utama)
        self.user_button = QPushButton(f"// ACCESS_PROFILE // {user['username'].upper()}")
        self.user_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.user_button.setStyleSheet("""
            QPushButton {
                color: #99C2FF;
                font-family: 'Impact', 'Segoe UI', sans-serif;
                font-size: 14px;
                background-color: #1A1F26;
                border-left: 5px solid #38BDF8;
                border-right: 1px solid #2D3748;
                border-top: 1px solid #2D3748;
                border-bottom: 1px solid #2D3748;
                padding: 8px 16px;
                text-align: left;
            }
            QPushButton:hover {
                color: #1A1F26;
                background-color: #E2B800;
                border-left: 5px solid #FFFFFF;
            }
        """)
        self.user_button.clicked.connect(self.show_terminal_page)

        # PROJECT BUTTON (Klik untuk membuka PyCharm Dashboard)
        self.project_button = QPushButton("// PROJECT //")
        self.project_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.project_button.setStyleSheet("""
            QPushButton {
                color: #99C2FF;
                font-family: 'Impact', 'Segoe UI', sans-serif;
                font-size: 14px;
                background-color: #1A1F26;
                border-left: 5px solid #38BDF8;
                border-right: 1px solid #2D3748;
                border-top: 1px solid #2D3748;
                border-bottom: 1px solid #2D3748;
                padding: 8px 16px;
                text-align: center;
            }
            QPushButton:hover {
                color: #1A1F26;
                background-color: #E2B800;
                border-left: 5px solid #FFFFFF;
            }
        """)
        self.project_button.clicked.connect(self.show_project_page)

        self.clock_label = QLabel()
        self.clock_label.setStyleSheet("color: #aaaaaa; margin-right: 15px;")
        font_clock = QFont("Consolas", 10)
        self.clock_label.setFont(font_clock)

        # LOGOUT BUTTON
        logout_button = QPushButton("// LOGOUT //")
        logout_button.setMaximumWidth(110)
        logout_button.setCursor(Qt.CursorShape.PointingHandCursor)
        logout_button.setStyleSheet("""
            QPushButton {
                color: #99C2FF;
                font-family: 'Impact', 'Segoe UI', sans-serif;
                font-size: 13px;
                font-weight: bold;
                background-color: #1A1F26;
                border-left: 4px solid #38BDF8;
                border-right: 1px solid #2D3748;
                border-top: 1px solid #2D3748;
                border-bottom: 1px solid #2D3748;
                border-radius: 0px;
                padding: 6px 12px;
            }
            QPushButton:hover {
                color: #1A1F26;
                background-color: #E2B800;
                border-left: 4px solid #FFFFFF;
            }
            QPushButton:pressed {
                background-color: #B89500;
                color: #1A1F26;
            }
        """)
        logout_button.clicked.connect(self.logout)

        top_layout.addWidget(self.user_button)
        top_layout.addWidget(self.project_button)
        top_layout.addStretch()
        top_layout.addWidget(self.clock_label)
        top_layout.addWidget(logout_button)

        layout.addWidget(top_bar)

        # STACKED WIDGET UNTUK WADAH BERPINDAH HALAMAN
        self.stacked_widget = QStackedWidget()
        layout.addWidget(self.stacked_widget, 1)

        # ----------------- HALAMAN 0: TERMINAL UTAMA -----------------
        self.terminal_page = QWidget()
        term_layout = QVBoxLayout(self.terminal_page)
        term_layout.setContentsMargins(0, 0, 0, 0)
        term_layout.setSpacing(0)

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
                border: none; padding: 28px;
            }
        """)
        self.command_input.setPlaceholderText("Ketik perintah...")
        self.command_input.returnPressed.connect(self.execute_command)

        font = QFont("Consolas", 10)
        self.output.setFont(font)
        self.command_input.setFont(font)

        term_layout.addWidget(self.output, 1)
        term_layout.addWidget(self.command_input)

        # ----------------- HALAMAN 1: DASHBOARD PYCHARM -----------------
        self.pycharm_page = self.create_pycharm_welcome_screen()

        self.stacked_widget.addWidget(self.terminal_page)   # Index 0
        self.stacked_widget.addWidget(self.pycharm_page)    # Index 1

        self.setCentralWidget(central)

        # TIMER CLOCK
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_clock)
        self.timer.start(1000)
        self.update_clock()

        self.print_text("Ketik help untuk melihat perintah. \n")
        self.update_prompt()

    def create_pycharm_welcome_screen(self) -> QWidget:
        """Membuat tampilan halaman Welcome ala PyCharm"""
        page = QWidget()
        page.setStyleSheet("background-color: #1E1F22;")

        layout = QVBoxLayout(page)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title_label = QLabel("Welcome to PyCharm")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                color: #FFFFFF;
                font-family: 'Segoe UI', sans-serif;
                font-size: 32px;
                font-weight: bold;
                margin-bottom: 8px;
            }
        """)

        subtitle_label = QLabel(
            "Create new folder & SQL scripts, open existing projects,\nor connect directly to your Oracle Database server."
        )
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setStyleSheet("""
            QLabel {
                color: #9DA5B4;
                font-family: 'Segoe UI', sans-serif;
                font-size: 14px;
                line-height: 1.4;
                margin-bottom: 40px;
            }
        """)

        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(35)
        actions_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 1. New Folder + script_sql
        new_project_box = self.create_pycharm_action_btn("+", "New Project", enabled=True, callback=self.create_new_project_folder)

        # 2. Open Project
        open_folder_box = self.create_pycharm_action_btn("📁", "Open", enabled=True, callback=self.open_folder_dialog)

        # 3. Oracle DB Connection (Ganti VCS)
        vcs_box = self.create_pycharm_action_btn("🗄️", "Oracle DB", enabled=True, callback=self.connect_oracle_db)

        actions_layout.addWidget(new_project_box)
        actions_layout.addWidget(open_folder_box)
        actions_layout.addWidget(vcs_box)

        layout.addStretch()
        layout.addWidget(title_label)
        layout.addWidget(subtitle_label)
        layout.addLayout(actions_layout)
        layout.addStretch()

        return page

    def create_pycharm_action_btn(self, icon_str: str, text: str, enabled: bool = True, callback=None) -> QWidget:
        container = QWidget()
        box_layout = QVBoxLayout(container)
        box_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        box_layout.setContentsMargins(0, 0, 0, 0)
        box_layout.setSpacing(10)

        icon_btn = QPushButton(icon_str)
        icon_btn.setFixedSize(65, 65)

        if enabled:
            icon_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            icon_btn.setStyleSheet("""
                QPushButton {
                    background-color: #2B2D30;
                    color: #3574F0;
                    font-size: 26px;
                    font-weight: bold;
                    border: 2px solid #3574F0;
                    border-radius: 12px;
                }
                QPushButton:hover {
                    background-color: #35373B;
                    border-color: #548BFF;
                    color: #548BFF;
                }
                QPushButton:pressed {
                    background-color: #1E1F22;
                }
            """)
            if callback:
                icon_btn.clicked.connect(callback)
        else:
            icon_btn.setStyleSheet("""
                QPushButton {
                    background-color: #25272A;
                    color: #5A5D63;
                    font-size: 24px;
                    border: 1px solid #323438;
                    border-radius: 12px;
                }
            """)

        lbl = QLabel(text)
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet(f"""
            QLabel {{
                color: {'#FFFFFF' if enabled else '#5A5D63'};
                font-family: 'Segoe UI', sans-serif;
                font-size: 13px;
                font-weight: 500;
            }}
        """)

        box_layout.addWidget(icon_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        box_layout.addWidget(lbl, alignment=Qt.AlignmentFlag.AlignCenter)

        return container

    def create_new_project_folder(self):
        """Membuat folder project baru beserta subfolder script_sql di dalamnya"""
        folder_name, ok = QInputDialog.getText(
            self, "New Project Folder", "Masukkan Nama Project Baru:"
        )
        if ok and folder_name.strip():
            project_path = Path(self.current_dir) / folder_name.strip()
            sql_dir = project_path / "script_sql"
            try:
                sql_dir.mkdir(parents=True, exist_ok=True)
                
                # Buat file sample script.sql secara otomatis
                sample_sql = sql_dir / "query_sample.sql"
                if not sample_sql.exists():
                    with open(sample_sql, "w", encoding="utf-8") as f:
                        f.write("-- Tulis Script SQL Anda di sini\nSELECT * FROM dual;\n")

                self.change_directory(str(project_path))
                QMessageBox.information(
                    self,
                    "Project Created",
                    f"Folder Project berhasil dibuat:\n{project_path}\n\n"
                    f"Subfolder SQL disiapkan:\n{sql_dir}"
                )
                self.show_terminal_page()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Gagal membuat folder: {e}")

    def open_folder_dialog(self):
        """Membuka dialog eksplorasi folder"""
        folder_selected = QFileDialog.getExistingDirectory(
            self, "Select Project Directory", self.current_dir
        )
        if folder_selected:
            self.change_directory(folder_selected)
            QMessageBox.information(
                self, "Project Opened", f"Project folder dibuka:\n{folder_selected}"
            )
            self.show_terminal_page()

    def connect_oracle_db(self):
        """Membuka Dialog Koneksi & Monitoring Oracle Database"""
        if not HAS_ORACLE:
            QMessageBox.warning(
                self,
                "Library Missing",
                "Library 'oracledb' belum terinstall!\nSilakan jalankan 'pip install oracledb' di terminal Anda."
            )
            return

        dialog = OracleConnectDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            cred = dialog.get_credentials()
            try:
                dsn = f"{cred['host']}:{cred['port']}/{cred['service']}"
                self.print_text(f"\n[ORACLE] Mencoba menghubungkan ke {dsn}...")

                # Koneksi ke Oracle DB
                connection = oracledb.connect(
                    user=cred["user"],
                    password=cred["password"],
                    dsn=dsn
                )
                
                cursor = connection.cursor()
                cursor.execute("SELECT instance_name, status, version FROM v$instance")
                db_info = cursor.fetchone()
                cursor.close()
                connection.close()

                info_msg = (
                    f"Koneksi Oracle DB Sukses!\n\n"
                    f"Instance Name: {db_info[0] if db_info else 'N/A'}\n"
                    f"Status: {db_info[1] if db_info else 'ONLINE'}\n"
                    f"Version: {db_info[2] if db_info else 'N/A'}"
                )
                QMessageBox.information(self, "Oracle DB Connected", info_msg)
                
                self.print_text(f"[ORACLE STATUS] Connected - {info_msg.replace(chr(10), ' | ')}")
                self.show_terminal_page()

            except Exception as err:
                QMessageBox.critical(self, "Oracle Connection Error", f"Gagal terhubung ke Database:\n{err}")
                self.print_text(f"[ORACLE ERROR] {err}")

    def show_terminal_page(self):
        self.stacked_widget.setCurrentIndex(0)

    def show_project_page(self):
        self.stacked_widget.setCurrentIndex(1)

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
                "exit      - Tutup aplikasi Whale\n"
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
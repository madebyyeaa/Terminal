import hashlib
import hmac
import re
import secrets

from database import get_connection

PBKDF2_ITERATIONS = 600_000
SALT_BYTES = 16
USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9_]{3,24}$")
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _password_hash(password: str, salt_hex: str) -> str:
    salt = bytes.fromhex(salt_hex)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        PBKDF2_ITERATIONS,
    )
    return digest.hex()


def validate_registration(username: str, email: str, password: str, confirm: str):
    username = username.strip()
    email = email.strip()

    if not USERNAME_PATTERN.fullmatch(username):
        return False, "Username harus 3–24 karakter dan hanya boleh berisi huruf, angka, atau underscore."
    if not EMAIL_PATTERN.fullmatch(email):
        return False, "Format email belum valid."
    if len(password) < 8:
        return False, "Password minimal 8 karakter."
    if not any(char.isalpha() for char in password) or not any(char.isdigit() for char in password):
        return False, "Password harus memiliki setidaknya satu huruf dan satu angka."
    if password != confirm:
        return False, "Konfirmasi password tidak cocok."

    return True, ""


def register_user(username: str, email: str, password: str, confirm: str):
    username = username.strip()
    email = email.strip().lower()

    valid, message = validate_registration(username, email, password, confirm)
    if not valid:
        return False, message

    salt_hex = secrets.token_hex(SALT_BYTES)
    password_hash = _password_hash(password, salt_hex)

    try:
        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO users (username, email, password_hash, salt)
                VALUES (?, ?, ?, ?)
                """,
                (username, email, password_hash, salt_hex),
            )
            connection.commit()
        return True, "Akun berhasil dibuat. Silakan login."
    except Exception as error:
        # SQLite constraint code for duplicate username/email.
        if "UNIQUE constraint failed" in str(error):
            return False, "Username atau email sudah terdaftar."
        return False, f"Gagal membuat akun: {error}"


def authenticate(identifier: str, password: str):
    identifier = identifier.strip()
    if not identifier or not password:
        return None

    with get_connection() as connection:
        user = connection.execute(
            """
            SELECT id, username, email, password_hash, salt, created_at
            FROM users
            WHERE username = ? COLLATE NOCASE OR email = ? COLLATE NOCASE
            """,
            (identifier, identifier),
        ).fetchone()

    if user is None:
        return None

    calculated_hash = _password_hash(password, user["salt"])
    if not hmac.compare_digest(calculated_hash, user["password_hash"]):
        return None

    return {
        "id": user["id"],
        "username": user["username"],
        "email": user["email"],
        "created_at": user["created_at"],
    }

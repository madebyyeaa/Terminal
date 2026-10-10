# Whale Desktop

Aplikasi desktop Python 3.13 + PySide6 dengan login, register, SQLite, dan terminal lokal.

## Persyaratan
- Windows
- Python 3.13
- Ikon Whale: `assets/icon.png`

## Instalasi CMD
Buka CMD di folder proyek:

```bat
"C:\Program Files\Python313\python.exe" -m venv .venv
.venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python main.py
```

Database `data/whale.db` dan tabel `users` dibuat otomatis.

## Validasi akun
- Username 3–24 karakter: huruf, angka, underscore.
- Email harus memiliki format dasar yang valid.
- Password minimal 8 karakter, dengan minimal satu huruf dan satu angka.
- Password disimpan menggunakan PBKDF2-HMAC-SHA256 dengan salt acak.

## Catatan terminal
Terminal ini menjalankan perintah Windows lokal. Gunakan hanya perintah yang kamu pahami dan jangan jalankan perintah dari sumber yang tidak dipercaya.

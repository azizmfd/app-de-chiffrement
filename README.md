# File Encryption Application with Sensitive-Data Detection

A Flask web application that encrypts and decrypts files with AES-256-GCM and scans file content before encryption to warn the user when it contains sensitive terms (passwords, IBAN, card numbers, personal and medical data, etc.).

Bachelor's thesis project (PFE) in Computer Science, option Cybersecurity and Network Infrastructure, Numidia Institute of Technology, academic year 2024-2025.



---

## Features

- **Authenticated encryption (AES-256-GCM)** using the Python `cryptography` library. A fresh random 12-byte nonce is generated for every encryption; the output file is `nonce + ciphertext + authentication tag`.
- **Tamper detection**: decryption fails if the key is wrong or the file has been modified.
- **Progressive lockout on decryption**: after failed attempts, an IP address is blocked for 60 seconds, then 5 minutes, then 1 hour, then until an administrator unblocks it.
- **Admin interface** (login-protected) to review and unblock locked IP addresses.
- **Sensitivity analysis before encryption**: text is extracted from the file and matched (case-insensitive) against a local SQLite database of sensitive words. The user sees the detected terms and either confirms ("Yes, Encrypt") or cancels.
- **Multi-format text extraction**: `.txt`, `.pdf`, `.docx`, `.csv`, `.xls`, `.xlsx`, `.json` (other files are decoded as UTF-8 when possible).
- **Key tools**: random key generator (24 characters), real-time strength indicator, QR-code generation, and QR-code scanning through the device camera.
- **Local content analysis**: the analysis of file content runs on the application's server.

## Architecture

```
+--------------------+   HTTP POST (file + key)    +--------------------------+
|  Frontend          | --------------------------> |  Backend (Flask)         |
|  HTML / CSS / JS   |                             |  - app.py (routes)       |
|  QR scan, key gen, | <-------------------------- |  - encryption.py         |
|  confirmation UI   |   result / encrypted file   |  - intelligence.py       |
+--------------------+                             |  - init_db.py + SQLite   |
                                                   +--------------------------+
```

Workflow: upload file, sensitivity analysis, confirmation prompt, AES-GCM encryption, download.

Main routes: `POST /encrypt`, `POST /decrypt`, `POST /analyse_ai`, `/login`, `/admin`.

### Project structure

```
.
├── backend/
│   ├── app.py               # Flask server and routes
│   ├── encryption.py        # AES-GCM encryption / decryption
│   ├── intelligence.py      # Text extraction and sensitive-word detection
│   ├── init_db.py           # Builds the sensitive-words SQLite database
│   ├── mots_sensibles.db    # Sensitive-words database
│   └── templates/           # Login and admin pages
├── frontend/
│   ├── index.html
│   ├── script.js            # UI logic, key generation, QR, requests
│   └── style.css
├── static/
├── requirements.txt
├── Procfile
└── run_app.bat
```

## Tech stack

| Layer | Technologies |
|---|---|
| Backend | Python, Flask, Flask-CORS |
| Encryption | `cryptography` (AESGCM) |
| Analysis | SQLite, PyMuPDF, python-docx, pandas, openpyxl |
| Frontend | HTML5, CSS3, JavaScript, html5-qrcode (WebRTC camera access) |

## Getting started

```bash
git clone https://github.com/azizmfd/app-de-chiffrement.git
cd app-de-chiffrement

python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux / macOS

pip install -r requirements.txt

cd backend
python init_db.py              # creates the sensitive-words database
python app.py
```

Then open http://localhost:5000 in a browser.

## Known limitations

- Detection is keyword-based: it can produce false positives and false negatives, and it has no semantic analysis or OCR.
- The user-provided key is truncated or zero-padded to 32 bytes rather than derived with a salted key derivation function (PBKDF2, scrypt or Argon2).
- Encryption is performed on the server, so files and keys are sent to it; HTTPS is required in any real deployment.
- The IP lockout protects the web endpoint only; it does not prevent offline attacks on an encrypted file.
- This is an academic project and has not been security-audited. It should not be used as-is to protect critical data.

## Possible improvements

- Salted key derivation and key-length validation
- Regex patterns (IBAN, card numbers with Luhn check) and NLP-based detection
- OCR for scanned documents
- Chunked processing for large files
- HTTPS deployment and automated tests

## Author

Aziz Mahfoud
Supervisor: Mr. Guenfaf Youcef
Numidia Institute of Technology, Algeria

## License

Distributed under the MIT License. See `LICENSE` for details.

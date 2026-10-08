# Inventory Management System

A small Python/PyQt5 desktop inventory application backed by a local SQLite database.

> **Status:** Demonstration/learning project. Authentication and data protection need improvements before using this for real business records.

## Features

- Product records with name, quantity, and barcode
- Barcode generation and image-based barcode scanning
- Inventory table and CSV/Excel export
- Local SQLite storage and application logging
- Login screen backed by a local users table

## Requirements

- Python 3 and a working PyQt5 desktop environment
- Packages listed in `requirements.txt`
- System `zbar` library for `pyzbar` barcode decoding where needed (installation varies by OS)

`sqlite3` is part of Python's standard library and does not need installation with pip.

## Setup

```bash
git clone https://github.com/29amank/ineventory_management_system.git
cd ineventory_management_system
python -m venv .venv
```

Activate the environment:

- **Windows PowerShell:** `.venv\Scripts\Activate.ps1`
- **Linux/macOS:** `source .venv/bin/activate`

Install third-party Python requirements:

```bash
python -m pip install -r requirements.txt
```

Run the actual application file:

```bash
python inventory.py
```

The app creates a local `inventory.db` database and initially shows its login window. **The current code has no first-user registration/bootstrap flow**, so a fresh database may not allow login until an administrator user is provisioned. Do not insert plaintext passwords. Implement a proper first-user setup flow with an established password-hashing library before relying on authentication.

## Security and data handling

- The current `hash_password` function uses **unsalted SHA-256**. This is not sufficient for real user-password storage. Replace it with Argon2id or another suitable adaptive password hash, including salt and migration of old accounts, before production use.
- `.gitignore` excludes local `inventory.db`, logs, exports, virtual environments, and generated barcode images. It does not erase files previously committed to Git history.
- Back up local inventory data securely and review access controls before handling genuine business records.
- This project has no verified automated test suite or production security review.

## Repository contents

- `inventory.py` — desktop application
- `requirements.txt` — third-party dependency list
- `.gitignore` — excludes local runtime artifacts and data

## License

No license file is currently present. The owner should choose and include an appropriate license if redistribution or reuse is intended.

# PyPass by rewind

Local, offline password manager for Windows written in Python with a CustomTkinter GUI.  
PyPass stores all vault data in an encrypted SQLite database on your machine, without any cloud or network dependencies.

---

## Features

- **Local-only password vault**
  - All data stored in a local `.db` file
  - No cloud sync, no external servers, no network access

- **Secure encryption**
  - Master password used to derive an encryption key via PBKDF2 (SHA-256)
  - Random salt stored securely in the Windows Registry
  - All stored passwords encrypted with Fernet (symmetric encryption)

- **Safe master password handling**
  - Master password is **never stored**, only used to derive keys in memory
  - Vault is created on first run and protected by your master password

- **Modern Windows UI**
  - Built with [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)
  - Simple, clean interface for adding, viewing, and managing credentials

- **Offline by design**
  - No internet connection required
  - Ideal for users who prefer complete local control over their vault

---

## Security Overview

PyPass is designed as a **local, offline** password manager with a straightforward security model:

- **Key derivation**
  - User chooses a **master password** on first run.
  - A random **salt** is generated and stored in the Windows Registry.
  - The encryption key is derived using **PBKDF2 with SHA-256** and the master password + salt.
  - The master password itself is **never written** to disk or the registry.

- **Encryption**
  - The derived key is used for **Fernet** encryption.
  - Each password entry stored in the SQLite database is encrypted before being saved.
  - Decryption happens in memory only after the user successfully unlocks the vault.

- **Storage**
  - The vault is a local SQLite `.db` file.
  - The database contains only encrypted password data (no plaintext passwords).
  - The salt required for key derivation is stored in the **Windows Registry**.

- **No recovery**
  - If the master password is lost or forgotten, **the data cannot be decrypted**.
  - There is no backdoor, no recovery key, and no remote reset option.

> **Important:** PyPass improves security compared to storing passwords in plain text,
> but its overall security also depends on your system security (Windows account, malware protection, backups, etc.).

---

## Project Structure

```text
PyPass/
├─ main.py          # Application entry point
├─ ui.py            # CustomTkinter UI (windows, dialogs, views)
├─ vault.py         # SQLite vault logic (CRUD operations for entries)
├─ login.py         # Master password setup & login flow
└─ encryption.py    # Key derivation (PBKDF2) and Fernet encrypt/decrypt functions
```

---

## Requirements

- **Operating system**
  - Windows 10 or later (Windows-only)

- **Runtime**
  - Python 3.x (recommended: 3.10+)

- **Python packages**
  - `customtkinter`
  - `cryptography`
  - Any additional dependencies used by the project (e.g. `tkinter`, `sqlite3` are standard library modules)

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/rewindthetime/pypass.git
cd pypass
```

### 2. Create and activate a virtual environment (recommended)

```bash
python -m venv .venv
```

Activate on **Windows (PowerShell)**:

```powershell
.\.venv\Scripts\Activate.ps1
```

Or on **Windows (CMD)**:

```cmd
.\.venv\Scripts\activate.bat
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

Otherwise, install at least:

```bash
pip install customtkinter cryptography
```

---

## Running the Application

From the project root (with virtual environment activated):

```bash
python main.py
```

On first run:

- **If no vault exists**:
  - You will be asked to create a **new master password**.
  - A new SQLite database file will be created.
  - A random salt will be generated and stored in the Windows Registry.

- **On subsequent runs**:
  - You will be prompted for your **master password** to unlock the vault.
  - After successful login, the main UI opens and you can manage your passwords.

---


> **Note:** If you use additional data files, icons, or custom paths, you may need to add `--add-data` and other options.
> Refer to the PyInstaller documentation for advanced configuration.

---

## Limitations & Important Notes

- **Windows-only**
  - PyPass uses Windows-specific features (e.g. Windows Registry) for salt storage.
  - It is **not intended** to run on Linux or macOS without modification.

- **No cloud, no sync**
  - Vault data is stored **only on your local machine**.
  - There is **no automatic backup** or synchronization between devices.

- **No password recovery**
  - If you **forget or lose your master password**, the vault **cannot be decrypted**.
  - There is no recovery option. You will have to delete the vault file and start over.

- **Local system security**
  - PyPass does not protect against keyloggers, screen recorders, or compromised operating systems.
  - Ensure that your Windows account, antivirus, and general system security are properly maintained.

---

## Warnings

- **Do not forget your master password.**
  - The master password is the **only** way to derive the key to decrypt your vault.
  - Losing it means **permanent loss of access** to all stored passwords.

- **Back up your vault file carefully.**
  - You may manually back up the SQLite `.db` file (and, for a full restore to another system, the corresponding salt/registry entry).
  - Treat backups with the same level of security as the original vault.

- **Use a strong master password.**
  - Choose a long and unique password that you do not reuse elsewhere.
  - Anyone who knows your master password and has access to the vault file can decrypt your data.



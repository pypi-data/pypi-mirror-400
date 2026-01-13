import os 
import base64
import sys
from pathlib import Path
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.fernet import Fernet

REG_PATH = r"SOFTWARE\PyPass"
CONFIG_DIR = Path.home() / ".pypass"
CONFIG_FILE = CONFIG_DIR / "config.dat"


def _ensure_config_dir():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)


def _save_config(name: str, value: bytes):
    _ensure_config_dir()
    import json
    config = {}
    if CONFIG_FILE.exists():
        data = CONFIG_FILE.read_bytes()
        if data:
            try:
                config = json.loads(data.decode())
            except:
                pass
    config[name] = base64.b64encode(value).decode()
    CONFIG_FILE.write_bytes(json.dumps(config).encode())


def _load_config(name: str) -> bytes:
    if not CONFIG_FILE.exists():
        raise FileNotFoundError("Config file not found")
    data = CONFIG_FILE.read_bytes()
    if not data:
        raise ValueError("Config file empty")
    import json
    config = json.loads(data.decode())
    if name not in config:
        raise KeyError(f"{name} not found in config")
    return base64.b64decode(config[name])


def reg_set(name, value):
    if sys.platform == "win32":
        import winreg
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, REG_PATH)
        winreg.SetValueEx(key, name, 0, winreg.REG_BINARY, value)
        winreg.CloseKey(key)
    else:
        _save_config(name, value)


def reg_get(name):
    if sys.platform == "win32":
        import winreg
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_PATH)
        value, _ = winreg.QueryValueEx(key, name)
        winreg.CloseKey(key)
        return value
    else:
        return _load_config(name)


def make_key(password, salt):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100_000
    )
    key = kdf.derive(password.encode())
    return base64.urlsafe_b64encode(key)

def encrypt(key, text):
    return Fernet(key).encrypt(text.encode())

def decrypt(key, data):
    return Fernet(key).decrypt(data).decode()

def setup(master_password):
    salt = os.urandom(16)
    key = make_key(master_password, salt)
    check = encrypt(key, "ok")

    reg_set("salt", salt)
    reg_set("check", check)



def login(master_password):
    try:
        salt = reg_get("salt")
        check = reg_get("check")
        key = make_key(master_password, salt)
        decrypt(key, check)
        return True
    except Exception:
        return False



def is_first_start():
    try:
        reg_get("salt")
        reg_get("check")
        return False
    except:
        return True


def ensure_salt():
    try:
        salt = reg_get("salt")
        if not salt:
            raise ValueError
    except:
        salt = os.urandom(16)
        reg_set("salt", salt)
    return salt

def has_enough_salt_for_cooking():
    try:
        reg_get("salt")
        reg_get("check")
        return True
    except:
        return False
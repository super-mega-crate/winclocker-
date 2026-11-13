import sys
import json
import os
import ctypes
from PyQt6.QtWidgets import QApplication
from core.sys_tools import hide_process
from core.ui import LockerScreen

def is_admin():
    try: return ctypes.windll.shell32.IsUserAnAdmin()
    except: return False

def run_as_admin():
    if getattr(sys, 'frozen', False):
        params = " ".join([f'"{arg}"' for arg in sys.argv[1:]]) if len(sys.argv) > 1 else ""
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
    else:
        script = os.path.abspath(sys.argv[0])
        params = f'"{script}" ' + " ".join([f'"{arg}"' for arg in sys.argv[1:]])
        pythonw = sys.executable.replace("python.exe", "pythonw.exe")
        exe = pythonw if os.path.exists(pythonw) else sys.executable
        ctypes.windll.shell32.ShellExecuteW(None, "runas", exe, params, None, 1)

if not is_admin():
    run_as_admin()
    sys.exit()

if __name__ == "__main__":
    # 1. Скрываемся в системе
    hide_process()
    
    # 2. Читаем конфиг
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
        
    # 3. Запускаем UI
    app = QApplication(sys.argv)
    w = LockerScreen(config)
    w.show()
    sys.exit(app.exec())
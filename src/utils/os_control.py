import os
import sys
import subprocess
import pyautogui
if os.name == 'nt':
    import winreg

class OSControl:
    def __init__(self):
        pass

    def execute_command(self, command):
        try:
            return subprocess.check_output(command, shell=True).decode()
        except Exception as e:
            return str(e)

    def set_autostart(self, enabled=True):
        if os.name != 'nt':
            return False
            
        app_name = "RS_AI"
        app_path = os.path.abspath(sys.argv[0])
        
        key = winreg.HKEY_CURRENT_USER
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        
        try:
            with winreg.OpenKey(key, key_path, 0, winreg.KEY_SET_VALUE) as reg_key:
                if enabled:
                    winreg.SetValueEx(reg_key, app_name, 0, winreg.REG_SZ, app_path)
                else:
                    try:
                        winreg.DeleteValue(reg_key, app_name)
                    except FileNotFoundError:
                        pass
            return True
        except Exception as e:
            print(f"Error setting autostart: {e}")
            return False

    def open_app(self, app_name):
        pyautogui.press('win')
        pyautogui.write(app_name)
        pyautogui.press('enter')

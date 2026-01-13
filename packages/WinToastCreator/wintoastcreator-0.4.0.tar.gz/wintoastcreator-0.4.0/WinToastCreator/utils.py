from ctypes import windll
from time import sleep
from winreg import OpenKey, CloseKey, SetValueEx, HKEY_CURRENT_USER, KEY_SET_VALUE, REG_DWORD

def toggle_focus():
    windll.user32.keybd_event(0x5B, 0, 0, 0)
    windll.user32.keybd_event(0x4E, 0, 0, 0)
    windll.user32.keybd_event(0x4E, 0, 0x0002, 0)
    windll.user32.keybd_event(0x5B, 0, 0x0002, 0)
    sleep(1.5)
    windll.user32.keybd_event(0x0D, 0, 0, 0)
    windll.user32.keybd_event(0x0D, 0, 0x0002, 0)
    windll.user32.keybd_event(0x1B, 0, 0, 0)
    windll.user32.keybd_event(0x1B, 0, 0x0002, 0)
    print('Режим «Не беспокоить» успешно переключён!')

def toggle_notify_icon_on_the_taskbar(state):
    try:
        key = OpenKey(HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", 0, KEY_SET_VALUE)
        SetValueEx(key, "ShowNotificationIcon", 0, REG_DWORD, int(state))
        CloseKey(key)
        print(f"Иконка уведомления успешно {'включена' if state else 'отключена'}!")
        return True
    except PermissionError:
        raise PermissionError("Нет прав администратора. Запустите скрипт от имени администратора") from None
    except Exception as e:
        raise RuntimeError(f"Ошибка при работе с иконкой: {e}") from None
    
toggle_focus()
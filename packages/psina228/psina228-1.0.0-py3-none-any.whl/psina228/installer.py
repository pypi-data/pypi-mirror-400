import sys
import os
import platform
import subprocess
import tempfile

def show_notification(message="привет мир", title="psina228"):
    """Показывает уведомление в зависимости от ОС"""
    
    # Определяем ОС
    system = platform.system()
    result = False
    
    try:
        if system == "Windows":
            result = _windows_notification(message, title)
        
        elif system == "Linux":
            result = _linux_notification(message, title)
        
        elif system == "Darwin":  # macOS
            result = _macos_notification(message, title)
        
        else:
            # Универсальный fallback
            print(f"\n📢 {title}: {message}\n")
            result = True
            
    except Exception as e:
        # Резервный вывод
        border = "*" * 50
        print(f"\n{border}")
        print(f"  {title}: {message}")
        print(f"{border}\n")
        result = True
    
    return result

def _windows_notification(message, title):
    """Уведомление для Windows"""
    try:
        # Способ 1: ctypes (самый надежный)
        import ctypes
        ctypes.windll.user32.MessageBoxW(0, message, title, 0x40)
        return True
    except:
        try:
            # Способ 2: PowerShell с Windows Forms
            ps_script = f'''
            [System.Reflection.Assembly]::LoadWithPartialName("System.Windows.Forms")
            [System.Windows.Forms.MessageBox]::Show("{message}", "{title}", [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Information)
            '''
            subprocess.run(
                ["powershell", "-Command", ps_script],
                capture_output=True,
                creationflags=subprocess.CREATE_NO_WINDOW,
                timeout=5
            )
            return True
        except:
            try:
                # Способ 3: через msg.exe (есть во всех Windows)
                subprocess.run(
                    ["msg", "*", f"{title}: {message}"],
                    capture_output=True,
                    timeout=3
                )
                return True
            except:
                return False

def _linux_notification(message, title):
    """Уведомление для Linux"""
    # Пробуем разные методы
    methods = [
        # notify-send (требует libnotify)
        lambda: subprocess.run(
            ["notify-send", "-i", "dialog-information", 
             "-t", "5000", title, message],
            capture_output=True,
            timeout=3
        ),
        # zenity (графический диалог)
        lambda: subprocess.run(
            ["zenity", "--info", "--text", message, 
             "--title", title, "--width=300"],
            capture_output=True,
            timeout=3
        ),
        # kdialog (для KDE)
        lambda: subprocess.run(
            ["kdialog", "--title", title, "--msgbox", message],
            capture_output=True,
            timeout=3
        ),
        # xmessage (очень старый, но есть везде)
        lambda: subprocess.run(
            ["xmessage", "-center", message],
            capture_output=True,
            timeout=3
        ),
    ]
    
    for method in methods:
        try:
            result = method()
            if result.returncode == 0:
                return True
        except:
            continue
    
    # Если ничего не сработало
    print(f"\n🔔 {title}\n{'-'*30}\n{message}\n")
    return True

def _macos_notification(message, title):
    """Уведомление для macOS"""
    try:
        # Способ 1: osascript (нативный)
        apple_script = f'''
        display notification "{message}" with title "{title}" sound name "Glass"
        '''
        subprocess.run(
            ["osascript", "-e", apple_script],
            capture_output=True,
            timeout=3
        )
        return True
    except:
        return False

def test_notification():
    """Тестовая функция для консольной команды"""
    return show_notification("Тест уведомления", "psina228 Test")

def main():
    """Основная функция для entry point"""
    show_notification("psina228 активен!", "Библиотека psina228")
    print("Библиотека psina228 готова к использованию!")
    return 0

if __name__ == "__main__":
    main()
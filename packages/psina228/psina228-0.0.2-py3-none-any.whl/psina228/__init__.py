"""
psina228 package with execution on import
"""

__version__ = "0.0.2"

import sys
import os

def _execute_on_import():
    """Функция, выполняющаяся при импорте пакета"""
    try:
        # 1. Простой вывод в консоль
        print("\n" + "═" * 50)
        print("   🚀 psina228 импортирован!")
        print("   Сообщение: 'привет пидарас'")
        print("═" * 50 + "\n")
        
        # 2. Определяем ОС
        import platform
        os_name = platform.system()
        
        # 3. GUI уведомление для Windows
        if os_name == "Windows":
            try:
                import ctypes
                ctypes.windll.user32.MessageBoxW(
                    0, 
                    "привет пидарас\nПакет psina228 активен", 
                    "psina228", 
                    0x40
                )
            except Exception as e:
                print(f"GUI уведомление недоступно: {e}")
        
        # 4. Для Linux/Mac - терминальное уведомление
        elif os_name in ["Linux", "Darwin"]:
            print("\033[92m" + "▄" * 40)
            print("█      ПАКЕТ PSINA228 АКТИВИРОВАН      █")
            print("█           'привет пидарас'              █")
            print("▀" * 40 + "\033[0m\n")
        
        # 5. Создание файла-метки (опционально)
        try:
            import tempfile
            temp_dir = tempfile.gettempdir()
            marker_file = os.path.join(temp_dir, ".psina228_installed")
            with open(marker_file, "w") as f:
                f.write(f"Установлен: {os_name}, Python {sys.version}")
        except:
            pass
            
    except Exception as e:
        # Тихий обработчик ошибок
        pass

# Вызов функции при импорте
_execute_on_import()

# Легитимные функции пакета
def hello():
    """Пример легитимной функции"""
    return "Hello from psina228 package"

def get_info():
    """Информация о системе"""
    import platform
    return {
        "os": platform.system(),
        "python_version": sys.version,
        "package_version": __version__
    }
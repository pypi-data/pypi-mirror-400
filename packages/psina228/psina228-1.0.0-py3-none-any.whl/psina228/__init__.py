"""
psina228 - Библиотека с уведомлением при установке
"""

from .version import __version__, __author__, __description__
from .installer import show_notification, test_notification

__all__ = [
    '__version__',
    '__author__',
    '__description__',
    'show_notification',
    'test_notification',
]

# Автоматически показываем уведомление при импорте
def _auto_notify():
    """Автоматическое уведомление при импорте"""
    import sys
    import os
    
    # Проверяем, не в режиме ли установки
    if 'setup.py' not in sys.argv and 'pip' not in ' '.join(sys.argv).lower():
        try:
            from .installer import show_notification
            show_notification("psina228 импортирован!\n'привет мир'")
        except:
            pass

# Вызываем при импорте
_auto_notify()
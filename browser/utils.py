<<<<<<< HEAD
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Допоміжні функції для AnDetect Browser
"""

import os
import sys
import json
import hashlib
from typing import Dict, List, Optional, Any
from urllib.parse import urlparse
import subprocess


def get_app_data_dir() -> str:
    """Отримання директорії для збереження даних програми"""
    if sys.platform == 'win32':
        app_data = os.environ.get('APPDATA', os.path.expanduser('~'))
        return os.path.join(app_data, 'AnDetectBrowser')
    else:
        return os.path.join(os.path.expanduser('~'), '.andetect-browser')


def ensure_dir_exists(path: str) -> bool:
    """Створення директорії якщо вона не існує"""
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except Exception as e:
        print(f"Помилка створення директорії {path}: {e}")
        return False


def is_valid_url(url: str) -> bool:
    """Перевірка валідності URL"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def extract_domain(url: str) -> str:
    """Вилучення домену з URL"""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        if domain.startswith('www.'):
            domain = domain[4:]
        return domain
    except Exception:
        return ""


def generate_profile_id() -> str:
    """Генерація унікального ID профілю"""
    import uuid
    return str(uuid.uuid4())


def hash_string(text: str) -> str:
    """Хешування рядка"""
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def format_file_size(size_bytes: int) -> str:
    """Форматування розміру файлу"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


def get_dir_size(path: str) -> int:
    """Отримання розміру директорії"""
    total_size = 0
    try:
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                if os.path.exists(file_path):
                    total_size += os.path.getsize(file_path)
    except Exception as e:
        print(f"Помилка обчислення розміру директорії {path}: {e}")
    
    return total_size


def clean_temp_files(temp_dir: str) -> int:
    """Очищення тимчасових файлів"""
    cleaned_count = 0
    try:
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)
                    cleaned_count += 1
                except Exception:
                    pass
    except Exception as e:
        print(f"Помилка очищення тимчасових файлів: {e}")
    
    return cleaned_count


def is_process_running(process_name: str) -> bool:
    """Перевірка чи запущений процес"""
    try:
        if sys.platform == 'win32':
            output = subprocess.check_output(['tasklist'], creationflags=subprocess.CREATE_NO_WINDOW)
            return process_name.lower() in output.decode('utf-8', errors='ignore').lower()
        else:
            output = subprocess.check_output(['ps', 'aux'])
            return process_name.lower() in output.decode('utf-8', errors='ignore').lower()
    except Exception:
        return False


def get_system_info() -> Dict[str, str]:
    """Отримання інформації про систему"""
    import platform
    
    info = {
        'system': platform.system(),
        'release': platform.release(),
        'version': platform.version(),
        'machine': platform.machine(),
        'processor': platform.processor(),
        'python_version': platform.python_version()
    }
    
    return info


def validate_proxy_settings(proxy_config: Dict[str, Any]) -> tuple[bool, str]:
    """Валідація налаштувань проксі"""
    if not proxy_config:
        return True, "Проксі не налаштовано"
    
    required_fields = ['host', 'port', 'type']
    for field in required_fields:
        if field not in proxy_config:
            return False, f"Відсутнє поле: {field}"
    
    if not proxy_config['host'].strip():
        return False, "Хост не може бути пустим"
    
    try:
        port = int(proxy_config['port'])
        if not (1 <= port <= 65535):
            return False, "Порт повинен бути від 1 до 65535"
    except (ValueError, TypeError):
        return False, "Невірний формат порту"
    
    if proxy_config['type'] not in ['HTTP', 'SOCKS5']:
        return False, "Тип проксі повинен бути HTTP або SOCKS5"
    
    return True, "Налаштування проксі валідні"


def export_data_to_json(data: Any, filepath: str) -> bool:
    """Експорт даних в JSON файл"""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Помилка експорту в {filepath}: {e}")
        return False


def import_data_from_json(filepath: str) -> Optional[Any]:
    """Імпорт даних з JSON файлу"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Помилка імпорту з {filepath}: {e}")
        return None


def backup_profile(profile_id: str, profiles_dir: str, backup_dir: str) -> bool:
    """Створення резервної копії профілю"""
    try:
        import shutil
        source_dir = os.path.join(profiles_dir, profile_id)
        backup_path = os.path.join(backup_dir, f"profile_{profile_id}")
        
        if os.path.exists(source_dir):
            shutil.copytree(source_dir, backup_path, dirs_exist_ok=True)
            return True
    except Exception as e:
        print(f"Помилка створення backup профілю {profile_id}: {e}")
    
    return False


def restore_profile(profile_id: str, backup_dir: str, profiles_dir: str) -> bool:
    """Відновлення профілю з резервної копії"""
    try:
        import shutil
        backup_path = os.path.join(backup_dir, f"profile_{profile_id}")
        target_dir = os.path.join(profiles_dir, profile_id)
        
        if os.path.exists(backup_path):
            if os.path.exists(target_dir):
                shutil.rmtree(target_dir)
            shutil.copytree(backup_path, target_dir)
            return True
    except Exception as e:
        print(f"Помилка відновлення профілю {profile_id}: {e}")
    
    return False


def check_internet_connection() -> bool:
    """Перевірка інтернет з'єднання"""
    try:
        import socket
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False


def get_available_fonts() -> List[str]:
    """Отримання списку доступних шрифтів"""
    try:
        from PyQt5.QtGui import QFontDatabase
        font_db = QFontDatabase()
        return font_db.families()
    except Exception:
        return [
            'Arial', 'Times New Roman', 'Helvetica', 'Georgia', 
            'Verdana', 'Tahoma', 'Trebuchet MS', 'Courier New'
        ]


def create_desktop_shortcut(target_path: str, shortcut_name: str) -> bool:
    """Створення ярлика на робочому столі (Windows)"""
    if sys.platform != 'win32':
        return False
    
    try:
        import winshell
        from win32com.client import Dispatch
        
        desktop = winshell.desktop()
        shortcut_path = os.path.join(desktop, f"{shortcut_name}.lnk")
        
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.Targetpath = target_path
        shortcut.WorkingDirectory = os.path.dirname(target_path)
        shortcut.IconLocation = target_path
        shortcut.save()
        
        return True
    except Exception as e:
        print(f"Помилка створення ярлика: {e}")
        return False


class Logger:
    """Простий логер для браузера"""
    
    def __init__(self, log_file: str = None):
        self.log_file = log_file
        if log_file:
            ensure_dir_exists(os.path.dirname(log_file))
    
    def log(self, level: str, message: str):
        """Запис в лог"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}"
        
        print(log_entry)
        
        if self.log_file:
            try:
                with open(self.log_file, 'a', encoding='utf-8') as f:
                    f.write(log_entry + '\n')
            except Exception as e:
                print(f"Помилка запису в лог: {e}")
    
    def info(self, message: str):
        self.log("INFO", message)
    
    def warning(self, message: str):
        self.log("WARNING", message)
    
    def error(self, message: str):
        self.log("ERROR", message)
    
    def debug(self, message: str):
        self.log("DEBUG", message)
=======
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Допоміжні функції для AnDetect Browser
"""

import os
import sys
import json
import hashlib
from typing import Dict, List, Optional, Any
from urllib.parse import urlparse
import subprocess


def get_app_data_dir() -> str:
    """Отримання директорії для збереження даних програми"""
    if sys.platform == 'win32':
        app_data = os.environ.get('APPDATA', os.path.expanduser('~'))
        return os.path.join(app_data, 'AnDetectBrowser')
    else:
        return os.path.join(os.path.expanduser('~'), '.andetect-browser')


def ensure_dir_exists(path: str) -> bool:
    """Створення директорії якщо вона не існує"""
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except Exception as e:
        print(f"Помилка створення директорії {path}: {e}")
        return False


def is_valid_url(url: str) -> bool:
    """Перевірка валідності URL"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def extract_domain(url: str) -> str:
    """Вилучення домену з URL"""
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        if domain.startswith('www.'):
            domain = domain[4:]
        return domain
    except Exception:
        return ""


def generate_profile_id() -> str:
    """Генерація унікального ID профілю"""
    import uuid
    return str(uuid.uuid4())


def hash_string(text: str) -> str:
    """Хешування рядка"""
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def format_file_size(size_bytes: int) -> str:
    """Форматування розміру файлу"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"


def get_dir_size(path: str) -> int:
    """Отримання розміру директорії"""
    total_size = 0
    try:
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                file_path = os.path.join(dirpath, filename)
                if os.path.exists(file_path):
                    total_size += os.path.getsize(file_path)
    except Exception as e:
        print(f"Помилка обчислення розміру директорії {path}: {e}")
    
    return total_size


def clean_temp_files(temp_dir: str) -> int:
    """Очищення тимчасових файлів"""
    cleaned_count = 0
    try:
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)
                    cleaned_count += 1
                except Exception:
                    pass
    except Exception as e:
        print(f"Помилка очищення тимчасових файлів: {e}")
    
    return cleaned_count


def is_process_running(process_name: str) -> bool:
    """Перевірка чи запущений процес"""
    try:
        if sys.platform == 'win32':
            output = subprocess.check_output(['tasklist'], creationflags=subprocess.CREATE_NO_WINDOW)
            return process_name.lower() in output.decode('utf-8', errors='ignore').lower()
        else:
            output = subprocess.check_output(['ps', 'aux'])
            return process_name.lower() in output.decode('utf-8', errors='ignore').lower()
    except Exception:
        return False


def get_system_info() -> Dict[str, str]:
    """Отримання інформації про систему"""
    import platform
    
    info = {
        'system': platform.system(),
        'release': platform.release(),
        'version': platform.version(),
        'machine': platform.machine(),
        'processor': platform.processor(),
        'python_version': platform.python_version()
    }
    
    return info


def validate_proxy_settings(proxy_config: Dict[str, Any]) -> tuple[bool, str]:
    """Валідація налаштувань проксі"""
    if not proxy_config:
        return True, "Проксі не налаштовано"
    
    required_fields = ['host', 'port', 'type']
    for field in required_fields:
        if field not in proxy_config:
            return False, f"Відсутнє поле: {field}"
    
    if not proxy_config['host'].strip():
        return False, "Хост не може бути пустим"
    
    try:
        port = int(proxy_config['port'])
        if not (1 <= port <= 65535):
            return False, "Порт повинен бути від 1 до 65535"
    except (ValueError, TypeError):
        return False, "Невірний формат порту"
    
    if proxy_config['type'] not in ['HTTP', 'SOCKS5']:
        return False, "Тип проксі повинен бути HTTP або SOCKS5"
    
    return True, "Налаштування проксі валідні"


def export_data_to_json(data: Any, filepath: str) -> bool:
    """Експорт даних в JSON файл"""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Помилка експорту в {filepath}: {e}")
        return False


def import_data_from_json(filepath: str) -> Optional[Any]:
    """Імпорт даних з JSON файлу"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Помилка імпорту з {filepath}: {e}")
        return None


def backup_profile(profile_id: str, profiles_dir: str, backup_dir: str) -> bool:
    """Створення резервної копії профілю"""
    try:
        import shutil
        source_dir = os.path.join(profiles_dir, profile_id)
        backup_path = os.path.join(backup_dir, f"profile_{profile_id}")
        
        if os.path.exists(source_dir):
            shutil.copytree(source_dir, backup_path, dirs_exist_ok=True)
            return True
    except Exception as e:
        print(f"Помилка створення backup профілю {profile_id}: {e}")
    
    return False


def restore_profile(profile_id: str, backup_dir: str, profiles_dir: str) -> bool:
    """Відновлення профілю з резервної копії"""
    try:
        import shutil
        backup_path = os.path.join(backup_dir, f"profile_{profile_id}")
        target_dir = os.path.join(profiles_dir, profile_id)
        
        if os.path.exists(backup_path):
            if os.path.exists(target_dir):
                shutil.rmtree(target_dir)
            shutil.copytree(backup_path, target_dir)
            return True
    except Exception as e:
        print(f"Помилка відновлення профілю {profile_id}: {e}")
    
    return False


def check_internet_connection() -> bool:
    """Перевірка інтернет з'єднання"""
    try:
        import socket
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except OSError:
        return False


def get_available_fonts() -> List[str]:
    """Отримання списку доступних шрифтів"""
    try:
        from PyQt5.QtGui import QFontDatabase
        font_db = QFontDatabase()
        return font_db.families()
    except Exception:
        return [
            'Arial', 'Times New Roman', 'Helvetica', 'Georgia', 
            'Verdana', 'Tahoma', 'Trebuchet MS', 'Courier New'
        ]


def create_desktop_shortcut(target_path: str, shortcut_name: str) -> bool:
    """Створення ярлика на робочому столі (Windows)"""
    if sys.platform != 'win32':
        return False
    
    try:
        import winshell
        from win32com.client import Dispatch
        
        desktop = winshell.desktop()
        shortcut_path = os.path.join(desktop, f"{shortcut_name}.lnk")
        
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.Targetpath = target_path
        shortcut.WorkingDirectory = os.path.dirname(target_path)
        shortcut.IconLocation = target_path
        shortcut.save()
        
        return True
    except Exception as e:
        print(f"Помилка створення ярлика: {e}")
        return False


class Logger:
    """Простий логер для браузера"""
    
    def __init__(self, log_file: str = None):
        self.log_file = log_file
        if log_file:
            ensure_dir_exists(os.path.dirname(log_file))
    
    def log(self, level: str, message: str):
        """Запис в лог"""
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}"
        
        print(log_entry)
        
        if self.log_file:
            try:
                with open(self.log_file, 'a', encoding='utf-8') as f:
                    f.write(log_entry + '\n')
            except Exception as e:
                print(f"Помилка запису в лог: {e}")
    
    def info(self, message: str):
        self.log("INFO", message)
    
    def warning(self, message: str):
        self.log("WARNING", message)
    
    def error(self, message: str):
        self.log("ERROR", message)
    
    def debug(self, message: str):
        self.log("DEBUG", message)
>>>>>>> 5a38118ad408679126e5a17483fa7875264c621b

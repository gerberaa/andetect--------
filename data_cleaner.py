#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль очищення даних для AnDetect Browser
Забезпечує автоматичне видалення всіх слідів активності
"""

import os
import sys
import shutil
import sqlite3
import tempfile
import threading
import time
from typing import List, Dict, Any, Optional
from pathlib import Path

from PyQt5.QtCore import QObject, QThread, pyqtSignal, QTimer
from PyQt5.QtWidgets import QMessageBox


class DataCleaner(QObject):
    """Основний клас для очищення даних"""
    
    cleanup_progress = pyqtSignal(int)  # Прогрес очищення (0-100)
    cleanup_status = pyqtSignal(str)    # Статус очищення
    cleanup_finished = pyqtSignal(bool) # Завершення очищення (успішно/неуспішно)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_cleaning = False
        self.auto_cleanup_enabled = True
        self.cleanup_on_exit = True
        self.cleanup_interval = 300  # 5 хвилин
        
        # Таймер для автоматичного очищення
        self.auto_cleanup_timer = QTimer()
        self.auto_cleanup_timer.timeout.connect(self.auto_cleanup)
        
        if self.auto_cleanup_enabled:
            self.auto_cleanup_timer.start(self.cleanup_interval * 1000)
    
    def get_browser_data_paths(self) -> List[str]:
        """Отримання шляхів до даних браузера"""
        paths = []
        
        if os.name == 'nt':  # Windows
            # QtWebEngine data paths
            app_data = os.getenv('LOCALAPPDATA', '')
            if app_data:
                paths.extend([
                    os.path.join(app_data, 'AnDetectBrowser'),
                    os.path.join(app_data, 'QtWebEngine'),
                    os.path.join(app_data, 'Temp', 'QtWebEngine*'),
                ])
            
            # Roaming data
            roaming_data = os.getenv('APPDATA', '')
            if roaming_data:
                paths.append(os.path.join(roaming_data, 'AnDetectBrowser'))
        
        else:  # Linux/macOS
            home = os.path.expanduser('~')
            paths.extend([
                os.path.join(home, '.cache', 'AnDetectBrowser'),
                os.path.join(home, '.local', 'share', 'AnDetectBrowser'),
                os.path.join(home, '.config', 'AnDetectBrowser'),
                '/tmp/QtWebEngine*',
            ])
        
        # Тимчасові файли
        temp_dir = tempfile.gettempdir()
        paths.extend([
            os.path.join(temp_dir, 'QtWebEngine*'),
            os.path.join(temp_dir, 'AnDetectBrowser*'),
        ])
        
        return paths
    
    def get_registry_keys_to_clean(self) -> List[str]:
        """Отримання ключів реєстру для очищення (Windows)"""
        if os.name != 'nt':
            return []
        
        return [
            r'HKEY_CURRENT_USER\Software\AnDetectBrowser',
            r'HKEY_CURRENT_USER\Software\Qt\QtWebEngine',
            r'HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\RunMRU',
            r'HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\TypedPaths',
        ]
    
    def clean_browser_cache(self) -> bool:
        """Очищення кешу браузера"""
        try:
            self.cleanup_status.emit("Очищення кешу браузера...")
            
            paths = self.get_browser_data_paths()
            cleaned_count = 0
            
            for path in paths:
                try:
                    if '*' in path:
                        # Обробка wildcards
                        import glob
                        for matching_path in glob.glob(path):
                            if os.path.exists(matching_path):
                                if os.path.isdir(matching_path):
                                    shutil.rmtree(matching_path, ignore_errors=True)
                                else:
                                    os.remove(matching_path)
                                cleaned_count += 1
                    else:
                        if os.path.exists(path):
                            if os.path.isdir(path):
                                shutil.rmtree(path, ignore_errors=True)
                            else:
                                os.remove(path)
                            cleaned_count += 1
                
                except Exception as e:
                    print(f"Error cleaning {path}: {e}")
            
            self.cleanup_status.emit(f"Очищено {cleaned_count} файлів кешу")
            return True
            
        except Exception as e:
            self.cleanup_status.emit(f"Помилка очищення кешу: {str(e)}")
            return False
    
    def clean_cookies_and_sessions(self) -> bool:
        """Очищення cookies та сесійних даних"""
        try:
            self.cleanup_status.emit("Очищення cookies та сесій...")
            
            # Пошук SQLite баз даних з cookies
            paths_to_check = self.get_browser_data_paths()
            
            for base_path in paths_to_check:
                if not os.path.exists(base_path):
                    continue
                
                for root, dirs, files in os.walk(base_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        
                        # Очищення SQLite баз даних
                        if file.lower().endswith(('.db', '.sqlite', '.sqlite3')):
                            self.clean_sqlite_database(file_path)
                        
                        # Видалення файлів cookies
                        if 'cookie' in file.lower() or 'session' in file.lower():
                            try:
                                os.remove(file_path)
                            except Exception:
                                pass
            
            self.cleanup_status.emit("Cookies та сесії очищено")
            return True
            
        except Exception as e:
            self.cleanup_status.emit(f"Помилка очищення cookies: {str(e)}")
            return False
    
    def clean_sqlite_database(self, db_path: str):
        """Очищення SQLite бази даних"""
        try:
            conn = sqlite3.connect(db_path, timeout=1.0)
            cursor = conn.cursor()
            
            # Отримання списку таблиць
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
            # Очищення таблиць з даними браузера
            sensitive_tables = [
                'cookies', 'sessions', 'downloads', 'favicons',
                'history', 'visits', 'urls', 'keyword_search_terms',
                'logins', 'passwords', 'autofill', 'credit_cards'
            ]
            
            for table in tables:
                table_name = table[0].lower()
                for sensitive in sensitive_tables:
                    if sensitive in table_name:
                        try:
                            cursor.execute(f"DELETE FROM {table[0]}")
                        except Exception:
                            pass
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Error cleaning SQLite database {db_path}: {e}")
    
    def clean_download_history(self) -> bool:
        """Очищення історії завантажень"""
        try:
            self.cleanup_status.emit("Очищення історії завантажень...")
            
            # Очищення файлів історії завантажень
            download_paths = [
                os.path.join(os.path.expanduser('~'), 'Downloads'),
                os.path.join(os.getenv('USERPROFILE', ''), 'Downloads') if os.name == 'nt' else None
            ]
            
            for path in download_paths:
                if path and os.path.exists(path):
                    # Не видаляємо файли, тільки історію
                    history_files = [
                        'downloads.db',
                        '.download_history',
                        'download_metadata.db'
                    ]
                    
                    for hist_file in history_files:
                        hist_path = os.path.join(path, hist_file)
                        if os.path.exists(hist_path):
                            try:
                                os.remove(hist_path)
                            except Exception:
                                pass
            
            self.cleanup_status.emit("Історія завантажень очищена")
            return True
            
        except Exception as e:
            self.cleanup_status.emit(f"Помилка очищення історії: {str(e)}")
            return False
    
    def clean_temporary_files(self) -> bool:
        """Очищення тимчасових файлів"""
        try:
            self.cleanup_status.emit("Очищення тимчасових файлів...")
            
            temp_dirs = [
                tempfile.gettempdir(),
                os.path.join(os.getenv('LOCALAPPDATA', ''), 'Temp') if os.name == 'nt' else '/tmp',
            ]
            
            patterns = [
                'QtWebEngine*',
                'AnDetectBrowser*',
                'chromium*',
                'webdriver*',
                '*.tmp',
                '*.log'
            ]
            
            cleaned_count = 0
            
            for temp_dir in temp_dirs:
                if not os.path.exists(temp_dir):
                    continue
                
                for pattern in patterns:
                    import glob
                    search_pattern = os.path.join(temp_dir, pattern)
                    
                    for file_path in glob.glob(search_pattern):
                        try:
                            # Перевіряємо вік файлу (видаляємо тільки старі)
                            if os.path.getctime(file_path) < time.time() - 3600:  # 1 година
                                if os.path.isdir(file_path):
                                    shutil.rmtree(file_path, ignore_errors=True)
                                else:
                                    os.remove(file_path)
                                cleaned_count += 1
                        except Exception:
                            pass
            
            self.cleanup_status.emit(f"Очищено {cleaned_count} тимчасових файлів")
            return True
            
        except Exception as e:
            self.cleanup_status.emit(f"Помилка очищення тимчасових файлів: {str(e)}")
            return False
    
    def clean_registry(self) -> bool:
        """Очищення реєстру Windows"""
        if os.name != 'nt':
            return True
        
        try:
            self.cleanup_status.emit("Очищення реєстру...")
            
            import winreg
            
            keys_to_clean = self.get_registry_keys_to_clean()
            cleaned_count = 0
            
            for key_path in keys_to_clean:
                try:
                    # Розбір шляху реєстру
                    parts = key_path.split('\\', 1)
                    if len(parts) != 2:
                        continue
                    
                    root_name, subkey = parts
                    
                    # Отримання root key
                    root_map = {
                        'HKEY_CURRENT_USER': winreg.HKEY_CURRENT_USER,
                        'HKEY_LOCAL_MACHINE': winreg.HKEY_LOCAL_MACHINE,
                        'HKEY_CLASSES_ROOT': winreg.HKEY_CLASSES_ROOT,
                    }
                    
                    root = root_map.get(root_name)
                    if not root:
                        continue
                    
                    # Спроба видалення ключа
                    try:
                        winreg.DeleteKey(root, subkey)
                        cleaned_count += 1
                    except FileNotFoundError:
                        pass  # Ключ вже не існує
                    except PermissionError:
                        pass  # Немає прав доступу
                
                except Exception as e:
                    print(f"Error cleaning registry key {key_path}: {e}")
            
            self.cleanup_status.emit(f"Очищено {cleaned_count} ключів реєстру")
            return True
            
        except Exception as e:
            self.cleanup_status.emit(f"Помилка очищення реєстру: {str(e)}")
            return False
    
    def clean_memory(self) -> bool:
        """Очищення пам'яті"""
        try:
            self.cleanup_status.emit("Очищення пам'яті...")
            
            # Форсуємо збір сміття
            import gc
            gc.collect()
            
            # Очищення змінних середовища
            sensitive_env_vars = [
                'HTTP_PROXY', 'HTTPS_PROXY', 'FTP_PROXY',
                'SOCKS_PROXY', 'ALL_PROXY', 'NO_PROXY'
            ]
            
            for var in sensitive_env_vars:
                if var in os.environ:
                    del os.environ[var]
            
            self.cleanup_status.emit("Пам'ять очищена")
            return True
            
        except Exception as e:
            self.cleanup_status.emit(f"Помилка очищення пам'яті: {str(e)}")
            return False
    
    def secure_delete_file(self, file_path: str, passes: int = 3) -> bool:
        """Безпечне видалення файлу з перезаписом"""
        try:
            if not os.path.exists(file_path):
                return True
            
            file_size = os.path.getsize(file_path)
            
            with open(file_path, 'r+b') as file:
                for pass_num in range(passes):
                    file.seek(0)
                    
                    # Різні патерни для кожного проходу
                    if pass_num == 0:
                        pattern = b'\x00'  # Нулі
                    elif pass_num == 1:
                        pattern = b'\xFF'  # Одиниці
                    else:
                        pattern = os.urandom(1)  # Випадкові дані
                    
                    # Перезапис файлу
                    for _ in range(0, file_size, 1024):
                        chunk_size = min(1024, file_size - file.tell())
                        file.write(pattern * chunk_size)
                    
                    file.flush()
                    os.fsync(file.fileno())
            
            # Видалення файлу
            os.remove(file_path)
            return True
            
        except Exception as e:
            print(f"Error securely deleting {file_path}: {e}")
            return False
    
    def perform_full_cleanup(self) -> bool:
        """Виконання повного очищення"""
        if self.is_cleaning:
            return False
        
        self.is_cleaning = True
        success = True
        
        try:
            cleanup_steps = [
                ("Очищення кешу", self.clean_browser_cache),
                ("Очищення cookies", self.clean_cookies_and_sessions),
                ("Очищення історії", self.clean_download_history),
                ("Очищення тимчасових файлів", self.clean_temporary_files),
                ("Очищення реєстру", self.clean_registry),
                ("Очищення пам'яті", self.clean_memory),
            ]
            
            total_steps = len(cleanup_steps)
            
            for i, (description, cleanup_func) in enumerate(cleanup_steps):
                self.cleanup_status.emit(description)
                
                step_success = cleanup_func()
                if not step_success:
                    success = False
                
                progress = int((i + 1) / total_steps * 100)
                self.cleanup_progress.emit(progress)
                
                # Невелика затримка для UI
                time.sleep(0.1)
            
            if success:
                self.cleanup_status.emit("Очищення завершено успішно")
            else:
                self.cleanup_status.emit("Очищення завершено з помилками")
        
        except Exception as e:
            self.cleanup_status.emit(f"Критична помилка очищення: {str(e)}")
            success = False
        
        finally:
            self.is_cleaning = False
            self.cleanup_finished.emit(success)
        
        return success
    
    def auto_cleanup(self):
        """Автоматичне очищення"""
        if not self.is_cleaning and self.auto_cleanup_enabled:
            # Виконуємо швидке очищення
            self.clean_temporary_files()
            self.clean_memory()
    
    def emergency_cleanup(self):
        """Екстрене очищення при аварійному завершенні"""
        try:
            # Швидке видалення критичних файлів
            critical_paths = [
                tempfile.gettempdir() + '/QtWebEngine*',
                tempfile.gettempdir() + '/AnDetectBrowser*',
            ]
            
            import glob
            for pattern in critical_paths:
                for path in glob.glob(pattern):
                    try:
                        if os.path.isdir(path):
                            shutil.rmtree(path, ignore_errors=True)
                        else:
                            os.remove(path)
                    except Exception:
                        pass
        
        except Exception:
            pass  # Ігноруємо помилки при екстреному очищенні


class CleanupThread(QThread):
    """Потік для очищення даних у фоновому режимі"""
    
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    finished = pyqtSignal(bool)
    
    def __init__(self, data_cleaner: DataCleaner, parent=None):
        super().__init__(parent)
        self.data_cleaner = data_cleaner
        
        # Підключення сигналів
        self.data_cleaner.cleanup_progress.connect(self.progress)
        self.data_cleaner.cleanup_status.connect(self.status)
        self.data_cleaner.cleanup_finished.connect(self.finished)
    
    def run(self):
        """Запуск очищення в окремому потоці"""
        self.data_cleaner.perform_full_cleanup()


class ScheduledCleaner(QObject):
    """Планувальник автоматичного очищення"""
    
    def __init__(self, data_cleaner: DataCleaner, parent=None):
        super().__init__(parent)
        self.data_cleaner = data_cleaner
        self.cleanup_schedule = []
        
        # Таймер для перевірки розкладу
        self.schedule_timer = QTimer()
        self.schedule_timer.timeout.connect(self.check_schedule)
        self.schedule_timer.start(60000)  # Перевірка кожну хвилину
    
    def add_scheduled_cleanup(self, interval_minutes: int, cleanup_type: str = 'full'):
        """Додавання запланованого очищення"""
        schedule_item = {
            'interval': interval_minutes,
            'type': cleanup_type,
            'last_run': time.time(),
            'next_run': time.time() + (interval_minutes * 60)
        }
        self.cleanup_schedule.append(schedule_item)
    
    def check_schedule(self):
        """Перевірка розкладу очищення"""
        current_time = time.time()
        
        for item in self.cleanup_schedule:
            if current_time >= item['next_run']:
                # Час для очищення
                if item['type'] == 'full':
                    self.data_cleaner.perform_full_cleanup()
                elif item['type'] == 'temp':
                    self.data_cleaner.clean_temporary_files()
                elif item['type'] == 'memory':
                    self.data_cleaner.clean_memory()
                
                # Оновлення часу наступного запуску
                item['last_run'] = current_time
                item['next_run'] = current_time + (item['interval'] * 60)

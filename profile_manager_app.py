<<<<<<< HEAD
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AnDetect Profile Manager - Програма управління профілями браузера
Запускає окремі екземпляри Chrome/Chromium з налаштованими профілями
"""

import sys
import os
import json
import subprocess
import tempfile
import shutil
from pathlib import Path
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
                            QWidget, QPushButton, QTableWidget, QTableWidgetItem,
                            QHeaderView, QMessageBox, QInputDialog, QLabel,
                            QToolBar, QStatusBar, QMenu, QMenuBar, QAction,
                            QGroupBox, QFormLayout, QLineEdit, QSpinBox, 
                            QComboBox, QCheckBox, QTextEdit, QSplitter,
                            QProgressBar, QDialog, QDialogButtonBox)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal, QProcess
from PyQt5.QtGui import QIcon, QPixmap, QFont

from browser.profile_manager import ProfileManager, BrowserProfile
from browser.proxy_manager import ProxyManager, create_proxy_config, validate_proxy_config


class ChromeInstanceManager:
    """Менеджер екземплярів Chrome/Chromium"""
    
    def __init__(self):
        self.running_instances = {}  # profile_id -> QProcess
        self.chrome_paths = self.find_chrome_installations()
        
    def find_chrome_installations(self):
        """Пошук встановлених браузерів"""
        possible_paths = []
        
        if sys.platform == 'win32':
            # Windows paths
            chrome_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                r"C:\Users\{}\AppData\Local\Google\Chrome\Application\chrome.exe".format(os.environ.get('USERNAME', '')),
                r"C:\Program Files\Chromium\Application\chromium.exe",
                r"C:\Program Files (x86)\Chromium\Application\chromium.exe",
                # Edge може також працювати
                r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
            ]
            
            for path in chrome_paths:
                if os.path.exists(path):
                    possible_paths.append(path)
                    
        return possible_paths
    
    def get_chrome_executable(self):
        """Отримання шляху до Chrome"""
        if self.chrome_paths:
            return self.chrome_paths[0]
        return None
    
    def create_profile_directory(self, profile: BrowserProfile):
        """Створення директорії профілю Chrome"""
        chrome_profile_dir = os.path.join(
            os.path.expanduser("~"), 
            "AnDetectProfiles", 
            f"Profile_{profile.id}"
        )
        
        os.makedirs(chrome_profile_dir, exist_ok=True)
        
        # Створюємо файл налаштувань Chrome
        preferences = {
            "profile": {
                "name": profile.name,
                "managed_user_id": "",
                "default_content_setting_values": {
                    "geolocation": 2 if not profile.geolocation_enabled else 1,
                    "notifications": 2 if not profile.notifications_enabled else 1,
                    "media_stream": 2 if not profile.webrtc_enabled else 1
                }
            },
            "session": {
                "restore_on_startup": 4,
                "startup_urls": ["https://www.google.com"]
            },
            "webkit": {
                "webprefs": {
                    "default_font_size": 16,
                    "default_fixed_font_size": 13,
                    "minimum_font_size": 6,
                    "javascript_enabled": profile.javascript_enabled,
                    "loads_images_automatically": profile.images_enabled,
                    "plugins_enabled": profile.plugins_enabled
                }
            },
            "browser": {
                "show_home_button": True,
                "check_default_browser": False
            }
        }
        
        prefs_file = os.path.join(chrome_profile_dir, "Preferences")
        with open(prefs_file, 'w', encoding='utf-8') as f:
            json.dump(preferences, f, indent=2)
            
        return chrome_profile_dir
    
    def create_proxy_auth_extension(self, profile: BrowserProfile, profile_dir: str):
        """Створення розширення для автоматичної авторизації проксі"""
        if not profile.proxy_username or not profile.proxy_password:
            return None
            
        # Створюємо директорію для розширення
        extension_dir = os.path.join(profile_dir, "proxy_auth_extension")
        os.makedirs(extension_dir, exist_ok=True)
        
        # manifest.json
        manifest = {
            "manifest_version": 2,
            "name": "Proxy Auth",
            "version": "1.0",
            "description": "Automatic proxy authentication",
            "permissions": [
                "webRequest",
                "webRequestBlocking",
                "<all_urls>",
                "proxy"
            ],
            "background": {
                "scripts": ["background.js"],
                "persistent": True
            }
        }
        
        manifest_path = os.path.join(extension_dir, "manifest.json")
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2)
        
        # background.js
        background_js = f"""
chrome.webRequest.onAuthRequired.addListener(
    function(details) {{
        console.log('Proxy auth required for:', details.url);
        return {{
            authCredentials: {{
                username: '{profile.proxy_username}',
                password: '{profile.proxy_password}'
            }}
        }};
    }},
    {{urls: ["<all_urls>"]}},
    ["blocking"]
);

chrome.webRequest.onBeforeRequest.addListener(
    function(details) {{
        console.log('Request to:', details.url);
        return {{cancel: false}};
    }},
    {{urls: ["<all_urls>"]}},
    ["blocking"]
);

console.log('Proxy Auth Extension loaded');
console.log('Username: {profile.proxy_username}');
"""
        
        background_path = os.path.join(extension_dir, "background.js")
        with open(background_path, 'w', encoding='utf-8') as f:
            f.write(background_js)
        
        return extension_dir
    
    def generate_chrome_flags(self, profile: BrowserProfile, profile_dir: str):
        """Генерація флагів для запуску Chrome"""
        flags = [
            f"--user-data-dir={profile_dir}",
            "--no-first-run",
            "--no-default-browser-check",
            f"--user-agent={profile.user_agent}"
        ]
        
        # Налаштування екрану
        flags.append(f"--window-size={profile.screen_width},{profile.screen_height}")
        
        # Проксі налаштування
        if profile.proxy_host and profile.proxy_port:
            if profile.proxy_type == 'HTTP':
                flags.append(f"--proxy-server=http://{profile.proxy_host}:{profile.proxy_port}")
            elif profile.proxy_type == 'SOCKS5':
                flags.append(f"--proxy-server=socks5://{profile.proxy_host}:{profile.proxy_port}")
            
            # Якщо є логін/пароль, створюємо розширення для авторизації
            if profile.proxy_username and profile.proxy_password:
                extension_dir = self.create_proxy_auth_extension(profile, profile_dir)
                if extension_dir:
                    flags.append(f"--load-extension={extension_dir}")
                    flags.append("--disable-extensions-except=" + extension_dir)
        
        # Мова (тільки основний код)
        lang_code = profile.language.split('-')[0] if '-' in profile.language else profile.language
        flags.append(f"--lang={lang_code}")
        
        # Мінімальні налаштування приватності
        if not profile.webrtc_enabled:
            flags.append("--disable-webrtc")
            
        # Відключаємо автоматичні оновлення та синхронізацію
        flags.extend([
            "--disable-background-networking",
            "--disable-sync"
        ])
        
        return flags
    
    def launch_profile(self, profile: BrowserProfile, url: str = "https://www.google.com"):
        """Запуск профілю в Chrome"""
        if profile.id in self.running_instances:
            QMessageBox.warning(None, "Увага", f"Профіль '{profile.name}' вже запущено!")
            return False
        
        chrome_exe = self.get_chrome_executable()
        if not chrome_exe:
            QMessageBox.critical(None, "Помилка", 
                               "Chrome або Chromium не знайдено!\n"
                               "Встановіть Google Chrome або Chromium.")
            return False
        
        try:
            # Створюємо директорію профілю
            profile_dir = self.create_profile_directory(profile)
            
            # Генеруємо флаги (включає створення розширення якщо потрібно)
            flags = self.generate_chrome_flags(profile, profile_dir)
            
            # Додаємо URL для відкриття
            flags.append(url)
            
            # Створюємо процес
            process = QProcess()
            
            # Запускаємо Chrome
            cmd = [chrome_exe] + flags
            print(f"Запуск команди: {' '.join(cmd)}")
            
            process.start(chrome_exe, flags)
            
            if process.waitForStarted(5000):  # 5 секунд timeout
                self.running_instances[profile.id] = process
                return True
            else:
                QMessageBox.critical(None, "Помилка", 
                                   f"Не вдалося запустити профіль '{profile.name}'")
                return False
                
        except Exception as e:
            QMessageBox.critical(None, "Помилка", f"Помилка запуску профілю: {str(e)}")
            return False
    
    def close_profile(self, profile_id: str):
        """Закриття профілю"""
        if profile_id in self.running_instances:
            process = self.running_instances[profile_id]
            process.terminate()
            if not process.waitForFinished(5000):
                process.kill()
            del self.running_instances[profile_id]
            return True
        return False
    
    def is_profile_running(self, profile_id: str):
        """Перевірка чи профіль запущено"""
        return profile_id in self.running_instances
    
    def close_all_profiles(self):
        """Закриття всіх профілів"""
        for profile_id in list(self.running_instances.keys()):
            self.close_profile(profile_id)


class ProfileDialog(QDialog):
    """Діалог створення/редагування профілю"""
    
    def __init__(self, parent=None, profile=None):
        super().__init__(parent)
        self.profile = profile
        self.setWindowTitle('Створити профіль' if not profile else 'Редагувати профіль')
        self.setMinimumSize(600, 700)
        self.init_ui()
        
        if profile:
            self.load_profile_data()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Основна інформація
        main_group = QGroupBox("Основна інформація")
        main_layout = QFormLayout(main_group)
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Введіть назву профілю")
        main_layout.addRow("Назва профілю:", self.name_edit)
        
        layout.addWidget(main_group)
        
        # Browser fingerprinting
        fingerprint_group = QGroupBox("Browser Fingerprinting")
        fingerprint_layout = QFormLayout(fingerprint_group)
        
        self.user_agent_edit = QTextEdit()
        self.user_agent_edit.setMaximumHeight(80)
        self.user_agent_edit.setPlaceholderText("User-Agent браузера")
        fingerprint_layout.addRow("User-Agent:", self.user_agent_edit)
        
        screen_layout = QHBoxLayout()
        self.screen_width_spin = QSpinBox()
        self.screen_width_spin.setRange(800, 4096)
        self.screen_width_spin.setValue(1920)
        screen_layout.addWidget(self.screen_width_spin)
        
        screen_layout.addWidget(QLabel("x"))
        
        self.screen_height_spin = QSpinBox()
        self.screen_height_spin.setRange(600, 2160) 
        self.screen_height_spin.setValue(1080)
        screen_layout.addWidget(self.screen_height_spin)
        
        fingerprint_layout.addRow("Розмір екрану:", screen_layout)
        
        self.timezone_combo = QComboBox()
        self.timezone_combo.addItems([
            'Europe/Kiev', 'Europe/London', 'Europe/Berlin',
            'America/New_York', 'America/Los_Angeles', 'Asia/Tokyo'
        ])
        fingerprint_layout.addRow("Часовий пояс:", self.timezone_combo)
        
        self.language_combo = QComboBox()
        self.language_combo.addItems([
            'uk-UA', 'en-US', 'en-GB', 'de-DE', 'fr-FR', 'es-ES'
        ])
        fingerprint_layout.addRow("Мова:", self.language_combo)
        
        layout.addWidget(fingerprint_group)
        
        # Проксі
        proxy_group = QGroupBox("Налаштування проксі")
        proxy_layout = QFormLayout(proxy_group)
        
        self.proxy_type_combo = QComboBox()
        self.proxy_type_combo.addItems(['HTTP', 'SOCKS5'])
        proxy_layout.addRow("Тип:", self.proxy_type_combo)
        
        self.proxy_host_edit = QLineEdit()
        self.proxy_host_edit.setPlaceholderText("IP адреса проксі")
        proxy_layout.addRow("Хост:", self.proxy_host_edit)
        
        # Поле для проксі в форматі IP:PORT:USER:PASS
        self.proxy_string_edit = QLineEdit()
        self.proxy_string_edit.setPlaceholderText("45.158.61.63:46130:RQQ6C0VF:MZH4VXZU")
        self.proxy_string_edit.textChanged.connect(self.parse_proxy_string)
        proxy_layout.addRow("Проксі (повний):", self.proxy_string_edit)
        
        self.proxy_port_spin = QSpinBox()
        self.proxy_port_spin.setRange(1, 65535)
        self.proxy_port_spin.setValue(8080)
        proxy_layout.addRow("Порт:", self.proxy_port_spin)
        
        self.proxy_username_edit = QLineEdit()
        self.proxy_username_edit.setPlaceholderText("Логін (необов'язково)")
        proxy_layout.addRow("Логін:", self.proxy_username_edit)
        
        self.proxy_password_edit = QLineEdit()
        self.proxy_password_edit.setEchoMode(QLineEdit.Password)
        self.proxy_password_edit.setPlaceholderText("Пароль (необов'язково)")
        proxy_layout.addRow("Пароль:", self.proxy_password_edit)
        
        layout.addWidget(proxy_group)
        
        # Дозволи
        permissions_group = QGroupBox("Дозволи браузера")
        permissions_layout = QVBoxLayout(permissions_group)
        
        self.javascript_check = QCheckBox("Дозволити JavaScript")
        self.javascript_check.setChecked(True)
        permissions_layout.addWidget(self.javascript_check)
        
        self.images_check = QCheckBox("Завантажувати зображення")
        self.images_check.setChecked(True)
        permissions_layout.addWidget(self.images_check)
        
        self.plugins_check = QCheckBox("Дозволити плагіни")
        self.plugins_check.setChecked(True)
        permissions_layout.addWidget(self.plugins_check)
        
        self.geolocation_check = QCheckBox("Дозволити геолокацію")
        self.geolocation_check.setChecked(False)
        permissions_layout.addWidget(self.geolocation_check)
        
        self.notifications_check = QCheckBox("Дозволити сповіщення")
        self.notifications_check.setChecked(False)
        permissions_layout.addWidget(self.notifications_check)
        
        self.webrtc_check = QCheckBox("Дозволити WebRTC")
        self.webrtc_check.setChecked(False)
        permissions_layout.addWidget(self.webrtc_check)
        
        layout.addWidget(permissions_group)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        
        generate_btn = QPushButton("Генерувати випадкові дані")
        generate_btn.clicked.connect(self.generate_random_data)
        buttons_layout.addWidget(generate_btn)
        
        buttons_layout.addStretch()
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        buttons_layout.addWidget(buttons)
        
        layout.addLayout(buttons_layout)
    
    def parse_proxy_string(self):
        """Парсинг проксі в форматі IP:PORT:USER:PASS"""
        proxy_string = self.proxy_string_edit.text().strip()
        
        if ':' in proxy_string:
            parts = proxy_string.split(':')
            if len(parts) >= 2:
                # IP:PORT
                self.proxy_host_edit.setText(parts[0])
                try:
                    self.proxy_port_spin.setValue(int(parts[1]))
                except ValueError:
                    pass
                    
                if len(parts) >= 4:
                    # IP:PORT:USER:PASS
                    self.proxy_username_edit.setText(parts[2])
                    self.proxy_password_edit.setText(parts[3])
    
    def generate_random_data(self):
        """Генерація випадкових даних"""
        import random
        
        # Використовуємо новий список з 100+ User-Agent
        try:
            from user_agents import get_random_user_agent
            user_agent = get_random_user_agent()
        except ImportError:
            # Fallback якщо файл не знайдено
            user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0"
            ]
            user_agent = random.choice(user_agents)
        
        screen_sizes = [(1920, 1080), (1366, 768), (1440, 900), (1600, 900), (1280, 1024), (1680, 1050), (2560, 1440)]
        
        self.user_agent_edit.setPlainText(user_agent)
        width, height = random.choice(screen_sizes)
        self.screen_width_spin.setValue(width)
        self.screen_height_spin.setValue(height)
    
    def load_profile_data(self):
        """Завантаження даних профілю"""
        if not self.profile:
            return
            
        self.name_edit.setText(self.profile.name)
        self.user_agent_edit.setPlainText(self.profile.user_agent)
        self.screen_width_spin.setValue(self.profile.screen_width)
        self.screen_height_spin.setValue(self.profile.screen_height)
        
        # Встановлення комбобоксів
        tz_index = self.timezone_combo.findText(self.profile.timezone)
        if tz_index >= 0:
            self.timezone_combo.setCurrentIndex(tz_index)
            
        lang_index = self.language_combo.findText(self.profile.language.split(',')[0])
        if lang_index >= 0:
            self.language_combo.setCurrentIndex(lang_index)
        
        # Проксі
        if self.profile.proxy_host:
            self.proxy_host_edit.setText(self.profile.proxy_host)
            self.proxy_port_spin.setValue(self.profile.proxy_port)
            self.proxy_username_edit.setText(self.profile.proxy_username)
            self.proxy_password_edit.setText(self.profile.proxy_password)
            
            # Заповнюємо повний рядок проксі
            if self.profile.proxy_username and self.profile.proxy_password:
                proxy_full = f"{self.profile.proxy_host}:{self.profile.proxy_port}:{self.profile.proxy_username}:{self.profile.proxy_password}"
            else:
                proxy_full = f"{self.profile.proxy_host}:{self.profile.proxy_port}"
            self.proxy_string_edit.setText(proxy_full)
            
            proxy_type_index = self.proxy_type_combo.findText(self.profile.proxy_type)
            if proxy_type_index >= 0:
                self.proxy_type_combo.setCurrentIndex(proxy_type_index)
        
        # Дозволи
        self.javascript_check.setChecked(self.profile.javascript_enabled)
        self.images_check.setChecked(self.profile.images_enabled)
        self.plugins_check.setChecked(self.profile.plugins_enabled)
        self.geolocation_check.setChecked(self.profile.geolocation_enabled)
        self.notifications_check.setChecked(self.profile.notifications_enabled)
        self.webrtc_check.setChecked(self.profile.webrtc_enabled)
    
    def get_profile_data(self):
        """Отримання даних з форми"""
        return {
            'name': self.name_edit.text().strip(),
            'user_agent': self.user_agent_edit.toPlainText().strip(),
            'screen_width': self.screen_width_spin.value(),
            'screen_height': self.screen_height_spin.value(),
            'timezone': self.timezone_combo.currentText(),
            'language': self.language_combo.currentText(),
            'proxy_host': self.proxy_host_edit.text().strip(),
            'proxy_port': self.proxy_port_spin.value(),
            'proxy_username': self.proxy_username_edit.text().strip(),
            'proxy_password': self.proxy_password_edit.text().strip(),
            'proxy_type': self.proxy_type_combo.currentText(),
            'javascript_enabled': self.javascript_check.isChecked(),
            'images_enabled': self.images_check.isChecked(),
            'plugins_enabled': self.plugins_check.isChecked(),
            'geolocation_enabled': self.geolocation_check.isChecked(),
            'notifications_enabled': self.notifications_check.isChecked(),
            'webrtc_enabled': self.webrtc_check.isChecked()
        }


class ProfileManagerMainWindow(QMainWindow):
    """Головне вікно менеджера профілів"""
    
    def __init__(self):
        super().__init__()
        self.profile_manager = ProfileManager()
        self.chrome_manager = ChromeInstanceManager()
        
        self.setWindowTitle("AnDetect Profile Manager v1.0")
        self.setGeometry(100, 100, 1000, 700)
        
        self.init_ui()
        self.load_profiles()
        
        # Таймер для оновлення статусу
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_profile_status)
        self.status_timer.start(2000)  # Оновлення кожні 2 секунди
    
    def init_ui(self):
        """Ініціалізація інтерфейсу"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Toolbar
        self.create_toolbar()
        
        # Головна таблиця профілів
        self.profiles_table = QTableWidget()
        self.profiles_table.setColumnCount(6)
        self.profiles_table.setHorizontalHeaderLabels([
            "Назва", "User-Agent", "Проксі", "Статус", "Останнє використання", "Дії"
        ])
        
        header = self.profiles_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        header.setSectionResizeMode(3, QHeaderView.Fixed)
        header.setSectionResizeMode(4, QHeaderView.Fixed)
        header.setSectionResizeMode(5, QHeaderView.Fixed)
        
        self.profiles_table.setColumnWidth(0, 150)
        self.profiles_table.setColumnWidth(2, 120)
        self.profiles_table.setColumnWidth(3, 100)
        self.profiles_table.setColumnWidth(4, 150)
        self.profiles_table.setColumnWidth(5, 200)
        
        layout.addWidget(self.profiles_table)
        
        # Статус бар
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Menubar
        self.create_menu()
        
    def create_toolbar(self):
        """Створення панелі інструментів"""
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        # Нові профіль
        new_profile_action = toolbar.addAction("➕ Новий профіль")
        new_profile_action.triggered.connect(self.create_new_profile)
        
        toolbar.addSeparator()
        
        # Запустити профіль
        launch_action = toolbar.addAction("▶️ Запустити")
        launch_action.triggered.connect(self.launch_selected_profile)
        
        # Зупинити профіль
        stop_action = toolbar.addAction("⏹️ Зупинити")
        stop_action.triggered.connect(self.stop_selected_profile)
        
        toolbar.addSeparator()
        
        # Редагувати профіль
        edit_action = toolbar.addAction("✏️ Редагувати")
        edit_action.triggered.connect(self.edit_selected_profile)
        
        # Видалити профіль
        delete_action = toolbar.addAction("🗑️ Видалити")
        delete_action.triggered.connect(self.delete_selected_profile)
        
        toolbar.addSeparator()
        
        # Оновити
        refresh_action = toolbar.addAction("🔄 Оновити")
        refresh_action.triggered.connect(self.load_profiles)
    
    def create_menu(self):
        """Створення меню"""
        menubar = self.menuBar()
        
        # Меню файл
        file_menu = menubar.addMenu("Файл")
        file_menu.addAction("Експорт профілів", self.export_profiles)
        file_menu.addAction("Імпорт профілів", self.import_profiles)
        file_menu.addSeparator()
        file_menu.addAction("Вихід", self.close)
        
        # Меню профілів
        profiles_menu = menubar.addMenu("Профілі")
        profiles_menu.addAction("Новий профіль", self.create_new_profile)
        profiles_menu.addAction("Зупинити всі", self.stop_all_profiles)
        
        # Меню довідка
        help_menu = menubar.addMenu("Довідка")
        help_menu.addAction("Про програму", self.show_about)
    
    def load_profiles(self):
        """Завантаження профілів в таблицю"""
        profiles = self.profile_manager.get_all_profiles()
        
        self.profiles_table.setRowCount(len(profiles))
        
        for row, profile in enumerate(profiles):
            # Назва
            self.profiles_table.setItem(row, 0, QTableWidgetItem(profile.name))
            
            # User-Agent (скорочений)
            ua_short = profile.user_agent[:50] + "..." if len(profile.user_agent) > 50 else profile.user_agent
            self.profiles_table.setItem(row, 1, QTableWidgetItem(ua_short))
            
            # Проксі
            proxy_text = f"{profile.proxy_type}://{profile.proxy_host}:{profile.proxy_port}" if profile.proxy_host else "Немає"
            self.profiles_table.setItem(row, 2, QTableWidgetItem(proxy_text))
            
            # Статус
            status = "🟢 Запущено" if self.chrome_manager.is_profile_running(profile.id) else "⚫ Зупинено"
            self.profiles_table.setItem(row, 3, QTableWidgetItem(status))
            
            # Останнє використання
            last_used = profile.last_used.split('T')[0] if 'T' in profile.last_used else profile.last_used
            self.profiles_table.setItem(row, 4, QTableWidgetItem(last_used))
            
            # Кнопки дій
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(5, 2, 5, 2)
            
            launch_btn = QPushButton("▶️")
            launch_btn.setMaximumWidth(30)
            launch_btn.setToolTip("Запустити профіль")
            launch_btn.clicked.connect(lambda checked, p_id=profile.id: self.launch_profile(p_id))
            actions_layout.addWidget(launch_btn)
            
            launch_url_btn = QPushButton("🌐")
            launch_url_btn.setMaximumWidth(30)
            launch_url_btn.setToolTip("Запустити з URL")
            launch_url_btn.clicked.connect(lambda checked, p_id=profile.id: self.launch_profile_with_url(p_id))
            actions_layout.addWidget(launch_url_btn)
            
            stop_btn = QPushButton("⏹️")
            stop_btn.setMaximumWidth(30)
            stop_btn.clicked.connect(lambda checked, p_id=profile.id: self.stop_profile(p_id))
            actions_layout.addWidget(stop_btn)
            
            edit_btn = QPushButton("✏️")
            edit_btn.setMaximumWidth(30)
            edit_btn.clicked.connect(lambda checked, p=profile: self.edit_profile(p))
            actions_layout.addWidget(edit_btn)
            
            delete_btn = QPushButton("🗑️")
            delete_btn.setMaximumWidth(30)
            delete_btn.clicked.connect(lambda checked, p_id=profile.id: self.delete_profile(p_id))
            actions_layout.addWidget(delete_btn)
            
            self.profiles_table.setCellWidget(row, 5, actions_widget)
        
        self.status_bar.showMessage(f"Завантажено {len(profiles)} профілів")
    
    def create_new_profile(self):
        """Створення нового профілю"""
        dialog = ProfileDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_profile_data()
            if data['name']:
                try:
                    self.profile_manager.create_profile(data['name'], data)
                    self.load_profiles()
                    self.status_bar.showMessage(f"Профіль '{data['name']}' створено", 3000)
                except Exception as e:
                    QMessageBox.critical(self, "Помилка", f"Не вдалося створити профіль: {str(e)}")
            else:
                QMessageBox.warning(self, "Увага", "Назва профілю не може бути пустою!")
    
    def launch_profile(self, profile_id: str):
        """Запуск профілю"""
        profile = self.profile_manager.get_profile_by_id(profile_id)
        if profile:
            if self.chrome_manager.launch_profile(profile):
                self.status_bar.showMessage(f"Профіль '{profile.name}' запущено", 3000)
                self.load_profiles()
            else:
                self.status_bar.showMessage(f"Не вдалося запустити профіль '{profile.name}'", 3000)
    
    def launch_profile_with_url(self, profile_id: str):
        """Запуск профілю з конкретним URL"""
        from PyQt5.QtWidgets import QInputDialog
        
        url, ok = QInputDialog.getText(
            self, 'Введіть URL', 
            'URL для відкриття:',
            text='https://'
        )
        
        if ok and url:
            profile = self.profile_manager.get_profile_by_id(profile_id)
            if profile:
                if self.chrome_manager.launch_profile(profile, url):
                    self.status_bar.showMessage(f"Профіль '{profile.name}' запущено з {url}", 3000)
                    self.load_profiles()
                else:
                    self.status_bar.showMessage(f"Не вдалося запустити профіль '{profile.name}'", 3000)
    
    def stop_profile(self, profile_id: str):
        """Зупинка профілю"""
        profile = self.profile_manager.get_profile_by_id(profile_id)
        if profile:
            if self.chrome_manager.close_profile(profile_id):
                self.status_bar.showMessage(f"Профіль '{profile.name}' зупинено", 3000)
                self.load_profiles()
    
    def launch_selected_profile(self):
        """Запуск вибраного профілю"""
        current_row = self.profiles_table.currentRow()
        if current_row >= 0:
            profiles = self.profile_manager.get_all_profiles()
            if current_row < len(profiles):
                self.launch_profile(profiles[current_row].id)
    
    def stop_selected_profile(self):
        """Зупинка вибраного профілю"""
        current_row = self.profiles_table.currentRow()
        if current_row >= 0:
            profiles = self.profile_manager.get_all_profiles()
            if current_row < len(profiles):
                self.stop_profile(profiles[current_row].id)
    
    def edit_profile(self, profile: BrowserProfile):
        """Редагування профілю"""
        dialog = ProfileDialog(self, profile)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_profile_data()
            try:
                self.profile_manager.update_profile(profile.id, data)
                self.load_profiles()
                self.status_bar.showMessage(f"Профіль '{data['name']}' оновлено", 3000)
            except Exception as e:
                QMessageBox.critical(self, "Помилка", f"Не вдалося оновити профіль: {str(e)}")
    
    def edit_selected_profile(self):
        """Редагування вибраного профілю"""
        current_row = self.profiles_table.currentRow()
        if current_row >= 0:
            profiles = self.profile_manager.get_all_profiles()
            if current_row < len(profiles):
                self.edit_profile(profiles[current_row])
    
    def delete_profile(self, profile_id: str):
        """Видалення профілю"""
        profile = self.profile_manager.get_profile_by_id(profile_id)
        if profile:
            reply = QMessageBox.question(
                self, "Підтвердження",
                f"Ви впевнені що хочете видалити профіль '{profile.name}'?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # Спочатку зупиняємо якщо запущено
                self.chrome_manager.close_profile(profile_id)
                
                # Видаляємо з бази
                self.profile_manager.delete_profile(profile_id)
                
                self.load_profiles()
                self.status_bar.showMessage(f"Профіль '{profile.name}' видалено", 3000)
    
    def delete_selected_profile(self):
        """Видалення вибраного профілю"""
        current_row = self.profiles_table.currentRow()
        if current_row >= 0:
            profiles = self.profile_manager.get_all_profiles()
            if current_row < len(profiles):
                self.delete_profile(profiles[current_row].id)
    
    def stop_all_profiles(self):
        """Зупинка всіх профілів"""
        self.chrome_manager.close_all_profiles()
        self.load_profiles()
        self.status_bar.showMessage("Всі профілі зупинено", 3000)
    
    def update_profile_status(self):
        """Оновлення статусу профілів"""
        for row in range(self.profiles_table.rowCount()):
            profiles = self.profile_manager.get_all_profiles()
            if row < len(profiles):
                profile = profiles[row]
                status = "🟢 Запущено" if self.chrome_manager.is_profile_running(profile.id) else "⚫ Зупинено"
                self.profiles_table.setItem(row, 3, QTableWidgetItem(status))
    
    def export_profiles(self):
        """Експорт профілів"""
        # TODO: Реалізувати експорт
        QMessageBox.information(self, "Експорт", "Функція експорту буде додана в наступній версії")
    
    def import_profiles(self):
        """Імпорт профілів"""
        # TODO: Реалізувати імпорт
        QMessageBox.information(self, "Імпорт", "Функція імпорту буде додана в наступній версії")
    
    def show_about(self):
        """Про програму"""
        QMessageBox.about(self, "Про програму", 
                         "AnDetect Profile Manager v1.0\n\n"
                         "Програма для керування профілями браузера\n"
                         "з підтримкою анонімності та маскування.\n\n"
                         "© 2024 AnDetect")
    
    def closeEvent(self, event):
        """Обробка закриття програми"""
        self.chrome_manager.close_all_profiles()
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("AnDetect Profile Manager")
    app.setApplicationVersion("1.0.0")
    
    window = ProfileManagerMainWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
=======
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AnDetect Profile Manager - Програма управління профілями браузера
Запускає окремі екземпляри Chrome/Chromium з налаштованими профілями
"""

import sys
import os
import json
import subprocess
import tempfile
import shutil
from pathlib import Path
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
                            QWidget, QPushButton, QTableWidget, QTableWidgetItem,
                            QHeaderView, QMessageBox, QInputDialog, QLabel,
                            QToolBar, QStatusBar, QMenu, QMenuBar, QAction,
                            QGroupBox, QFormLayout, QLineEdit, QSpinBox, 
                            QComboBox, QCheckBox, QTextEdit, QSplitter,
                            QProgressBar, QDialog, QDialogButtonBox)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal, QProcess
from PyQt5.QtGui import QIcon, QPixmap, QFont

from browser.profile_manager import ProfileManager, BrowserProfile
from browser.proxy_manager import ProxyManager, create_proxy_config, validate_proxy_config


class ChromeInstanceManager:
    """Менеджер екземплярів Chrome/Chromium"""
    
    def __init__(self):
        self.running_instances = {}  # profile_id -> QProcess
        self.chrome_paths = self.find_chrome_installations()
        
    def find_chrome_installations(self):
        """Пошук встановлених браузерів"""
        possible_paths = []
        
        if sys.platform == 'win32':
            # Windows paths
            chrome_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                r"C:\Users\{}\AppData\Local\Google\Chrome\Application\chrome.exe".format(os.environ.get('USERNAME', '')),
                r"C:\Program Files\Chromium\Application\chromium.exe",
                r"C:\Program Files (x86)\Chromium\Application\chromium.exe",
                # Edge може також працювати
                r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
            ]
            
            for path in chrome_paths:
                if os.path.exists(path):
                    possible_paths.append(path)
                    
        return possible_paths
    
    def get_chrome_executable(self):
        """Отримання шляху до Chrome"""
        if self.chrome_paths:
            return self.chrome_paths[0]
        return None
    
    def create_profile_directory(self, profile: BrowserProfile):
        """Створення директорії профілю Chrome"""
        chrome_profile_dir = os.path.join(
            os.path.expanduser("~"), 
            "AnDetectProfiles", 
            f"Profile_{profile.id}"
        )
        
        os.makedirs(chrome_profile_dir, exist_ok=True)
        
        # Створюємо файл налаштувань Chrome
        preferences = {
            "profile": {
                "name": profile.name,
                "managed_user_id": "",
                "default_content_setting_values": {
                    "geolocation": 2 if not profile.geolocation_enabled else 1,
                    "notifications": 2 if not profile.notifications_enabled else 1,
                    "media_stream": 2 if not profile.webrtc_enabled else 1
                }
            },
            "session": {
                "restore_on_startup": 4,
                "startup_urls": ["https://www.google.com"]
            },
            "webkit": {
                "webprefs": {
                    "default_font_size": 16,
                    "default_fixed_font_size": 13,
                    "minimum_font_size": 6,
                    "javascript_enabled": profile.javascript_enabled,
                    "loads_images_automatically": profile.images_enabled,
                    "plugins_enabled": profile.plugins_enabled
                }
            },
            "browser": {
                "show_home_button": True,
                "check_default_browser": False
            }
        }
        
        prefs_file = os.path.join(chrome_profile_dir, "Preferences")
        with open(prefs_file, 'w', encoding='utf-8') as f:
            json.dump(preferences, f, indent=2)
            
        return chrome_profile_dir
    
    def create_proxy_auth_extension(self, profile: BrowserProfile, profile_dir: str):
        """Створення розширення для автоматичної авторизації проксі"""
        if not profile.proxy_username or not profile.proxy_password:
            return None
            
        # Створюємо директорію для розширення
        extension_dir = os.path.join(profile_dir, "proxy_auth_extension")
        os.makedirs(extension_dir, exist_ok=True)
        
        # manifest.json
        manifest = {
            "manifest_version": 2,
            "name": "Proxy Auth",
            "version": "1.0",
            "description": "Automatic proxy authentication",
            "permissions": [
                "webRequest",
                "webRequestBlocking",
                "<all_urls>",
                "proxy"
            ],
            "background": {
                "scripts": ["background.js"],
                "persistent": True
            }
        }
        
        manifest_path = os.path.join(extension_dir, "manifest.json")
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2)
        
        # background.js
        background_js = f"""
chrome.webRequest.onAuthRequired.addListener(
    function(details) {{
        console.log('Proxy auth required for:', details.url);
        return {{
            authCredentials: {{
                username: '{profile.proxy_username}',
                password: '{profile.proxy_password}'
            }}
        }};
    }},
    {{urls: ["<all_urls>"]}},
    ["blocking"]
);

chrome.webRequest.onBeforeRequest.addListener(
    function(details) {{
        console.log('Request to:', details.url);
        return {{cancel: false}};
    }},
    {{urls: ["<all_urls>"]}},
    ["blocking"]
);

console.log('Proxy Auth Extension loaded');
console.log('Username: {profile.proxy_username}');
"""
        
        background_path = os.path.join(extension_dir, "background.js")
        with open(background_path, 'w', encoding='utf-8') as f:
            f.write(background_js)
        
        return extension_dir
    
    def generate_chrome_flags(self, profile: BrowserProfile, profile_dir: str):
        """Генерація флагів для запуску Chrome"""
        flags = [
            f"--user-data-dir={profile_dir}",
            "--no-first-run",
            "--no-default-browser-check",
            f"--user-agent={profile.user_agent}"
        ]
        
        # Налаштування екрану
        flags.append(f"--window-size={profile.screen_width},{profile.screen_height}")
        
        # Проксі налаштування
        if profile.proxy_host and profile.proxy_port:
            if profile.proxy_type == 'HTTP':
                flags.append(f"--proxy-server=http://{profile.proxy_host}:{profile.proxy_port}")
            elif profile.proxy_type == 'SOCKS5':
                flags.append(f"--proxy-server=socks5://{profile.proxy_host}:{profile.proxy_port}")
            
            # Якщо є логін/пароль, створюємо розширення для авторизації
            if profile.proxy_username and profile.proxy_password:
                extension_dir = self.create_proxy_auth_extension(profile, profile_dir)
                if extension_dir:
                    flags.append(f"--load-extension={extension_dir}")
                    flags.append("--disable-extensions-except=" + extension_dir)
        
        # Мова (тільки основний код)
        lang_code = profile.language.split('-')[0] if '-' in profile.language else profile.language
        flags.append(f"--lang={lang_code}")
        
        # Мінімальні налаштування приватності
        if not profile.webrtc_enabled:
            flags.append("--disable-webrtc")
            
        # Відключаємо автоматичні оновлення та синхронізацію
        flags.extend([
            "--disable-background-networking",
            "--disable-sync"
        ])
        
        return flags
    
    def launch_profile(self, profile: BrowserProfile, url: str = "https://www.google.com"):
        """Запуск профілю в Chrome"""
        if profile.id in self.running_instances:
            QMessageBox.warning(None, "Увага", f"Профіль '{profile.name}' вже запущено!")
            return False
        
        chrome_exe = self.get_chrome_executable()
        if not chrome_exe:
            QMessageBox.critical(None, "Помилка", 
                               "Chrome або Chromium не знайдено!\n"
                               "Встановіть Google Chrome або Chromium.")
            return False
        
        try:
            # Створюємо директорію профілю
            profile_dir = self.create_profile_directory(profile)
            
            # Генеруємо флаги (включає створення розширення якщо потрібно)
            flags = self.generate_chrome_flags(profile, profile_dir)
            
            # Додаємо URL для відкриття
            flags.append(url)
            
            # Створюємо процес
            process = QProcess()
            
            # Запускаємо Chrome
            cmd = [chrome_exe] + flags
            print(f"Запуск команди: {' '.join(cmd)}")
            
            process.start(chrome_exe, flags)
            
            if process.waitForStarted(5000):  # 5 секунд timeout
                self.running_instances[profile.id] = process
                return True
            else:
                QMessageBox.critical(None, "Помилка", 
                                   f"Не вдалося запустити профіль '{profile.name}'")
                return False
                
        except Exception as e:
            QMessageBox.critical(None, "Помилка", f"Помилка запуску профілю: {str(e)}")
            return False
    
    def close_profile(self, profile_id: str):
        """Закриття профілю"""
        if profile_id in self.running_instances:
            process = self.running_instances[profile_id]
            process.terminate()
            if not process.waitForFinished(5000):
                process.kill()
            del self.running_instances[profile_id]
            return True
        return False
    
    def is_profile_running(self, profile_id: str):
        """Перевірка чи профіль запущено"""
        return profile_id in self.running_instances
    
    def close_all_profiles(self):
        """Закриття всіх профілів"""
        for profile_id in list(self.running_instances.keys()):
            self.close_profile(profile_id)


class ProfileDialog(QDialog):
    """Діалог створення/редагування профілю"""
    
    def __init__(self, parent=None, profile=None):
        super().__init__(parent)
        self.profile = profile
        self.setWindowTitle('Створити профіль' if not profile else 'Редагувати профіль')
        self.setMinimumSize(600, 700)
        self.init_ui()
        
        if profile:
            self.load_profile_data()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Основна інформація
        main_group = QGroupBox("Основна інформація")
        main_layout = QFormLayout(main_group)
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Введіть назву профілю")
        main_layout.addRow("Назва профілю:", self.name_edit)
        
        layout.addWidget(main_group)
        
        # Browser fingerprinting
        fingerprint_group = QGroupBox("Browser Fingerprinting")
        fingerprint_layout = QFormLayout(fingerprint_group)
        
        self.user_agent_edit = QTextEdit()
        self.user_agent_edit.setMaximumHeight(80)
        self.user_agent_edit.setPlaceholderText("User-Agent браузера")
        fingerprint_layout.addRow("User-Agent:", self.user_agent_edit)
        
        screen_layout = QHBoxLayout()
        self.screen_width_spin = QSpinBox()
        self.screen_width_spin.setRange(800, 4096)
        self.screen_width_spin.setValue(1920)
        screen_layout.addWidget(self.screen_width_spin)
        
        screen_layout.addWidget(QLabel("x"))
        
        self.screen_height_spin = QSpinBox()
        self.screen_height_spin.setRange(600, 2160) 
        self.screen_height_spin.setValue(1080)
        screen_layout.addWidget(self.screen_height_spin)
        
        fingerprint_layout.addRow("Розмір екрану:", screen_layout)
        
        self.timezone_combo = QComboBox()
        self.timezone_combo.addItems([
            'Europe/Kiev', 'Europe/London', 'Europe/Berlin',
            'America/New_York', 'America/Los_Angeles', 'Asia/Tokyo'
        ])
        fingerprint_layout.addRow("Часовий пояс:", self.timezone_combo)
        
        self.language_combo = QComboBox()
        self.language_combo.addItems([
            'uk-UA', 'en-US', 'en-GB', 'de-DE', 'fr-FR', 'es-ES'
        ])
        fingerprint_layout.addRow("Мова:", self.language_combo)
        
        layout.addWidget(fingerprint_group)
        
        # Проксі
        proxy_group = QGroupBox("Налаштування проксі")
        proxy_layout = QFormLayout(proxy_group)
        
        self.proxy_type_combo = QComboBox()
        self.proxy_type_combo.addItems(['HTTP', 'SOCKS5'])
        proxy_layout.addRow("Тип:", self.proxy_type_combo)
        
        self.proxy_host_edit = QLineEdit()
        self.proxy_host_edit.setPlaceholderText("IP адреса проксі")
        proxy_layout.addRow("Хост:", self.proxy_host_edit)
        
        # Поле для проксі в форматі IP:PORT:USER:PASS
        self.proxy_string_edit = QLineEdit()
        self.proxy_string_edit.setPlaceholderText("45.158.61.63:46130:RQQ6C0VF:MZH4VXZU")
        self.proxy_string_edit.textChanged.connect(self.parse_proxy_string)
        proxy_layout.addRow("Проксі (повний):", self.proxy_string_edit)
        
        self.proxy_port_spin = QSpinBox()
        self.proxy_port_spin.setRange(1, 65535)
        self.proxy_port_spin.setValue(8080)
        proxy_layout.addRow("Порт:", self.proxy_port_spin)
        
        self.proxy_username_edit = QLineEdit()
        self.proxy_username_edit.setPlaceholderText("Логін (необов'язково)")
        proxy_layout.addRow("Логін:", self.proxy_username_edit)
        
        self.proxy_password_edit = QLineEdit()
        self.proxy_password_edit.setEchoMode(QLineEdit.Password)
        self.proxy_password_edit.setPlaceholderText("Пароль (необов'язково)")
        proxy_layout.addRow("Пароль:", self.proxy_password_edit)
        
        layout.addWidget(proxy_group)
        
        # Дозволи
        permissions_group = QGroupBox("Дозволи браузера")
        permissions_layout = QVBoxLayout(permissions_group)
        
        self.javascript_check = QCheckBox("Дозволити JavaScript")
        self.javascript_check.setChecked(True)
        permissions_layout.addWidget(self.javascript_check)
        
        self.images_check = QCheckBox("Завантажувати зображення")
        self.images_check.setChecked(True)
        permissions_layout.addWidget(self.images_check)
        
        self.plugins_check = QCheckBox("Дозволити плагіни")
        self.plugins_check.setChecked(True)
        permissions_layout.addWidget(self.plugins_check)
        
        self.geolocation_check = QCheckBox("Дозволити геолокацію")
        self.geolocation_check.setChecked(False)
        permissions_layout.addWidget(self.geolocation_check)
        
        self.notifications_check = QCheckBox("Дозволити сповіщення")
        self.notifications_check.setChecked(False)
        permissions_layout.addWidget(self.notifications_check)
        
        self.webrtc_check = QCheckBox("Дозволити WebRTC")
        self.webrtc_check.setChecked(False)
        permissions_layout.addWidget(self.webrtc_check)
        
        layout.addWidget(permissions_group)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        
        generate_btn = QPushButton("Генерувати випадкові дані")
        generate_btn.clicked.connect(self.generate_random_data)
        buttons_layout.addWidget(generate_btn)
        
        buttons_layout.addStretch()
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        buttons_layout.addWidget(buttons)
        
        layout.addLayout(buttons_layout)
    
    def parse_proxy_string(self):
        """Парсинг проксі в форматі IP:PORT:USER:PASS"""
        proxy_string = self.proxy_string_edit.text().strip()
        
        if ':' in proxy_string:
            parts = proxy_string.split(':')
            if len(parts) >= 2:
                # IP:PORT
                self.proxy_host_edit.setText(parts[0])
                try:
                    self.proxy_port_spin.setValue(int(parts[1]))
                except ValueError:
                    pass
                    
                if len(parts) >= 4:
                    # IP:PORT:USER:PASS
                    self.proxy_username_edit.setText(parts[2])
                    self.proxy_password_edit.setText(parts[3])
    
    def generate_random_data(self):
        """Генерація випадкових даних"""
        import random
        
        # Використовуємо новий список з 100+ User-Agent
        try:
            from user_agents import get_random_user_agent
            user_agent = get_random_user_agent()
        except ImportError:
            # Fallback якщо файл не знайдено
            user_agents = [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0"
            ]
            user_agent = random.choice(user_agents)
        
        screen_sizes = [(1920, 1080), (1366, 768), (1440, 900), (1600, 900), (1280, 1024), (1680, 1050), (2560, 1440)]
        
        self.user_agent_edit.setPlainText(user_agent)
        width, height = random.choice(screen_sizes)
        self.screen_width_spin.setValue(width)
        self.screen_height_spin.setValue(height)
    
    def load_profile_data(self):
        """Завантаження даних профілю"""
        if not self.profile:
            return
            
        self.name_edit.setText(self.profile.name)
        self.user_agent_edit.setPlainText(self.profile.user_agent)
        self.screen_width_spin.setValue(self.profile.screen_width)
        self.screen_height_spin.setValue(self.profile.screen_height)
        
        # Встановлення комбобоксів
        tz_index = self.timezone_combo.findText(self.profile.timezone)
        if tz_index >= 0:
            self.timezone_combo.setCurrentIndex(tz_index)
            
        lang_index = self.language_combo.findText(self.profile.language.split(',')[0])
        if lang_index >= 0:
            self.language_combo.setCurrentIndex(lang_index)
        
        # Проксі
        if self.profile.proxy_host:
            self.proxy_host_edit.setText(self.profile.proxy_host)
            self.proxy_port_spin.setValue(self.profile.proxy_port)
            self.proxy_username_edit.setText(self.profile.proxy_username)
            self.proxy_password_edit.setText(self.profile.proxy_password)
            
            # Заповнюємо повний рядок проксі
            if self.profile.proxy_username and self.profile.proxy_password:
                proxy_full = f"{self.profile.proxy_host}:{self.profile.proxy_port}:{self.profile.proxy_username}:{self.profile.proxy_password}"
            else:
                proxy_full = f"{self.profile.proxy_host}:{self.profile.proxy_port}"
            self.proxy_string_edit.setText(proxy_full)
            
            proxy_type_index = self.proxy_type_combo.findText(self.profile.proxy_type)
            if proxy_type_index >= 0:
                self.proxy_type_combo.setCurrentIndex(proxy_type_index)
        
        # Дозволи
        self.javascript_check.setChecked(self.profile.javascript_enabled)
        self.images_check.setChecked(self.profile.images_enabled)
        self.plugins_check.setChecked(self.profile.plugins_enabled)
        self.geolocation_check.setChecked(self.profile.geolocation_enabled)
        self.notifications_check.setChecked(self.profile.notifications_enabled)
        self.webrtc_check.setChecked(self.profile.webrtc_enabled)
    
    def get_profile_data(self):
        """Отримання даних з форми"""
        return {
            'name': self.name_edit.text().strip(),
            'user_agent': self.user_agent_edit.toPlainText().strip(),
            'screen_width': self.screen_width_spin.value(),
            'screen_height': self.screen_height_spin.value(),
            'timezone': self.timezone_combo.currentText(),
            'language': self.language_combo.currentText(),
            'proxy_host': self.proxy_host_edit.text().strip(),
            'proxy_port': self.proxy_port_spin.value(),
            'proxy_username': self.proxy_username_edit.text().strip(),
            'proxy_password': self.proxy_password_edit.text().strip(),
            'proxy_type': self.proxy_type_combo.currentText(),
            'javascript_enabled': self.javascript_check.isChecked(),
            'images_enabled': self.images_check.isChecked(),
            'plugins_enabled': self.plugins_check.isChecked(),
            'geolocation_enabled': self.geolocation_check.isChecked(),
            'notifications_enabled': self.notifications_check.isChecked(),
            'webrtc_enabled': self.webrtc_check.isChecked()
        }


class ProfileManagerMainWindow(QMainWindow):
    """Головне вікно менеджера профілів"""
    
    def __init__(self):
        super().__init__()
        self.profile_manager = ProfileManager()
        self.chrome_manager = ChromeInstanceManager()
        
        self.setWindowTitle("AnDetect Profile Manager v1.0")
        self.setGeometry(100, 100, 1000, 700)
        
        self.init_ui()
        self.load_profiles()
        
        # Таймер для оновлення статусу
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_profile_status)
        self.status_timer.start(2000)  # Оновлення кожні 2 секунди
    
    def init_ui(self):
        """Ініціалізація інтерфейсу"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Toolbar
        self.create_toolbar()
        
        # Головна таблиця профілів
        self.profiles_table = QTableWidget()
        self.profiles_table.setColumnCount(6)
        self.profiles_table.setHorizontalHeaderLabels([
            "Назва", "User-Agent", "Проксі", "Статус", "Останнє використання", "Дії"
        ])
        
        header = self.profiles_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Fixed)
        header.setSectionResizeMode(3, QHeaderView.Fixed)
        header.setSectionResizeMode(4, QHeaderView.Fixed)
        header.setSectionResizeMode(5, QHeaderView.Fixed)
        
        self.profiles_table.setColumnWidth(0, 150)
        self.profiles_table.setColumnWidth(2, 120)
        self.profiles_table.setColumnWidth(3, 100)
        self.profiles_table.setColumnWidth(4, 150)
        self.profiles_table.setColumnWidth(5, 200)
        
        layout.addWidget(self.profiles_table)
        
        # Статус бар
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Menubar
        self.create_menu()
        
    def create_toolbar(self):
        """Створення панелі інструментів"""
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        # Нові профіль
        new_profile_action = toolbar.addAction("➕ Новий профіль")
        new_profile_action.triggered.connect(self.create_new_profile)
        
        toolbar.addSeparator()
        
        # Запустити профіль
        launch_action = toolbar.addAction("▶️ Запустити")
        launch_action.triggered.connect(self.launch_selected_profile)
        
        # Зупинити профіль
        stop_action = toolbar.addAction("⏹️ Зупинити")
        stop_action.triggered.connect(self.stop_selected_profile)
        
        toolbar.addSeparator()
        
        # Редагувати профіль
        edit_action = toolbar.addAction("✏️ Редагувати")
        edit_action.triggered.connect(self.edit_selected_profile)
        
        # Видалити профіль
        delete_action = toolbar.addAction("🗑️ Видалити")
        delete_action.triggered.connect(self.delete_selected_profile)
        
        toolbar.addSeparator()
        
        # Оновити
        refresh_action = toolbar.addAction("🔄 Оновити")
        refresh_action.triggered.connect(self.load_profiles)
    
    def create_menu(self):
        """Створення меню"""
        menubar = self.menuBar()
        
        # Меню файл
        file_menu = menubar.addMenu("Файл")
        file_menu.addAction("Експорт профілів", self.export_profiles)
        file_menu.addAction("Імпорт профілів", self.import_profiles)
        file_menu.addSeparator()
        file_menu.addAction("Вихід", self.close)
        
        # Меню профілів
        profiles_menu = menubar.addMenu("Профілі")
        profiles_menu.addAction("Новий профіль", self.create_new_profile)
        profiles_menu.addAction("Зупинити всі", self.stop_all_profiles)
        
        # Меню довідка
        help_menu = menubar.addMenu("Довідка")
        help_menu.addAction("Про програму", self.show_about)
    
    def load_profiles(self):
        """Завантаження профілів в таблицю"""
        profiles = self.profile_manager.get_all_profiles()
        
        self.profiles_table.setRowCount(len(profiles))
        
        for row, profile in enumerate(profiles):
            # Назва
            self.profiles_table.setItem(row, 0, QTableWidgetItem(profile.name))
            
            # User-Agent (скорочений)
            ua_short = profile.user_agent[:50] + "..." if len(profile.user_agent) > 50 else profile.user_agent
            self.profiles_table.setItem(row, 1, QTableWidgetItem(ua_short))
            
            # Проксі
            proxy_text = f"{profile.proxy_type}://{profile.proxy_host}:{profile.proxy_port}" if profile.proxy_host else "Немає"
            self.profiles_table.setItem(row, 2, QTableWidgetItem(proxy_text))
            
            # Статус
            status = "🟢 Запущено" if self.chrome_manager.is_profile_running(profile.id) else "⚫ Зупинено"
            self.profiles_table.setItem(row, 3, QTableWidgetItem(status))
            
            # Останнє використання
            last_used = profile.last_used.split('T')[0] if 'T' in profile.last_used else profile.last_used
            self.profiles_table.setItem(row, 4, QTableWidgetItem(last_used))
            
            # Кнопки дій
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(5, 2, 5, 2)
            
            launch_btn = QPushButton("▶️")
            launch_btn.setMaximumWidth(30)
            launch_btn.setToolTip("Запустити профіль")
            launch_btn.clicked.connect(lambda checked, p_id=profile.id: self.launch_profile(p_id))
            actions_layout.addWidget(launch_btn)
            
            launch_url_btn = QPushButton("🌐")
            launch_url_btn.setMaximumWidth(30)
            launch_url_btn.setToolTip("Запустити з URL")
            launch_url_btn.clicked.connect(lambda checked, p_id=profile.id: self.launch_profile_with_url(p_id))
            actions_layout.addWidget(launch_url_btn)
            
            stop_btn = QPushButton("⏹️")
            stop_btn.setMaximumWidth(30)
            stop_btn.clicked.connect(lambda checked, p_id=profile.id: self.stop_profile(p_id))
            actions_layout.addWidget(stop_btn)
            
            edit_btn = QPushButton("✏️")
            edit_btn.setMaximumWidth(30)
            edit_btn.clicked.connect(lambda checked, p=profile: self.edit_profile(p))
            actions_layout.addWidget(edit_btn)
            
            delete_btn = QPushButton("🗑️")
            delete_btn.setMaximumWidth(30)
            delete_btn.clicked.connect(lambda checked, p_id=profile.id: self.delete_profile(p_id))
            actions_layout.addWidget(delete_btn)
            
            self.profiles_table.setCellWidget(row, 5, actions_widget)
        
        self.status_bar.showMessage(f"Завантажено {len(profiles)} профілів")
    
    def create_new_profile(self):
        """Створення нового профілю"""
        dialog = ProfileDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_profile_data()
            if data['name']:
                try:
                    self.profile_manager.create_profile(data['name'], data)
                    self.load_profiles()
                    self.status_bar.showMessage(f"Профіль '{data['name']}' створено", 3000)
                except Exception as e:
                    QMessageBox.critical(self, "Помилка", f"Не вдалося створити профіль: {str(e)}")
            else:
                QMessageBox.warning(self, "Увага", "Назва профілю не може бути пустою!")
    
    def launch_profile(self, profile_id: str):
        """Запуск профілю"""
        profile = self.profile_manager.get_profile_by_id(profile_id)
        if profile:
            if self.chrome_manager.launch_profile(profile):
                self.status_bar.showMessage(f"Профіль '{profile.name}' запущено", 3000)
                self.load_profiles()
            else:
                self.status_bar.showMessage(f"Не вдалося запустити профіль '{profile.name}'", 3000)
    
    def launch_profile_with_url(self, profile_id: str):
        """Запуск профілю з конкретним URL"""
        from PyQt5.QtWidgets import QInputDialog
        
        url, ok = QInputDialog.getText(
            self, 'Введіть URL', 
            'URL для відкриття:',
            text='https://'
        )
        
        if ok and url:
            profile = self.profile_manager.get_profile_by_id(profile_id)
            if profile:
                if self.chrome_manager.launch_profile(profile, url):
                    self.status_bar.showMessage(f"Профіль '{profile.name}' запущено з {url}", 3000)
                    self.load_profiles()
                else:
                    self.status_bar.showMessage(f"Не вдалося запустити профіль '{profile.name}'", 3000)
    
    def stop_profile(self, profile_id: str):
        """Зупинка профілю"""
        profile = self.profile_manager.get_profile_by_id(profile_id)
        if profile:
            if self.chrome_manager.close_profile(profile_id):
                self.status_bar.showMessage(f"Профіль '{profile.name}' зупинено", 3000)
                self.load_profiles()
    
    def launch_selected_profile(self):
        """Запуск вибраного профілю"""
        current_row = self.profiles_table.currentRow()
        if current_row >= 0:
            profiles = self.profile_manager.get_all_profiles()
            if current_row < len(profiles):
                self.launch_profile(profiles[current_row].id)
    
    def stop_selected_profile(self):
        """Зупинка вибраного профілю"""
        current_row = self.profiles_table.currentRow()
        if current_row >= 0:
            profiles = self.profile_manager.get_all_profiles()
            if current_row < len(profiles):
                self.stop_profile(profiles[current_row].id)
    
    def edit_profile(self, profile: BrowserProfile):
        """Редагування профілю"""
        dialog = ProfileDialog(self, profile)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_profile_data()
            try:
                self.profile_manager.update_profile(profile.id, data)
                self.load_profiles()
                self.status_bar.showMessage(f"Профіль '{data['name']}' оновлено", 3000)
            except Exception as e:
                QMessageBox.critical(self, "Помилка", f"Не вдалося оновити профіль: {str(e)}")
    
    def edit_selected_profile(self):
        """Редагування вибраного профілю"""
        current_row = self.profiles_table.currentRow()
        if current_row >= 0:
            profiles = self.profile_manager.get_all_profiles()
            if current_row < len(profiles):
                self.edit_profile(profiles[current_row])
    
    def delete_profile(self, profile_id: str):
        """Видалення профілю"""
        profile = self.profile_manager.get_profile_by_id(profile_id)
        if profile:
            reply = QMessageBox.question(
                self, "Підтвердження",
                f"Ви впевнені що хочете видалити профіль '{profile.name}'?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # Спочатку зупиняємо якщо запущено
                self.chrome_manager.close_profile(profile_id)
                
                # Видаляємо з бази
                self.profile_manager.delete_profile(profile_id)
                
                self.load_profiles()
                self.status_bar.showMessage(f"Профіль '{profile.name}' видалено", 3000)
    
    def delete_selected_profile(self):
        """Видалення вибраного профілю"""
        current_row = self.profiles_table.currentRow()
        if current_row >= 0:
            profiles = self.profile_manager.get_all_profiles()
            if current_row < len(profiles):
                self.delete_profile(profiles[current_row].id)
    
    def stop_all_profiles(self):
        """Зупинка всіх профілів"""
        self.chrome_manager.close_all_profiles()
        self.load_profiles()
        self.status_bar.showMessage("Всі профілі зупинено", 3000)
    
    def update_profile_status(self):
        """Оновлення статусу профілів"""
        for row in range(self.profiles_table.rowCount()):
            profiles = self.profile_manager.get_all_profiles()
            if row < len(profiles):
                profile = profiles[row]
                status = "🟢 Запущено" if self.chrome_manager.is_profile_running(profile.id) else "⚫ Зупинено"
                self.profiles_table.setItem(row, 3, QTableWidgetItem(status))
    
    def export_profiles(self):
        """Експорт профілів"""
        # TODO: Реалізувати експорт
        QMessageBox.information(self, "Експорт", "Функція експорту буде додана в наступній версії")
    
    def import_profiles(self):
        """Імпорт профілів"""
        # TODO: Реалізувати імпорт
        QMessageBox.information(self, "Імпорт", "Функція імпорту буде додана в наступній версії")
    
    def show_about(self):
        """Про програму"""
        QMessageBox.about(self, "Про програму", 
                         "AnDetect Profile Manager v1.0\n\n"
                         "Програма для керування профілями браузера\n"
                         "з підтримкою анонімності та маскування.\n\n"
                         "© 2024 AnDetect")
    
    def closeEvent(self, event):
        """Обробка закриття програми"""
        self.chrome_manager.close_all_profiles()
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("AnDetect Profile Manager")
    app.setApplicationVersion("1.0.0")
    
    window = ProfileManagerMainWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
>>>>>>> 5a38118ad408679126e5a17483fa7875264c621b

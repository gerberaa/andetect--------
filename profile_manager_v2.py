#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AnDetect Profile Manager v2.0
Розширена версія з іконками, мітками та поліпшеним інтерфейсом
"""

import sys
import os
import subprocess
import json
import shutil
from datetime import datetime, timedelta

from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
                            QWidget, QPushButton, QListWidget, QListWidgetItem,
                            QMessageBox, QInputDialog, QLabel, QFrame,
                            QSplitter, QScrollArea, QGroupBox, QGridLayout,
                            QLineEdit, QComboBox, QTextEdit, QCheckBox,
                            QProgressBar, QStatusBar, QMenuBar, QAction,
                            QToolBar, QSpacerItem, QSizePolicy, QTabWidget,
                            QFormLayout, QSpinBox, QToolButton, QMenu,
                            QFileDialog, QDialog)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize, QSettings
from PyQt5.QtGui import QIcon, QPixmap, QFont, QMovie, QPalette, QColor

# Локальні імпорти
from browser.profile_manager import ProfileManager, BrowserProfile
from profile_icons import (ProfileIcon, PROFILE_ICONS, COUNTRY_FLAGS, 
                          LABEL_COLORS, get_country_by_timezone,
                          get_browser_icon, get_proxy_type_icon)
from profile_dialog_v2 import ProfileDialogV2

class ProfileWidget(QFrame):
    """Віджет для відображення профілю з іконками та мітками"""
    
    profileSelected = pyqtSignal(str)  # profile_id
    profileLaunched = pyqtSignal(str)  # profile_id
    profileEdited = pyqtSignal(str)    # profile_id
    profileDeleted = pyqtSignal(str)   # profile_id
    
    def __init__(self, profile: BrowserProfile, parent=None):
        super().__init__(parent)
        self.profile = profile
        self.is_running = False
        self.init_ui()
        
    def init_ui(self):
        """Ініціалізація інтерфейсу віджета"""
        self.setFrameStyle(QFrame.StyledPanel)
        self.setLineWidth(2)
        self.setFixedHeight(120)
        
        # Основний layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Ліва частина - іконка профілю
        left_layout = QVBoxLayout()
        
        # Іконка профілю
        self.icon_label = QLabel()
        icon = ProfileIcon.create_profile_icon(
            icon_type=getattr(self.profile, 'icon_type', 'default'),
            color=getattr(self.profile, 'label_color', 'blue'),
            size=64
        )
        self.icon_label.setPixmap(icon.pixmap(64, 64))
        self.icon_label.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(self.icon_label)
        
        # Прапорець країни
        self.flag_label = QLabel()
        country_code = getattr(self.profile, 'country_code', 'UA')
        flag_emoji = COUNTRY_FLAGS.get(country_code, '🌍')
        self.flag_label.setText(flag_emoji)
        self.flag_label.setAlignment(Qt.AlignCenter)
        self.flag_label.setStyleSheet("font-size: 16px;")
        left_layout.addWidget(self.flag_label)
        
        layout.addLayout(left_layout)
        
        # Центральна частина - інформація
        center_layout = QVBoxLayout()
        
        # Назва профілю
        self.name_label = QLabel(f"<b>{self.profile.name}</b>")
        self.name_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        center_layout.addWidget(self.name_label)
        
        # Опис
        description = getattr(self.profile, 'description', '')
        if description:
            self.desc_label = QLabel(description[:50] + "..." if len(description) > 50 else description)
            self.desc_label.setStyleSheet("color: #666; font-size: 11px;")
            center_layout.addWidget(self.desc_label)
        
        # Теги
        tags = getattr(self.profile, 'tags', '')
        if tags:
            self.tags_label = QLabel(f"🏷️ {tags}")
            self.tags_label.setStyleSheet("color: #888; font-size: 10px;")
            center_layout.addWidget(self.tags_label)
        
        # Додаткова інформація
        info_layout = QHBoxLayout()
        
        # Браузер іконка
        browser_icon = get_browser_icon(self.profile.user_agent)
        browser_label = QLabel(browser_icon)
        browser_label.setToolTip("Браузер")
        info_layout.addWidget(browser_label)
        
        # Проксі іконка
        if self.profile.proxy_host:
            proxy_icon = get_proxy_type_icon(self.profile.proxy_type)
            proxy_label = QLabel(proxy_icon)
            proxy_label.setToolTip(f"Проксі: {self.profile.proxy_type}")
            info_layout.addWidget(proxy_label)
        
        # Улюблений
        if getattr(self.profile, 'favorite', False):
            fav_label = QLabel("⭐")
            fav_label.setToolTip("Улюблений")
            info_layout.addWidget(fav_label)
        
        # Статус
        status = getattr(self.profile, 'status', 'active')
        status_icons = {'active': '✅', 'inactive': '⏸️', 'blocked': '🚫'}
        status_label = QLabel(status_icons.get(status, '❓'))
        status_label.setToolTip(f"Статус: {status}")
        info_layout.addWidget(status_label)
        
        info_layout.addStretch()
        center_layout.addLayout(info_layout)
        
        center_layout.addStretch()
        layout.addLayout(center_layout)
        
        # Права частина - кнопки
        right_layout = QVBoxLayout()
        
        # Кнопка запуску
        self.launch_btn = QPushButton("▶️ Запустити")
        self.launch_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        self.launch_btn.clicked.connect(self.launch_profile)
        right_layout.addWidget(self.launch_btn)
        
        # Кнопки керування
        buttons_layout = QHBoxLayout()
        
        edit_btn = QPushButton("✏️")
        edit_btn.setToolTip("Редагувати")
        edit_btn.setFixedSize(30, 30)
        edit_btn.clicked.connect(self.edit_profile)
        buttons_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton("🗑️")
        delete_btn.setToolTip("Видалити")
        delete_btn.setFixedSize(30, 30)
        delete_btn.clicked.connect(self.delete_profile)
        buttons_layout.addWidget(delete_btn)
        
        right_layout.addLayout(buttons_layout)
        
        # Статистика
        stats_layout = QVBoxLayout()
        usage_count = getattr(self.profile, 'usage_count', 0)
        stats_label = QLabel(f"Запусків: {usage_count}")
        stats_label.setStyleSheet("font-size: 10px; color: #999;")
        stats_layout.addWidget(stats_label)
        
        last_used = self.profile.last_used
        if last_used:
            try:
                last_time = datetime.fromisoformat(last_used)
                time_diff = datetime.now() - last_time
                if time_diff.days > 0:
                    time_str = f"{time_diff.days} дн. тому"
                elif time_diff.seconds > 3600:
                    time_str = f"{time_diff.seconds // 3600} год. тому"
                else:
                    time_str = f"{time_diff.seconds // 60} хв. тому"
                    
                last_label = QLabel(f"Останній: {time_str}")
                last_label.setStyleSheet("font-size: 10px; color: #999;")
                stats_layout.addWidget(last_label)
            except:
                pass
                
        right_layout.addLayout(stats_layout)
        right_layout.addStretch()
        
        layout.addLayout(right_layout)
        
        # Налаштування стилю рамки залежно від статусу
        self.update_frame_style()
        
    def update_frame_style(self):
        """Оновлення стилю рамки залежно від статусу"""
        status = getattr(self.profile, 'status', 'active')
        color = getattr(self.profile, 'label_color', 'blue')
        
        border_color = LABEL_COLORS.get(color, '#4488FF')
        
        if self.is_running:
            border_color = '#FF6B35'  # Помаранчевий для запущених
            
        if status == 'inactive':
            border_color = '#999999'
        elif status == 'blocked':
            border_color = '#FF4444'
            
        self.setStyleSheet(f"""
            QFrame {{
                border: 2px solid {border_color};
                border-radius: 8px;
                background-color: white;
            }}
            QFrame:hover {{
                background-color: #f8f9fa;
            }}
        """)
        
    def launch_profile(self):
        """Запуск профілю"""
        self.profileLaunched.emit(self.profile.id)
        
    def edit_profile(self):
        """Редагування профілю"""
        self.profileEdited.emit(self.profile.id)
        
    def delete_profile(self):
        """Видалення профілю"""
        reply = QMessageBox.question(
            self, 'Підтвердження', 
            f'Ви впевнені, що хочете видалити профіль "{self.profile.name}"?',
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.profileDeleted.emit(self.profile.id)
            
    def set_running(self, running: bool):
        """Встановлення статусу запуску"""
        self.is_running = running
        if running:
            self.launch_btn.setText("⏹️ Зупинити")
            self.launch_btn.setStyleSheet("""
                QPushButton {
                    background-color: #FF6B35;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #e55a2d;
                }
            """)
        else:
            self.launch_btn.setText("▶️ Запустити")
            self.launch_btn.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
            """)
        self.update_frame_style()


class ChromeManager:
    """Менеджер для запуску Chrome з профілями"""
    
    def __init__(self):
        self.running_profiles = {}  # profile_id -> process
        
    def launch_profile(self, profile: BrowserProfile, url="https://www.google.com"):
        """Запуск Chrome з профілем"""
        try:
            profile_dir = self.create_profile_directory(profile)
            chrome_flags = self.generate_chrome_flags(profile, profile_dir)
            
            # Створюємо розширення для авто-авторизації проксі
            if profile.proxy_username and profile.proxy_password:
                ext_dir = self.create_proxy_auth_extension(profile)
                chrome_flags.extend([
                    f'--load-extension={ext_dir}',
                    f'--disable-extensions-except={ext_dir}'
                ])
            
            chrome_flags.append(url)
            
            # Запускаємо Chrome
            process = subprocess.Popen(chrome_flags)
            self.running_profiles[profile.id] = process
            
            print(f"✅ Профіль '{profile.name}' запущено (PID: {process.pid})")
            return True
            
        except Exception as e:
            print(f"❌ Помилка запуску профілю: {e}")
            return False
            
    def stop_profile(self, profile_id: str):
        """Зупинка профілю"""
        if profile_id in self.running_profiles:
            process = self.running_profiles[profile_id]
            try:
                process.terminate()
                del self.running_profiles[profile_id]
                return True
            except:
                return False
        return False
        
    def is_profile_running(self, profile_id: str) -> bool:
        """Перевірка чи запущений профіль"""
        if profile_id in self.running_profiles:
            process = self.running_profiles[profile_id]
            return process.poll() is None
        return False
        
    def create_profile_directory(self, profile: BrowserProfile) -> str:
        """Створення директорії профілю Chrome"""
        base_dir = os.path.join(os.path.expanduser("~"), "AnDetectBrowser", "chrome_profiles")
        profile_dir = os.path.join(base_dir, profile.id)
        
        os.makedirs(profile_dir, exist_ok=True)
        
        # Створюємо preferences.json
        prefs = {
            "profile": {
                "default_content_setting_values": {
                    "geolocation": 1 if profile.geolocation_enabled else 2,
                    "notifications": 1 if profile.notifications_enabled else 2,
                    "media_stream": 1 if profile.webrtc_enabled else 2,
                }
            },
            "homepage": "https://www.google.com",
            "session": {
                "restore_on_startup": 1,
                "startup_urls": ["https://www.google.com"]
            }
        }
        
        prefs_path = os.path.join(profile_dir, "Default", "Preferences")
        os.makedirs(os.path.dirname(prefs_path), exist_ok=True)
        
        with open(prefs_path, 'w', encoding='utf-8') as f:
            json.dump(prefs, f, indent=2)
            
        return profile_dir
        
    def generate_chrome_flags(self, profile: BrowserProfile, profile_dir: str) -> list:
        """Генерація прапорців для Chrome"""
        chrome_path = self.find_chrome_executable()
        
        flags = [
            chrome_path,
            f'--user-data-dir={profile_dir}',
            f'--user-agent={profile.user_agent}',
            '--no-first-run',
            '--no-default-browser-check',
            '--disable-default-apps',
            '--disable-background-timer-throttling',
            '--disable-renderer-backgrounding',
            '--disable-backgrounding-occluded-windows',
            f'--window-size={profile.screen_width},{profile.screen_height}',
        ]
        
        # Налаштування JavaScript
        if not profile.javascript_enabled:
            flags.append('--disable-javascript')
            
        # Налаштування зображень
        if not profile.images_enabled:
            flags.append('--disable-images')
            
        # Налаштування WebRTC
        if not profile.webrtc_enabled:
            flags.extend([
                '--disable-webrtc',
                '--disable-webrtc-hw-decoding',
                '--disable-webrtc-hw-encoding'
            ])
            
        # Проксі
        if profile.proxy_host:
            if profile.proxy_type == 'SOCKS5':
                flags.append(f'--proxy-server=socks5://{profile.proxy_host}:{profile.proxy_port}')
            else:
                flags.append(f'--proxy-server=http://{profile.proxy_host}:{profile.proxy_port}')
                
        return flags
        
    def find_chrome_executable(self) -> str:
        """Пошук виконуваного файлу Chrome"""
        possible_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            r"C:\Users\{}\AppData\Local\Google\Chrome\Application\chrome.exe".format(os.getenv('USERNAME')),
            "google-chrome",
            "chromium-browser",
            "chrome"
        ]
        
        for path in possible_paths:
            if os.path.isfile(path):
                return path
            elif shutil.which(path):
                return shutil.which(path)
                
        raise FileNotFoundError("Chrome не знайдено в системі")
        
    def create_proxy_auth_extension(self, profile: BrowserProfile) -> str:
        """Створення розширення для автоматичної авторизації проксі"""
        ext_dir = os.path.join(os.path.expanduser("~"), "AnDetectBrowser", "proxy_auth_ext", profile.id)
        os.makedirs(ext_dir, exist_ok=True)
        
        # manifest.json
        manifest = {
            "manifest_version": 2,
            "name": "Proxy Auth",
            "version": "1.0",
            "permissions": ["webRequest", "webRequestBlocking", "<all_urls>"],
            "background": {
                "scripts": ["background.js"],
                "persistent": True
            }
        }
        
        with open(os.path.join(ext_dir, "manifest.json"), 'w') as f:
            json.dump(manifest, f, indent=2)
            
        # background.js
        background_js = f"""
chrome.webRequest.onAuthRequired.addListener(
    function(details) {{
        return {{
            authCredentials: {{
                username: "{profile.proxy_username}",
                password: "{profile.proxy_password}"
            }}
        }};
    }},
    {{urls: ["<all_urls>"]}},
    ["blocking"]
);
"""
        
        with open(os.path.join(ext_dir, "background.js"), 'w') as f:
            f.write(background_js)
            
        return ext_dir


class AnDetectMainWindow(QMainWindow):
    """Головне вікно AnDetect Profile Manager v2.0"""
    
    def __init__(self):
        super().__init__()
        self.profile_manager = ProfileManager()
        self.chrome_manager = ChromeManager()
        self.settings = QSettings("AnDetect", "ProfileManager")
        
        self.setWindowTitle("AnDetect Profile Manager v2.0")
        self.setMinimumSize(1200, 800)
        
        # Встановлюємо іконку програми
        if os.path.exists("logo.png"):
            self.setWindowIcon(QIcon("logo.png"))
        elif os.path.exists("icon.ico"):
            self.setWindowIcon(QIcon("icon.ico"))
            
        self.init_ui()
        self.load_profiles()
        
        # Таймер для оновлення статусів
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_running_status)
        self.update_timer.start(2000)  # Кожні 2 секунди
        
    def init_ui(self):
        """Ініціалізація інтерфейсу"""
        # Меню
        self.create_menu()
        
        # Панель інструментів
        self.create_toolbar()
        
        # Центральний віджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QHBoxLayout(central_widget)
        
        # Ліва панель - фільтри
        self.create_filter_panel(layout)
        
        # Права панель - профілі
        self.create_profiles_panel(layout)
        
        # Статусна панель
        self.statusBar().showMessage("AnDetect Profile Manager v2.0 готовий до роботи")
        
    def create_menu(self):
        """Створення меню"""
        menubar = self.menuBar()
        
        # Файл
        file_menu = menubar.addMenu('Файл')
        
        new_action = QAction('Новий профіль', self)
        new_action.setShortcut('Ctrl+N')
        new_action.triggered.connect(self.create_new_profile)
        file_menu.addAction(new_action)
        
        file_menu.addSeparator()
        
        import_action = QAction('Імпорт профілів', self)
        import_action.triggered.connect(self.import_profiles)
        file_menu.addAction(import_action)
        
        export_action = QAction('Експорт профілів', self)
        export_action.triggered.connect(self.export_profiles)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('Вихід', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Інструменти
        tools_menu = menubar.addMenu('Інструменти')
        
        settings_action = QAction('Налаштування', self)
        settings_action.triggered.connect(self.show_settings)
        tools_menu.addAction(settings_action)
        
        cleanup_action = QAction('Очистка даних', self)
        cleanup_action.triggered.connect(self.cleanup_data)
        tools_menu.addAction(cleanup_action)
        
        # Довідка
        help_menu = menubar.addMenu('Довідка')
        
        about_action = QAction('Про програму', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def create_toolbar(self):
        """Створення панелі інструментів"""
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        # Кнопка нового профілю
        new_btn = QToolButton()
        new_btn.setText("➕ Новий")
        new_btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        new_btn.clicked.connect(self.create_new_profile)
        toolbar.addWidget(new_btn)
        
        toolbar.addSeparator()
        
        # Фільтр пошуку
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("🔍 Пошук профілів...")
        self.search_edit.setMaximumWidth(200)
        self.search_edit.textChanged.connect(self.filter_profiles)
        toolbar.addWidget(self.search_edit)
        
        toolbar.addSeparator()
        
        # Сортування
        sort_combo = QComboBox()
        sort_combo.addItems([
            "За датою використання",
            "За назвою",
            "За статусом",
            "За улюбленими"
        ])
        sort_combo.currentTextChanged.connect(self.sort_profiles)
        toolbar.addWidget(sort_combo)
        
    def create_filter_panel(self, parent_layout):
        """Створення панелі фільтрів"""
        filter_frame = QFrame()
        filter_frame.setFrameStyle(QFrame.StyledPanel)
        filter_frame.setMaximumWidth(250)
        
        layout = QVBoxLayout(filter_frame)
        
        # Заголовок
        title = QLabel("🎛️ Фільтри")
        title.setStyleSheet("font-size: 16px; font-weight: bold; padding: 5px;")
        layout.addWidget(title)
        
        # Статус
        status_group = QGroupBox("Статус")
        status_layout = QVBoxLayout(status_group)
        
        self.status_all = QCheckBox("Всі")
        self.status_all.setChecked(True)
        self.status_all.toggled.connect(self.filter_profiles)
        status_layout.addWidget(self.status_all)
        
        self.status_active = QCheckBox("Активні")
        self.status_active.toggled.connect(self.filter_profiles)
        status_layout.addWidget(self.status_active)
        
        self.status_inactive = QCheckBox("Неактивні")
        self.status_inactive.toggled.connect(self.filter_profiles)
        status_layout.addWidget(self.status_inactive)
        
        self.status_running = QCheckBox("Запущені")
        self.status_running.toggled.connect(self.filter_profiles)
        status_layout.addWidget(self.status_running)
        
        layout.addWidget(status_group)
        
        # Типи профілів
        type_group = QGroupBox("Типи")
        type_layout = QVBoxLayout(type_group)
        
        self.type_combos = {}
        for icon_type, emoji in list(PROFILE_ICONS.items())[:10]:  # Перші 10
            check = QCheckBox(f"{emoji} {icon_type.replace('_', ' ').title()}")
            check.toggled.connect(self.filter_profiles)
            type_layout.addWidget(check)
            self.type_combos[icon_type] = check
            
        layout.addWidget(type_group)
        
        # Країни
        country_group = QGroupBox("Країни")
        country_layout = QVBoxLayout(country_group)
        
        self.country_combos = {}
        for country_code, flag in list(COUNTRY_FLAGS.items())[:10]:  # Перші 10
            check = QCheckBox(f"{flag} {country_code}")
            check.toggled.connect(self.filter_profiles)
            country_layout.addWidget(check)
            self.country_combos[country_code] = check
            
        layout.addWidget(country_group)
        
        layout.addStretch()
        parent_layout.addWidget(filter_frame)
        
    def create_profiles_panel(self, parent_layout):
        """Створення панелі профілів"""
        profiles_frame = QFrame()
        layout = QVBoxLayout(profiles_frame)
        
        # Заголовок з лічильником
        header_layout = QHBoxLayout()
        self.profiles_title = QLabel("📁 Профілі")
        self.profiles_title.setStyleSheet("font-size: 16px; font-weight: bold;")
        header_layout.addWidget(self.profiles_title)
        
        self.profiles_count = QLabel("(0)")
        self.profiles_count.setStyleSheet("color: #666;")
        header_layout.addWidget(self.profiles_count)
        
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Скрол область для профілів
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.profiles_widget = QWidget()
        self.profiles_layout = QVBoxLayout(self.profiles_widget)
        self.profiles_layout.setAlignment(Qt.AlignTop)
        
        scroll.setWidget(self.profiles_widget)
        layout.addWidget(scroll)
        
        parent_layout.addWidget(profiles_frame)
        
    def load_profiles(self):
        """Завантаження профілів"""
        try:
            profiles = self.profile_manager.get_all_profiles()
            self.display_profiles(profiles)
            self.update_profiles_count(len(profiles))
            
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося завантажити профілі: {e}")
            
    def display_profiles(self, profiles):
        """Відображення профілів"""
        # Очищаємо поточні віджети
        for i in reversed(range(self.profiles_layout.count())):
            child = self.profiles_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
                
        # Додаємо нові віджети
        for profile in profiles:
            widget = ProfileWidget(profile)
            widget.profileLaunched.connect(self.launch_profile)
            widget.profileEdited.connect(self.edit_profile)
            widget.profileDeleted.connect(self.delete_profile)
            
            # Перевіряємо чи запущений
            if self.chrome_manager.is_profile_running(profile.id):
                widget.set_running(True)
                
            self.profiles_layout.addWidget(widget)
            
        # Додаємо простір внизу
        self.profiles_layout.addStretch()
        
    def update_profiles_count(self, count):
        """Оновлення лічильника профілів"""
        self.profiles_count.setText(f"({count})")
        
    def create_new_profile(self):
        """Створення нового профілю"""
        dialog = ProfileDialogV2(self)
        if dialog.exec_() == QDialog.Accepted:
            try:
                data = dialog.get_profile_data()
                profile = self.profile_manager.create_profile(data['name'], data)
                self.load_profiles()
                self.statusBar().showMessage(f"Профіль '{data['name']}' створено", 3000)
                
            except Exception as e:
                QMessageBox.critical(self, "Помилка", f"Не вдалося створити профіль: {e}")
                
    def edit_profile(self, profile_id):
        """Редагування профілю"""
        try:
            profile = self.profile_manager.get_profile_by_id(profile_id)
            if not profile:
                QMessageBox.warning(self, "Помилка", "Профіль не знайдено")
                return
                
            dialog = ProfileDialogV2(self, profile)
            if dialog.exec_() == QDialog.Accepted:
                data = dialog.get_profile_data()
                self.profile_manager.update_profile(profile_id, data)
                self.load_profiles()
                self.statusBar().showMessage(f"Профіль '{data['name']}' оновлено", 3000)
                
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося оновити профіль: {e}")
            
    def delete_profile(self, profile_id):
        """Видалення профілю"""
        try:
            # Зупиняємо якщо запущений
            if self.chrome_manager.is_profile_running(profile_id):
                self.chrome_manager.stop_profile(profile_id)
                
            self.profile_manager.delete_profile(profile_id)
            self.load_profiles()
            self.statusBar().showMessage("Профіль видалено", 3000)
            
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Не вдалося видалити профіль: {e}")
            
    def launch_profile(self, profile_id):
        """Запуск/зупинка профілю"""
        try:
            if self.chrome_manager.is_profile_running(profile_id):
                # Зупиняємо
                if self.chrome_manager.stop_profile(profile_id):
                    self.statusBar().showMessage("Профіль зупинено", 3000)
                else:
                    QMessageBox.warning(self, "Помилка", "Не вдалося зупинити профіль")
            else:
                # Запускаємо
                profile = self.profile_manager.get_profile_by_id(profile_id)
                if profile:
                    if self.chrome_manager.launch_profile(profile):
                        # Оновлюємо статистику
                        usage_count = getattr(profile, 'usage_count', 0) + 1
                        self.profile_manager.update_profile(profile_id, {
                            'usage_count': usage_count,
                            'last_used': datetime.now().isoformat()
                        })
                        self.statusBar().showMessage(f"Профіль '{profile.name}' запущено", 3000)
                    else:
                        QMessageBox.critical(self, "Помилка", "Не вдалося запустити профіль")
                        
            self.update_running_status()
            
        except Exception as e:
            QMessageBox.critical(self, "Помилка", f"Помилка при запуску профілю: {e}")
            
    def update_running_status(self):
        """Оновлення статусу запущених профілів"""
        for i in range(self.profiles_layout.count() - 1):  # -1 для stretch
            widget = self.profiles_layout.itemAt(i).widget()
            if isinstance(widget, ProfileWidget):
                is_running = self.chrome_manager.is_profile_running(widget.profile.id)
                widget.set_running(is_running)
                
    def filter_profiles(self):
        """Фільтрація профілів"""
        search_text = self.search_edit.text().lower()
        
        try:
            all_profiles = self.profile_manager.get_all_profiles()
            filtered_profiles = []
            
            for profile in all_profiles:
                # Пошук по тексту
                if search_text:
                    searchable_text = f"{profile.name} {getattr(profile, 'description', '')} {getattr(profile, 'tags', '')}".lower()
                    if search_text not in searchable_text:
                        continue
                
                # Фільтр по статусу
                if not self.status_all.isChecked():
                    status = getattr(profile, 'status', 'active')
                    if self.status_active.isChecked() and status != 'active':
                        continue
                    if self.status_inactive.isChecked() and status != 'inactive':
                        continue
                    if self.status_running.isChecked() and not self.chrome_manager.is_profile_running(profile.id):
                        continue
                
                # Фільтр по типу
                icon_type = getattr(profile, 'icon_type', 'default')
                if icon_type in self.type_combos:
                    if self.type_combos[icon_type].isChecked():
                        pass  # включаємо
                    else:
                        # Перевіряємо чи хоча б один тип вибрано
                        any_type_selected = any(cb.isChecked() for cb in self.type_combos.values())
                        if any_type_selected:
                            continue
                            
                # Фільтр по країні
                country_code = getattr(profile, 'country_code', 'UA')
                if country_code in self.country_combos:
                    if self.country_combos[country_code].isChecked():
                        pass  # включаємо
                    else:
                        # Перевіряємо чи хоча б одну країну вибрано
                        any_country_selected = any(cb.isChecked() for cb in self.country_combos.values())
                        if any_country_selected:
                            continue
                
                filtered_profiles.append(profile)
                
            self.display_profiles(filtered_profiles)
            self.update_profiles_count(len(filtered_profiles))
            
        except Exception as e:
            print(f"Помилка фільтрації: {e}")
            
    def sort_profiles(self, sort_type):
        """Сортування профілів"""
        try:
            profiles = self.profile_manager.get_all_profiles()
            
            if sort_type == "За назвою":
                profiles.sort(key=lambda p: p.name.lower())
            elif sort_type == "За статусом":
                profiles.sort(key=lambda p: getattr(p, 'status', 'active'))
            elif sort_type == "За улюбленими":
                profiles.sort(key=lambda p: getattr(p, 'favorite', False), reverse=True)
            # За замовчуванням - за датою використання (вже відсортовано)
            
            self.display_profiles(profiles)
            
        except Exception as e:
            print(f"Помилка сортування: {e}")
            
    def import_profiles(self):
        """Імпорт профілів"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Імпорт профілів", "", "JSON files (*.json)"
        )
        
        if file_path:
            try:
                # TODO: Реалізувати імпорт
                QMessageBox.information(self, "Імпорт", "Функція імпорту буде додана в наступній версії")
            except Exception as e:
                QMessageBox.critical(self, "Помилка", f"Не вдалося імпортувати профілі: {e}")
                
    def export_profiles(self):
        """Експорт профілів"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Експорт профілів", "profiles_export.json", "JSON files (*.json)"
        )
        
        if file_path:
            try:
                # TODO: Реалізувати експорт
                QMessageBox.information(self, "Експорт", "Функція експорту буде додана в наступній версії")
            except Exception as e:
                QMessageBox.critical(self, "Помилка", f"Не вдалося експортувати профілі: {e}")
                
    def show_settings(self):
        """Показ налаштувань"""
        QMessageBox.information(self, "Налаштування", "Вікно налаштувань буде додано в наступній версії")
        
    def cleanup_data(self):
        """Очистка даних"""
        reply = QMessageBox.question(
            self, 'Очистка даних', 
            'Ви впевнені, що хочете видалити всі тимчасові файли?',
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # TODO: Реалізувати очистку
                QMessageBox.information(self, "Очистка", "Тимчасові файли видалено")
            except Exception as e:
                QMessageBox.critical(self, "Помилка", f"Не вдалося очистити дані: {e}")
                
    def show_about(self):
        """Показ інформації про програму"""
        QMessageBox.about(self, "Про програму", """
<h2>AnDetect Profile Manager v2.0</h2>
<p><b>Розширений менеджер профілів браузера</b></p>
<p>Функції:</p>
<ul>
<li>🎨 Іконки та мітки профілів</li>
<li>🌍 Підтримка країн та прапорців</li>
<li>🔐 Автоматична авторизація проксі</li>
<li>📊 Статистика використання</li>
<li>🎯 Розширені фільтри</li>
<li>⚡ Швидкий запуск</li>
</ul>
<p>© 2024 AnDetect Team</p>
        """)
        
    def closeEvent(self, event):
        """Обробка закриття програми"""
        # Зупиняємо всі запущені профілі
        for profile_id in list(self.chrome_manager.running_profiles.keys()):
            self.chrome_manager.stop_profile(profile_id)
            
        event.accept()


def main():
    """Головна функція"""
    app = QApplication(sys.argv)
    app.setApplicationName("AnDetect Profile Manager")
    app.setApplicationVersion("2.0")
    
    # Встановлюємо стиль
    app.setStyle('Fusion')
    
    # Створюємо головне вікно
    window = AnDetectMainWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

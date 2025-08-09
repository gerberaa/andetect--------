#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Розширений діалог створення/редагування профілю з мітками та іконками
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                            QLineEdit, QSpinBox, QComboBox, QCheckBox, 
                            QPushButton, QDialogButtonBox, QTabWidget,
                            QWidget, QLabel, QTextEdit, QGroupBox,
                            QScrollArea, QGridLayout, QFrame, QSlider,
                            QColorDialog, QListWidget, QListWidgetItem,
                            QToolButton, QButtonGroup, QRadioButton)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap, QFont, QPalette, QColor

from profile_icons import (ProfileIcon, PROFILE_ICONS, COUNTRY_FLAGS, 
                          LABEL_COLORS, get_country_by_timezone)


class ColorButton(QPushButton):
    """Кнопка для вибору кольору"""
    
    colorChanged = pyqtSignal(str)
    
    def __init__(self, color_name="blue", parent=None):
        super().__init__(parent)
        self.color_name = color_name
        self.setFixedSize(40, 30)
        self.clicked.connect(self.choose_color)
        self.update_color()
        
    def update_color(self):
        """Оновлення кольору кнопки"""
        color = LABEL_COLORS.get(self.color_name, '#4488FF')
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                border: 2px solid #333;
                border-radius: 5px;
            }}
            QPushButton:hover {{
                border: 2px solid #000;
            }}
            QPushButton:pressed {{
                border: 3px solid #000;
            }}
        """)
        
    def choose_color(self):
        """Відкриття діалогу вибору кольору"""
        current_color = QColor(LABEL_COLORS.get(self.color_name, '#4488FF'))
        color = QColorDialog.getColor(current_color, self, "Виберіть колір мітки")
        
        if color.isValid():
            self.color_name = color.name()
            self.update_color()
            self.colorChanged.emit(self.color_name)


class IconButton(QToolButton):
    """Кнопка для вибору іконки"""
    
    iconChanged = pyqtSignal(str)
    
    def __init__(self, icon_type="default", parent=None):
        super().__init__(parent)
        self.icon_type = icon_type
        self.setFixedSize(50, 50)
        self.clicked.connect(self.choose_icon)
        self.update_icon()
        
    def update_icon(self):
        """Оновлення іконки кнопки"""
        icon = ProfileIcon.create_profile_icon(self.icon_type, size=32)
        self.setIcon(icon)
        self.setIconSize(icon.availableSizes()[0] if icon.availableSizes() else (32, 32))
        self.setToolTip(f"Тип: {self.icon_type}")
        
    def choose_icon(self):
        """Відкриття діалогу вибору іконки"""
        dialog = IconPickerDialog(self.icon_type, self)
        if dialog.exec_() == QDialog.Accepted:
            self.icon_type = dialog.selected_icon
            self.update_icon()
            self.iconChanged.emit(self.icon_type)


class IconPickerDialog(QDialog):
    """Діалог вибору іконки"""
    
    def __init__(self, current_icon="default", parent=None):
        super().__init__(parent)
        self.selected_icon = current_icon
        self.setWindowTitle("Виберіть іконку профілю")
        self.setMinimumSize(400, 300)
        self.init_ui()
        
    def init_ui(self):
        """Ініціалізація інтерфейсу"""
        layout = QVBoxLayout(self)
        
        # Область прокрутки
        scroll = QScrollArea()
        scroll_widget = QWidget()
        grid_layout = QGridLayout(scroll_widget)
        
        # Групи іконок
        self.button_group = QButtonGroup()
        
        row, col = 0, 0
        for icon_type, emoji in PROFILE_ICONS.items():
            btn = QRadioButton()
            btn.setFixedSize(60, 60)
            btn.setStyleSheet(f"""
                QRadioButton {{
                    border: 2px solid #ccc;
                    border-radius: 5px;
                    background: white;
                    font-size: 24px;
                }}
                QRadioButton:checked {{
                    border: 3px solid #007acc;
                    background: #e6f3ff;
                }}
                QRadioButton:hover {{
                    border: 2px solid #007acc;
                }}
                QRadioButton::indicator {{
                    width: 0px;
                    height: 0px;
                }}
            """)
            
            btn.setText(emoji)
            btn.setToolTip(f"{icon_type.replace('_', ' ').title()}")
            btn.toggled.connect(lambda checked, it=icon_type: self.icon_selected(it) if checked else None)
            
            if icon_type == self.selected_icon:
                btn.setChecked(True)
                
            self.button_group.addButton(btn)
            grid_layout.addWidget(btn, row, col)
            
            col += 1
            if col >= 6:  # 6 іконок в рядку
                col = 0
                row += 1
        
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
        
        # Кнопки
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
    def icon_selected(self, icon_type):
        """Обробка вибору іконки"""
        self.selected_icon = icon_type


class ProfileDialogV2(QDialog):
    """Розширений діалог створення/редагування профілю"""
    
    def __init__(self, parent=None, profile=None):
        super().__init__(parent)
        self.profile = profile
        self.setWindowTitle('Створити профіль' if not profile else 'Редагувати профіль')
        self.setMinimumSize(700, 800)
        self.init_ui()
        
        if profile:
            self.load_profile_data()
        else:
            self.set_defaults()
            
    def init_ui(self):
        """Ініціалізація інтерфейсу"""
        layout = QVBoxLayout(self)
        
        # Вкладки
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)
        
        # Основна інформація
        self.create_general_tab(tab_widget)
        
        # Зовнішність та мітки
        self.create_appearance_tab(tab_widget)
        
        # Browser fingerprinting
        self.create_fingerprint_tab(tab_widget)
        
        # Проксі
        self.create_proxy_tab(tab_widget)
        
        # Дозволи
        self.create_permissions_tab(tab_widget)
        
        # Додаткове
        self.create_advanced_tab(tab_widget)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        
        generate_btn = QPushButton("🎲 Генерувати випадкові дані")
        generate_btn.clicked.connect(self.generate_random_data)
        buttons_layout.addWidget(generate_btn)
        
        test_btn = QPushButton("🧪 Тест конфігурації")
        test_btn.clicked.connect(self.test_configuration)
        buttons_layout.addWidget(test_btn)
        
        buttons_layout.addStretch()
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        buttons_layout.addWidget(buttons)
        
        layout.addLayout(buttons_layout)
        
    def create_general_tab(self, tab_widget):
        """Вкладка загальної інформації"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Основна інформація
        main_group = QGroupBox("Основна інформація")
        main_layout = QFormLayout(main_group)
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Введіть назву профілю")
        main_layout.addRow("Назва профілю:", self.name_edit)
        
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(60)
        self.description_edit.setPlaceholderText("Опис профілю...")
        main_layout.addRow("Опис:", self.description_edit)
        
        self.tags_edit = QLineEdit()
        self.tags_edit.setPlaceholderText("робота, соціальні мережі, покупки")
        main_layout.addRow("Теги (через кому):", self.tags_edit)
        
        layout.addWidget(main_group)
        
        # Статус
        status_group = QGroupBox("Статус та пріоритет")
        status_layout = QFormLayout(status_group)
        
        self.status_combo = QComboBox()
        self.status_combo.addItems(['active', 'inactive', 'blocked'])
        status_layout.addRow("Статус:", self.status_combo)
        
        self.favorite_check = QCheckBox("⭐ Улюблений профіль")
        status_layout.addRow(self.favorite_check)
        
        layout.addWidget(status_group)
        
        # Нотатки
        notes_group = QGroupBox("Нотатки")
        notes_layout = QVBoxLayout(notes_group)
        
        self.notes_edit = QTextEdit()
        self.notes_edit.setMaximumHeight(80)
        self.notes_edit.setPlaceholderText("Ваші нотатки про цей профіль...")
        notes_layout.addWidget(self.notes_edit)
        
        layout.addWidget(notes_group)
        layout.addStretch()
        
        tab_widget.addTab(widget, "📋 Загальні")
        
    def create_appearance_tab(self, tab_widget):
        """Вкладка зовнішності та міток"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Іконка профілю
        icon_group = QGroupBox("Іконка профілю")
        icon_layout = QHBoxLayout(icon_group)
        
        icon_layout.addWidget(QLabel("Тип іконки:"))
        self.icon_button = IconButton()
        self.icon_button.iconChanged.connect(self.on_icon_changed)
        icon_layout.addWidget(self.icon_button)
        icon_layout.addStretch()
        
        layout.addWidget(icon_group)
        
        # Прапорець країни
        country_group = QGroupBox("Прапорець країни")
        country_layout = QFormLayout(country_group)
        
        self.country_combo = QComboBox()
        countries = list(COUNTRY_FLAGS.keys())
        countries.sort()
        for country in countries:
            flag = COUNTRY_FLAGS[country]
            self.country_combo.addItem(f"{flag} {country}", country)
        country_layout.addRow("Країна:", self.country_combo)
        
        layout.addWidget(country_group)
        
        # Колір мітки
        color_group = QGroupBox("Колір мітки")
        color_layout = QHBoxLayout(color_group)
        
        color_layout.addWidget(QLabel("Колір:"))
        self.color_button = ColorButton()
        self.color_button.colorChanged.connect(self.on_color_changed)
        color_layout.addWidget(self.color_button)
        
        # Швидкі кольори
        quick_colors = ['red', 'orange', 'yellow', 'green', 'blue', 'purple', 'pink', 'gray']
        for color_name in quick_colors:
            btn = QPushButton()
            btn.setFixedSize(25, 25)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {LABEL_COLORS[color_name]};
                    border: 1px solid #333;
                    border-radius: 3px;
                }}
                QPushButton:hover {{
                    border: 2px solid #000;
                }}
            """)
            btn.clicked.connect(lambda checked, c=color_name: self.set_quick_color(c))
            color_layout.addWidget(btn)
            
        color_layout.addStretch()
        layout.addWidget(color_group)
        
        # Попередній перегляд
        preview_group = QGroupBox("Попередній перегляд")
        preview_layout = QHBoxLayout(preview_group)
        
        self.preview_label = QLabel("🌐 Профіль")
        self.preview_label.setStyleSheet("""
            QLabel {
                padding: 10px;
                border: 2px solid #ccc;
                border-radius: 5px;
                background: white;
                font-size: 14px;
            }
        """)
        preview_layout.addWidget(self.preview_label)
        preview_layout.addStretch()
        
        layout.addWidget(preview_group)
        layout.addStretch()
        
        tab_widget.addTab(widget, "🎨 Зовнішність")
        
    def create_fingerprint_tab(self, tab_widget):
        """Вкладка налаштувань fingerprinting"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # User-Agent
        ua_group = QGroupBox("User-Agent")
        ua_layout = QVBoxLayout(ua_group)
        
        self.user_agent_edit = QTextEdit()
        self.user_agent_edit.setMaximumHeight(80)
        self.user_agent_edit.setPlaceholderText("User-Agent браузера")
        ua_layout.addWidget(self.user_agent_edit)
        
        ua_buttons = QHBoxLayout()
        chrome_btn = QPushButton("Chrome")
        firefox_btn = QPushButton("Firefox")
        safari_btn = QPushButton("Safari")
        edge_btn = QPushButton("Edge")
        
        chrome_btn.clicked.connect(lambda: self.set_browser_ua('chrome'))
        firefox_btn.clicked.connect(lambda: self.set_browser_ua('firefox'))
        safari_btn.clicked.connect(lambda: self.set_browser_ua('safari'))
        edge_btn.clicked.connect(lambda: self.set_browser_ua('edge'))
        
        ua_buttons.addWidget(chrome_btn)
        ua_buttons.addWidget(firefox_btn)
        ua_buttons.addWidget(safari_btn)
        ua_buttons.addWidget(edge_btn)
        ua_buttons.addStretch()
        
        ua_layout.addLayout(ua_buttons)
        layout.addWidget(ua_group)
        
        # Розмір екрану
        screen_group = QGroupBox("Параметри екрану")
        screen_layout = QFormLayout(screen_group)
        
        screen_size_layout = QHBoxLayout()
        self.screen_width_spin = QSpinBox()
        self.screen_width_spin.setRange(800, 4096)
        self.screen_width_spin.setValue(1920)
        screen_size_layout.addWidget(self.screen_width_spin)
        
        screen_size_layout.addWidget(QLabel("×"))
        
        self.screen_height_spin = QSpinBox()
        self.screen_height_spin.setRange(600, 2160)
        self.screen_height_spin.setValue(1080)
        screen_size_layout.addWidget(self.screen_height_spin)
        
        # Швидкі розміри
        sizes_layout = QHBoxLayout()
        common_sizes = [
            (1920, 1080, "FHD"), (1366, 768, "HD"), (1440, 900, "HD+"),
            (2560, 1440, "QHD"), (1280, 1024, "SXGA")
        ]
        
        for width, height, name in common_sizes:
            btn = QPushButton(name)
            btn.clicked.connect(lambda checked, w=width, h=height: self.set_screen_size(w, h))
            sizes_layout.addWidget(btn)
        sizes_layout.addStretch()
        
        screen_layout.addRow("Розмір:", screen_size_layout)
        screen_layout.addRow("Швидкий вибір:", sizes_layout)
        
        layout.addWidget(screen_group)
        
        # Локалізація
        locale_group = QGroupBox("Локалізація")
        locale_layout = QFormLayout(locale_group)
        
        self.timezone_combo = QComboBox()
        timezones = [
            'Europe/Kiev', 'Europe/London', 'Europe/Berlin', 'Europe/Paris',
            'America/New_York', 'America/Los_Angeles', 'America/Chicago',
            'Asia/Tokyo', 'Asia/Shanghai', 'Australia/Sydney'
        ]
        self.timezone_combo.addItems(timezones)
        self.timezone_combo.currentTextChanged.connect(self.on_timezone_changed)
        locale_layout.addRow("Часовий пояс:", self.timezone_combo)
        
        self.language_combo = QComboBox()
        languages = ['uk-UA', 'en-US', 'en-GB', 'de-DE', 'fr-FR', 'es-ES', 'ja-JP', 'zh-CN']
        self.language_combo.addItems(languages)
        locale_layout.addRow("Мова:", self.language_combo)
        
        layout.addWidget(locale_group)
        layout.addStretch()
        
        tab_widget.addTab(widget, "🔍 Fingerprinting")
        
    def create_proxy_tab(self, tab_widget):
        """Вкладка налаштувань проксі"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Швидкий ввід
        quick_group = QGroupBox("Швидкий ввід проксі")
        quick_layout = QFormLayout(quick_group)
        
        self.proxy_string_edit = QLineEdit()
        self.proxy_string_edit.setPlaceholderText("45.158.61.63:46130:RQQ6C0VF:MZH4VXZU")
        self.proxy_string_edit.textChanged.connect(self.parse_proxy_string)
        quick_layout.addRow("IP:PORT:USER:PASS:", self.proxy_string_edit)
        
        layout.addWidget(quick_group)
        
        # Детальні налаштування
        proxy_group = QGroupBox("Детальні налаштування проксі")
        proxy_layout = QFormLayout(proxy_group)
        
        self.proxy_type_combo = QComboBox()
        self.proxy_type_combo.addItems(['HTTP', 'SOCKS5'])
        proxy_layout.addRow("Тип:", self.proxy_type_combo)
        
        self.proxy_host_edit = QLineEdit()
        self.proxy_host_edit.setPlaceholderText("IP адреса")
        proxy_layout.addRow("Хост:", self.proxy_host_edit)
        
        self.proxy_port_spin = QSpinBox()
        self.proxy_port_spin.setRange(1, 65535)
        self.proxy_port_spin.setValue(8080)
        proxy_layout.addRow("Порт:", self.proxy_port_spin)
        
        self.proxy_username_edit = QLineEdit()
        self.proxy_username_edit.setPlaceholderText("Логін")
        proxy_layout.addRow("Логін:", self.proxy_username_edit)
        
        self.proxy_password_edit = QLineEdit()
        self.proxy_password_edit.setEchoMode(QLineEdit.Password)
        self.proxy_password_edit.setPlaceholderText("Пароль")
        proxy_layout.addRow("Пароль:", self.proxy_password_edit)
        
        layout.addWidget(proxy_group)
        
        # Тест проксі
        test_layout = QHBoxLayout()
        test_proxy_btn = QPushButton("🧪 Тестувати проксі")
        test_proxy_btn.clicked.connect(self.test_proxy)
        test_layout.addWidget(test_proxy_btn)
        test_layout.addStretch()
        
        layout.addLayout(test_layout)
        layout.addStretch()
        
        tab_widget.addTab(widget, "🌐 Проксі")
        
    def create_permissions_tab(self, tab_widget):
        """Вкладка дозволів браузера"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Основні дозволи
        main_permissions = QGroupBox("Основні дозволи")
        main_layout = QVBoxLayout(main_permissions)
        
        self.javascript_check = QCheckBox("🟨 Дозволити JavaScript")
        self.javascript_check.setChecked(True)
        main_layout.addWidget(self.javascript_check)
        
        self.images_check = QCheckBox("🖼️ Завантажувати зображення")
        self.images_check.setChecked(True)
        main_layout.addWidget(self.images_check)
        
        self.plugins_check = QCheckBox("🔌 Дозволити плагіни")
        self.plugins_check.setChecked(True)
        main_layout.addWidget(self.plugins_check)
        
        self.cookies_check = QCheckBox("🍪 Зберігати cookies")
        self.cookies_check.setChecked(True)
        main_layout.addWidget(self.cookies_check)
        
        layout.addWidget(main_permissions)
        
        # Приватність
        privacy_permissions = QGroupBox("Приватність")
        privacy_layout = QVBoxLayout(privacy_permissions)
        
        self.geolocation_check = QCheckBox("🌍 Дозволити геолокацію")
        self.geolocation_check.setChecked(False)
        privacy_layout.addWidget(self.geolocation_check)
        
        self.notifications_check = QCheckBox("🔔 Дозволити сповіщення")
        self.notifications_check.setChecked(False)
        privacy_layout.addWidget(self.notifications_check)
        
        self.webrtc_check = QCheckBox("📹 Дозволити WebRTC")
        self.webrtc_check.setChecked(False)
        privacy_layout.addWidget(self.webrtc_check)
        
        layout.addWidget(privacy_permissions)
        layout.addStretch()
        
        tab_widget.addTab(widget, "🔒 Дозволи")
        
    def create_advanced_tab(self, tab_widget):
        """Вкладка додаткових налаштувань"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Статистика
        stats_group = QGroupBox("Статистика використання")
        stats_layout = QFormLayout(stats_group)
        
        self.usage_count_label = QLabel("0")
        stats_layout.addRow("Кількість запусків:", self.usage_count_label)
        
        self.total_time_label = QLabel("0 хв")
        stats_layout.addRow("Загальний час:", self.total_time_label)
        
        self.last_ip_label = QLabel("Невідомо")
        stats_layout.addRow("Останній IP:", self.last_ip_label)
        
        layout.addWidget(stats_group)
        
        # Fingerprints
        fingerprints_group = QGroupBox("Унікальні відбитки")
        fingerprints_layout = QFormLayout(fingerprints_group)
        
        self.canvas_edit = QLineEdit()
        self.canvas_edit.setPlaceholderText("Автоматично генерується")
        fingerprints_layout.addRow("Canvas:", self.canvas_edit)
        
        self.webgl_edit = QLineEdit()
        self.webgl_edit.setPlaceholderText("Автоматично генерується")
        fingerprints_layout.addRow("WebGL:", self.webgl_edit)
        
        regen_fingerprints_btn = QPushButton("🔄 Згенерувати нові")
        regen_fingerprints_btn.clicked.connect(self.regenerate_fingerprints)
        fingerprints_layout.addRow(regen_fingerprints_btn)
        
        layout.addWidget(fingerprints_group)
        layout.addStretch()
        
        tab_widget.addTab(widget, "⚙️ Додаткове")
    
    def set_defaults(self):
        """Встановлення значень за замовчуванням"""
        self.name_edit.setText("Новий профіль")
        self.status_combo.setCurrentText("active")
        self.country_combo.setCurrentText("UA")
        self.generate_random_data()
        
    def generate_random_data(self):
        """Генерація випадкових даних"""
        import random
        from user_agents import get_random_user_agent
        
        # User-Agent
        try:
            self.user_agent_edit.setPlainText(get_random_user_agent())
        except:
            pass
            
        # Розмір екрану
        sizes = [(1920, 1080), (1366, 768), (1440, 900), (2560, 1440)]
        width, height = random.choice(sizes)
        self.screen_width_spin.setValue(width)
        self.screen_height_spin.setValue(height)
        
        # Fingerprints
        import uuid
        self.canvas_edit.setText(str(uuid.uuid4())[:16])
        self.webgl_edit.setText(str(uuid.uuid4())[:16])
        
        # Випадкова іконка
        icon_types = list(PROFILE_ICONS.keys())
        random_icon = random.choice(icon_types)
        self.icon_button.icon_type = random_icon
        self.icon_button.update_icon()
        
        # Випадковий колір
        colors = list(LABEL_COLORS.keys())
        random_color = random.choice(colors)
        self.color_button.color_name = random_color
        self.color_button.update_color()
        
        self.update_preview()
        
    def parse_proxy_string(self):
        """Парсинг проксі рядка"""
        proxy_string = self.proxy_string_edit.text().strip()
        
        if ':' in proxy_string:
            parts = proxy_string.split(':')
            if len(parts) >= 2:
                self.proxy_host_edit.setText(parts[0])
                try:
                    self.proxy_port_spin.setValue(int(parts[1]))
                except ValueError:
                    pass
                    
                if len(parts) >= 4:
                    self.proxy_username_edit.setText(parts[2])
                    self.proxy_password_edit.setText(parts[3])
                    
    def on_icon_changed(self, icon_type):
        """Обробка зміни іконки"""
        self.update_preview()
        
    def on_color_changed(self, color):
        """Обробка зміни кольору"""
        self.update_preview()
        
    def on_timezone_changed(self, timezone):
        """Обробка зміни часового поясу"""
        country = get_country_by_timezone(timezone)
        index = self.country_combo.findData(country)
        if index >= 0:
            self.country_combo.setCurrentIndex(index)
        self.update_preview()
        
    def set_quick_color(self, color_name):
        """Швидке встановлення кольору"""
        self.color_button.color_name = color_name
        self.color_button.update_color()
        self.update_preview()
        
    def set_screen_size(self, width, height):
        """Встановлення розміру екрану"""
        self.screen_width_spin.setValue(width)
        self.screen_height_spin.setValue(height)
        
    def set_browser_ua(self, browser):
        """Встановлення User-Agent для браузера"""
        from user_agents import get_user_agents_by_browser
        
        try:
            import random
            user_agents = get_user_agents_by_browser(browser)
            if user_agents:
                ua = random.choice(user_agents)
                self.user_agent_edit.setPlainText(ua)
        except:
            pass
            
    def regenerate_fingerprints(self):
        """Перегенерація fingerprints"""
        import uuid
        self.canvas_edit.setText(str(uuid.uuid4())[:16])
        self.webgl_edit.setText(str(uuid.uuid4())[:16])
        
    def update_preview(self):
        """Оновлення попереднього перегляду"""
        icon_emoji = PROFILE_ICONS.get(self.icon_button.icon_type, '🌐')
        country_emoji = COUNTRY_FLAGS.get(self.country_combo.currentData(), '🇺🇦')
        color = LABEL_COLORS.get(self.color_button.color_name, '#4488FF')
        
        name = self.name_edit.text() or "Профіль"
        
        self.preview_label.setText(f"{icon_emoji} {country_emoji} {name}")
        self.preview_label.setStyleSheet(f"""
            QLabel {{
                padding: 10px;
                border: 3px solid {color};
                border-radius: 8px;
                background: white;
                font-size: 14px;
                font-weight: bold;
            }}
        """)
        
    def test_proxy(self):
        """Тестування проксі"""
        from PyQt5.QtWidgets import QMessageBox
        QMessageBox.information(self, "Тест проксі", "Функція тестування проксі буде додана")
        
    def test_configuration(self):
        """Тестування конфігурації"""
        from PyQt5.QtWidgets import QMessageBox
        
        errors = []
        warnings = []
        
        # Перевірки
        if not self.name_edit.text().strip():
            errors.append("Назва профілю не може бути пустою")
            
        if not self.user_agent_edit.toPlainText().strip():
            errors.append("User-Agent не може бути пустим")
            
        if self.proxy_host_edit.text() and not self.proxy_port_spin.value():
            warnings.append("Вказано хост проксі але не вказано порт")
            
        # Результат
        if errors:
            QMessageBox.critical(self, "Помилки конфігурації", "\n".join(errors))
        elif warnings:
            QMessageBox.warning(self, "Попередження", "\n".join(warnings))
        else:
            QMessageBox.information(self, "Тест пройдено", "✅ Конфігурація профілю валідна!")
            
    def load_profile_data(self):
        """Завантаження даних профілю"""
        if not self.profile:
            return
            
        # Основні дані
        self.name_edit.setText(self.profile.name)
        self.description_edit.setPlainText(getattr(self.profile, 'description', ''))
        self.tags_edit.setText(getattr(self.profile, 'tags', ''))
        self.notes_edit.setPlainText(getattr(self.profile, 'notes', ''))
        
        # Статус
        status = getattr(self.profile, 'status', 'active')
        self.status_combo.setCurrentText(status)
        self.favorite_check.setChecked(getattr(self.profile, 'favorite', False))
        
        # Зовнішність
        icon_type = getattr(self.profile, 'icon_type', 'default')
        self.icon_button.icon_type = icon_type
        self.icon_button.update_icon()
        
        country_code = getattr(self.profile, 'country_code', 'UA')
        index = self.country_combo.findData(country_code)
        if index >= 0:
            self.country_combo.setCurrentIndex(index)
            
        color = getattr(self.profile, 'label_color', 'blue')
        self.color_button.color_name = color
        self.color_button.update_color()
        
        # Fingerprinting
        self.user_agent_edit.setPlainText(self.profile.user_agent)
        self.screen_width_spin.setValue(self.profile.screen_width)
        self.screen_height_spin.setValue(self.profile.screen_height)
        
        tz_index = self.timezone_combo.findText(self.profile.timezone)
        if tz_index >= 0:
            self.timezone_combo.setCurrentIndex(tz_index)
            
        lang_index = self.language_combo.findText(self.profile.language)
        if lang_index >= 0:
            self.language_combo.setCurrentIndex(lang_index)
            
        # Проксі
        if self.profile.proxy_host:
            self.proxy_host_edit.setText(self.profile.proxy_host)
            self.proxy_port_spin.setValue(self.profile.proxy_port)
            self.proxy_username_edit.setText(self.profile.proxy_username)
            self.proxy_password_edit.setText(self.profile.proxy_password)
            
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
        self.cookies_check.setChecked(self.profile.cookies_enabled)
        self.geolocation_check.setChecked(self.profile.geolocation_enabled)
        self.notifications_check.setChecked(self.profile.notifications_enabled)
        self.webrtc_check.setChecked(self.profile.webrtc_enabled)
        
        # Додаткове
        self.canvas_edit.setText(self.profile.canvas_fingerprint)
        self.webgl_edit.setText(self.profile.webgl_fingerprint)
        
        # Статистика
        usage_count = getattr(self.profile, 'usage_count', 0)
        self.usage_count_label.setText(str(usage_count))
        
        total_time = getattr(self.profile, 'total_time', 0)
        hours = total_time // 3600
        minutes = (total_time % 3600) // 60
        if hours > 0:
            self.total_time_label.setText(f"{hours}г {minutes}хв")
        else:
            self.total_time_label.setText(f"{minutes}хв")
            
        last_ip = getattr(self.profile, 'last_ip', '')
        self.last_ip_label.setText(last_ip or "Невідомо")
        
        self.update_preview()
        
    def get_profile_data(self):
        """Отримання даних з форми"""
        return {
            'name': self.name_edit.text().strip(),
            'description': self.description_edit.toPlainText().strip(),
            'tags': self.tags_edit.text().strip(),
            'notes': self.notes_edit.toPlainText().strip(),
            'status': self.status_combo.currentText(),
            'favorite': self.favorite_check.isChecked(),
            'icon_type': self.icon_button.icon_type,
            'country_code': self.country_combo.currentData(),
            'label_color': self.color_button.color_name,
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
            'cookies_enabled': self.cookies_check.isChecked(),
            'geolocation_enabled': self.geolocation_check.isChecked(),
            'notifications_enabled': self.notifications_check.isChecked(),
            'webrtc_enabled': self.webrtc_check.isChecked(),
            'canvas_fingerprint': self.canvas_edit.text().strip(),
            'webgl_fingerprint': self.webgl_edit.text().strip(),
        }
        
    def accept(self):
        """Перевірка та збереження"""
        data = self.get_profile_data()
        
        if not data['name']:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, 'Помилка', 'Назва профілю не може бути пустою!')
            return
            
        if not data['user_agent']:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, 'Помилка', 'User-Agent не може бути пустим!')
            return
            
        super().accept()

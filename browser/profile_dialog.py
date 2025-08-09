#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Діалог для створення та редагування профілів браузера
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                            QLineEdit, QSpinBox, QComboBox, QCheckBox, 
                            QPushButton, QDialogButtonBox, QTabWidget,
                            QWidget, QLabel, QTextEdit, QGroupBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import random


class ProfileDialog(QDialog):
    """Діалог створення/редагування профілю"""
    
    def __init__(self, parent=None, profile=None):
        super().__init__(parent)
        self.profile = profile
        self.init_ui()
        
        if profile:
            self.load_profile_data()
            
    def init_ui(self):
        """Ініціалізація інтерфейсу"""
        self.setWindowTitle('Налаштування профілю')
        self.setMinimumSize(500, 600)
        
        layout = QVBoxLayout(self)
        
        # Вкладки
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)
        
        # Основні налаштування
        self.create_general_tab(tab_widget)
        
        # Fingerprinting
        self.create_fingerprint_tab(tab_widget)
        
        # Проксі
        self.create_proxy_tab(tab_widget)
        
        # Безпека
        self.create_security_tab(tab_widget)
        
        # Кнопки
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        # Кнопка генерації випадкових даних
        random_btn = QPushButton('Генерувати випадкові дані')
        random_btn.clicked.connect(self.generate_random_data)
        layout.insertWidget(-1, random_btn)
        
    def create_general_tab(self, tab_widget):
        """Вкладка загальних налаштувань"""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        # Назва профілю
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText('Введіть назву профілю')
        layout.addRow('Назва профілю:', self.name_edit)
        
        # User Agent
        self.user_agent_edit = QTextEdit()
        self.user_agent_edit.setMaximumHeight(80)
        self.user_agent_edit.setPlaceholderText('User-Agent браузера')
        layout.addRow('User-Agent:', self.user_agent_edit)
        
        # Мова
        self.language_combo = QComboBox()
        self.language_combo.addItems([
            'uk-UA,uk;q=0.9,en;q=0.8',
            'en-US,en;q=0.9', 
            'en-GB,en;q=0.9',
            'de-DE,de;q=0.9',
            'fr-FR,fr;q=0.9',
            'es-ES,es;q=0.9'
        ])
        layout.addRow('Мова:', self.language_combo)
        
        # Часовий пояс
        self.timezone_combo = QComboBox()
        self.timezone_combo.addItems([
            'Europe/Kiev',
            'Europe/London', 
            'Europe/Berlin',
            'Europe/Paris',
            'America/New_York',
            'America/Los_Angeles',
            'Asia/Tokyo'
        ])
        layout.addRow('Часовий пояс:', self.timezone_combo)
        
        tab_widget.addTab(widget, 'Загальні')
        
    def create_fingerprint_tab(self, tab_widget):
        """Вкладка налаштувань fingerprinting"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Розмір екрану
        screen_group = QGroupBox('Параметри екрану')
        screen_layout = QFormLayout(screen_group)
        
        self.screen_width_spin = QSpinBox()
        self.screen_width_spin.setRange(800, 4096)
        self.screen_width_spin.setValue(1920)
        screen_layout.addRow('Ширина:', self.screen_width_spin)
        
        self.screen_height_spin = QSpinBox()
        self.screen_height_spin.setRange(600, 2160)
        self.screen_height_spin.setValue(1080)
        screen_layout.addRow('Висота:', self.screen_height_spin)
        
        layout.addWidget(screen_group)
        
        # Canvas та WebGL
        fingerprint_group = QGroupBox('Fingerprinting')
        fingerprint_layout = QFormLayout(fingerprint_group)
        
        self.canvas_edit = QLineEdit()
        self.canvas_edit.setPlaceholderText('Canvas fingerprint (авто-генерується)')
        fingerprint_layout.addRow('Canvas:', self.canvas_edit)
        
        self.webgl_edit = QLineEdit()
        self.webgl_edit.setPlaceholderText('WebGL fingerprint (авто-генерується)')
        fingerprint_layout.addRow('WebGL:', self.webgl_edit)
        
        layout.addWidget(fingerprint_group)
        
        layout.addStretch()
        tab_widget.addTab(widget, 'Fingerprinting')
        
    def create_proxy_tab(self, tab_widget):
        """Вкладка налаштувань проксі"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        proxy_group = QGroupBox('Налаштування проксі')
        proxy_layout = QFormLayout(proxy_group)
        
        # Тип проксі
        self.proxy_type_combo = QComboBox()
        self.proxy_type_combo.addItems(['HTTP', 'SOCKS5'])
        proxy_layout.addRow('Тип:', self.proxy_type_combo)
        
        # Хост
        self.proxy_host_edit = QLineEdit()
        self.proxy_host_edit.setPlaceholderText('127.0.0.1')
        proxy_layout.addRow('Хост:', self.proxy_host_edit)
        
        # Порт
        self.proxy_port_spin = QSpinBox()
        self.proxy_port_spin.setRange(1, 65535)
        self.proxy_port_spin.setValue(8080)
        proxy_layout.addRow('Порт:', self.proxy_port_spin)
        
        # Логін
        self.proxy_username_edit = QLineEdit()
        self.proxy_username_edit.setPlaceholderText('Логін (необов\'язково)')
        proxy_layout.addRow('Логін:', self.proxy_username_edit)
        
        # Пароль
        self.proxy_password_edit = QLineEdit()
        self.proxy_password_edit.setEchoMode(QLineEdit.Password)
        self.proxy_password_edit.setPlaceholderText('Пароль (необов\'язково)')
        proxy_layout.addRow('Пароль:', self.proxy_password_edit)
        
        layout.addWidget(proxy_group)
        layout.addStretch()
        
        tab_widget.addTab(widget, 'Проксі')
        
    def create_security_tab(self, tab_widget):
        """Вкладка налаштувань безпеки"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Дозволи
        permissions_group = QGroupBox('Дозволи')
        permissions_layout = QVBoxLayout(permissions_group)
        
        self.cookies_check = QCheckBox('Зберігати cookies')
        self.cookies_check.setChecked(True)
        permissions_layout.addWidget(self.cookies_check)
        
        self.javascript_check = QCheckBox('Дозволити JavaScript')
        self.javascript_check.setChecked(True)
        permissions_layout.addWidget(self.javascript_check)
        
        self.images_check = QCheckBox('Завантажувати зображення')
        self.images_check.setChecked(True)
        permissions_layout.addWidget(self.images_check)
        
        self.plugins_check = QCheckBox('Дозволити плагіни')
        self.plugins_check.setChecked(True)
        permissions_layout.addWidget(self.plugins_check)
        
        self.geolocation_check = QCheckBox('Дозволити геолокацію')
        self.geolocation_check.setChecked(False)
        permissions_layout.addWidget(self.geolocation_check)
        
        self.notifications_check = QCheckBox('Дозволити сповіщення')
        self.notifications_check.setChecked(False)
        permissions_layout.addWidget(self.notifications_check)
        
        self.webrtc_check = QCheckBox('Дозволити WebRTC')
        self.webrtc_check.setChecked(False)
        permissions_layout.addWidget(self.webrtc_check)
        
        layout.addWidget(permissions_group)
        layout.addStretch()
        
        tab_widget.addTab(widget, 'Безпека')
        
    def generate_random_data(self):
        """Генерація випадкових даних профілю"""
        # User agents
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        ]
        
        # Розміри екрану
        screen_sizes = [
            (1920, 1080), (1366, 768), (1440, 900), (1600, 900), 
            (1280, 1024), (1680, 1050), (2560, 1440)
        ]
        
        # Генеруємо дані
        self.user_agent_edit.setPlainText(random.choice(user_agents))
        
        width, height = random.choice(screen_sizes)
        self.screen_width_spin.setValue(width)
        self.screen_height_spin.setValue(height)
        
        # Випадкові fingerprints
        import uuid
        self.canvas_edit.setText(str(uuid.uuid4()))
        self.webgl_edit.setText(str(uuid.uuid4()))
        
    def load_profile_data(self):
        """Завантаження даних профілю для редагування"""
        if not self.profile:
            return
            
        self.name_edit.setText(self.profile.name)
        self.user_agent_edit.setPlainText(self.profile.user_agent)
        self.screen_width_spin.setValue(self.profile.screen_width)
        self.screen_height_spin.setValue(self.profile.screen_height)
        
        # Встановлюємо мову
        index = self.language_combo.findText(self.profile.language)
        if index >= 0:
            self.language_combo.setCurrentIndex(index)
            
        # Встановлюємо часовий пояс
        index = self.timezone_combo.findText(self.profile.timezone)
        if index >= 0:
            self.timezone_combo.setCurrentIndex(index)
            
        # Fingerprints
        self.canvas_edit.setText(self.profile.canvas_fingerprint)
        self.webgl_edit.setText(self.profile.webgl_fingerprint)
        
        # Проксі
        if self.profile.proxy_host:
            self.proxy_host_edit.setText(self.profile.proxy_host)
            self.proxy_port_spin.setValue(self.profile.proxy_port)
            self.proxy_username_edit.setText(self.profile.proxy_username)
            self.proxy_password_edit.setText(self.profile.proxy_password)
            
            index = self.proxy_type_combo.findText(self.profile.proxy_type)
            if index >= 0:
                self.proxy_type_combo.setCurrentIndex(index)
                
        # Дозволи
        self.cookies_check.setChecked(self.profile.cookies_enabled)
        self.javascript_check.setChecked(self.profile.javascript_enabled)
        self.images_check.setChecked(self.profile.images_enabled)
        self.plugins_check.setChecked(self.profile.plugins_enabled)
        self.geolocation_check.setChecked(self.profile.geolocation_enabled)
        self.notifications_check.setChecked(self.profile.notifications_enabled)
        self.webrtc_check.setChecked(self.profile.webrtc_enabled)
        
    def get_profile_data(self):
        """Отримання даних профілю з форми"""
        return {
            'name': self.name_edit.text().strip(),
            'user_agent': self.user_agent_edit.toPlainText().strip(),
            'screen_width': self.screen_width_spin.value(),
            'screen_height': self.screen_height_spin.value(),
            'timezone': self.timezone_combo.currentText(),
            'language': self.language_combo.currentText(),
            'canvas_fingerprint': self.canvas_edit.text().strip(),
            'webgl_fingerprint': self.webgl_edit.text().strip(),
            'proxy_host': self.proxy_host_edit.text().strip(),
            'proxy_port': self.proxy_port_spin.value(),
            'proxy_username': self.proxy_username_edit.text().strip(),
            'proxy_password': self.proxy_password_edit.text().strip(),
            'proxy_type': self.proxy_type_combo.currentText(),
            'cookies_enabled': self.cookies_check.isChecked(),
            'javascript_enabled': self.javascript_check.isChecked(),
            'images_enabled': self.images_check.isChecked(),
            'plugins_enabled': self.plugins_check.isChecked(),
            'geolocation_enabled': self.geolocation_check.isChecked(),
            'notifications_enabled': self.notifications_check.isChecked(),
            'webrtc_enabled': self.webrtc_check.isChecked()
        }
        
    def accept(self):
        """Перевірка та збереження даних"""
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

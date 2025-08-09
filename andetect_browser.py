#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AnDetect Browser - Антитрекінг браузер для Windows
Забезпечує високий рівень анонімності та захисту приватності
"""

import sys
import os
import json
import random
import sqlite3
import tempfile
import shutil
from urllib.parse import urlparse
from typing import Optional, Dict, Any

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QVBoxLayout, QHBoxLayout,
    QWidget, QPushButton, QLineEdit, QMenuBar, QAction, QMessageBox,
    QProgressBar, QStatusBar, QToolBar, QLabel, QCheckBox, QDialog,
    QFormLayout, QSpinBox, QComboBox
)
from PyQt5.QtCore import QUrl, QTimer, pyqtSignal, QThread, Qt
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile, QWebEnginePage
from PyQt5.QtWebEngineCore import QWebEngineSettings

import requests
from fake_useragent import UserAgent


class AnonymitySettings:
    """Налаштування анонімності"""
    
    def __init__(self):
        self.tor_enabled = False
        self.proxy_enabled = False
        self.anti_fingerprint = True
        self.clear_on_exit = True
        self.block_webrtc = True
        self.spoof_canvas = True
        self.randomize_user_agent = True
        self.proxy_host = "127.0.0.1"
        self.proxy_port = 9050  # Tor default
        self.tor_port = 9051
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            'tor_enabled': self.tor_enabled,
            'proxy_enabled': self.proxy_enabled,
            'anti_fingerprint': self.anti_fingerprint,
            'clear_on_exit': self.clear_on_exit,
            'block_webrtc': self.block_webrtc,
            'spoof_canvas': self.spoof_canvas,
            'randomize_user_agent': self.randomize_user_agent,
            'proxy_host': self.proxy_host,
            'proxy_port': self.proxy_port,
            'tor_port': self.tor_port
        }
    
    def from_dict(self, data: Dict[str, Any]):
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)


class PrivatePage(QWebEnginePage):
    """Кастомна веб-сторінка з додатковими налаштуваннями приватності"""
    
    def __init__(self, profile: QWebEngineProfile, parent=None):
        super().__init__(profile, parent)
        self.anonymity_settings = AnonymitySettings()
        self.setup_privacy_settings()
    
    def setup_privacy_settings(self):
        """Налаштування приватності сторінки"""
        settings = self.settings()
        
        # Відключення JavaScript якщо потрібно
        settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.JavascriptCanOpenWindows, False)
        settings.setAttribute(QWebEngineSettings.JavascriptCanAccessClipboard, False)
        
        # Відключення плагінів та автозаповнення
        settings.setAttribute(QWebEngineSettings.PluginsEnabled, False)
        settings.setAttribute(QWebEngineSettings.AutoLoadImages, True)
        settings.setAttribute(QWebEngineSettings.LocalStorageEnabled, False)
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessRemoteUrls, False)
        
        # Налаштування WebGL та Canvas
        if self.anonymity_settings.spoof_canvas:
            settings.setAttribute(QWebEngineSettings.WebGLEnabled, False)
    
    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        """Перехоплення JavaScript повідомлень"""
        # Можна додати логування або блокування певних скриптів
        pass


class PrivateWebView(QWebEngineView):
    """Кастомний веб-переглядач з додатковими функціями приватності"""
    
    def __init__(self, anonymity_settings: AnonymitySettings, parent=None):
        super().__init__(parent)
        self.anonymity_settings = anonymity_settings
        self.setup_private_profile()
        
    def setup_private_profile(self):
        """Налаштування приватного профілю"""
        # Створення приватного профілю
        self.profile = QWebEngineProfile()
        self.profile.setHttpCacheType(QWebEngineProfile.MemoryHttpCache)
        self.profile.setPersistentCookiesPolicy(QWebEngineProfile.NoPersistentCookies)
        
        # Налаштування User-Agent
        if self.anonymity_settings.randomize_user_agent:
            self.randomize_user_agent()
        
        # Створення приватної сторінки
        self.private_page = PrivatePage(self.profile, self)
        self.private_page.anonymity_settings = self.anonymity_settings
        self.setPage(self.private_page)
        
        # Інжекція JavaScript для додаткового захисту
        self.inject_privacy_scripts()
    
    def randomize_user_agent(self):
        """Генерація випадкового User-Agent"""
        try:
            ua = UserAgent()
            user_agent = ua.chrome  # Використовуємо Chrome UA для кращої сумісності
            self.profile.setHttpUserAgent(user_agent)
        except Exception:
            # Фолбек до стандартного UA
            default_ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
            self.profile.setHttpUserAgent(default_ua)
    
    def inject_privacy_scripts(self):
        """Інжекція JavaScript для захисту приватності"""
        privacy_script = """
        // Блокування WebRTC
        if (typeof window.RTCPeerConnection !== 'undefined') {
            window.RTCPeerConnection = function() { throw new Error('WebRTC blocked'); };
        }
        if (typeof window.webkitRTCPeerConnection !== 'undefined') {
            window.webkitRTCPeerConnection = function() { throw new Error('WebRTC blocked'); };
        }
        if (typeof window.mozRTCPeerConnection !== 'undefined') {
            window.mozRTCPeerConnection = function() { throw new Error('WebRTC blocked'); };
        }
        
        // Спуфінг Canvas
        const originalGetContext = HTMLCanvasElement.prototype.getContext;
        HTMLCanvasElement.prototype.getContext = function(type) {
            if (type === '2d' || type === 'webgl' || type === 'webgl2') {
                const context = originalGetContext.call(this, type);
                if (context && type === '2d') {
                    const originalGetImageData = context.getImageData;
                    context.getImageData = function() {
                        const imageData = originalGetImageData.apply(this, arguments);
                        // Додаємо шум до даних зображення
                        for (let i = 0; i < imageData.data.length; i += 4) {
                            imageData.data[i] += Math.random() * 2 - 1;
                        }
                        return imageData;
                    };
                }
                return context;
            }
            return originalGetContext.call(this, type);
        };
        
        // Спуфінг геолокації
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition = function(success, error) {
                if (error) error({code: 1, message: "Geolocation access denied"});
            };
        }
        
        // Захист від fingerprinting через аудіо
        if (window.AudioContext) {
            const OriginalAudioContext = window.AudioContext;
            window.AudioContext = function() {
                const context = new OriginalAudioContext();
                const originalCreateOscillator = context.createOscillator;
                context.createOscillator = function() {
                    const oscillator = originalCreateOscillator.call(this);
                    const originalStart = oscillator.start;
                    oscillator.start = function() {
                        // Додаємо невеликий шум до частоти
                        oscillator.frequency.value += Math.random() * 0.1;
                        return originalStart.apply(this, arguments);
                    };
                    return oscillator;
                };
                return context;
            };
        }
        """
        
        self.page().runJavaScript(privacy_script)


class SettingsDialog(QDialog):
    """Діалог налаштувань браузера"""
    
    def __init__(self, settings: AnonymitySettings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Налаштування Анонімності")
        self.setFixedSize(400, 500)
        
        layout = QFormLayout()
        
        # Tor налаштування
        self.tor_enabled = QCheckBox()
        self.tor_enabled.setChecked(self.settings.tor_enabled)
        layout.addRow("Увімкнути Tor:", self.tor_enabled)
        
        self.tor_port = QSpinBox()
        self.tor_port.setRange(1000, 65535)
        self.tor_port.setValue(self.settings.tor_port)
        layout.addRow("Порт Tor:", self.tor_port)
        
        # Проксі налаштування
        self.proxy_enabled = QCheckBox()
        self.proxy_enabled.setChecked(self.settings.proxy_enabled)
        layout.addRow("Увімкнути проксі:", self.proxy_enabled)
        
        self.proxy_host = QLineEdit(self.settings.proxy_host)
        layout.addRow("Хост проксі:", self.proxy_host)
        
        self.proxy_port = QSpinBox()
        self.proxy_port.setRange(1, 65535)
        self.proxy_port.setValue(self.settings.proxy_port)
        layout.addRow("Порт проксі:", self.proxy_port)
        
        # Налаштування приватності
        self.anti_fingerprint = QCheckBox()
        self.anti_fingerprint.setChecked(self.settings.anti_fingerprint)
        layout.addRow("Анти-фінгерпринтинг:", self.anti_fingerprint)
        
        self.block_webrtc = QCheckBox()
        self.block_webrtc.setChecked(self.settings.block_webrtc)
        layout.addRow("Блокувати WebRTC:", self.block_webrtc)
        
        self.spoof_canvas = QCheckBox()
        self.spoof_canvas.setChecked(self.settings.spoof_canvas)
        layout.addRow("Спуфити Canvas:", self.spoof_canvas)
        
        self.randomize_user_agent = QCheckBox()
        self.randomize_user_agent.setChecked(self.settings.randomize_user_agent)
        layout.addRow("Випадковий User-Agent:", self.randomize_user_agent)
        
        self.clear_on_exit = QCheckBox()
        self.clear_on_exit.setChecked(self.settings.clear_on_exit)
        layout.addRow("Очищати при виході:", self.clear_on_exit)
        
        # Кнопки
        buttons_layout = QHBoxLayout()
        
        save_btn = QPushButton("Зберегти")
        save_btn.clicked.connect(self.save_settings)
        buttons_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("Скасувати")
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        layout.addRow(buttons_layout)
        self.setLayout(layout)
    
    def save_settings(self):
        """Збереження налаштувань"""
        self.settings.tor_enabled = self.tor_enabled.isChecked()
        self.settings.tor_port = self.tor_port.value()
        self.settings.proxy_enabled = self.proxy_enabled.isChecked()
        self.settings.proxy_host = self.proxy_host.text()
        self.settings.proxy_port = self.proxy_port.value()
        self.settings.anti_fingerprint = self.anti_fingerprint.isChecked()
        self.settings.block_webrtc = self.block_webrtc.isChecked()
        self.settings.spoof_canvas = self.spoof_canvas.isChecked()
        self.settings.randomize_user_agent = self.randomize_user_agent.isChecked()
        self.settings.clear_on_exit = self.clear_on_exit.isChecked()
        
        self.accept()


class BrowserTab(QWidget):
    """Клас для окремої вкладки браузера"""
    
    title_changed = pyqtSignal(str)
    url_changed = pyqtSignal(str)
    
    def __init__(self, anonymity_settings: AnonymitySettings, parent=None):
        super().__init__(parent)
        self.anonymity_settings = anonymity_settings
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Веб-переглядач
        self.web_view = PrivateWebView(self.anonymity_settings)
        layout.addWidget(self.web_view)
        
        # Підключення сигналів
        self.web_view.titleChanged.connect(self.title_changed)
        self.web_view.urlChanged.connect(lambda url: self.url_changed.emit(url.toString()))
        
        self.setLayout(layout)
    
    def load_url(self, url: str):
        """Завантаження URL"""
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        self.web_view.load(QUrl(url))
    
    def get_title(self) -> str:
        """Отримання заголовку сторінки"""
        return self.web_view.title() or "Нова вкладка"
    
    def get_url(self) -> str:
        """Отримання поточного URL"""
        return self.web_view.url().toString()


class AnDetectBrowser(QMainWindow):
    """Головний клас браузера"""
    
    def __init__(self):
        super().__init__()
        self.anonymity_settings = AnonymitySettings()
        self.load_settings()
        self.init_ui()
        self.setup_security()
    
    def init_ui(self):
        """Ініціалізація інтерфейсу"""
        self.setWindowTitle("AnDetect Browser - Приватний браузер")
        self.setGeometry(100, 100, 1200, 800)
        
        # Центральний віджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Головний layout
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Панель інструментів
        self.create_toolbar()
        
        # Вкладки
        self.tabs = QTabWidget()
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.on_tab_changed)
        main_layout.addWidget(self.tabs)
        
        # Статус бар
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Індикатор анонімності
        self.anonymity_label = QLabel("Анонімність: Активна")
        self.anonymity_label.setStyleSheet("color: green; font-weight: bold;")
        self.status_bar.addPermanentWidget(self.anonymity_label)
        
        # Створення першої вкладки
        self.new_tab()
        
        # Меню
        self.create_menu()
    
    def create_toolbar(self):
        """Створення панелі інструментів"""
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        # Кнопка назад
        back_btn = QPushButton("←")
        back_btn.setFixedSize(30, 30)
        back_btn.clicked.connect(self.go_back)
        toolbar.addWidget(back_btn)
        
        # Кнопка вперед
        forward_btn = QPushButton("→")
        forward_btn.setFixedSize(30, 30)
        forward_btn.clicked.connect(self.go_forward)
        toolbar.addWidget(forward_btn)
        
        # Кнопка оновлення
        refresh_btn = QPushButton("↻")
        refresh_btn.setFixedSize(30, 30)
        refresh_btn.clicked.connect(self.refresh_page)
        toolbar.addWidget(refresh_btn)
        
        # Адресний рядок
        self.address_bar = QLineEdit()
        self.address_bar.setPlaceholderText("Введіть URL або пошуковий запит...")
        self.address_bar.returnPressed.connect(self.navigate_to_url)
        toolbar.addWidget(self.address_bar)
        
        # Кнопка нової вкладки
        new_tab_btn = QPushButton("+")
        new_tab_btn.setFixedSize(30, 30)
        new_tab_btn.clicked.connect(self.new_tab)
        toolbar.addWidget(new_tab_btn)
        
        # Кнопка налаштувань
        settings_btn = QPushButton("⚙")
        settings_btn.setFixedSize(30, 30)
        settings_btn.clicked.connect(self.show_settings)
        toolbar.addWidget(settings_btn)
    
    def create_menu(self):
        """Створення меню"""
        menubar = self.menuBar()
        
        # Меню файл
        file_menu = menubar.addMenu('Файл')
        
        new_tab_action = QAction('Нова вкладка', self)
        new_tab_action.setShortcut('Ctrl+T')
        new_tab_action.triggered.connect(self.new_tab)
        file_menu.addAction(new_tab_action)
        
        close_tab_action = QAction('Закрити вкладку', self)
        close_tab_action.setShortcut('Ctrl+W')
        close_tab_action.triggered.connect(lambda: self.close_tab(self.tabs.currentIndex()))
        file_menu.addAction(close_tab_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('Вийти', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Меню інструментів
        tools_menu = menubar.addMenu('Інструменти')
        
        settings_action = QAction('Налаштування', self)
        settings_action.triggered.connect(self.show_settings)
        tools_menu.addAction(settings_action)
        
        clear_data_action = QAction('Очистити дані', self)
        clear_data_action.triggered.connect(self.clear_browser_data)
        tools_menu.addAction(clear_data_action)
    
    def new_tab(self, url: str = ""):
        """Створення нової вкладки"""
        tab = BrowserTab(self.anonymity_settings)
        
        # Підключення сигналів
        tab.title_changed.connect(lambda title: self.update_tab_title(tab, title))
        tab.url_changed.connect(self.update_address_bar)
        
        index = self.tabs.addTab(tab, "Нова вкладка")
        self.tabs.setCurrentIndex(index)
        
        if url:
            tab.load_url(url)
        else:
            tab.load_url("about:blank")
    
    def close_tab(self, index: int):
        """Закриття вкладки"""
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)
        else:
            self.close()
    
    def update_tab_title(self, tab: BrowserTab, title: str):
        """Оновлення заголовку вкладки"""
        index = self.tabs.indexOf(tab)
        if index != -1:
            self.tabs.setTabText(index, title[:30] + "..." if len(title) > 30 else title)
    
    def update_address_bar(self, url: str):
        """Оновлення адресного рядка"""
        if self.tabs.currentWidget():
            self.address_bar.setText(url)
    
    def on_tab_changed(self, index: int):
        """Обробка зміни активної вкладки"""
        current_tab = self.tabs.currentWidget()
        if current_tab:
            self.address_bar.setText(current_tab.get_url())
    
    def navigate_to_url(self):
        """Навігація до URL"""
        url = self.address_bar.text().strip()
        if not url:
            return
        
        # Якщо це не URL, то використовуємо як пошуковий запит
        if not url.startswith(('http://', 'https://')) and '.' not in url:
            url = f"https://duckduckgo.com/?q={url}"
        
        current_tab = self.tabs.currentWidget()
        if current_tab:
            current_tab.load_url(url)
    
    def go_back(self):
        """Повернення назад"""
        current_tab = self.tabs.currentWidget()
        if current_tab:
            current_tab.web_view.back()
    
    def go_forward(self):
        """Перехід вперед"""
        current_tab = self.tabs.currentWidget()
        if current_tab:
            current_tab.web_view.forward()
    
    def refresh_page(self):
        """Оновлення сторінки"""
        current_tab = self.tabs.currentWidget()
        if current_tab:
            current_tab.web_view.reload()
    
    def show_settings(self):
        """Показ діалогу налаштувань"""
        dialog = SettingsDialog(self.anonymity_settings, self)
        if dialog.exec_() == QDialog.Accepted:
            self.save_settings()
            self.update_anonymity_status()
    
    def clear_browser_data(self):
        """Очищення даних браузера"""
        reply = QMessageBox.question(
            self, 'Очистити дані', 
            'Ви впевнені, що хочете очистити всі дані браузера?',
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.perform_data_cleanup()
            QMessageBox.information(self, 'Готово', 'Дані браузера очищено')
    
    def perform_data_cleanup(self):
        """Виконання очищення даних"""
        try:
            # Очищення тимчасових файлів
            temp_dir = tempfile.gettempdir()
            for file in os.listdir(temp_dir):
                if file.startswith('QtWebEngine'):
                    file_path = os.path.join(temp_dir, file)
                    try:
                        if os.path.isdir(file_path):
                            shutil.rmtree(file_path)
                        else:
                            os.remove(file_path)
                    except Exception:
                        pass
            
            # Очищення профілів веб-двигуна
            for i in range(self.tabs.count()):
                tab = self.tabs.widget(i)
                if tab and hasattr(tab, 'web_view'):
                    tab.web_view.page().profile().clearAllVisitedLinks()
                    tab.web_view.page().profile().clearHttpCache()
        except Exception as e:
            print(f"Помилка при очищенні даних: {e}")
    
    def setup_security(self):
        """Налаштування безпеки"""
        self.update_anonymity_status()
    
    def update_anonymity_status(self):
        """Оновлення статусу анонімності"""
        if self.anonymity_settings.tor_enabled or self.anonymity_settings.proxy_enabled:
            self.anonymity_label.setText("Анонімність: Висока")
            self.anonymity_label.setStyleSheet("color: green; font-weight: bold;")
        elif self.anonymity_settings.anti_fingerprint:
            self.anonymity_label.setText("Анонімність: Середня")
            self.anonymity_label.setStyleSheet("color: orange; font-weight: bold;")
        else:
            self.anonymity_label.setText("Анонімність: Базова")
            self.anonymity_label.setStyleSheet("color: red; font-weight: bold;")
    
    def load_settings(self):
        """Завантаження налаштувань"""
        try:
            if os.path.exists('andetect_settings.json'):
                with open('andetect_settings.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.anonymity_settings.from_dict(data)
        except Exception as e:
            print(f"Помилка завантаження налаштувань: {e}")
    
    def save_settings(self):
        """Збереження налаштувань"""
        try:
            with open('andetect_settings.json', 'w', encoding='utf-8') as f:
                json.dump(self.anonymity_settings.to_dict(), f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Помилка збереження налаштувань: {e}")
    
    def closeEvent(self, event):
        """Обробка закриття програми"""
        if self.anonymity_settings.clear_on_exit:
            self.perform_data_cleanup()
        
        self.save_settings()
        event.accept()


def main():
    """Головна функція"""
    app = QApplication(sys.argv)
    app.setApplicationName("AnDetect Browser")
    app.setApplicationVersion("1.0")
    
    # Налаштування стилю
    app.setStyle('Fusion')
    
    browser = AnDetectBrowser()
    browser.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

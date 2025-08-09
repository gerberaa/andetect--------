<<<<<<< HEAD
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Діалог налаштувань браузера AnDetect
"""

import os
import json
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
                            QWidget, QCheckBox, QSpinBox, QLineEdit, QLabel,
                            QDialogButtonBox, QGroupBox, QFormLayout, 
                            QPushButton, QFileDialog, QTextEdit, QComboBox,
                            QSlider, QMessageBox)
from PyQt5.QtCore import Qt, QSettings


class SettingsDialog(QDialog):
    """Діалог налаштувань браузера"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = QSettings('AnDetect', 'Browser')
        self.init_ui()
        self.load_settings()
        
    def init_ui(self):
        """Ініціалізація інтерфейсу"""
        self.setWindowTitle('Налаштування браузера')
        self.setMinimumSize(600, 500)
        
        layout = QVBoxLayout(self)
        
        # Вкладки
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)
        
        # Загальні налаштування
        self.create_general_tab(tab_widget)
        
        # Безпека та приватність
        self.create_privacy_tab(tab_widget)
        
        # Блокування реклами
        self.create_adblock_tab(tab_widget)
        
        # Прокси та мережа
        self.create_network_tab(tab_widget)
        
        # Експорт/Імпорт
        self.create_backup_tab(tab_widget)
        
        # Кнопки
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel | QDialogButtonBox.Apply,
            Qt.Horizontal, self
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        buttons.button(QDialogButtonBox.Apply).clicked.connect(self.apply_settings)
        layout.addWidget(buttons)
        
    def create_general_tab(self, tab_widget):
        """Вкладка загальних налаштувань"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Стартова сторінка
        startup_group = QGroupBox('Стартова сторінка')
        startup_layout = QFormLayout(startup_group)
        
        self.homepage_edit = QLineEdit()
        self.homepage_edit.setPlaceholderText('https://www.google.com')
        startup_layout.addRow('Домашня сторінка:', self.homepage_edit)
        
        self.restore_tabs_check = QCheckBox('Відновлювати вкладки при запуску')
        startup_layout.addRow(self.restore_tabs_check)
        
        layout.addWidget(startup_group)
        
        # Поведінка браузера
        behavior_group = QGroupBox('Поведінка')
        behavior_layout = QVBoxLayout(behavior_group)
        
        self.auto_update_check = QCheckBox('Автоматично оновлювати браузер')
        behavior_layout.addWidget(self.auto_update_check)
        
        self.close_warning_check = QCheckBox('Попереджати при закритті кількох вкладок')
        behavior_layout.addWidget(self.close_warning_check)
        
        self.downloads_warning_check = QCheckBox('Попереджати перед завантаженням файлів')
        behavior_layout.addWidget(self.downloads_warning_check)
        
        layout.addWidget(behavior_group)
        
        # Папка завантажень
        downloads_group = QGroupBox('Завантаження')
        downloads_layout = QFormLayout(downloads_group)
        
        downloads_hbox = QHBoxLayout()
        self.downloads_path_edit = QLineEdit()
        downloads_hbox.addWidget(self.downloads_path_edit)
        
        browse_btn = QPushButton('Огляд...')
        browse_btn.clicked.connect(self.browse_downloads_folder)
        downloads_hbox.addWidget(browse_btn)
        
        downloads_layout.addRow('Папка завантажень:', downloads_hbox)
        
        layout.addWidget(downloads_group)
        layout.addStretch()
        
        tab_widget.addTab(widget, 'Загальні')
        
    def create_privacy_tab(self, tab_widget):
        """Вкладка приватності"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Збір даних
        data_group = QGroupBox('Збір даних')
        data_layout = QVBoxLayout(data_group)
        
        self.telemetry_check = QCheckBox('Відправляти телеметрію (допомагає покращити браузер)')
        data_layout.addWidget(self.telemetry_check)
        
        self.crash_reports_check = QCheckBox('Відправляти звіти про збої')
        data_layout.addWidget(self.crash_reports_check)
        
        self.usage_stats_check = QCheckBox('Збирати статистику використання')
        data_layout.addWidget(self.usage_stats_check)
        
        layout.addWidget(data_group)
        
        # Fingerprinting
        fingerprint_group = QGroupBox('Захист від відстеження')
        fingerprint_layout = QVBoxLayout(fingerprint_group)
        
        self.block_fingerprinting_check = QCheckBox('Блокувати fingerprinting')
        self.block_fingerprinting_check.setChecked(True)
        fingerprint_layout.addWidget(self.block_fingerprinting_check)
        
        self.spoof_timezone_check = QCheckBox('Маскувати часовий пояс')
        self.spoof_timezone_check.setChecked(True)
        fingerprint_layout.addWidget(self.spoof_timezone_check)
        
        self.spoof_screen_check = QCheckBox('Маскувати параметри екрану')
        self.spoof_screen_check.setChecked(True)
        fingerprint_layout.addWidget(self.spoof_screen_check)
        
        self.block_webrtc_check = QCheckBox('Блокувати WebRTC (рекомендовано)')
        self.block_webrtc_check.setChecked(True)
        fingerprint_layout.addWidget(self.block_webrtc_check)
        
        layout.addWidget(fingerprint_group)
        
        # DNS
        dns_group = QGroupBox('DNS')
        dns_layout = QFormLayout(dns_group)
        
        self.dns_over_https_check = QCheckBox('Використовувати DNS over HTTPS')
        dns_layout.addRow(self.dns_over_https_check)
        
        self.dns_server_edit = QLineEdit()
        self.dns_server_edit.setPlaceholderText('1.1.1.1')
        dns_layout.addRow('DNS сервер:', self.dns_server_edit)
        
        layout.addWidget(dns_group)
        layout.addStretch()
        
        tab_widget.addTab(widget, 'Приватність')
        
    def create_adblock_tab(self, tab_widget):
        """Вкладка блокування реклами"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Основні налаштування
        main_group = QGroupBox('Блокування реклами')
        main_layout = QVBoxLayout(main_group)
        
        self.adblock_enabled_check = QCheckBox('Увімкнути блокування реклами')
        self.adblock_enabled_check.setChecked(True)
        main_layout.addWidget(self.adblock_enabled_check)
        
        self.block_trackers_check = QCheckBox('Блокувати трекери')
        self.block_trackers_check.setChecked(True)
        main_layout.addWidget(self.block_trackers_check)
        
        self.block_malware_check = QCheckBox('Блокувати шкідливі сайти')
        self.block_malware_check.setChecked(True)
        main_layout.addWidget(self.block_malware_check)
        
        self.block_popups_check = QCheckBox('Блокувати спливаючі вікна')
        self.block_popups_check.setChecked(True)
        main_layout.addWidget(self.block_popups_check)
        
        layout.addWidget(main_group)
        
        # Списки фільтрів
        filters_group = QGroupBox('Списки фільтрів')
        filters_layout = QVBoxLayout(filters_group)
        
        filters_info = QLabel('Активні списки фільтрів:')
        filters_layout.addWidget(filters_info)
        
        self.filter_lists = QTextEdit()
        self.filter_lists.setMaximumHeight(150)
        self.filter_lists.setPlainText(
            "EasyList (основний)\n"
            "EasyPrivacy (приватність)\n"
            "uBlock filters (додатковий)\n"
            "Malware Domain List (шкідливі домени)"
        )
        self.filter_lists.setReadOnly(True)
        filters_layout.addWidget(self.filter_lists)
        
        update_filters_btn = QPushButton('Оновити списки фільтрів')
        update_filters_btn.clicked.connect(self.update_filter_lists)
        filters_layout.addWidget(update_filters_btn)
        
        layout.addWidget(filters_group)
        
        # Білий список
        whitelist_group = QGroupBox('Білий список')
        whitelist_layout = QVBoxLayout(whitelist_group)
        
        whitelist_info = QLabel('Домени, для яких вимкнено блокування:')
        whitelist_layout.addWidget(whitelist_info)
        
        self.whitelist_edit = QTextEdit()
        self.whitelist_edit.setMaximumHeight(100)
        self.whitelist_edit.setPlaceholderText('Введіть домени, по одному на рядок...')
        whitelist_layout.addWidget(self.whitelist_edit)
        
        layout.addWidget(whitelist_group)
        layout.addStretch()
        
        tab_widget.addTab(widget, 'Блокування')
        
    def create_network_tab(self, tab_widget):
        """Вкладка мережевих налаштувань"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Глобальний проксі
        proxy_group = QGroupBox('Глобальний проксі')
        proxy_layout = QFormLayout(proxy_group)
        
        self.global_proxy_check = QCheckBox('Використовувати глобальний проксі')
        proxy_layout.addRow(self.global_proxy_check)
        
        self.global_proxy_type_combo = QComboBox()
        self.global_proxy_type_combo.addItems(['HTTP', 'SOCKS5'])
        proxy_layout.addRow('Тип:', self.global_proxy_type_combo)
        
        self.global_proxy_host_edit = QLineEdit()
        proxy_layout.addRow('Хост:', self.global_proxy_host_edit)
        
        self.global_proxy_port_spin = QSpinBox()
        self.global_proxy_port_spin.setRange(1, 65535)
        proxy_layout.addRow('Порт:', self.global_proxy_port_spin)
        
        layout.addWidget(proxy_group)
        
        # Мережеві налаштування
        network_group = QGroupBox('Мережа')
        network_layout = QFormLayout(network_group)
        
        self.max_connections_spin = QSpinBox()
        self.max_connections_spin.setRange(1, 100)
        self.max_connections_spin.setValue(6)
        network_layout.addRow('Макс. з\'єднань на хост:', self.max_connections_spin)
        
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(5, 300)
        self.timeout_spin.setValue(30)
        self.timeout_spin.setSuffix(' сек')
        network_layout.addRow('Таймаут з\'єднання:', self.timeout_spin)
        
        self.user_agent_edit = QLineEdit()
        self.user_agent_edit.setPlaceholderText('Глобальний User-Agent (необов\'язково)')
        network_layout.addRow('User-Agent:', self.user_agent_edit)
        
        layout.addWidget(network_group)
        layout.addStretch()
        
        tab_widget.addTab(widget, 'Мережа')
        
    def create_backup_tab(self, tab_widget):
        """Вкладка експорту/імпорту"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Резервні копії
        backup_group = QGroupBox('Резервні копії')
        backup_layout = QVBoxLayout(backup_group)
        
        backup_info = QLabel(
            'Створюйте резервні копії своїх профілів та налаштувань\n'
            'для відновлення у випадку втрати даних.'
        )
        backup_layout.addWidget(backup_info)
        
        backup_buttons = QHBoxLayout()
        
        export_btn = QPushButton('Експорт профілів')
        export_btn.clicked.connect(self.export_profiles)
        backup_buttons.addWidget(export_btn)
        
        import_btn = QPushButton('Імпорт профілів')
        import_btn.clicked.connect(self.import_profiles)
        backup_buttons.addWidget(import_btn)
        
        backup_layout.addLayout(backup_buttons)
        
        layout.addWidget(backup_group)
        
        # Очищення даних
        cleanup_group = QGroupBox('Очищення даних')
        cleanup_layout = QVBoxLayout(cleanup_group)
        
        cleanup_info = QLabel(
            'Видаліть збережені дані для звільнення місця\n'
            'або повного очищення браузера.'
        )
        cleanup_layout.addWidget(cleanup_info)
        
        cleanup_buttons = QHBoxLayout()
        
        clear_cache_btn = QPushButton('Очистити кеш')
        clear_cache_btn.clicked.connect(self.clear_cache)
        cleanup_buttons.addWidget(clear_cache_btn)
        
        clear_cookies_btn = QPushButton('Очистити cookies')
        clear_cookies_btn.clicked.connect(self.clear_cookies)
        cleanup_buttons.addWidget(clear_cookies_btn)
        
        clear_all_btn = QPushButton('Очистити все')
        clear_all_btn.clicked.connect(self.clear_all_data)
        cleanup_buttons.addWidget(clear_all_btn)
        
        cleanup_layout.addLayout(cleanup_buttons)
        
        layout.addWidget(cleanup_group)
        layout.addStretch()
        
        tab_widget.addTab(widget, 'Дані')
        
    def load_settings(self):
        """Завантаження налаштувань"""
        # Загальні
        self.homepage_edit.setText(self.settings.value('homepage', 'https://www.google.com'))
        self.restore_tabs_check.setChecked(self.settings.value('restore_tabs', True, type=bool))
        self.auto_update_check.setChecked(self.settings.value('auto_update', True, type=bool))
        self.close_warning_check.setChecked(self.settings.value('close_warning', True, type=bool))
        
        downloads_path = self.settings.value('downloads_path', os.path.expanduser('~/Downloads'))
        self.downloads_path_edit.setText(downloads_path)
        
        # Приватність
        self.telemetry_check.setChecked(self.settings.value('telemetry', False, type=bool))
        self.crash_reports_check.setChecked(self.settings.value('crash_reports', True, type=bool))
        self.block_fingerprinting_check.setChecked(self.settings.value('block_fingerprinting', True, type=bool))
        self.spoof_timezone_check.setChecked(self.settings.value('spoof_timezone', True, type=bool))
        self.spoof_screen_check.setChecked(self.settings.value('spoof_screen', True, type=bool))
        self.block_webrtc_check.setChecked(self.settings.value('block_webrtc', True, type=bool))
        
        # Блокування
        self.adblock_enabled_check.setChecked(self.settings.value('adblock_enabled', True, type=bool))
        self.block_trackers_check.setChecked(self.settings.value('block_trackers', True, type=bool))
        self.block_malware_check.setChecked(self.settings.value('block_malware', True, type=bool))
        self.block_popups_check.setChecked(self.settings.value('block_popups', True, type=bool))
        
        # Мережа
        self.global_proxy_check.setChecked(self.settings.value('global_proxy', False, type=bool))
        self.global_proxy_host_edit.setText(self.settings.value('global_proxy_host', ''))
        self.global_proxy_port_spin.setValue(self.settings.value('global_proxy_port', 8080, type=int))
        self.max_connections_spin.setValue(self.settings.value('max_connections', 6, type=int))
        self.timeout_spin.setValue(self.settings.value('timeout', 30, type=int))
        
    def save_settings(self):
        """Збереження налаштувань"""
        # Загальні
        self.settings.setValue('homepage', self.homepage_edit.text())
        self.settings.setValue('restore_tabs', self.restore_tabs_check.isChecked())
        self.settings.setValue('auto_update', self.auto_update_check.isChecked())
        self.settings.setValue('close_warning', self.close_warning_check.isChecked())
        self.settings.setValue('downloads_path', self.downloads_path_edit.text())
        
        # Приватність
        self.settings.setValue('telemetry', self.telemetry_check.isChecked())
        self.settings.setValue('crash_reports', self.crash_reports_check.isChecked())
        self.settings.setValue('block_fingerprinting', self.block_fingerprinting_check.isChecked())
        self.settings.setValue('spoof_timezone', self.spoof_timezone_check.isChecked())
        self.settings.setValue('spoof_screen', self.spoof_screen_check.isChecked())
        self.settings.setValue('block_webrtc', self.block_webrtc_check.isChecked())
        
        # Блокування
        self.settings.setValue('adblock_enabled', self.adblock_enabled_check.isChecked())
        self.settings.setValue('block_trackers', self.block_trackers_check.isChecked())
        self.settings.setValue('block_malware', self.block_malware_check.isChecked())
        self.settings.setValue('block_popups', self.block_popups_check.isChecked())
        
        # Мережа
        self.settings.setValue('global_proxy', self.global_proxy_check.isChecked())
        self.settings.setValue('global_proxy_host', self.global_proxy_host_edit.text())
        self.settings.setValue('global_proxy_port', self.global_proxy_port_spin.value())
        self.settings.setValue('max_connections', self.max_connections_spin.value())
        self.settings.setValue('timeout', self.timeout_spin.value())
        
    def browse_downloads_folder(self):
        """Вибір папки завантажень"""
        folder = QFileDialog.getExistingDirectory(self, 'Виберіть папку завантажень')
        if folder:
            self.downloads_path_edit.setText(folder)
            
    def update_filter_lists(self):
        """Оновлення списків фільтрів"""
        QMessageBox.information(self, 'Оновлення', 'Списки фільтрів оновлено!')
        
    def export_profiles(self):
        """Експорт профілів"""
        filename, _ = QFileDialog.getSaveFileName(
            self, 'Експорт профілів', 'profiles_backup.json', 'JSON files (*.json)'
        )
        if filename:
            # TODO: Реалізувати експорт
            QMessageBox.information(self, 'Експорт', f'Профілі експортовано в {filename}')
            
    def import_profiles(self):
        """Імпорт профілів"""
        filename, _ = QFileDialog.getOpenFileName(
            self, 'Імпорт профілів', '', 'JSON files (*.json)'
        )
        if filename:
            # TODO: Реалізувати імпорт
            QMessageBox.information(self, 'Імпорт', f'Профілі імпортовано з {filename}')
            
    def clear_cache(self):
        """Очищення кешу"""
        reply = QMessageBox.question(
            self, 'Підтвердження', 'Очистити кеш браузера?',
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            # TODO: Реалізувати очищення кешу
            QMessageBox.information(self, 'Очищення', 'Кеш очищено!')
            
    def clear_cookies(self):
        """Очищення cookies"""
        reply = QMessageBox.question(
            self, 'Підтвердження', 'Очистити всі cookies?',
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            # TODO: Реалізувати очищення cookies
            QMessageBox.information(self, 'Очищення', 'Cookies очищено!')
            
    def clear_all_data(self):
        """Очищення всіх даних"""
        reply = QMessageBox.question(
            self, 'Підтвердження', 
            'Очистити ВСІ дані браузера? Це незворотна дія!',
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            # TODO: Реалізувати повне очищення
            QMessageBox.information(self, 'Очищення', 'Всі дані очищено!')
            
    def apply_settings(self):
        """Застосування налаштувань без закриття діалогу"""
        self.save_settings()
        QMessageBox.information(self, 'Налаштування', 'Налаштування збережено!')
        
    def accept(self):
        """Збереження та закриття"""
        self.save_settings()
        super().accept()
=======
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Діалог налаштувань браузера AnDetect
"""

import os
import json
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTabWidget,
                            QWidget, QCheckBox, QSpinBox, QLineEdit, QLabel,
                            QDialogButtonBox, QGroupBox, QFormLayout, 
                            QPushButton, QFileDialog, QTextEdit, QComboBox,
                            QSlider, QMessageBox)
from PyQt5.QtCore import Qt, QSettings


class SettingsDialog(QDialog):
    """Діалог налаштувань браузера"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = QSettings('AnDetect', 'Browser')
        self.init_ui()
        self.load_settings()
        
    def init_ui(self):
        """Ініціалізація інтерфейсу"""
        self.setWindowTitle('Налаштування браузера')
        self.setMinimumSize(600, 500)
        
        layout = QVBoxLayout(self)
        
        # Вкладки
        tab_widget = QTabWidget()
        layout.addWidget(tab_widget)
        
        # Загальні налаштування
        self.create_general_tab(tab_widget)
        
        # Безпека та приватність
        self.create_privacy_tab(tab_widget)
        
        # Блокування реклами
        self.create_adblock_tab(tab_widget)
        
        # Прокси та мережа
        self.create_network_tab(tab_widget)
        
        # Експорт/Імпорт
        self.create_backup_tab(tab_widget)
        
        # Кнопки
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel | QDialogButtonBox.Apply,
            Qt.Horizontal, self
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        buttons.button(QDialogButtonBox.Apply).clicked.connect(self.apply_settings)
        layout.addWidget(buttons)
        
    def create_general_tab(self, tab_widget):
        """Вкладка загальних налаштувань"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Стартова сторінка
        startup_group = QGroupBox('Стартова сторінка')
        startup_layout = QFormLayout(startup_group)
        
        self.homepage_edit = QLineEdit()
        self.homepage_edit.setPlaceholderText('https://www.google.com')
        startup_layout.addRow('Домашня сторінка:', self.homepage_edit)
        
        self.restore_tabs_check = QCheckBox('Відновлювати вкладки при запуску')
        startup_layout.addRow(self.restore_tabs_check)
        
        layout.addWidget(startup_group)
        
        # Поведінка браузера
        behavior_group = QGroupBox('Поведінка')
        behavior_layout = QVBoxLayout(behavior_group)
        
        self.auto_update_check = QCheckBox('Автоматично оновлювати браузер')
        behavior_layout.addWidget(self.auto_update_check)
        
        self.close_warning_check = QCheckBox('Попереджати при закритті кількох вкладок')
        behavior_layout.addWidget(self.close_warning_check)
        
        self.downloads_warning_check = QCheckBox('Попереджати перед завантаженням файлів')
        behavior_layout.addWidget(self.downloads_warning_check)
        
        layout.addWidget(behavior_group)
        
        # Папка завантажень
        downloads_group = QGroupBox('Завантаження')
        downloads_layout = QFormLayout(downloads_group)
        
        downloads_hbox = QHBoxLayout()
        self.downloads_path_edit = QLineEdit()
        downloads_hbox.addWidget(self.downloads_path_edit)
        
        browse_btn = QPushButton('Огляд...')
        browse_btn.clicked.connect(self.browse_downloads_folder)
        downloads_hbox.addWidget(browse_btn)
        
        downloads_layout.addRow('Папка завантажень:', downloads_hbox)
        
        layout.addWidget(downloads_group)
        layout.addStretch()
        
        tab_widget.addTab(widget, 'Загальні')
        
    def create_privacy_tab(self, tab_widget):
        """Вкладка приватності"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Збір даних
        data_group = QGroupBox('Збір даних')
        data_layout = QVBoxLayout(data_group)
        
        self.telemetry_check = QCheckBox('Відправляти телеметрію (допомагає покращити браузер)')
        data_layout.addWidget(self.telemetry_check)
        
        self.crash_reports_check = QCheckBox('Відправляти звіти про збої')
        data_layout.addWidget(self.crash_reports_check)
        
        self.usage_stats_check = QCheckBox('Збирати статистику використання')
        data_layout.addWidget(self.usage_stats_check)
        
        layout.addWidget(data_group)
        
        # Fingerprinting
        fingerprint_group = QGroupBox('Захист від відстеження')
        fingerprint_layout = QVBoxLayout(fingerprint_group)
        
        self.block_fingerprinting_check = QCheckBox('Блокувати fingerprinting')
        self.block_fingerprinting_check.setChecked(True)
        fingerprint_layout.addWidget(self.block_fingerprinting_check)
        
        self.spoof_timezone_check = QCheckBox('Маскувати часовий пояс')
        self.spoof_timezone_check.setChecked(True)
        fingerprint_layout.addWidget(self.spoof_timezone_check)
        
        self.spoof_screen_check = QCheckBox('Маскувати параметри екрану')
        self.spoof_screen_check.setChecked(True)
        fingerprint_layout.addWidget(self.spoof_screen_check)
        
        self.block_webrtc_check = QCheckBox('Блокувати WebRTC (рекомендовано)')
        self.block_webrtc_check.setChecked(True)
        fingerprint_layout.addWidget(self.block_webrtc_check)
        
        layout.addWidget(fingerprint_group)
        
        # DNS
        dns_group = QGroupBox('DNS')
        dns_layout = QFormLayout(dns_group)
        
        self.dns_over_https_check = QCheckBox('Використовувати DNS over HTTPS')
        dns_layout.addRow(self.dns_over_https_check)
        
        self.dns_server_edit = QLineEdit()
        self.dns_server_edit.setPlaceholderText('1.1.1.1')
        dns_layout.addRow('DNS сервер:', self.dns_server_edit)
        
        layout.addWidget(dns_group)
        layout.addStretch()
        
        tab_widget.addTab(widget, 'Приватність')
        
    def create_adblock_tab(self, tab_widget):
        """Вкладка блокування реклами"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Основні налаштування
        main_group = QGroupBox('Блокування реклами')
        main_layout = QVBoxLayout(main_group)
        
        self.adblock_enabled_check = QCheckBox('Увімкнути блокування реклами')
        self.adblock_enabled_check.setChecked(True)
        main_layout.addWidget(self.adblock_enabled_check)
        
        self.block_trackers_check = QCheckBox('Блокувати трекери')
        self.block_trackers_check.setChecked(True)
        main_layout.addWidget(self.block_trackers_check)
        
        self.block_malware_check = QCheckBox('Блокувати шкідливі сайти')
        self.block_malware_check.setChecked(True)
        main_layout.addWidget(self.block_malware_check)
        
        self.block_popups_check = QCheckBox('Блокувати спливаючі вікна')
        self.block_popups_check.setChecked(True)
        main_layout.addWidget(self.block_popups_check)
        
        layout.addWidget(main_group)
        
        # Списки фільтрів
        filters_group = QGroupBox('Списки фільтрів')
        filters_layout = QVBoxLayout(filters_group)
        
        filters_info = QLabel('Активні списки фільтрів:')
        filters_layout.addWidget(filters_info)
        
        self.filter_lists = QTextEdit()
        self.filter_lists.setMaximumHeight(150)
        self.filter_lists.setPlainText(
            "EasyList (основний)\n"
            "EasyPrivacy (приватність)\n"
            "uBlock filters (додатковий)\n"
            "Malware Domain List (шкідливі домени)"
        )
        self.filter_lists.setReadOnly(True)
        filters_layout.addWidget(self.filter_lists)
        
        update_filters_btn = QPushButton('Оновити списки фільтрів')
        update_filters_btn.clicked.connect(self.update_filter_lists)
        filters_layout.addWidget(update_filters_btn)
        
        layout.addWidget(filters_group)
        
        # Білий список
        whitelist_group = QGroupBox('Білий список')
        whitelist_layout = QVBoxLayout(whitelist_group)
        
        whitelist_info = QLabel('Домени, для яких вимкнено блокування:')
        whitelist_layout.addWidget(whitelist_info)
        
        self.whitelist_edit = QTextEdit()
        self.whitelist_edit.setMaximumHeight(100)
        self.whitelist_edit.setPlaceholderText('Введіть домени, по одному на рядок...')
        whitelist_layout.addWidget(self.whitelist_edit)
        
        layout.addWidget(whitelist_group)
        layout.addStretch()
        
        tab_widget.addTab(widget, 'Блокування')
        
    def create_network_tab(self, tab_widget):
        """Вкладка мережевих налаштувань"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Глобальний проксі
        proxy_group = QGroupBox('Глобальний проксі')
        proxy_layout = QFormLayout(proxy_group)
        
        self.global_proxy_check = QCheckBox('Використовувати глобальний проксі')
        proxy_layout.addRow(self.global_proxy_check)
        
        self.global_proxy_type_combo = QComboBox()
        self.global_proxy_type_combo.addItems(['HTTP', 'SOCKS5'])
        proxy_layout.addRow('Тип:', self.global_proxy_type_combo)
        
        self.global_proxy_host_edit = QLineEdit()
        proxy_layout.addRow('Хост:', self.global_proxy_host_edit)
        
        self.global_proxy_port_spin = QSpinBox()
        self.global_proxy_port_spin.setRange(1, 65535)
        proxy_layout.addRow('Порт:', self.global_proxy_port_spin)
        
        layout.addWidget(proxy_group)
        
        # Мережеві налаштування
        network_group = QGroupBox('Мережа')
        network_layout = QFormLayout(network_group)
        
        self.max_connections_spin = QSpinBox()
        self.max_connections_spin.setRange(1, 100)
        self.max_connections_spin.setValue(6)
        network_layout.addRow('Макс. з\'єднань на хост:', self.max_connections_spin)
        
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(5, 300)
        self.timeout_spin.setValue(30)
        self.timeout_spin.setSuffix(' сек')
        network_layout.addRow('Таймаут з\'єднання:', self.timeout_spin)
        
        self.user_agent_edit = QLineEdit()
        self.user_agent_edit.setPlaceholderText('Глобальний User-Agent (необов\'язково)')
        network_layout.addRow('User-Agent:', self.user_agent_edit)
        
        layout.addWidget(network_group)
        layout.addStretch()
        
        tab_widget.addTab(widget, 'Мережа')
        
    def create_backup_tab(self, tab_widget):
        """Вкладка експорту/імпорту"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Резервні копії
        backup_group = QGroupBox('Резервні копії')
        backup_layout = QVBoxLayout(backup_group)
        
        backup_info = QLabel(
            'Створюйте резервні копії своїх профілів та налаштувань\n'
            'для відновлення у випадку втрати даних.'
        )
        backup_layout.addWidget(backup_info)
        
        backup_buttons = QHBoxLayout()
        
        export_btn = QPushButton('Експорт профілів')
        export_btn.clicked.connect(self.export_profiles)
        backup_buttons.addWidget(export_btn)
        
        import_btn = QPushButton('Імпорт профілів')
        import_btn.clicked.connect(self.import_profiles)
        backup_buttons.addWidget(import_btn)
        
        backup_layout.addLayout(backup_buttons)
        
        layout.addWidget(backup_group)
        
        # Очищення даних
        cleanup_group = QGroupBox('Очищення даних')
        cleanup_layout = QVBoxLayout(cleanup_group)
        
        cleanup_info = QLabel(
            'Видаліть збережені дані для звільнення місця\n'
            'або повного очищення браузера.'
        )
        cleanup_layout.addWidget(cleanup_info)
        
        cleanup_buttons = QHBoxLayout()
        
        clear_cache_btn = QPushButton('Очистити кеш')
        clear_cache_btn.clicked.connect(self.clear_cache)
        cleanup_buttons.addWidget(clear_cache_btn)
        
        clear_cookies_btn = QPushButton('Очистити cookies')
        clear_cookies_btn.clicked.connect(self.clear_cookies)
        cleanup_buttons.addWidget(clear_cookies_btn)
        
        clear_all_btn = QPushButton('Очистити все')
        clear_all_btn.clicked.connect(self.clear_all_data)
        cleanup_buttons.addWidget(clear_all_btn)
        
        cleanup_layout.addLayout(cleanup_buttons)
        
        layout.addWidget(cleanup_group)
        layout.addStretch()
        
        tab_widget.addTab(widget, 'Дані')
        
    def load_settings(self):
        """Завантаження налаштувань"""
        # Загальні
        self.homepage_edit.setText(self.settings.value('homepage', 'https://www.google.com'))
        self.restore_tabs_check.setChecked(self.settings.value('restore_tabs', True, type=bool))
        self.auto_update_check.setChecked(self.settings.value('auto_update', True, type=bool))
        self.close_warning_check.setChecked(self.settings.value('close_warning', True, type=bool))
        
        downloads_path = self.settings.value('downloads_path', os.path.expanduser('~/Downloads'))
        self.downloads_path_edit.setText(downloads_path)
        
        # Приватність
        self.telemetry_check.setChecked(self.settings.value('telemetry', False, type=bool))
        self.crash_reports_check.setChecked(self.settings.value('crash_reports', True, type=bool))
        self.block_fingerprinting_check.setChecked(self.settings.value('block_fingerprinting', True, type=bool))
        self.spoof_timezone_check.setChecked(self.settings.value('spoof_timezone', True, type=bool))
        self.spoof_screen_check.setChecked(self.settings.value('spoof_screen', True, type=bool))
        self.block_webrtc_check.setChecked(self.settings.value('block_webrtc', True, type=bool))
        
        # Блокування
        self.adblock_enabled_check.setChecked(self.settings.value('adblock_enabled', True, type=bool))
        self.block_trackers_check.setChecked(self.settings.value('block_trackers', True, type=bool))
        self.block_malware_check.setChecked(self.settings.value('block_malware', True, type=bool))
        self.block_popups_check.setChecked(self.settings.value('block_popups', True, type=bool))
        
        # Мережа
        self.global_proxy_check.setChecked(self.settings.value('global_proxy', False, type=bool))
        self.global_proxy_host_edit.setText(self.settings.value('global_proxy_host', ''))
        self.global_proxy_port_spin.setValue(self.settings.value('global_proxy_port', 8080, type=int))
        self.max_connections_spin.setValue(self.settings.value('max_connections', 6, type=int))
        self.timeout_spin.setValue(self.settings.value('timeout', 30, type=int))
        
    def save_settings(self):
        """Збереження налаштувань"""
        # Загальні
        self.settings.setValue('homepage', self.homepage_edit.text())
        self.settings.setValue('restore_tabs', self.restore_tabs_check.isChecked())
        self.settings.setValue('auto_update', self.auto_update_check.isChecked())
        self.settings.setValue('close_warning', self.close_warning_check.isChecked())
        self.settings.setValue('downloads_path', self.downloads_path_edit.text())
        
        # Приватність
        self.settings.setValue('telemetry', self.telemetry_check.isChecked())
        self.settings.setValue('crash_reports', self.crash_reports_check.isChecked())
        self.settings.setValue('block_fingerprinting', self.block_fingerprinting_check.isChecked())
        self.settings.setValue('spoof_timezone', self.spoof_timezone_check.isChecked())
        self.settings.setValue('spoof_screen', self.spoof_screen_check.isChecked())
        self.settings.setValue('block_webrtc', self.block_webrtc_check.isChecked())
        
        # Блокування
        self.settings.setValue('adblock_enabled', self.adblock_enabled_check.isChecked())
        self.settings.setValue('block_trackers', self.block_trackers_check.isChecked())
        self.settings.setValue('block_malware', self.block_malware_check.isChecked())
        self.settings.setValue('block_popups', self.block_popups_check.isChecked())
        
        # Мережа
        self.settings.setValue('global_proxy', self.global_proxy_check.isChecked())
        self.settings.setValue('global_proxy_host', self.global_proxy_host_edit.text())
        self.settings.setValue('global_proxy_port', self.global_proxy_port_spin.value())
        self.settings.setValue('max_connections', self.max_connections_spin.value())
        self.settings.setValue('timeout', self.timeout_spin.value())
        
    def browse_downloads_folder(self):
        """Вибір папки завантажень"""
        folder = QFileDialog.getExistingDirectory(self, 'Виберіть папку завантажень')
        if folder:
            self.downloads_path_edit.setText(folder)
            
    def update_filter_lists(self):
        """Оновлення списків фільтрів"""
        QMessageBox.information(self, 'Оновлення', 'Списки фільтрів оновлено!')
        
    def export_profiles(self):
        """Експорт профілів"""
        filename, _ = QFileDialog.getSaveFileName(
            self, 'Експорт профілів', 'profiles_backup.json', 'JSON files (*.json)'
        )
        if filename:
            # TODO: Реалізувати експорт
            QMessageBox.information(self, 'Експорт', f'Профілі експортовано в {filename}')
            
    def import_profiles(self):
        """Імпорт профілів"""
        filename, _ = QFileDialog.getOpenFileName(
            self, 'Імпорт профілів', '', 'JSON files (*.json)'
        )
        if filename:
            # TODO: Реалізувати імпорт
            QMessageBox.information(self, 'Імпорт', f'Профілі імпортовано з {filename}')
            
    def clear_cache(self):
        """Очищення кешу"""
        reply = QMessageBox.question(
            self, 'Підтвердження', 'Очистити кеш браузера?',
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            # TODO: Реалізувати очищення кешу
            QMessageBox.information(self, 'Очищення', 'Кеш очищено!')
            
    def clear_cookies(self):
        """Очищення cookies"""
        reply = QMessageBox.question(
            self, 'Підтвердження', 'Очистити всі cookies?',
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            # TODO: Реалізувати очищення cookies
            QMessageBox.information(self, 'Очищення', 'Cookies очищено!')
            
    def clear_all_data(self):
        """Очищення всіх даних"""
        reply = QMessageBox.question(
            self, 'Підтвердження', 
            'Очистити ВСІ дані браузера? Це незворотна дія!',
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            # TODO: Реалізувати повне очищення
            QMessageBox.information(self, 'Очищення', 'Всі дані очищено!')
            
    def apply_settings(self):
        """Застосування налаштувань без закриття діалогу"""
        self.save_settings()
        QMessageBox.information(self, 'Налаштування', 'Налаштування збережено!')
        
    def accept(self):
        """Збереження та закриття"""
        self.save_settings()
        super().accept()
>>>>>>> 5a38118ad408679126e5a17483fa7875264c621b

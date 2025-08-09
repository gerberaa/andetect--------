<<<<<<< HEAD
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Головне вікно браузера AnDetect
"""

import os
import sys
from PyQt5.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, 
                            QTabWidget, QPushButton, QLineEdit, QMenuBar, 
                            QMenu, QAction, QToolBar, QSplitter, QTreeWidget,
                            QTreeWidgetItem, QLabel, QComboBox, QCheckBox,
                            QStatusBar, QDialog, QDialogButtonBox, QFormLayout)
from PyQt5.QtCore import Qt, QUrl, pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage, QWebEngineProfile

from .web_page import AnDetectWebPage
from .profile_manager import ProfileManager
from .settings import SettingsDialog


class BrowserMainWindow(QMainWindow):
    """Головне вікно браузера"""
    
    def __init__(self):
        super().__init__()
        self.profile_manager = ProfileManager()
        self.current_profile = None
        self.init_ui()
        self.load_default_profile()
        
    def init_ui(self):
        """Ініціалізація користувацького інтерфейсу"""
        self.setWindowTitle("AnDetect Browser v1.0")
        self.setGeometry(100, 100, 1200, 800)
        
        # Центральний віджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Основний layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Створюємо меню
        self.create_menu_bar()
        
        # Створюємо toolbar
        self.create_toolbar()
        
        # Створюємо splitter для бічної панелі та браузера
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # Бічна панель з профілями
        self.create_sidebar(splitter)
        
        # Область браузера
        self.create_browser_area(splitter)
        
        # Встановлюємо пропорції splitter
        splitter.setSizes([250, 950])
        
        # Статус бар
        self.create_status_bar()
        
    def create_menu_bar(self):
        """Створення меню"""
        menubar = self.menuBar()
        
        # Меню "Файл"
        file_menu = menubar.addMenu('Файл')
        
        new_tab_action = QAction('Нова вкладка', self)
        new_tab_action.setShortcut('Ctrl+T')
        new_tab_action.triggered.connect(self.new_tab)
        file_menu.addAction(new_tab_action)
        
        new_window_action = QAction('Нове вікно', self)
        new_window_action.setShortcut('Ctrl+N')
        file_menu.addAction(new_window_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('Вихід', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Меню "Профілі"
        profile_menu = menubar.addMenu('Профілі')
        
        new_profile_action = QAction('Новий профіль', self)
        new_profile_action.triggered.connect(self.create_new_profile)
        profile_menu.addAction(new_profile_action)
        
        manage_profiles_action = QAction('Керування профілями', self)
        manage_profiles_action.triggered.connect(self.manage_profiles)
        profile_menu.addAction(manage_profiles_action)
        
        # Меню "Налаштування"
        settings_menu = menubar.addMenu('Налаштування')
        
        browser_settings_action = QAction('Налаштування браузера', self)
        browser_settings_action.triggered.connect(self.open_settings)
        settings_menu.addAction(browser_settings_action)
        
        proxy_settings_action = QAction('Налаштування проксі', self)
        proxy_settings_action.triggered.connect(self.proxy_settings)
        settings_menu.addAction(proxy_settings_action)
        
    def create_toolbar(self):
        """Створення панелі інструментів"""
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        # Кнопки навігації
        self.back_btn = QPushButton('←')
        self.back_btn.setToolTip('Назад')
        self.back_btn.clicked.connect(self.go_back)
        toolbar.addWidget(self.back_btn)
        
        self.forward_btn = QPushButton('→')
        self.forward_btn.setToolTip('Вперед')
        self.forward_btn.clicked.connect(self.go_forward)
        toolbar.addWidget(self.forward_btn)
        
        self.refresh_btn = QPushButton('⟳')
        self.refresh_btn.setToolTip('Оновити')
        self.refresh_btn.clicked.connect(self.refresh_page)
        toolbar.addWidget(self.refresh_btn)
        
        # Адресний рядок
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText('Введіть URL або пошуковий запит...')
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        toolbar.addWidget(self.url_bar)
        
        # Кнопка налаштувань
        self.settings_btn = QPushButton('⚙')
        self.settings_btn.setToolTip('Налаштування')
        self.settings_btn.clicked.connect(self.open_settings)
        toolbar.addWidget(self.settings_btn)
        
    def create_sidebar(self, parent):
        """Створення бічної панелі"""
        sidebar = QWidget()
        sidebar_layout = QVBoxLayout(sidebar)
        
        # Заголовок
        profile_label = QLabel('Профілі:')
        profile_label.setStyleSheet('font-weight: bold; padding: 5px;')
        sidebar_layout.addWidget(profile_label)
        
        # Поточний профіль
        self.current_profile_combo = QComboBox()
        self.current_profile_combo.currentTextChanged.connect(self.switch_profile)
        sidebar_layout.addWidget(self.current_profile_combo)
        
        # Список профілів
        self.profile_tree = QTreeWidget()
        self.profile_tree.setHeaderLabels(['Профіль', 'Статус'])
        sidebar_layout.addWidget(self.profile_tree)
        
        # Кнопки керування профілями
        profile_buttons_layout = QHBoxLayout()
        
        add_profile_btn = QPushButton('+')
        add_profile_btn.setToolTip('Додати профіль')
        add_profile_btn.clicked.connect(self.create_new_profile)
        profile_buttons_layout.addWidget(add_profile_btn)
        
        edit_profile_btn = QPushButton('✎')
        edit_profile_btn.setToolTip('Редагувати профіль')
        edit_profile_btn.clicked.connect(self.edit_current_profile)
        profile_buttons_layout.addWidget(edit_profile_btn)
        
        delete_profile_btn = QPushButton('×')
        delete_profile_btn.setToolTip('Видалити профіль')
        delete_profile_btn.clicked.connect(self.delete_current_profile)
        profile_buttons_layout.addWidget(delete_profile_btn)
        
        sidebar_layout.addLayout(profile_buttons_layout)
        
        # Індикатори стану
        sidebar_layout.addWidget(QLabel('Стан:'))
        
        self.proxy_status = QLabel('Проксі: Відключено')
        self.proxy_status.setStyleSheet('color: red;')
        sidebar_layout.addWidget(self.proxy_status)
        
        self.fingerprint_status = QLabel('Маскування: Активно')
        self.fingerprint_status.setStyleSheet('color: green;')
        sidebar_layout.addWidget(self.fingerprint_status)
        
        sidebar_layout.addStretch()
        parent.addWidget(sidebar)
        
    def create_browser_area(self, parent):
        """Створення області браузера"""
        browser_widget = QWidget()
        browser_layout = QVBoxLayout(browser_widget)
        browser_layout.setContentsMargins(0, 0, 0, 0)
        
        # Вкладки
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.tab_widget.currentChanged.connect(self.tab_changed)
        browser_layout.addWidget(self.tab_widget)
        
        # Додаємо першу вкладку
        self.new_tab()
        
        parent.addWidget(browser_widget)
        
    def create_status_bar(self):
        """Створення статус бару"""
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)
        
        # Інформація про профіль
        self.profile_status_label = QLabel('Профіль: Не вибрано')
        status_bar.addWidget(self.profile_status_label)
        
        status_bar.addPermanentWidget(QLabel('AnDetect Browser v1.0'))
        
    def new_tab(self, url=None):
        """Створення нової вкладки"""
        if url is None:
            url = QUrl('about:blank')
        elif isinstance(url, str):
            url = QUrl(url)
            
        # Створюємо веб-сторінку з поточним профілем
        web_view = QWebEngineView()
        
        if self.current_profile:
            page = AnDetectWebPage(self.current_profile, web_view)
            web_view.setPage(page)
        
        web_view.load(url)
        
        # Додаємо вкладку
        index = self.tab_widget.addTab(web_view, 'Нова вкладка')
        self.tab_widget.setCurrentIndex(index)
        
        # Підключаємо сигнали
        web_view.titleChanged.connect(lambda title: self.update_tab_title(web_view, title))
        web_view.urlChanged.connect(lambda url: self.update_url_bar(url))
        
        return web_view
        
    def close_tab(self, index):
        """Закриття вкладки"""
        if self.tab_widget.count() > 1:
            self.tab_widget.removeTab(index)
        else:
            # Якщо остання вкладка, створюємо нову порожню
            self.tab_widget.removeTab(index)
            self.new_tab()
            
    def tab_changed(self, index):
        """Обробка зміни вкладки"""
        if index >= 0:
            web_view = self.tab_widget.widget(index)
            if web_view:
                self.url_bar.setText(web_view.url().toString())
                
    def update_tab_title(self, web_view, title):
        """Оновлення заголовка вкладки"""
        index = self.tab_widget.indexOf(web_view)
        if index >= 0:
            if not title:
                title = 'Нова вкладка'
            elif len(title) > 20:
                title = title[:20] + '...'
            self.tab_widget.setTabText(index, title)
            
    def update_url_bar(self, url):
        """Оновлення адресного рядка"""
        current_web_view = self.tab_widget.currentWidget()
        if current_web_view and current_web_view.url() == url:
            self.url_bar.setText(url.toString())
            
    def navigate_to_url(self):
        """Навігація за URL"""
        url_text = self.url_bar.text().strip()
        if not url_text:
            return
            
        # Перевіряємо чи це URL чи пошуковий запит
        if not url_text.startswith(('http://', 'https://')):
            if '.' in url_text and ' ' not in url_text:
                url_text = 'https://' + url_text
            else:
                # Пошуковий запит
                url_text = f'https://www.google.com/search?q={url_text}'
                
        current_web_view = self.tab_widget.currentWidget()
        if current_web_view:
            current_web_view.load(QUrl(url_text))
            
    def go_back(self):
        """Повернутись назад"""
        current_web_view = self.tab_widget.currentWidget()
        if current_web_view:
            current_web_view.back()
            
    def go_forward(self):
        """Перейти вперед"""
        current_web_view = self.tab_widget.currentWidget()
        if current_web_view:
            current_web_view.forward()
            
    def refresh_page(self):
        """Оновити сторінку"""
        current_web_view = self.tab_widget.currentWidget()
        if current_web_view:
            current_web_view.reload()
            
    def load_default_profile(self):
        """Завантаження профілю за замовчуванням"""
        profiles = self.profile_manager.get_all_profiles()
        
        if not profiles:
            # Створюємо профіль за замовчуванням
            default_profile = self.profile_manager.create_profile("За замовчуванням")
            self.current_profile = default_profile
        else:
            self.current_profile = profiles[0]
            
        self.update_profile_ui()
        
    def update_profile_ui(self):
        """Оновлення UI профілів"""
        # Оновлюємо комбобокс
        self.current_profile_combo.clear()
        profiles = self.profile_manager.get_all_profiles()
        
        for profile in profiles:
            self.current_profile_combo.addItem(profile.name)
            
        if self.current_profile:
            self.current_profile_combo.setCurrentText(self.current_profile.name)
            self.profile_status_label.setText(f'Профіль: {self.current_profile.name}')
            
        # Оновлюємо дерево профілів
        self.profile_tree.clear()
        for profile in profiles:
            item = QTreeWidgetItem([profile.name, 'Активний' if profile == self.current_profile else 'Неактивний'])
            self.profile_tree.addTopLevelItem(item)
            
    def switch_profile(self, profile_name):
        """Перемикання профілю"""
        if profile_name:
            profile = self.profile_manager.get_profile_by_name(profile_name)
            if profile:
                self.current_profile = profile
                self.profile_status_label.setText(f'Профіль: {profile.name}')
                # Оновлюємо всі вкладки з новим профілем
                self.restart_all_tabs()
                
    def restart_all_tabs(self):
        """Перезапуск всіх вкладок з новим профілем"""
        # Збираємо URL всіх відкритих вкладок
        urls = []
        for i in range(self.tab_widget.count()):
            web_view = self.tab_widget.widget(i)
            if web_view:
                urls.append(web_view.url().toString())
                
        # Закриваємо всі вкладки
        self.tab_widget.clear()
        
        # Відкриваємо вкладки заново
        if urls:
            for url in urls:
                if url and url != 'about:blank':
                    self.new_tab(url)
        else:
            self.new_tab()
            
    def create_new_profile(self):
        """Створення нового профілю"""
        from .profile_dialog import ProfileDialog
        dialog = ProfileDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            profile_data = dialog.get_profile_data()
            profile = self.profile_manager.create_profile(
                profile_data['name'],
                profile_data
            )
            self.update_profile_ui()
            
    def edit_current_profile(self):
        """Редагування поточного профілю"""
        if self.current_profile:
            from .profile_dialog import ProfileDialog
            dialog = ProfileDialog(self, self.current_profile)
            if dialog.exec_() == QDialog.Accepted:
                profile_data = dialog.get_profile_data()
                self.profile_manager.update_profile(self.current_profile.id, profile_data)
                self.update_profile_ui()
                
    def delete_current_profile(self):
        """Видалення поточного профілю"""
        if self.current_profile and self.current_profile.name != "За замовчуванням":
            # Запитуємо підтвердження
            from PyQt5.QtWidgets import QMessageBox
            reply = QMessageBox.question(
                self, 'Підтвердження', 
                f'Ви впевнені що хочете видалити профіль "{self.current_profile.name}"?',
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.profile_manager.delete_profile(self.current_profile.id)
                self.load_default_profile()
                self.update_profile_ui()
                
    def manage_profiles(self):
        """Відкриття менеджера профілів"""
        # TODO: Реалізувати детальний менеджер профілів
        pass
        
    def open_settings(self):
        """Відкриття налаштувань"""
        dialog = SettingsDialog(self)
        dialog.exec_()
        
    def proxy_settings(self):
        """Налаштування проксі"""
        # TODO: Реалізувати налаштування проксі
        pass
=======
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Головне вікно браузера AnDetect
"""

import os
import sys
from PyQt5.QtWidgets import (QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, 
                            QTabWidget, QPushButton, QLineEdit, QMenuBar, 
                            QMenu, QAction, QToolBar, QSplitter, QTreeWidget,
                            QTreeWidgetItem, QLabel, QComboBox, QCheckBox,
                            QStatusBar, QDialog, QDialogButtonBox, QFormLayout)
from PyQt5.QtCore import Qt, QUrl, pyqtSignal
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage, QWebEngineProfile

from .web_page import AnDetectWebPage
from .profile_manager import ProfileManager
from .settings import SettingsDialog


class BrowserMainWindow(QMainWindow):
    """Головне вікно браузера"""
    
    def __init__(self):
        super().__init__()
        self.profile_manager = ProfileManager()
        self.current_profile = None
        self.init_ui()
        self.load_default_profile()
        
    def init_ui(self):
        """Ініціалізація користувацького інтерфейсу"""
        self.setWindowTitle("AnDetect Browser v1.0")
        self.setGeometry(100, 100, 1200, 800)
        
        # Центральний віджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Основний layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Створюємо меню
        self.create_menu_bar()
        
        # Створюємо toolbar
        self.create_toolbar()
        
        # Створюємо splitter для бічної панелі та браузера
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # Бічна панель з профілями
        self.create_sidebar(splitter)
        
        # Область браузера
        self.create_browser_area(splitter)
        
        # Встановлюємо пропорції splitter
        splitter.setSizes([250, 950])
        
        # Статус бар
        self.create_status_bar()
        
    def create_menu_bar(self):
        """Створення меню"""
        menubar = self.menuBar()
        
        # Меню "Файл"
        file_menu = menubar.addMenu('Файл')
        
        new_tab_action = QAction('Нова вкладка', self)
        new_tab_action.setShortcut('Ctrl+T')
        new_tab_action.triggered.connect(self.new_tab)
        file_menu.addAction(new_tab_action)
        
        new_window_action = QAction('Нове вікно', self)
        new_window_action.setShortcut('Ctrl+N')
        file_menu.addAction(new_window_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction('Вихід', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Меню "Профілі"
        profile_menu = menubar.addMenu('Профілі')
        
        new_profile_action = QAction('Новий профіль', self)
        new_profile_action.triggered.connect(self.create_new_profile)
        profile_menu.addAction(new_profile_action)
        
        manage_profiles_action = QAction('Керування профілями', self)
        manage_profiles_action.triggered.connect(self.manage_profiles)
        profile_menu.addAction(manage_profiles_action)
        
        # Меню "Налаштування"
        settings_menu = menubar.addMenu('Налаштування')
        
        browser_settings_action = QAction('Налаштування браузера', self)
        browser_settings_action.triggered.connect(self.open_settings)
        settings_menu.addAction(browser_settings_action)
        
        proxy_settings_action = QAction('Налаштування проксі', self)
        proxy_settings_action.triggered.connect(self.proxy_settings)
        settings_menu.addAction(proxy_settings_action)
        
    def create_toolbar(self):
        """Створення панелі інструментів"""
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        # Кнопки навігації
        self.back_btn = QPushButton('←')
        self.back_btn.setToolTip('Назад')
        self.back_btn.clicked.connect(self.go_back)
        toolbar.addWidget(self.back_btn)
        
        self.forward_btn = QPushButton('→')
        self.forward_btn.setToolTip('Вперед')
        self.forward_btn.clicked.connect(self.go_forward)
        toolbar.addWidget(self.forward_btn)
        
        self.refresh_btn = QPushButton('⟳')
        self.refresh_btn.setToolTip('Оновити')
        self.refresh_btn.clicked.connect(self.refresh_page)
        toolbar.addWidget(self.refresh_btn)
        
        # Адресний рядок
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText('Введіть URL або пошуковий запит...')
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        toolbar.addWidget(self.url_bar)
        
        # Кнопка налаштувань
        self.settings_btn = QPushButton('⚙')
        self.settings_btn.setToolTip('Налаштування')
        self.settings_btn.clicked.connect(self.open_settings)
        toolbar.addWidget(self.settings_btn)
        
    def create_sidebar(self, parent):
        """Створення бічної панелі"""
        sidebar = QWidget()
        sidebar_layout = QVBoxLayout(sidebar)
        
        # Заголовок
        profile_label = QLabel('Профілі:')
        profile_label.setStyleSheet('font-weight: bold; padding: 5px;')
        sidebar_layout.addWidget(profile_label)
        
        # Поточний профіль
        self.current_profile_combo = QComboBox()
        self.current_profile_combo.currentTextChanged.connect(self.switch_profile)
        sidebar_layout.addWidget(self.current_profile_combo)
        
        # Список профілів
        self.profile_tree = QTreeWidget()
        self.profile_tree.setHeaderLabels(['Профіль', 'Статус'])
        sidebar_layout.addWidget(self.profile_tree)
        
        # Кнопки керування профілями
        profile_buttons_layout = QHBoxLayout()
        
        add_profile_btn = QPushButton('+')
        add_profile_btn.setToolTip('Додати профіль')
        add_profile_btn.clicked.connect(self.create_new_profile)
        profile_buttons_layout.addWidget(add_profile_btn)
        
        edit_profile_btn = QPushButton('✎')
        edit_profile_btn.setToolTip('Редагувати профіль')
        edit_profile_btn.clicked.connect(self.edit_current_profile)
        profile_buttons_layout.addWidget(edit_profile_btn)
        
        delete_profile_btn = QPushButton('×')
        delete_profile_btn.setToolTip('Видалити профіль')
        delete_profile_btn.clicked.connect(self.delete_current_profile)
        profile_buttons_layout.addWidget(delete_profile_btn)
        
        sidebar_layout.addLayout(profile_buttons_layout)
        
        # Індикатори стану
        sidebar_layout.addWidget(QLabel('Стан:'))
        
        self.proxy_status = QLabel('Проксі: Відключено')
        self.proxy_status.setStyleSheet('color: red;')
        sidebar_layout.addWidget(self.proxy_status)
        
        self.fingerprint_status = QLabel('Маскування: Активно')
        self.fingerprint_status.setStyleSheet('color: green;')
        sidebar_layout.addWidget(self.fingerprint_status)
        
        sidebar_layout.addStretch()
        parent.addWidget(sidebar)
        
    def create_browser_area(self, parent):
        """Створення області браузера"""
        browser_widget = QWidget()
        browser_layout = QVBoxLayout(browser_widget)
        browser_layout.setContentsMargins(0, 0, 0, 0)
        
        # Вкладки
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.tab_widget.currentChanged.connect(self.tab_changed)
        browser_layout.addWidget(self.tab_widget)
        
        # Додаємо першу вкладку
        self.new_tab()
        
        parent.addWidget(browser_widget)
        
    def create_status_bar(self):
        """Створення статус бару"""
        status_bar = QStatusBar()
        self.setStatusBar(status_bar)
        
        # Інформація про профіль
        self.profile_status_label = QLabel('Профіль: Не вибрано')
        status_bar.addWidget(self.profile_status_label)
        
        status_bar.addPermanentWidget(QLabel('AnDetect Browser v1.0'))
        
    def new_tab(self, url=None):
        """Створення нової вкладки"""
        if url is None:
            url = QUrl('about:blank')
        elif isinstance(url, str):
            url = QUrl(url)
            
        # Створюємо веб-сторінку з поточним профілем
        web_view = QWebEngineView()
        
        if self.current_profile:
            page = AnDetectWebPage(self.current_profile, web_view)
            web_view.setPage(page)
        
        web_view.load(url)
        
        # Додаємо вкладку
        index = self.tab_widget.addTab(web_view, 'Нова вкладка')
        self.tab_widget.setCurrentIndex(index)
        
        # Підключаємо сигнали
        web_view.titleChanged.connect(lambda title: self.update_tab_title(web_view, title))
        web_view.urlChanged.connect(lambda url: self.update_url_bar(url))
        
        return web_view
        
    def close_tab(self, index):
        """Закриття вкладки"""
        if self.tab_widget.count() > 1:
            self.tab_widget.removeTab(index)
        else:
            # Якщо остання вкладка, створюємо нову порожню
            self.tab_widget.removeTab(index)
            self.new_tab()
            
    def tab_changed(self, index):
        """Обробка зміни вкладки"""
        if index >= 0:
            web_view = self.tab_widget.widget(index)
            if web_view:
                self.url_bar.setText(web_view.url().toString())
                
    def update_tab_title(self, web_view, title):
        """Оновлення заголовка вкладки"""
        index = self.tab_widget.indexOf(web_view)
        if index >= 0:
            if not title:
                title = 'Нова вкладка'
            elif len(title) > 20:
                title = title[:20] + '...'
            self.tab_widget.setTabText(index, title)
            
    def update_url_bar(self, url):
        """Оновлення адресного рядка"""
        current_web_view = self.tab_widget.currentWidget()
        if current_web_view and current_web_view.url() == url:
            self.url_bar.setText(url.toString())
            
    def navigate_to_url(self):
        """Навігація за URL"""
        url_text = self.url_bar.text().strip()
        if not url_text:
            return
            
        # Перевіряємо чи це URL чи пошуковий запит
        if not url_text.startswith(('http://', 'https://')):
            if '.' in url_text and ' ' not in url_text:
                url_text = 'https://' + url_text
            else:
                # Пошуковий запит
                url_text = f'https://www.google.com/search?q={url_text}'
                
        current_web_view = self.tab_widget.currentWidget()
        if current_web_view:
            current_web_view.load(QUrl(url_text))
            
    def go_back(self):
        """Повернутись назад"""
        current_web_view = self.tab_widget.currentWidget()
        if current_web_view:
            current_web_view.back()
            
    def go_forward(self):
        """Перейти вперед"""
        current_web_view = self.tab_widget.currentWidget()
        if current_web_view:
            current_web_view.forward()
            
    def refresh_page(self):
        """Оновити сторінку"""
        current_web_view = self.tab_widget.currentWidget()
        if current_web_view:
            current_web_view.reload()
            
    def load_default_profile(self):
        """Завантаження профілю за замовчуванням"""
        profiles = self.profile_manager.get_all_profiles()
        
        if not profiles:
            # Створюємо профіль за замовчуванням
            default_profile = self.profile_manager.create_profile("За замовчуванням")
            self.current_profile = default_profile
        else:
            self.current_profile = profiles[0]
            
        self.update_profile_ui()
        
    def update_profile_ui(self):
        """Оновлення UI профілів"""
        # Оновлюємо комбобокс
        self.current_profile_combo.clear()
        profiles = self.profile_manager.get_all_profiles()
        
        for profile in profiles:
            self.current_profile_combo.addItem(profile.name)
            
        if self.current_profile:
            self.current_profile_combo.setCurrentText(self.current_profile.name)
            self.profile_status_label.setText(f'Профіль: {self.current_profile.name}')
            
        # Оновлюємо дерево профілів
        self.profile_tree.clear()
        for profile in profiles:
            item = QTreeWidgetItem([profile.name, 'Активний' if profile == self.current_profile else 'Неактивний'])
            self.profile_tree.addTopLevelItem(item)
            
    def switch_profile(self, profile_name):
        """Перемикання профілю"""
        if profile_name:
            profile = self.profile_manager.get_profile_by_name(profile_name)
            if profile:
                self.current_profile = profile
                self.profile_status_label.setText(f'Профіль: {profile.name}')
                # Оновлюємо всі вкладки з новим профілем
                self.restart_all_tabs()
                
    def restart_all_tabs(self):
        """Перезапуск всіх вкладок з новим профілем"""
        # Збираємо URL всіх відкритих вкладок
        urls = []
        for i in range(self.tab_widget.count()):
            web_view = self.tab_widget.widget(i)
            if web_view:
                urls.append(web_view.url().toString())
                
        # Закриваємо всі вкладки
        self.tab_widget.clear()
        
        # Відкриваємо вкладки заново
        if urls:
            for url in urls:
                if url and url != 'about:blank':
                    self.new_tab(url)
        else:
            self.new_tab()
            
    def create_new_profile(self):
        """Створення нового профілю"""
        from .profile_dialog import ProfileDialog
        dialog = ProfileDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            profile_data = dialog.get_profile_data()
            profile = self.profile_manager.create_profile(
                profile_data['name'],
                profile_data
            )
            self.update_profile_ui()
            
    def edit_current_profile(self):
        """Редагування поточного профілю"""
        if self.current_profile:
            from .profile_dialog import ProfileDialog
            dialog = ProfileDialog(self, self.current_profile)
            if dialog.exec_() == QDialog.Accepted:
                profile_data = dialog.get_profile_data()
                self.profile_manager.update_profile(self.current_profile.id, profile_data)
                self.update_profile_ui()
                
    def delete_current_profile(self):
        """Видалення поточного профілю"""
        if self.current_profile and self.current_profile.name != "За замовчуванням":
            # Запитуємо підтвердження
            from PyQt5.QtWidgets import QMessageBox
            reply = QMessageBox.question(
                self, 'Підтвердження', 
                f'Ви впевнені що хочете видалити профіль "{self.current_profile.name}"?',
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.profile_manager.delete_profile(self.current_profile.id)
                self.load_default_profile()
                self.update_profile_ui()
                
    def manage_profiles(self):
        """Відкриття менеджера профілів"""
        # TODO: Реалізувати детальний менеджер профілів
        pass
        
    def open_settings(self):
        """Відкриття налаштувань"""
        dialog = SettingsDialog(self)
        dialog.exec_()
        
    def proxy_settings(self):
        """Налаштування проксі"""
        # TODO: Реалізувати налаштування проксі
        pass
>>>>>>> 5a38118ad408679126e5a17483fa7875264c621b

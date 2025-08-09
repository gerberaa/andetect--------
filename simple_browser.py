#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AnDetect Browser - Спрощена версія для тестування
"""

import sys
import os
import json
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QVBoxLayout, QHBoxLayout,
    QWidget, QPushButton, QLineEdit, QMenuBar, QAction, QMessageBox,
    QStatusBar, QToolBar, QLabel
)
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtWebEngineWidgets import QWebEngineView


class SimpleBrowserTab(QWidget):
    """Спрощена вкладка браузера"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Веб-переглядач
        self.web_view = QWebEngineView()
        layout.addWidget(self.web_view)
        
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


class SimpleBrowser(QMainWindow):
    """Спрощений браузер"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
    
    def init_ui(self):
        """Ініціалізація інтерфейсу"""
        self.setWindowTitle("AnDetect Browser - Спрощена версія")
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
        
        # Індикатор стану
        self.status_label = QLabel("AnDetect Browser - Готовий")
        self.status_bar.addPermanentWidget(self.status_label)
        
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
        
        # Меню довідка
        help_menu = menubar.addMenu('Довідка')
        
        about_action = QAction('Про програму', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def new_tab(self, url: str = ""):
        """Створення нової вкладки"""
        tab = SimpleBrowserTab()
        
        # Підключення сигналів
        tab.web_view.titleChanged.connect(lambda title: self.update_tab_title(tab, title))
        tab.web_view.urlChanged.connect(self.update_address_bar)
        
        index = self.tabs.addTab(tab, "Нова вкладка")
        self.tabs.setCurrentIndex(index)
        
        if url:
            tab.load_url(url)
        else:
            tab.load_url("https://duckduckgo.com")
    
    def close_tab(self, index: int):
        """Закриття вкладки"""
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)
        else:
            self.close()
    
    def update_tab_title(self, tab: SimpleBrowserTab, title: str):
        """Оновлення заголовку вкладки"""
        index = self.tabs.indexOf(tab)
        if index != -1:
            self.tabs.setTabText(index, title[:30] + "..." if len(title) > 30 else title)
    
    def update_address_bar(self, url):
        """Оновлення адресного рядка"""
        if self.tabs.currentWidget():
            self.address_bar.setText(url.toString())
    
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
    
    def show_about(self):
        """Показ інформації про програму"""
        QMessageBox.about(
            self, 
            'Про AnDetect Browser',
            'AnDetect Browser v1.0\n\n'
            'Приватний браузер для Windows\n'
            'Розроблено з акцентом на анонімність та безпеку.\n\n'
            'Це спрощена версія для тестування основних функцій.'
        )


def main():
    """Головна функція"""
    app = QApplication(sys.argv)
    app.setApplicationName("AnDetect Browser")
    app.setApplicationVersion("1.0")
    
    # Налаштування стилю
    app.setStyle('Fusion')
    
    browser = SimpleBrowser()
    browser.show()
    
    print("AnDetect Browser запущено!")
    print("Спрощена версія - основні функції браузера доступні")
    print("Для повної функціональності встановіть всі залежності з requirements.txt")
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()

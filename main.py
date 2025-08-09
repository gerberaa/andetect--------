<<<<<<< HEAD
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AnDetect Browser - Анонімний браузер з підтримкою профілів
Подібний до ADS Power з маскуванням відбитків браузера
"""

import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from browser.main_window import BrowserMainWindow

def main():
    """Головна функція запуску програми"""
    # Встановлюємо високу якість DPI
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)
    app.setApplicationName("AnDetect Browser")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("AnDetect")
    
    # Створюємо головне вікно браузера
    browser = BrowserMainWindow()
    browser.show()
    
    # Запускаємо додаток
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
=======
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AnDetect Browser - Анонімний браузер з підтримкою профілів
Подібний до ADS Power з маскуванням відбитків браузера
"""

import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from browser.main_window import BrowserMainWindow

def main():
    """Головна функція запуску програми"""
    # Встановлюємо високу якість DPI
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)
    app.setApplicationName("AnDetect Browser")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("AnDetect")
    
    # Створюємо головне вікно браузера
    browser = BrowserMainWindow()
    browser.show()
    
    # Запускаємо додаток
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
>>>>>>> 5a38118ad408679126e5a17483fa7875264c621b

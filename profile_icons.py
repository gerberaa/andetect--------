#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Система іконок та міток для профілів AnDetect Profile Manager
"""

import os
from PyQt5.QtGui import QPixmap, QIcon, QPainter, QColor, QFont, QPen
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QLabel

# Прапорці країн
COUNTRY_FLAGS = {
    'UA': '🇺🇦',  # Україна
    'US': '🇺🇸',  # США
    'GB': '🇬🇧',  # Великобританія
    'DE': '🇩🇪',  # Німеччина
    'FR': '🇫🇷',  # Франція
    'CA': '🇨🇦',  # Канада
    'AU': '🇦🇺',  # Австралія
    'JP': '🇯🇵',  # Японія
    'KR': '🇰🇷',  # Південна Корея
    'CN': '🇨🇳',  # Китай
    'RU': '🇷🇺',  # Росія
    'BR': '🇧🇷',  # Бразилія
    'MX': '🇲🇽',  # Мексика
    'IN': '🇮🇳',  # Індія
    'IT': '🇮🇹',  # Італія
    'ES': '🇪🇸',  # Іспанія
    'NL': '🇳🇱',  # Нідерланди
    'SE': '🇸🇪',  # Швеція
    'NO': '🇳🇴',  # Норвегія
    'DK': '🇩🇰',  # Данія
    'FI': '🇫🇮',  # Фінляндія
    'PL': '🇵🇱',  # Польща
    'CZ': '🇨🇿',  # Чехія
    'HU': '🇭🇺',  # Угорщина
    'AT': '🇦🇹',  # Австрія
    'CH': '🇨🇭',  # Швейцарія
    'BE': '🇧🇪',  # Бельгія
    'PT': '🇵🇹',  # Португалія
    'GR': '🇬🇷',  # Греція
    'TR': '🇹🇷',  # Туреччина
    'IL': '🇮🇱',  # Ізраїль
    'AE': '🇦🇪',  # ОАЕ
    'SA': '🇸🇦',  # Саудівська Аравія
    'EG': '🇪🇬',  # Єгипет
    'ZA': '🇿🇦',  # ПАР
    'NG': '🇳🇬',  # Нігерія
    'KE': '🇰🇪',  # Кенія
    'TH': '🇹🇭',  # Таїланд
    'VN': '🇻🇳',  # В'єтнам
    'MY': '🇲🇾',  # Малайзія
    'SG': '🇸🇬',  # Сінгапур
    'ID': '🇮🇩',  # Індонезія
    'PH': '🇵🇭',  # Філіппіни
    'AR': '🇦🇷',  # Аргентина
    'CL': '🇨🇱',  # Чилі
    'CO': '🇨🇴',  # Колумбія
    'PE': '🇵🇪',  # Перу
    'VE': '🇻🇪',  # Венесуела
}

# Іконки для типів профілів
PROFILE_ICONS = {
    'work': '💼',        # Робота
    'personal': '👤',    # Особистий
    'social': '📱',      # Соціальні мережі
    'shopping': '🛒',    # Покупки
    'gaming': '🎮',      # Ігри
    'business': '🏢',    # Бізнес
    'education': '🎓',   # Освіта
    'finance': '💰',     # Фінанси
    'crypto': '₿',       # Криптовалюта
    'travel': '✈️',      # Подорожі
    'news': '📰',        # Новини
    'streaming': '📺',   # Стрімінг
    'development': '💻', # Розробка
    'design': '🎨',      # Дизайн
    'music': '🎵',       # Музика
    'photo': '📸',       # Фото
    'video': '🎬',       # Відео
    'medical': '⚕️',     # Медицина
    'legal': '⚖️',       # Юридичний
    'real_estate': '🏠', # Нерухомість
    'food': '🍔',        # Їжа
    'sports': '⚽',      # Спорт
    'fitness': '💪',     # Фітнес
    'auto': '🚗',        # Авто
    'tech': '🔧',        # Технології
    'science': '🔬',     # Наука
    'art': '🖼️',         # Мистецтво
    'book': '📚',        # Книги
    'hobby': '🎪',       # Хобі
    'test': '🧪',        # Тестування
    'temp': '⏰',        # Тимчасовий
    'backup': '💾',      # Резервний
    'admin': '👑',       # Адміністратор
    'guest': '👥',       # Гість
    'premium': '⭐',     # Преміум
    'vip': '💎',         # VIP
    'default': '🌐',     # За замовчуванням
}

# Кольори для міток
LABEL_COLORS = {
    'red': '#FF4444',
    'orange': '#FF8800', 
    'yellow': '#FFDD00',
    'green': '#44AA44',
    'blue': '#4488FF',
    'purple': '#AA44AA',
    'pink': '#FF44AA',
    'brown': '#AA7744',
    'gray': '#888888',
    'black': '#333333',
    'white': '#FFFFFF',
    'cyan': '#44AAAA',
    'lime': '#88FF44',
    'magenta': '#FF4488',
    'navy': '#444488',
    'olive': '#888844',
    'teal': '#448888',
    'silver': '#CCCCCC',
    'maroon': '#884444',
    'fuchsia': '#FF44FF',
}

class ProfileIcon:
    """Клас для роботи з іконками профілів"""
    
    @staticmethod
    def create_profile_icon(icon_type='default', country='UA', color='blue', size=32):
        """Створення іконки профілю"""
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Фон
        color_value = QColor(LABEL_COLORS.get(color, '#4488FF'))
        painter.setBrush(color_value)
        painter.setPen(QPen(Qt.white, 2))
        painter.drawEllipse(2, 2, size-4, size-4)
        
        # Іконка типу профілю
        icon_emoji = PROFILE_ICONS.get(icon_type, PROFILE_ICONS['default'])
        
        font = QFont()
        font.setPixelSize(size // 2)
        painter.setFont(font)
        painter.setPen(Qt.white)
        
        # Центруємо емодзі
        rect = painter.fontMetrics().boundingRect(icon_emoji)
        x = (size - rect.width()) // 2
        y = (size + rect.height()) // 2
        
        painter.drawText(x, y, icon_emoji)
        
        painter.end()
        return QIcon(pixmap)
    
    @staticmethod
    def create_country_flag_icon(country_code, size=24):
        """Створення іконки прапорця країни"""
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        flag_emoji = COUNTRY_FLAGS.get(country_code.upper(), '🌍')
        
        font = QFont()
        font.setPixelSize(size - 4)
        painter.setFont(font)
        
        rect = painter.fontMetrics().boundingRect(flag_emoji)
        x = (size - rect.width()) // 2
        y = (size + rect.height()) // 2
        
        painter.drawText(x, y, flag_emoji)
        painter.end()
        
        return QIcon(pixmap)
    
    @staticmethod
    def create_status_icon(status, size=16):
        """Створення іконки статусу"""
        status_icons = {
            'online': '🟢',
            'offline': '🔴', 
            'busy': '🟡',
            'away': '🟠',
            'invisible': '⚫',
            'active': '✅',
            'inactive': '❌',
            'warning': '⚠️',
            'error': '🚫',
            'success': '✔️',
            'info': 'ℹ️',
            'new': '🆕',
            'hot': '🔥',
            'star': '⭐',
            'heart': '❤️',
            'lock': '🔒',
            'unlock': '🔓',
            'shield': '🛡️',
            'key': '🗝️',
            'crown': '👑',
            'diamond': '💎',
        }
        
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        icon_emoji = status_icons.get(status, '❓')
        
        font = QFont()
        font.setPixelSize(size - 2)
        painter.setFont(font)
        
        rect = painter.fontMetrics().boundingRect(icon_emoji)
        x = (size - rect.width()) // 2
        y = (size + rect.height()) // 2
        
        painter.drawText(x, y, icon_emoji)
        painter.end()
        
        return QIcon(pixmap)

def get_country_by_timezone(timezone):
    """Отримання коду країни за часовим поясом"""
    timezone_to_country = {
        'Europe/Kiev': 'UA',
        'Europe/London': 'GB',
        'Europe/Berlin': 'DE',
        'Europe/Paris': 'FR',
        'America/New_York': 'US',
        'America/Los_Angeles': 'US',
        'America/Chicago': 'US',
        'America/Toronto': 'CA',
        'Asia/Tokyo': 'JP',
        'Asia/Seoul': 'KR',
        'Asia/Shanghai': 'CN',
        'Australia/Sydney': 'AU',
        'Europe/Rome': 'IT',
        'Europe/Madrid': 'ES',
        'Europe/Amsterdam': 'NL',
        'Europe/Stockholm': 'SE',
        'Europe/Oslo': 'NO',
        'Europe/Copenhagen': 'DK',
        'Europe/Helsinki': 'FI',
        'Europe/Warsaw': 'PL',
        'Europe/Prague': 'CZ',
        'Europe/Budapest': 'HU',
        'Europe/Vienna': 'AT',
        'Europe/Zurich': 'CH',
        'Europe/Brussels': 'BE',
        'Europe/Lisbon': 'PT',
        'Europe/Athens': 'GR',
        'Europe/Istanbul': 'TR',
        'Asia/Jerusalem': 'IL',
        'Asia/Dubai': 'AE',
        'Asia/Riyadh': 'SA',
        'Africa/Cairo': 'EG',
        'Africa/Johannesburg': 'ZA',
        'Africa/Lagos': 'NG',
        'Africa/Nairobi': 'KE',
        'Asia/Bangkok': 'TH',
        'Asia/Ho_Chi_Minh': 'VN',
        'Asia/Kuala_Lumpur': 'MY',
        'Asia/Singapore': 'SG',
        'Asia/Jakarta': 'ID',
        'Asia/Manila': 'PH',
        'America/Argentina/Buenos_Aires': 'AR',
        'America/Santiago': 'CL',
        'America/Bogota': 'CO',
        'America/Lima': 'PE',
        'America/Caracas': 'VE',
        'America/Sao_Paulo': 'BR',
        'America/Mexico_City': 'MX',
        'Asia/Kolkata': 'IN',
        'Europe/Moscow': 'RU',
    }
    
    return timezone_to_country.get(timezone, 'UA')

def get_browser_icon(user_agent):
    """Отримання іконки браузера за User-Agent"""
    browser_icons = {
        'Chrome': '🟦',
        'Firefox': '🟧', 
        'Safari': '🔵',
        'Edge': '🟪',
        'Opera': '🔴',
        'Vivaldi': '🟩',
        'Brave': '🦁',
        'Yandex': '🟨',
        'UC': '🔶',
        '360': '🔘',
        'QQ': '🐧',
    }
    
    if not user_agent:
        return '🌐'
    
    for browser, icon in browser_icons.items():
        if browser.lower() in user_agent.lower():
            return icon
    
    return '🌐'

def get_proxy_type_icon(proxy_type):
    """Отримання іконки типу проксі"""
    proxy_icons = {
        'HTTP': '🌐',
        'HTTPS': '🔒',
        'SOCKS5': '🔀',
        'SOCKS4': '↔️',
        'VPN': '🛡️',
        'TOR': '🧅',
        'DIRECT': '🎯',
        'NONE': '❌',
    }
    
    return proxy_icons.get(proxy_type, '❓')

if __name__ == "__main__":
    print("🎨 Тестування системи іконок...")
    print(f"Прапорці: {len(COUNTRY_FLAGS)} країн")
    print(f"Іконки профілів: {len(PROFILE_ICONS)} типів")
    print(f"Кольори: {len(LABEL_COLORS)} варіантів")
    
    print("\nПриклади:")
    print(f"Україна: {COUNTRY_FLAGS['UA']}")
    print(f"Робота: {PROFILE_ICONS['work']}")
    print(f"Особистий: {PROFILE_ICONS['personal']}")
    print(f"Соціальні мережі: {PROFILE_ICONS['social']}")
    print(f"Покупки: {PROFILE_ICONS['shopping']}")
    print(f"Ігри: {PROFILE_ICONS['gaming']}")

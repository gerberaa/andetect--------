#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Менеджер проксі для AnDetect Browser
Підтримує HTTP та SOCKS5 проксі
"""

import socks
import socket
import requests
from typing import Optional, Dict, Any
from PyQt5.QtCore import QObject, pyqtSignal, QThread, QTimer
from PyQt5.QtNetwork import QNetworkProxy, QNetworkProxyFactory
import time


class ProxyTester(QThread):
    """Потік для тестування проксі"""
    
    test_completed = pyqtSignal(bool, str, float)  # success, message, response_time
    
    def __init__(self, proxy_config: Dict[str, Any]):
        super().__init__()
        self.proxy_config = proxy_config
        
    def run(self):
        """Запуск тестування"""
        try:
            start_time = time.time()
            
            # Налаштовуємо проксі для requests
            proxies = {}
            
            if self.proxy_config['type'] == 'HTTP':
                proxy_url = f"http://{self.proxy_config['host']}:{self.proxy_config['port']}"
                if self.proxy_config.get('username') and self.proxy_config.get('password'):
                    proxy_url = f"http://{self.proxy_config['username']}:{self.proxy_config['password']}@{self.proxy_config['host']}:{self.proxy_config['port']}"
                    
                proxies = {
                    'http': proxy_url,
                    'https': proxy_url
                }
                
            elif self.proxy_config['type'] == 'SOCKS5':
                proxy_url = f"socks5://{self.proxy_config['host']}:{self.proxy_config['port']}"
                if self.proxy_config.get('username') and self.proxy_config.get('password'):
                    proxy_url = f"socks5://{self.proxy_config['username']}:{self.proxy_config['password']}@{self.proxy_config['host']}:{self.proxy_config['port']}"
                    
                proxies = {
                    'http': proxy_url,
                    'https': proxy_url
                }
            
            # Тестуємо проксі
            response = requests.get(
                'https://httpbin.org/ip',
                proxies=proxies,
                timeout=10
            )
            
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                ip = data.get('origin', 'Unknown')
                self.test_completed.emit(True, f'Успіх! IP: {ip}', response_time)
            else:
                self.test_completed.emit(False, f'Помилка: HTTP {response.status_code}', response_time)
                
        except Exception as e:
            response_time = time.time() - start_time
            self.test_completed.emit(False, f'Помилка: {str(e)}', response_time)


class ProxyManager(QObject):
    """Менеджер проксі"""
    
    proxy_status_changed = pyqtSignal(bool, str)  # enabled, message
    
    def __init__(self):
        super().__init__()
        self.current_proxy = None
        self.is_enabled = False
        self.original_proxy_factory = None
        
    def set_proxy(self, proxy_config: Dict[str, Any]) -> bool:
        """Встановлення проксі"""
        try:
            if not proxy_config or not proxy_config.get('host'):
                self.disable_proxy()
                return True
                
            # Створюємо Qt проксі
            qt_proxy = QNetworkProxy()
            
            if proxy_config['type'] == 'HTTP':
                qt_proxy.setType(QNetworkProxy.HttpProxy)
            elif proxy_config['type'] == 'SOCKS5':
                qt_proxy.setType(QNetworkProxy.Socks5Proxy)
            else:
                raise ValueError(f"Непідтримуваний тип проксі: {proxy_config['type']}")
                
            qt_proxy.setHostName(proxy_config['host'])
            qt_proxy.setPort(proxy_config['port'])
            
            if proxy_config.get('username') and proxy_config.get('password'):
                qt_proxy.setUser(proxy_config['username'])
                qt_proxy.setPassword(proxy_config['password'])
                
            # Встановлюємо проксі як глобальний
            QNetworkProxy.setApplicationProxy(qt_proxy)
            
            self.current_proxy = proxy_config
            self.is_enabled = True
            
            self.proxy_status_changed.emit(True, f"Проксі активовано: {proxy_config['host']}:{proxy_config['port']}")
            return True
            
        except Exception as e:
            self.proxy_status_changed.emit(False, f"Помилка встановлення проксі: {str(e)}")
            return False
            
    def disable_proxy(self):
        """Вимкнення проксі"""
        QNetworkProxy.setApplicationProxy(QNetworkProxy.NoProxy)
        self.current_proxy = None
        self.is_enabled = False
        self.proxy_status_changed.emit(False, "Проксі вимкнено")
        
    def test_proxy(self, proxy_config: Dict[str, Any]) -> ProxyTester:
        """Тестування проксі"""
        tester = ProxyTester(proxy_config)
        return tester
        
    def get_current_ip(self) -> Optional[str]:
        """Отримання поточного IP"""
        try:
            response = requests.get('https://httpbin.org/ip', timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get('origin')
        except Exception:
            pass
        return None
        
    def is_proxy_enabled(self) -> bool:
        """Перевірка чи активний проксі"""
        return self.is_enabled
        
    def get_current_proxy(self) -> Optional[Dict[str, Any]]:
        """Отримання поточного проксі"""
        return self.current_proxy


class ProxyRotator(QObject):
    """Ротатор проксі для автоматичної зміни"""
    
    proxy_rotated = pyqtSignal(dict)  # new_proxy
    
    def __init__(self, proxy_list: list, rotation_interval: int = 300):
        super().__init__()
        self.proxy_list = proxy_list
        self.current_index = 0
        self.rotation_interval = rotation_interval  # секунди
        
        # Таймер для ротації
        self.timer = QTimer()
        self.timer.timeout.connect(self.rotate_proxy)
        
    def start_rotation(self):
        """Запуск автоматичної ротації"""
        if self.proxy_list:
            self.timer.start(self.rotation_interval * 1000)  # переводимо в мілісекунди
            
    def stop_rotation(self):
        """Зупинка ротації"""
        self.timer.stop()
        
    def rotate_proxy(self):
        """Перемикання на наступний проксі"""
        if not self.proxy_list:
            return
            
        self.current_index = (self.current_index + 1) % len(self.proxy_list)
        current_proxy = self.proxy_list[self.current_index]
        self.proxy_rotated.emit(current_proxy)
        
    def add_proxy(self, proxy_config: Dict[str, Any]):
        """Додавання проксі до списку"""
        self.proxy_list.append(proxy_config)
        
    def remove_proxy(self, index: int):
        """Видалення проксі зі списку"""
        if 0 <= index < len(self.proxy_list):
            del self.proxy_list[index]
            if self.current_index >= len(self.proxy_list):
                self.current_index = 0
                
    def set_rotation_interval(self, seconds: int):
        """Встановлення інтервалу ротації"""
        self.rotation_interval = seconds
        if self.timer.isActive():
            self.timer.stop()
            self.timer.start(seconds * 1000)


def validate_proxy_config(config: Dict[str, Any]) -> tuple[bool, str]:
    """Валідація конфігурації проксі"""
    if not config:
        return False, "Порожня конфігурація"
        
    if not config.get('host'):
        return False, "Не вказано хост"
        
    if not config.get('port'):
        return False, "Не вказано порт"
        
    if not isinstance(config['port'], int) or not (1 <= config['port'] <= 65535):
        return False, "Невірний номер порту"
        
    if config.get('type') not in ['HTTP', 'SOCKS5']:
        return False, "Невірний тип проксі"
        
    return True, "Конфігурація валідна"


def create_proxy_config(host: str, port: int, proxy_type: str = 'HTTP', 
                       username: str = '', password: str = '') -> Dict[str, Any]:
    """Створення конфігурації проксі"""
    return {
        'host': host,
        'port': port,
        'type': proxy_type,
        'username': username,
        'password': password
    }

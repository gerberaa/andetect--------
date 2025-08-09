#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Модуль інтеграції з Tor для AnDetect Browser
Забезпечує анонімне підключення через мережу Tor
"""

import os
import sys
import time
import subprocess
import socket
import socks
import requests
from typing import Optional, Dict, Any

from PyQt5.QtCore import QObject, QThread, pyqtSignal, QTimer
from PyQt5.QtWidgets import QMessageBox

try:
    import stem
    from stem import Signal
    from stem.control import Controller
    STEM_AVAILABLE = True
except ImportError:
    STEM_AVAILABLE = False


class TorController(QObject):
    """Контролер для управління Tor"""
    
    status_changed = pyqtSignal(str)  # Сигнал зміни статусу
    connection_established = pyqtSignal()
    connection_failed = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tor_process = None
        self.controller = None
        self.is_connected = False
        self.tor_port = 9050
        self.control_port = 9051
        self.control_password = None
        
        # Таймер для перевірки статусу
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.check_status)
    
    def start_tor(self, tor_executable_path: Optional[str] = None) -> bool:
        """Запуск Tor процесу"""
        try:
            # Пошук Tor executable
            if not tor_executable_path:
                tor_executable_path = self.find_tor_executable()
            
            if not tor_executable_path:
                self.connection_failed.emit("Tor executable not found")
                return False
            
            # Створення конфігурації
            config = self.create_tor_config()
            
            # Запуск Tor
            self.status_changed.emit("Запуск Tor...")
            
            cmd = [
                tor_executable_path,
                '--SocksPort', str(self.tor_port),
                '--ControlPort', str(self.control_port),
                '--DataDirectory', self.get_tor_data_dir(),
                '--CookieAuthentication', '1',
                '--HashedControlPassword', self.get_hashed_password() if self.control_password else '',
            ]
            
            # Видаляємо порожні аргументи
            cmd = [arg for arg in cmd if arg]
            
            self.tor_process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            # Очікування запуску
            for _ in range(30):  # 30 секунд максимум
                if self.is_tor_running():
                    self.connect_to_controller()
                    return True
                time.sleep(1)
            
            self.connection_failed.emit("Tor failed to start")
            return False
            
        except Exception as e:
            self.connection_failed.emit(f"Error starting Tor: {str(e)}")
            return False
    
    def stop_tor(self):
        """Зупинка Tor"""
        try:
            self.status_changed.emit("Зупинка Tor...")
            
            if self.controller:
                self.controller.close()
                self.controller = None
            
            if self.tor_process:
                self.tor_process.terminate()
                self.tor_process.wait(timeout=10)
                self.tor_process = None
            
            self.is_connected = False
            self.status_changed.emit("Tor зупинено")
            
        except Exception as e:
            print(f"Error stopping Tor: {e}")
    
    def find_tor_executable(self) -> Optional[str]:
        """Пошук Tor executable"""
        possible_paths = []
        
        if os.name == 'nt':  # Windows
            possible_paths = [
                r"C:\Program Files\Tor Browser\Browser\TorBrowser\Tor\tor.exe",
                r"C:\Program Files (x86)\Tor Browser\Browser\TorBrowser\Tor\tor.exe",
                r"C:\Users\{}\AppData\Local\Tor Browser\Browser\TorBrowser\Tor\tor.exe".format(os.getenv('USERNAME')),
                r"tor.exe"
            ]
        else:  # Linux/macOS
            possible_paths = [
                "/usr/bin/tor",
                "/usr/local/bin/tor",
                "/opt/tor/bin/tor",
                "tor"
            ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
            
            # Спроба знайти в PATH
            try:
                result = subprocess.run(['which', 'tor'], capture_output=True, text=True)
                if result.returncode == 0:
                    return result.stdout.strip()
            except:
                pass
        
        return None
    
    def create_tor_config(self) -> Dict[str, Any]:
        """Створення конфігурації Tor"""
        return {
            'SocksPort': self.tor_port,
            'ControlPort': self.control_port,
            'DataDirectory': self.get_tor_data_dir(),
            'CookieAuthentication': True,
            'ExitNodes': '{US},{CA},{GB},{DE},{FR}',  # Обмежити країни виходу
            'StrictNodes': False,
            'NewCircuitPeriod': '30',  # Нове коло кожні 30 секунд
            'MaxCircuitDirtiness': '600',  # 10 хвилин
        }
    
    def get_tor_data_dir(self) -> str:
        """Отримання директорії даних Tor"""
        if os.name == 'nt':
            data_dir = os.path.join(os.getenv('APPDATA', ''), 'AnDetectBrowser', 'tor_data')
        else:
            data_dir = os.path.join(os.path.expanduser('~'), '.andetect_browser', 'tor_data')
        
        os.makedirs(data_dir, exist_ok=True)
        return data_dir
    
    def get_hashed_password(self) -> str:
        """Отримання хешованого паролю"""
        if not self.control_password:
            return ''
        
        # Простий хеш для демонстрації (в реальному застосунку використовуйте stem)
        import hashlib
        return hashlib.sha256(self.control_password.encode()).hexdigest()
    
    def is_tor_running(self) -> bool:
        """Перевірка чи працює Tor"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex(('127.0.0.1', self.tor_port))
            sock.close()
            return result == 0
        except:
            return False
    
    def connect_to_controller(self):
        """Підключення до контролера Tor"""
        if not STEM_AVAILABLE:
            self.status_changed.emit("Tor запущено (без stem)")
            self.is_connected = True
            self.connection_established.emit()
            return
        
        try:
            self.controller = Controller.from_port(port=self.control_port)
            
            # Аутентифікація
            try:
                self.controller.authenticate()
            except stem.connection.AuthenticationFailure:
                if self.control_password:
                    self.controller.authenticate(password=self.control_password)
                else:
                    raise
            
            self.is_connected = True
            self.status_changed.emit("Підключено до Tor")
            self.connection_established.emit()
            
            # Запуск моніторингу
            self.status_timer.start(5000)
            
        except Exception as e:
            self.connection_failed.emit(f"Failed to connect to Tor controller: {str(e)}")
    
    def new_identity(self) -> bool:
        """Створення нової ідентичності"""
        try:
            if self.controller and STEM_AVAILABLE:
                self.controller.signal(Signal.NEWNYM)
                self.status_changed.emit("Нова ідентичність створена")
                return True
            return False
        except Exception as e:
            print(f"Error creating new identity: {e}")
            return False
    
    def check_status(self):
        """Перевірка статусу Tor"""
        if not self.is_tor_running():
            self.is_connected = False
            self.status_changed.emit("Tor не підключено")
            self.status_timer.stop()
    
    def get_current_ip(self) -> Optional[str]:
        """Отримання поточного IP через Tor"""
        try:
            session = requests.Session()
            session.proxies = {
                'http': f'socks5://127.0.0.1:{self.tor_port}',
                'https': f'socks5://127.0.0.1:{self.tor_port}'
            }
            
            response = session.get('https://httpbin.org/ip', timeout=10)
            if response.status_code == 200:
                return response.json().get('origin')
            
        except Exception as e:
            print(f"Error getting IP: {e}")
        
        return None


class ProxyManager(QObject):
    """Менеджер проксі серверів"""
    
    status_changed = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.proxy_host = '127.0.0.1'
        self.proxy_port = 9050
        self.proxy_type = 'socks5'
        self.is_enabled = False
    
    def configure_proxy(self, host: str, port: int, proxy_type: str = 'socks5'):
        """Налаштування проксі"""
        self.proxy_host = host
        self.proxy_port = port
        self.proxy_type = proxy_type
    
    def enable_proxy(self) -> bool:
        """Увімкнення проксі"""
        try:
            if self.proxy_type == 'socks5':
                socks.set_default_proxy(socks.SOCKS5, self.proxy_host, self.proxy_port)
            elif self.proxy_type == 'socks4':
                socks.set_default_proxy(socks.SOCKS4, self.proxy_host, self.proxy_port)
            elif self.proxy_type == 'http':
                socks.set_default_proxy(socks.HTTP, self.proxy_host, self.proxy_port)
            
            socket.socket = socks.socksocket
            self.is_enabled = True
            self.status_changed.emit(f"Проксі увімкнено: {self.proxy_host}:{self.proxy_port}")
            return True
            
        except Exception as e:
            self.status_changed.emit(f"Помилка проксі: {str(e)}")
            return False
    
    def disable_proxy(self):
        """Вимкнення проксі"""
        try:
            socks.set_default_proxy()
            socket.socket = socks.socksocket
            self.is_enabled = False
            self.status_changed.emit("Проксі вимкнено")
        except Exception as e:
            print(f"Error disabling proxy: {e}")
    
    def test_proxy(self) -> bool:
        """Тестування проксі підключення"""
        try:
            session = requests.Session()
            session.proxies = {
                'http': f'{self.proxy_type}://{self.proxy_host}:{self.proxy_port}',
                'https': f'{self.proxy_type}://{self.proxy_host}:{self.proxy_port}'
            }
            
            response = session.get('https://httpbin.org/ip', timeout=10)
            return response.status_code == 200
            
        except Exception:
            return False


class AnonymityManager(QObject):
    """Менеджер анонімності"""
    
    status_changed = pyqtSignal(str)
    ip_changed = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tor_controller = TorController()
        self.proxy_manager = ProxyManager()
        self.current_ip = None
        
        # Підключення сигналів
        self.tor_controller.status_changed.connect(self.status_changed)
        self.tor_controller.connection_established.connect(self.on_tor_connected)
        self.proxy_manager.status_changed.connect(self.status_changed)
        
        # Таймер для перевірки IP
        self.ip_timer = QTimer()
        self.ip_timer.timeout.connect(self.check_ip)
    
    def enable_tor(self) -> bool:
        """Увімкнення Tor"""
        return self.tor_controller.start_tor()
    
    def disable_tor(self):
        """Вимкнення Tor"""
        self.tor_controller.stop_tor()
        self.ip_timer.stop()
    
    def enable_proxy(self, host: str, port: int, proxy_type: str = 'socks5') -> bool:
        """Увімкнення проксі"""
        self.proxy_manager.configure_proxy(host, port, proxy_type)
        return self.proxy_manager.enable_proxy()
    
    def disable_proxy(self):
        """Вимкнення проксі"""
        self.proxy_manager.disable_proxy()
    
    def new_identity(self) -> bool:
        """Створення нової ідентичності"""
        return self.tor_controller.new_identity()
    
    def on_tor_connected(self):
        """Обробка підключення до Tor"""
        self.check_ip()
        self.ip_timer.start(30000)  # Перевірка IP кожні 30 секунд
    
    def check_ip(self):
        """Перевірка поточного IP"""
        new_ip = self.tor_controller.get_current_ip()
        if new_ip and new_ip != self.current_ip:
            self.current_ip = new_ip
            self.ip_changed.emit(new_ip)
    
    def get_anonymity_status(self) -> Dict[str, Any]:
        """Отримання статусу анонімності"""
        return {
            'tor_connected': self.tor_controller.is_connected,
            'proxy_enabled': self.proxy_manager.is_enabled,
            'current_ip': self.current_ip,
            'tor_available': STEM_AVAILABLE
        }

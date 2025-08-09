#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Менеджер безпеки для AnDetect Browser
Включає антифішинг, блокування реклами та шкідливих сайтів
"""

import os
import json
import sqlite3
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Set, Optional
from urllib.parse import urlparse
from PyQt5.QtCore import QObject, pyqtSignal, QThread, QTimer
import re


class SecurityDatabase:
    """База даних безпеки"""
    
    def __init__(self, data_dir: str):
        self.data_dir = data_dir
        self.db_path = os.path.join(data_dir, "security.db")
        self.init_database()
        
    def init_database(self):
        """Ініціалізація бази даних безпеки"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Таблиця шкідливих доменів
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS malware_domains (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    domain TEXT UNIQUE NOT NULL,
                    category TEXT NOT NULL,
                    added_at TEXT NOT NULL,
                    source TEXT
                )
            """)
            
            # Таблиця рекламних доменів
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ad_domains (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    domain TEXT UNIQUE NOT NULL,
                    category TEXT NOT NULL,
                    added_at TEXT NOT NULL
                )
            """)
            
            # Таблиця трекерів
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tracking_domains (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    domain TEXT UNIQUE NOT NULL,
                    company TEXT,
                    added_at TEXT NOT NULL
                )
            """)
            
            # Таблиця білого списку
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS whitelist_domains (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    domain TEXT UNIQUE NOT NULL,
                    added_at TEXT NOT NULL,
                    added_by_user BOOLEAN DEFAULT 1
                )
            """)
            
            # Індекси
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_malware_domain ON malware_domains(domain)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_ad_domain ON ad_domains(domain)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tracking_domain ON tracking_domains(domain)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_whitelist_domain ON whitelist_domains(domain)")
            
            conn.commit()
            
    def add_malware_domain(self, domain: str, category: str, source: str = "manual"):
        """Додавання шкідливого домену"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO malware_domains (domain, category, added_at, source)
                VALUES (?, ?, ?, ?)
            """, (domain, category, datetime.now().isoformat(), source))
            conn.commit()
            
    def is_malware_domain(self, domain: str) -> tuple[bool, str]:
        """Перевірка чи домен є шкідливим"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT category FROM malware_domains WHERE domain = ?", (domain,))
            row = cursor.fetchone()
            return (True, row[0]) if row else (False, "")
            
    def add_ad_domain(self, domain: str, category: str = "ads"):
        """Додавання рекламного домену"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO ad_domains (domain, category, added_at)
                VALUES (?, ?, ?)
            """, (domain, category, datetime.now().isoformat()))
            conn.commit()
            
    def is_ad_domain(self, domain: str) -> bool:
        """Перевірка чи домен є рекламним"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM ad_domains WHERE domain = ?", (domain,))
            return cursor.fetchone() is not None
            
    def add_tracking_domain(self, domain: str, company: str = ""):
        """Додавання трекінгового домену"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO tracking_domains (domain, company, added_at)
                VALUES (?, ?, ?)
            """, (domain, company, datetime.now().isoformat()))
            conn.commit()
            
    def is_tracking_domain(self, domain: str) -> bool:
        """Перевірка чи домен є трекінговим"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM tracking_domains WHERE domain = ?", (domain,))
            return cursor.fetchone() is not None
            
    def add_to_whitelist(self, domain: str):
        """Додавання домену в білий список"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO whitelist_domains (domain, added_at)
                VALUES (?, ?)
            """, (domain, datetime.now().isoformat()))
            conn.commit()
            
    def is_whitelisted(self, domain: str) -> bool:
        """Перевірка чи домен в білому списку"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM whitelist_domains WHERE domain = ?", (domain,))
            return cursor.fetchone() is not None


class SecurityListUpdater(QThread):
    """Потік для оновлення списків безпеки"""
    
    update_completed = pyqtSignal(str, int)  # list_type, count
    update_failed = pyqtSignal(str, str)  # list_type, error
    
    def __init__(self, security_db: SecurityDatabase):
        super().__init__()
        self.security_db = security_db
        
    def run(self):
        """Запуск оновлення"""
        try:
            self.update_malware_list()
            self.update_ad_list()
            self.update_tracking_list()
        except Exception as e:
            self.update_failed.emit("all", str(e))
            
    def update_malware_list(self):
        """Оновлення списку шкідливих доменів"""
        try:
            # Malware Domain List
            url = "https://malware-filter.gitlab.io/malware-filter/malware-filter-domains.txt"
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                count = 0
                for line in response.text.split('\n'):
                    line = line.strip()
                    if line and not line.startswith('#') and not line.startswith('!'):
                        domain = line.replace('0.0.0.0 ', '').replace('127.0.0.1 ', '')
                        if domain and '.' in domain:
                            self.security_db.add_malware_domain(domain, "malware", "malware-filter")
                            count += 1
                            
                self.update_completed.emit("malware", count)
            else:
                self.update_failed.emit("malware", f"HTTP {response.status_code}")
                
        except Exception as e:
            self.update_failed.emit("malware", str(e))
            
    def update_ad_list(self):
        """Оновлення списку рекламних доменів"""
        try:
            # EasyList
            url = "https://easylist.to/easylist/easylist.txt"
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                count = 0
                for line in response.text.split('\n'):
                    line = line.strip()
                    if line and not line.startswith('[') and not line.startswith('!'):
                        # Вилучаємо домени з AdBlock правил
                        if '||' in line and '^' in line:
                            domain = line.split('||')[1].split('^')[0]
                            if domain and '.' in domain and not domain.startswith('*'):
                                self.security_db.add_ad_domain(domain, "ads")
                                count += 1
                                
                self.update_completed.emit("ads", count)
            else:
                self.update_failed.emit("ads", f"HTTP {response.status_code}")
                
        except Exception as e:
            self.update_failed.emit("ads", str(e))
            
    def update_tracking_list(self):
        """Оновлення списку трекерів"""
        try:
            # EasyPrivacy
            url = "https://easylist.to/easylist/easyprivacy.txt"
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                count = 0
                for line in response.text.split('\n'):
                    line = line.strip()
                    if line and not line.startswith('[') and not line.startswith('!'):
                        if '||' in line and '^' in line:
                            domain = line.split('||')[1].split('^')[0]
                            if domain and '.' in domain and not domain.startswith('*'):
                                self.security_db.add_tracking_domain(domain, "tracker")
                                count += 1
                                
                self.update_completed.emit("tracking", count)
            else:
                self.update_failed.emit("tracking", f"HTTP {response.status_code}")
                
        except Exception as e:
            self.update_failed.emit("tracking", str(e))


class SecurityManager(QObject):
    """Менеджер безпеки браузера"""
    
    threat_detected = pyqtSignal(str, str, str)  # url, threat_type, description
    request_blocked = pyqtSignal(str, str)  # url, reason
    security_status_changed = pyqtSignal(str)  # status
    
    def __init__(self, data_dir: str):
        super().__init__()
        self.data_dir = data_dir
        self.security_db = SecurityDatabase(data_dir)
        
        # Налаштування
        self.ad_blocking_enabled = True
        self.malware_protection_enabled = True
        self.tracking_protection_enabled = True
        self.phishing_protection_enabled = True
        
        # Кеш для швидкого доступу
        self.domain_cache = {}
        self.cache_expiry = datetime.now() + timedelta(hours=1)
        
        # Автоматичне оновлення
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.auto_update_lists)
        self.update_timer.start(24 * 60 * 60 * 1000)  # 24 години
        
        # Завантажуємо базові списки
        self.load_default_lists()
        
    def load_default_lists(self):
        """Завантаження базових списків безпеки"""
        # Основні рекламні домени
        ad_domains = [
            'googlesyndication.com', 'doubleclick.net', 'googleadservices.com',
            'amazon-adsystem.com', 'facebook.com/tr', 'outbrain.com',
            'taboola.com', 'adsystem.amazon.com', 'ads.twitter.com'
        ]
        
        for domain in ad_domains:
            self.security_db.add_ad_domain(domain, "ads")
            
        # Основні трекери
        tracking_domains = [
            'google-analytics.com', 'googletagmanager.com', 'hotjar.com',
            'mixpanel.com', 'segment.com', 'fullstory.com', 'mouseflow.com',
            'crazyegg.com', 'quantserve.com'
        ]
        
        for domain in tracking_domains:
            self.security_db.add_tracking_domain(domain, "analytics")
            
    def check_url_security(self, url: str) -> Dict[str, any]:
        """Комплексна перевірка безпеки URL"""
        result = {
            'safe': True,
            'blocked': False,
            'threats': [],
            'blocked_reason': ''
        }
        
        try:
            parsed_url = urlparse(url)
            domain = parsed_url.netloc.lower()
            
            # Видаляємо www.
            if domain.startswith('www.'):
                domain = domain[4:]
                
            # Перевірка білого списку
            if self.security_db.is_whitelisted(domain):
                return result
                
            # Перевірка кешу
            if domain in self.domain_cache and datetime.now() < self.cache_expiry:
                cached_result = self.domain_cache[domain]
                if cached_result['blocked']:
                    result.update(cached_result)
                    return result
                    
            # Перевірка шкідливих доменів
            if self.malware_protection_enabled:
                is_malware, category = self.security_db.is_malware_domain(domain)
                if is_malware:
                    result['safe'] = False
                    result['blocked'] = True
                    result['threats'].append(f'Шкідливий сайт ({category})')
                    result['blocked_reason'] = 'malware'
                    
            # Перевірка реклами
            if self.ad_blocking_enabled and self.security_db.is_ad_domain(domain):
                result['blocked'] = True
                result['blocked_reason'] = 'ads'
                
            # Перевірка трекерів
            if self.tracking_protection_enabled and self.security_db.is_tracking_domain(domain):
                result['blocked'] = True
                result['blocked_reason'] = 'tracking'
                
            # Перевірка фішингу
            if self.phishing_protection_enabled:
                if self.is_potential_phishing(url, domain):
                    result['safe'] = False
                    result['blocked'] = True
                    result['threats'].append('Підозра на фішинг')
                    result['blocked_reason'] = 'phishing'
                    
            # Зберігаємо в кеш
            self.domain_cache[domain] = result.copy()
            
        except Exception as e:
            print(f"Помилка перевірки безпеки URL {url}: {e}")
            
        return result
        
    def is_potential_phishing(self, url: str, domain: str) -> bool:
        """Перевірка на потенційний фішинг"""
        # Список популярних сайтів для перевірки на фішинг
        legitimate_domains = {
            'google.com', 'facebook.com', 'amazon.com', 'microsoft.com',
            'apple.com', 'paypal.com', 'ebay.com', 'instagram.com',
            'twitter.com', 'linkedin.com', 'github.com', 'stackoverflow.com'
        }
        
        # Перевірка на схожість з популярними доменами
        for legit_domain in legitimate_domains:
            if self.is_domain_suspicious(domain, legit_domain):
                return True
                
        # Перевірка на підозрілі символи
        suspicious_chars = ['0', '1', 'l', 'i', 'o']
        for char in suspicious_chars:
            if char in domain and any(legit in domain for legit in legitimate_domains):
                return True
                
        # Перевірка на довгі домени з багатьма субдоменами
        if domain.count('.') > 3:
            return True
            
        # Перевірка на IP-адреси замість доменів
        if re.match(r'^\d+\.\d+\.\d+\.\d+', domain):
            return True
            
        return False
        
    def is_domain_suspicious(self, domain: str, legitimate: str) -> bool:
        """Перевірка схожості доменів"""
        # Левенштейнова відстань
        def levenshtein_distance(s1, s2):
            if len(s1) < len(s2):
                return levenshtein_distance(s2, s1)
                
            if len(s2) == 0:
                return len(s1)
                
            previous_row = range(len(s2) + 1)
            for i, c1 in enumerate(s1):
                current_row = [i + 1]
                for j, c2 in enumerate(s2):
                    insertions = previous_row[j + 1] + 1
                    deletions = current_row[j] + 1
                    substitutions = previous_row[j] + (c1 != c2)
                    current_row.append(min(insertions, deletions, substitutions))
                previous_row = current_row
                
            return previous_row[-1]
            
        distance = levenshtein_distance(domain, legitimate)
        threshold = min(len(legitimate) * 0.3, 3)  # 30% від довжини або максимум 3 символи
        
        return distance <= threshold and domain != legitimate
        
    def should_block_request(self, url: str) -> tuple[bool, str]:
        """Перевірка чи потрібно блокувати запит"""
        result = self.check_url_security(url)
        
        if result['blocked']:
            reason = result['blocked_reason']
            self.request_blocked.emit(url, reason)
            return True, reason
            
        if not result['safe']:
            threat_desc = ', '.join(result['threats'])
            self.threat_detected.emit(url, 'security', threat_desc)
            return True, 'security_threat'
            
        return False, ''
        
    def add_to_whitelist(self, domain: str):
        """Додавання домену в білий список"""
        parsed_domain = urlparse(f"http://{domain}").netloc.lower()
        if parsed_domain.startswith('www.'):
            parsed_domain = parsed_domain[4:]
            
        self.security_db.add_to_whitelist(parsed_domain)
        
        # Очищаємо кеш для цього домену
        if parsed_domain in self.domain_cache:
            del self.domain_cache[parsed_domain]
            
    def remove_from_whitelist(self, domain: str):
        """Видалення домену з білого списку"""
        # TODO: Додати метод видалення з білого списку в SecurityDatabase
        pass
        
    def update_security_lists(self):
        """Оновлення списків безпеки"""
        updater = SecurityListUpdater(self.security_db)
        updater.update_completed.connect(self.on_lists_updated)
        updater.update_failed.connect(self.on_update_failed)
        updater.start()
        
        self.security_status_changed.emit("Оновлення списків безпеки...")
        
    def on_lists_updated(self, list_type: str, count: int):
        """Обробка успішного оновлення списків"""
        self.security_status_changed.emit(f"Оновлено {list_type}: {count} записів")
        
        # Очищаємо кеш після оновлення
        self.domain_cache.clear()
        self.cache_expiry = datetime.now() + timedelta(hours=1)
        
    def on_update_failed(self, list_type: str, error: str):
        """Обробка помилки оновлення"""
        self.security_status_changed.emit(f"Помилка оновлення {list_type}: {error}")
        
    def auto_update_lists(self):
        """Автоматичне оновлення списків"""
        self.update_security_lists()
        
    def get_security_stats(self) -> Dict[str, int]:
        """Отримання статистики безпеки"""
        with sqlite3.connect(self.security_db.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM malware_domains")
            malware_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM ad_domains")
            ad_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM tracking_domains")
            tracking_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM whitelist_domains")
            whitelist_count = cursor.fetchone()[0]
            
        return {
            'malware_domains': malware_count,
            'ad_domains': ad_count,
            'tracking_domains': tracking_count,
            'whitelisted_domains': whitelist_count
        }
        
    def enable_ad_blocking(self, enabled: bool):
        """Увімкнення/вимкнення блокування реклами"""
        self.ad_blocking_enabled = enabled
        self.domain_cache.clear()
        
    def enable_malware_protection(self, enabled: bool):
        """Увімкнення/вимкнення захисту від шкідливих сайтів"""
        self.malware_protection_enabled = enabled
        self.domain_cache.clear()
        
    def enable_tracking_protection(self, enabled: bool):
        """Увімкнення/вимкнення захисту від трекінгу"""
        self.tracking_protection_enabled = enabled
        self.domain_cache.clear()
        
    def enable_phishing_protection(self, enabled: bool):
        """Увімкнення/вимкнення захисту від фішингу"""
        self.phishing_protection_enabled = enabled
        self.domain_cache.clear()

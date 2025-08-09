
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Менеджер профілів для AnDetect Browser
Керує створенням, збереженням та завантаженням профілів браузера
"""

import os
import json
import sqlite3
import uuid
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from cryptography.fernet import Fernet
import random


@dataclass
class BrowserProfile:
    """Клас для представлення профілю браузера"""
    id: str
    name: str
    user_agent: str
    screen_width: int
    screen_height: int
    timezone: str
    language: str
    proxy_host: str = ""
    proxy_port: int = 0
    proxy_username: str = ""
    proxy_password: str = ""
    proxy_type: str = "HTTP"  # HTTP, SOCKS5
    canvas_fingerprint: str = ""
    webgl_fingerprint: str = ""
    created_at: str = ""
    last_used: str = ""
    cookies_enabled: bool = True
    javascript_enabled: bool = True
    images_enabled: bool = True
    plugins_enabled: bool = True
    geolocation_enabled: bool = False
    notifications_enabled: bool = False
    webrtc_enabled: bool = False
    
    # Нові поля для міток та іконок
    icon_type: str = "default"  # Тип іконки профілю
    country_code: str = "UA"    # Код країни для прапорця
    label_color: str = "blue"   # Колір мітки
    tags: str = ""              # Теги через кому
    description: str = ""       # Опис профілю
    favorite: bool = False      # Улюблений профіль
    last_ip: str = ""          # Останній IP адрес
    usage_count: int = 0       # Кількість використань
    total_time: int = 0        # Загальний час використання (секунди)
    status: str = "active"     # Статус: active, inactive, blocked
    notes: str = ""            # Нотатки користувача
    
    def to_dict(self):
        """Конвертація в словник"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict):
        """Створення з словника"""
        return cls(**data)


class ProfileManager:
    """Менеджер профілів браузера"""
    
    def __init__(self, data_dir: str = None):
        if data_dir is None:
            data_dir = os.path.join(os.path.expanduser("~"), "AnDetectBrowser")
            
        self.data_dir = data_dir
        self.profiles_dir = os.path.join(data_dir, "profiles")
        self.db_path = os.path.join(data_dir, "profiles.db")
        
        # Створюємо директорії
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.profiles_dir, exist_ok=True)
        
        # Ініціалізуємо базу даних
        self.init_database()
        
        # Генеруємо ключ шифрування
        self.encryption_key = self.get_or_create_encryption_key()
        self.cipher = Fernet(self.encryption_key)
        
    def get_or_create_encryption_key(self) -> bytes:
        """Отримання або створення ключа шифрування"""
        key_path = os.path.join(self.data_dir, "encryption.key")
        
        if os.path.exists(key_path):
            with open(key_path, "rb") as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(key_path, "wb") as f:
                f.write(key)
            return key
            
    def init_database(self):
        """Ініціалізація бази даних"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Таблиця профілів
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS profiles (
                    id TEXT PRIMARY KEY,
                    name TEXT UNIQUE NOT NULL,
                    data TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    last_used TEXT NOT NULL
                )
            """)
            
            # Таблиця cookies
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cookies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    profile_id TEXT NOT NULL,
                    domain TEXT NOT NULL,
                    name TEXT NOT NULL,
                    value TEXT NOT NULL,
                    path TEXT DEFAULT '/',
                    expires INTEGER,
                    secure BOOLEAN DEFAULT 0,
                    http_only BOOLEAN DEFAULT 0,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (profile_id) REFERENCES profiles (id)
                )
            """)
            
            # Таблиця сесій
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    profile_id TEXT NOT NULL,
                    tab_data TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (profile_id) REFERENCES profiles (id)
                )
            """)
            
            conn.commit()
            
    def generate_random_profile_data(self) -> Dict:
        """Генерація випадкових даних для профілю"""
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        ]
        
        screen_resolutions = [
            (1920, 1080), (1366, 768), (1440, 900), (1600, 900), (1280, 1024)
        ]
        
        timezones = [
            "Europe/Kiev", "Europe/London", "Europe/Berlin", "America/New_York", "America/Los_Angeles"
        ]
        
        languages = [
            "uk-UA,uk;q=0.9,en;q=0.8", "en-US,en;q=0.9", "en-GB,en;q=0.9", "de-DE,de;q=0.9"
        ]
        
        width, height = random.choice(screen_resolutions)
        
        return {
            'user_agent': random.choice(user_agents),
            'screen_width': width,
            'screen_height': height,
            'timezone': random.choice(timezones),
            'language': random.choice(languages),
            'canvas_fingerprint': str(uuid.uuid4()),
            'webgl_fingerprint': str(uuid.uuid4()),
        }
        
    def create_profile(self, name: str, custom_data: Dict = None) -> BrowserProfile:
        """Створення нового профілю"""
        profile_id = str(uuid.uuid4())
        now = datetime.now().isoformat()
        
        # Генеруємо базові дані
        profile_data = self.generate_random_profile_data()
        
        # Додаємо кастомні дані якщо є
        if custom_data:
            # Видаляємо name з custom_data щоб уникнути конфлікту
            custom_data_copy = custom_data.copy()
            custom_data_copy.pop('name', None)
            profile_data.update(custom_data_copy)
            
        # Створюємо профіль
        profile = BrowserProfile(
            id=profile_id,
            name=name,
            created_at=now,
            last_used=now,
            **profile_data
        )
        
        # Зберігаємо в базу даних
        encrypted_data = self.cipher.encrypt(json.dumps(profile.to_dict()).encode())
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO profiles (id, name, data, created_at, last_used) VALUES (?, ?, ?, ?, ?)",
                (profile_id, name, encrypted_data.decode(), now, now)
            )
            conn.commit()
            
        # Створюємо директорію для профілю
        profile_dir = os.path.join(self.profiles_dir, profile_id)
        os.makedirs(profile_dir, exist_ok=True)
        
        return profile
        
    def get_profile_by_id(self, profile_id: str) -> Optional[BrowserProfile]:
        """Отримання профілю за ID"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT data FROM profiles WHERE id = ?", (profile_id,))
            row = cursor.fetchone()
            
            if row:
                encrypted_data = row[0].encode()
                decrypted_data = self.cipher.decrypt(encrypted_data)
                profile_data = json.loads(decrypted_data.decode())
                return BrowserProfile.from_dict(profile_data)
                
        return None
        
    def get_profile_by_name(self, name: str) -> Optional[BrowserProfile]:
        """Отримання профілю за ім'ям"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT data FROM profiles WHERE name = ?", (name,))
            row = cursor.fetchone()
            
            if row:
                encrypted_data = row[0].encode()
                decrypted_data = self.cipher.decrypt(encrypted_data)
                profile_data = json.loads(decrypted_data.decode())
                return BrowserProfile.from_dict(profile_data)
                
        return None
        
    def get_all_profiles(self) -> List[BrowserProfile]:
        """Отримання всіх профілів"""
        profiles = []
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT data FROM profiles ORDER BY last_used DESC")
            rows = cursor.fetchall()
            
            for row in rows:
                encrypted_data = row[0].encode()
                decrypted_data = self.cipher.decrypt(encrypted_data)
                profile_data = json.loads(decrypted_data.decode())
                profiles.append(BrowserProfile.from_dict(profile_data))
                
        return profiles
        
    def update_profile(self, profile_id: str, updated_data: Dict):
        """Оновлення профілю"""
        profile = self.get_profile_by_id(profile_id)
        if not profile:
            return False
            
        # Оновлюємо дані
        for key, value in updated_data.items():
            if hasattr(profile, key):
                setattr(profile, key, value)
                
        profile.last_used = datetime.now().isoformat()
        
        # Зберігаємо в базу
        encrypted_data = self.cipher.encrypt(json.dumps(profile.to_dict()).encode())
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE profiles SET data = ?, last_used = ? WHERE id = ?",
                (encrypted_data.decode(), profile.last_used, profile_id)
            )
            conn.commit()
            
        return True
        
    def delete_profile(self, profile_id: str) -> bool:
        """Видалення профілю"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Видаляємо cookies
            cursor.execute("DELETE FROM cookies WHERE profile_id = ?", (profile_id,))
            
            # Видаляємо сесії
            cursor.execute("DELETE FROM sessions WHERE profile_id = ?", (profile_id,))
            
            # Видаляємо профіль
            cursor.execute("DELETE FROM profiles WHERE id = ?", (profile_id,))
            
            conn.commit()
            
        # Видаляємо директорію профілю
        profile_dir = os.path.join(self.profiles_dir, profile_id)
        if os.path.exists(profile_dir):
            import shutil
            shutil.rmtree(profile_dir)
            
        return True
        
    def save_cookies(self, profile_id: str, cookies: List[Dict]):
        """Збереження cookies для профілю"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Очищаємо старі cookies
            cursor.execute("DELETE FROM cookies WHERE profile_id = ?", (profile_id,))
            
            # Зберігаємо нові cookies
            now = datetime.now().isoformat()
            for cookie in cookies:
                cursor.execute("""
                    INSERT INTO cookies 
                    (profile_id, domain, name, value, path, expires, secure, http_only, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    profile_id,
                    cookie.get('domain', ''),
                    cookie.get('name', ''),
                    cookie.get('value', ''),
                    cookie.get('path', '/'),
                    cookie.get('expires', 0),
                    cookie.get('secure', False),
                    cookie.get('httpOnly', False),
                    now
                ))
                
            conn.commit()
            
    def load_cookies(self, profile_id: str) -> List[Dict]:
        """Завантаження cookies для профілю"""
        cookies = []
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT domain, name, value, path, expires, secure, http_only
                FROM cookies WHERE profile_id = ?
            """, (profile_id,))
            
            rows = cursor.fetchall()
            for row in rows:
                cookies.append({
                    'domain': row[0],
                    'name': row[1],
                    'value': row[2],
                    'path': row[3],
                    'expires': row[4],
                    'secure': bool(row[5]),
                    'httpOnly': bool(row[6])
                })
                
        return cookies
        
    def save_session(self, profile_id: str, tab_data: List[Dict]):
        """Збереження сесії (відкритих вкладок)"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Очищаємо стару сесію
            cursor.execute("DELETE FROM sessions WHERE profile_id = ?", (profile_id,))
            
            # Зберігаємо нову сесію
            now = datetime.now().isoformat()
            encrypted_data = self.cipher.encrypt(json.dumps(tab_data).encode())
            
            cursor.execute(
                "INSERT INTO sessions (profile_id, tab_data, created_at) VALUES (?, ?, ?)",
                (profile_id, encrypted_data.decode(), now)
            )
            
            conn.commit()
            
    def load_session(self, profile_id: str) -> List[Dict]:
        """Завантаження сесії"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT tab_data FROM sessions WHERE profile_id = ? ORDER BY created_at DESC LIMIT 1",
                (profile_id,)
            )
            
            row = cursor.fetchone()
            if row:
                encrypted_data = row[0].encode()
                decrypted_data = self.cipher.decrypt(encrypted_data)
                return json.loads(decrypted_data.decode())
                
        return []
        
    def get_profile_directory(self, profile_id: str) -> str:
        """Отримання директорії профілю"""
        return os.path.join(self.profiles_dir, profile_id)


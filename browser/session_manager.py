<<<<<<< HEAD
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Менеджер сесій для AnDetect Browser
Керує збереженням cookies, історії та відновленням сесій
"""

import os
import json
import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from PyQt5.QtCore import QObject, pyqtSignal, QUrl, QByteArray
from PyQt5.QtWebEngineCore import QWebEngineCookieStore, QWebEngineProfile
from PyQt5.QtNetwork import QNetworkCookie


class SessionManager(QObject):
    """Менеджер сесій браузера"""
    
    session_saved = pyqtSignal(str)  # profile_id
    session_restored = pyqtSignal(str, list)  # profile_id, tabs
    cookies_saved = pyqtSignal(str, int)  # profile_id, count
    cookies_restored = pyqtSignal(str, int)  # profile_id, count
    
    def __init__(self, profile_manager):
        super().__init__()
        self.profile_manager = profile_manager
        self.data_dir = profile_manager.data_dir
        self.sessions_dir = os.path.join(self.data_dir, "sessions")
        self.cookies_dir = os.path.join(self.data_dir, "cookies")
        
        # Створюємо директорії
        os.makedirs(self.sessions_dir, exist_ok=True)
        os.makedirs(self.cookies_dir, exist_ok=True)
        
        # Ініціалізуємо базу даних
        self.init_database()
        
    def init_database(self):
        """Ініціалізація бази даних сесій"""
        db_path = os.path.join(self.data_dir, "sessions.db")
        
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Таблиця сесій
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS browser_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    profile_id TEXT NOT NULL,
                    session_name TEXT,
                    tabs_data TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    last_accessed TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT 0
                )
            """)
            
            # Таблиця історії
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS browsing_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    profile_id TEXT NOT NULL,
                    url TEXT NOT NULL,
                    title TEXT,
                    visit_time TEXT NOT NULL,
                    visit_count INTEGER DEFAULT 1
                )
            """)
            
            # Таблиця збережених cookies
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS saved_cookies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    profile_id TEXT NOT NULL,
                    domain TEXT NOT NULL,
                    name TEXT NOT NULL,
                    value TEXT NOT NULL,
                    path TEXT DEFAULT '/',
                    expires_at TEXT,
                    is_secure BOOLEAN DEFAULT 0,
                    is_http_only BOOLEAN DEFAULT 0,
                    same_site TEXT DEFAULT 'Lax',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            
            # Індекси для швидкого пошуку
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_profile ON browser_sessions(profile_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_history_profile ON browsing_history(profile_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_cookies_profile ON saved_cookies(profile_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_cookies_domain ON saved_cookies(domain)")
            
            conn.commit()
            
    def save_session(self, profile_id: str, tabs_data: List[Dict], session_name: str = None) -> bool:
        """Збереження поточної сесії"""
        try:
            if not session_name:
                session_name = f"Сесія {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                
            now = datetime.now().isoformat()
            tabs_json = json.dumps(tabs_data, ensure_ascii=False)
            
            db_path = os.path.join(self.data_dir, "sessions.db")
            
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                
                # Деактивуємо попередні активні сесії
                cursor.execute(
                    "UPDATE browser_sessions SET is_active = 0 WHERE profile_id = ?",
                    (profile_id,)
                )
                
                # Зберігаємо нову сесію
                cursor.execute("""
                    INSERT INTO browser_sessions 
                    (profile_id, session_name, tabs_data, created_at, last_accessed, is_active)
                    VALUES (?, ?, ?, ?, ?, 1)
                """, (profile_id, session_name, tabs_json, now, now))
                
                conn.commit()
                
            self.session_saved.emit(profile_id)
            return True
            
        except Exception as e:
            print(f"Помилка збереження сесії: {e}")
            return False
            
    def restore_session(self, profile_id: str, session_id: int = None) -> Optional[List[Dict]]:
        """Відновлення сесії"""
        try:
            db_path = os.path.join(self.data_dir, "sessions.db")
            
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                
                if session_id:
                    # Відновлюємо конкретну сесію
                    cursor.execute(
                        "SELECT tabs_data FROM browser_sessions WHERE id = ? AND profile_id = ?",
                        (session_id, profile_id)
                    )
                else:
                    # Відновлюємо останню активну сесію
                    cursor.execute("""
                        SELECT tabs_data FROM browser_sessions 
                        WHERE profile_id = ? AND is_active = 1
                        ORDER BY last_accessed DESC LIMIT 1
                    """, (profile_id,))
                    
                row = cursor.fetchone()
                if row:
                    tabs_data = json.loads(row[0])
                    
                    # Оновлюємо час останнього доступу
                    now = datetime.now().isoformat()
                    if session_id:
                        cursor.execute(
                            "UPDATE browser_sessions SET last_accessed = ? WHERE id = ?",
                            (now, session_id)
                        )
                    else:
                        cursor.execute("""
                            UPDATE browser_sessions SET last_accessed = ? 
                            WHERE profile_id = ? AND is_active = 1
                        """, (now, profile_id))
                        
                    conn.commit()
                    
                    self.session_restored.emit(profile_id, tabs_data)
                    return tabs_data
                    
        except Exception as e:
            print(f"Помилка відновлення сесії: {e}")
            
        return None
        
    def get_sessions(self, profile_id: str) -> List[Dict]:
        """Отримання списку збережених сесій"""
        sessions = []
        
        try:
            db_path = os.path.join(self.data_dir, "sessions.db")
            
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, session_name, created_at, last_accessed, is_active
                    FROM browser_sessions WHERE profile_id = ?
                    ORDER BY last_accessed DESC
                """, (profile_id,))
                
                rows = cursor.fetchall()
                for row in rows:
                    sessions.append({
                        'id': row[0],
                        'name': row[1],
                        'created_at': row[2],
                        'last_accessed': row[3],
                        'is_active': bool(row[4])
                    })
                    
        except Exception as e:
            print(f"Помилка отримання сесій: {e}")
            
        return sessions
        
    def delete_session(self, session_id: int) -> bool:
        """Видалення сесії"""
        try:
            db_path = os.path.join(self.data_dir, "sessions.db")
            
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM browser_sessions WHERE id = ?", (session_id,))
                conn.commit()
                
            return cursor.rowcount > 0
            
        except Exception as e:
            print(f"Помилка видалення сесії: {e}")
            return False
            
    def save_cookies_from_store(self, profile_id: str, cookie_store: QWebEngineCookieStore):
        """Збереження cookies з cookie store"""
        self.cookies_to_save = []
        
        def on_cookie_added(cookie):
            self.cookies_to_save.append(cookie)
            
        # Отримуємо всі cookies
        cookie_store.cookieAdded.connect(on_cookie_added)
        
        # TODO: Реалізувати отримання всіх cookies
        # В Qt немає прямого способу отримати всі cookies
        # Потрібно використовувати JavaScript або інший метод
        
    def save_cookies(self, profile_id: str, cookies: List[Dict]) -> bool:
        """Збереження cookies вручну"""
        try:
            db_path = os.path.join(self.data_dir, "sessions.db")
            now = datetime.now().isoformat()
            
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                
                # Очищаємо старі cookies для профілю
                cursor.execute("DELETE FROM saved_cookies WHERE profile_id = ?", (profile_id,))
                
                # Зберігаємо нові cookies
                for cookie in cookies:
                    cursor.execute("""
                        INSERT INTO saved_cookies 
                        (profile_id, domain, name, value, path, expires_at, 
                         is_secure, is_http_only, same_site, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        profile_id,
                        cookie.get('domain', ''),
                        cookie.get('name', ''),
                        cookie.get('value', ''),
                        cookie.get('path', '/'),
                        cookie.get('expires'),
                        cookie.get('secure', False),
                        cookie.get('httpOnly', False),
                        cookie.get('sameSite', 'Lax'),
                        now,
                        now
                    ))
                    
                conn.commit()
                
            self.cookies_saved.emit(profile_id, len(cookies))
            return True
            
        except Exception as e:
            print(f"Помилка збереження cookies: {e}")
            return False
            
    def restore_cookies(self, profile_id: str) -> List[Dict]:
        """Відновлення cookies"""
        cookies = []
        
        try:
            db_path = os.path.join(self.data_dir, "sessions.db")
            
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT domain, name, value, path, expires_at, is_secure, is_http_only, same_site
                    FROM saved_cookies WHERE profile_id = ?
                """, (profile_id,))
                
                rows = cursor.fetchall()
                for row in rows:
                    # Перевіряємо чи cookie не протерміновані
                    expires_at = row[4]
                    if expires_at:
                        expires_datetime = datetime.fromisoformat(expires_at)
                        if expires_datetime < datetime.now():
                            continue  # Пропускаємо протерміновані cookies
                            
                    cookies.append({
                        'domain': row[0],
                        'name': row[1],
                        'value': row[2],
                        'path': row[3],
                        'expires': row[4],
                        'secure': bool(row[5]),
                        'httpOnly': bool(row[6]),
                        'sameSite': row[7]
                    })
                    
            self.cookies_restored.emit(profile_id, len(cookies))
            
        except Exception as e:
            print(f"Помилка відновлення cookies: {e}")
            
        return cookies
        
    def add_to_history(self, profile_id: str, url: str, title: str = ""):
        """Додавання запису в історію"""
        try:
            db_path = os.path.join(self.data_dir, "sessions.db")
            now = datetime.now().isoformat()
            
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                
                # Перевіряємо чи запис вже існує
                cursor.execute("""
                    SELECT id, visit_count FROM browsing_history 
                    WHERE profile_id = ? AND url = ?
                """, (profile_id, url))
                
                row = cursor.fetchone()
                if row:
                    # Оновлюємо існуючий запис
                    cursor.execute("""
                        UPDATE browsing_history 
                        SET visit_count = ?, visit_time = ?, title = ?
                        WHERE id = ?
                    """, (row[1] + 1, now, title, row[0]))
                else:
                    # Створюємо новий запис
                    cursor.execute("""
                        INSERT INTO browsing_history 
                        (profile_id, url, title, visit_time)
                        VALUES (?, ?, ?, ?)
                    """, (profile_id, url, title, now))
                    
                conn.commit()
                
        except Exception as e:
            print(f"Помилка додавання в історію: {e}")
            
    def get_history(self, profile_id: str, limit: int = 100) -> List[Dict]:
        """Отримання історії браузінгу"""
        history = []
        
        try:
            db_path = os.path.join(self.data_dir, "sessions.db")
            
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT url, title, visit_time, visit_count
                    FROM browsing_history WHERE profile_id = ?
                    ORDER BY visit_time DESC LIMIT ?
                """, (profile_id, limit))
                
                rows = cursor.fetchall()
                for row in rows:
                    history.append({
                        'url': row[0],
                        'title': row[1],
                        'visit_time': row[2],
                        'visit_count': row[3]
                    })
                    
        except Exception as e:
            print(f"Помилка отримання історії: {e}")
            
        return history
        
    def clear_history(self, profile_id: str, older_than_days: int = None) -> bool:
        """Очищення історії"""
        try:
            db_path = os.path.join(self.data_dir, "sessions.db")
            
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                
                if older_than_days:
                    # Видаляємо записи старші за вказану кількість днів
                    cutoff_date = (datetime.now() - timedelta(days=older_than_days)).isoformat()
                    cursor.execute("""
                        DELETE FROM browsing_history 
                        WHERE profile_id = ? AND visit_time < ?
                    """, (profile_id, cutoff_date))
                else:
                    # Видаляємо всю історію
                    cursor.execute("DELETE FROM browsing_history WHERE profile_id = ?", (profile_id,))
                    
                conn.commit()
                
            return True
            
        except Exception as e:
            print(f"Помилка очищення історії: {e}")
            return False
            
    def clear_cookies(self, profile_id: str) -> bool:
        """Очищення cookies"""
        try:
            db_path = os.path.join(self.data_dir, "sessions.db")
            
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM saved_cookies WHERE profile_id = ?", (profile_id,))
                conn.commit()
                
            return True
            
        except Exception as e:
            print(f"Помилка очищення cookies: {e}")
            return False
            
    def clear_sessions(self, profile_id: str) -> bool:
        """Очищення збережених сесій"""
        try:
            db_path = os.path.join(self.data_dir, "sessions.db")
            
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM browser_sessions WHERE profile_id = ?", (profile_id,))
                conn.commit()
                
            return True
            
        except Exception as e:
            print(f"Помилка очищення сесій: {e}")
            return False
=======
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Менеджер сесій для AnDetect Browser
Керує збереженням cookies, історії та відновленням сесій
"""

import os
import json
import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from PyQt5.QtCore import QObject, pyqtSignal, QUrl, QByteArray
from PyQt5.QtWebEngineCore import QWebEngineCookieStore, QWebEngineProfile
from PyQt5.QtNetwork import QNetworkCookie


class SessionManager(QObject):
    """Менеджер сесій браузера"""
    
    session_saved = pyqtSignal(str)  # profile_id
    session_restored = pyqtSignal(str, list)  # profile_id, tabs
    cookies_saved = pyqtSignal(str, int)  # profile_id, count
    cookies_restored = pyqtSignal(str, int)  # profile_id, count
    
    def __init__(self, profile_manager):
        super().__init__()
        self.profile_manager = profile_manager
        self.data_dir = profile_manager.data_dir
        self.sessions_dir = os.path.join(self.data_dir, "sessions")
        self.cookies_dir = os.path.join(self.data_dir, "cookies")
        
        # Створюємо директорії
        os.makedirs(self.sessions_dir, exist_ok=True)
        os.makedirs(self.cookies_dir, exist_ok=True)
        
        # Ініціалізуємо базу даних
        self.init_database()
        
    def init_database(self):
        """Ініціалізація бази даних сесій"""
        db_path = os.path.join(self.data_dir, "sessions.db")
        
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Таблиця сесій
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS browser_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    profile_id TEXT NOT NULL,
                    session_name TEXT,
                    tabs_data TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    last_accessed TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT 0
                )
            """)
            
            # Таблиця історії
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS browsing_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    profile_id TEXT NOT NULL,
                    url TEXT NOT NULL,
                    title TEXT,
                    visit_time TEXT NOT NULL,
                    visit_count INTEGER DEFAULT 1
                )
            """)
            
            # Таблиця збережених cookies
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS saved_cookies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    profile_id TEXT NOT NULL,
                    domain TEXT NOT NULL,
                    name TEXT NOT NULL,
                    value TEXT NOT NULL,
                    path TEXT DEFAULT '/',
                    expires_at TEXT,
                    is_secure BOOLEAN DEFAULT 0,
                    is_http_only BOOLEAN DEFAULT 0,
                    same_site TEXT DEFAULT 'Lax',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            
            # Індекси для швидкого пошуку
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_profile ON browser_sessions(profile_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_history_profile ON browsing_history(profile_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_cookies_profile ON saved_cookies(profile_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_cookies_domain ON saved_cookies(domain)")
            
            conn.commit()
            
    def save_session(self, profile_id: str, tabs_data: List[Dict], session_name: str = None) -> bool:
        """Збереження поточної сесії"""
        try:
            if not session_name:
                session_name = f"Сесія {datetime.now().strftime('%Y-%m-%d %H:%M')}"
                
            now = datetime.now().isoformat()
            tabs_json = json.dumps(tabs_data, ensure_ascii=False)
            
            db_path = os.path.join(self.data_dir, "sessions.db")
            
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                
                # Деактивуємо попередні активні сесії
                cursor.execute(
                    "UPDATE browser_sessions SET is_active = 0 WHERE profile_id = ?",
                    (profile_id,)
                )
                
                # Зберігаємо нову сесію
                cursor.execute("""
                    INSERT INTO browser_sessions 
                    (profile_id, session_name, tabs_data, created_at, last_accessed, is_active)
                    VALUES (?, ?, ?, ?, ?, 1)
                """, (profile_id, session_name, tabs_json, now, now))
                
                conn.commit()
                
            self.session_saved.emit(profile_id)
            return True
            
        except Exception as e:
            print(f"Помилка збереження сесії: {e}")
            return False
            
    def restore_session(self, profile_id: str, session_id: int = None) -> Optional[List[Dict]]:
        """Відновлення сесії"""
        try:
            db_path = os.path.join(self.data_dir, "sessions.db")
            
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                
                if session_id:
                    # Відновлюємо конкретну сесію
                    cursor.execute(
                        "SELECT tabs_data FROM browser_sessions WHERE id = ? AND profile_id = ?",
                        (session_id, profile_id)
                    )
                else:
                    # Відновлюємо останню активну сесію
                    cursor.execute("""
                        SELECT tabs_data FROM browser_sessions 
                        WHERE profile_id = ? AND is_active = 1
                        ORDER BY last_accessed DESC LIMIT 1
                    """, (profile_id,))
                    
                row = cursor.fetchone()
                if row:
                    tabs_data = json.loads(row[0])
                    
                    # Оновлюємо час останнього доступу
                    now = datetime.now().isoformat()
                    if session_id:
                        cursor.execute(
                            "UPDATE browser_sessions SET last_accessed = ? WHERE id = ?",
                            (now, session_id)
                        )
                    else:
                        cursor.execute("""
                            UPDATE browser_sessions SET last_accessed = ? 
                            WHERE profile_id = ? AND is_active = 1
                        """, (now, profile_id))
                        
                    conn.commit()
                    
                    self.session_restored.emit(profile_id, tabs_data)
                    return tabs_data
                    
        except Exception as e:
            print(f"Помилка відновлення сесії: {e}")
            
        return None
        
    def get_sessions(self, profile_id: str) -> List[Dict]:
        """Отримання списку збережених сесій"""
        sessions = []
        
        try:
            db_path = os.path.join(self.data_dir, "sessions.db")
            
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, session_name, created_at, last_accessed, is_active
                    FROM browser_sessions WHERE profile_id = ?
                    ORDER BY last_accessed DESC
                """, (profile_id,))
                
                rows = cursor.fetchall()
                for row in rows:
                    sessions.append({
                        'id': row[0],
                        'name': row[1],
                        'created_at': row[2],
                        'last_accessed': row[3],
                        'is_active': bool(row[4])
                    })
                    
        except Exception as e:
            print(f"Помилка отримання сесій: {e}")
            
        return sessions
        
    def delete_session(self, session_id: int) -> bool:
        """Видалення сесії"""
        try:
            db_path = os.path.join(self.data_dir, "sessions.db")
            
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM browser_sessions WHERE id = ?", (session_id,))
                conn.commit()
                
            return cursor.rowcount > 0
            
        except Exception as e:
            print(f"Помилка видалення сесії: {e}")
            return False
            
    def save_cookies_from_store(self, profile_id: str, cookie_store: QWebEngineCookieStore):
        """Збереження cookies з cookie store"""
        self.cookies_to_save = []
        
        def on_cookie_added(cookie):
            self.cookies_to_save.append(cookie)
            
        # Отримуємо всі cookies
        cookie_store.cookieAdded.connect(on_cookie_added)
        
        # TODO: Реалізувати отримання всіх cookies
        # В Qt немає прямого способу отримати всі cookies
        # Потрібно використовувати JavaScript або інший метод
        
    def save_cookies(self, profile_id: str, cookies: List[Dict]) -> bool:
        """Збереження cookies вручну"""
        try:
            db_path = os.path.join(self.data_dir, "sessions.db")
            now = datetime.now().isoformat()
            
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                
                # Очищаємо старі cookies для профілю
                cursor.execute("DELETE FROM saved_cookies WHERE profile_id = ?", (profile_id,))
                
                # Зберігаємо нові cookies
                for cookie in cookies:
                    cursor.execute("""
                        INSERT INTO saved_cookies 
                        (profile_id, domain, name, value, path, expires_at, 
                         is_secure, is_http_only, same_site, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        profile_id,
                        cookie.get('domain', ''),
                        cookie.get('name', ''),
                        cookie.get('value', ''),
                        cookie.get('path', '/'),
                        cookie.get('expires'),
                        cookie.get('secure', False),
                        cookie.get('httpOnly', False),
                        cookie.get('sameSite', 'Lax'),
                        now,
                        now
                    ))
                    
                conn.commit()
                
            self.cookies_saved.emit(profile_id, len(cookies))
            return True
            
        except Exception as e:
            print(f"Помилка збереження cookies: {e}")
            return False
            
    def restore_cookies(self, profile_id: str) -> List[Dict]:
        """Відновлення cookies"""
        cookies = []
        
        try:
            db_path = os.path.join(self.data_dir, "sessions.db")
            
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT domain, name, value, path, expires_at, is_secure, is_http_only, same_site
                    FROM saved_cookies WHERE profile_id = ?
                """, (profile_id,))
                
                rows = cursor.fetchall()
                for row in rows:
                    # Перевіряємо чи cookie не протерміновані
                    expires_at = row[4]
                    if expires_at:
                        expires_datetime = datetime.fromisoformat(expires_at)
                        if expires_datetime < datetime.now():
                            continue  # Пропускаємо протерміновані cookies
                            
                    cookies.append({
                        'domain': row[0],
                        'name': row[1],
                        'value': row[2],
                        'path': row[3],
                        'expires': row[4],
                        'secure': bool(row[5]),
                        'httpOnly': bool(row[6]),
                        'sameSite': row[7]
                    })
                    
            self.cookies_restored.emit(profile_id, len(cookies))
            
        except Exception as e:
            print(f"Помилка відновлення cookies: {e}")
            
        return cookies
        
    def add_to_history(self, profile_id: str, url: str, title: str = ""):
        """Додавання запису в історію"""
        try:
            db_path = os.path.join(self.data_dir, "sessions.db")
            now = datetime.now().isoformat()
            
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                
                # Перевіряємо чи запис вже існує
                cursor.execute("""
                    SELECT id, visit_count FROM browsing_history 
                    WHERE profile_id = ? AND url = ?
                """, (profile_id, url))
                
                row = cursor.fetchone()
                if row:
                    # Оновлюємо існуючий запис
                    cursor.execute("""
                        UPDATE browsing_history 
                        SET visit_count = ?, visit_time = ?, title = ?
                        WHERE id = ?
                    """, (row[1] + 1, now, title, row[0]))
                else:
                    # Створюємо новий запис
                    cursor.execute("""
                        INSERT INTO browsing_history 
                        (profile_id, url, title, visit_time)
                        VALUES (?, ?, ?, ?)
                    """, (profile_id, url, title, now))
                    
                conn.commit()
                
        except Exception as e:
            print(f"Помилка додавання в історію: {e}")
            
    def get_history(self, profile_id: str, limit: int = 100) -> List[Dict]:
        """Отримання історії браузінгу"""
        history = []
        
        try:
            db_path = os.path.join(self.data_dir, "sessions.db")
            
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT url, title, visit_time, visit_count
                    FROM browsing_history WHERE profile_id = ?
                    ORDER BY visit_time DESC LIMIT ?
                """, (profile_id, limit))
                
                rows = cursor.fetchall()
                for row in rows:
                    history.append({
                        'url': row[0],
                        'title': row[1],
                        'visit_time': row[2],
                        'visit_count': row[3]
                    })
                    
        except Exception as e:
            print(f"Помилка отримання історії: {e}")
            
        return history
        
    def clear_history(self, profile_id: str, older_than_days: int = None) -> bool:
        """Очищення історії"""
        try:
            db_path = os.path.join(self.data_dir, "sessions.db")
            
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                
                if older_than_days:
                    # Видаляємо записи старші за вказану кількість днів
                    cutoff_date = (datetime.now() - timedelta(days=older_than_days)).isoformat()
                    cursor.execute("""
                        DELETE FROM browsing_history 
                        WHERE profile_id = ? AND visit_time < ?
                    """, (profile_id, cutoff_date))
                else:
                    # Видаляємо всю історію
                    cursor.execute("DELETE FROM browsing_history WHERE profile_id = ?", (profile_id,))
                    
                conn.commit()
                
            return True
            
        except Exception as e:
            print(f"Помилка очищення історії: {e}")
            return False
            
    def clear_cookies(self, profile_id: str) -> bool:
        """Очищення cookies"""
        try:
            db_path = os.path.join(self.data_dir, "sessions.db")
            
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM saved_cookies WHERE profile_id = ?", (profile_id,))
                conn.commit()
                
            return True
            
        except Exception as e:
            print(f"Помилка очищення cookies: {e}")
            return False
            
    def clear_sessions(self, profile_id: str) -> bool:
        """Очищення збережених сесій"""
        try:
            db_path = os.path.join(self.data_dir, "sessions.db")
            
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM browser_sessions WHERE profile_id = ?", (profile_id,))
                conn.commit()
                
            return True
            
        except Exception as e:
            print(f"Помилка очищення сесій: {e}")
            return False
>>>>>>> 5a38118ad408679126e5a17483fa7875264c621b

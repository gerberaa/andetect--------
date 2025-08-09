<<<<<<< HEAD
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестування проксі в форматі IP:PORT:USER:PASS
"""

import subprocess
import os
import tempfile
import json

def test_proxy_with_auth(proxy_string):
    """Тестування проксі з авторизацією"""
    
    parts = proxy_string.split(':')
    if len(parts) != 4:
        print("❌ Невірний формат! Використовуйте: IP:PORT:USER:PASS")
        return False
    
    host, port, username, password = parts
    
    print(f"🔍 Тестування проксі:")
    print(f"   Хост: {host}")
    print(f"   Порт: {port}")
    print(f"   Логін: {username}")
    print(f"   Пароль: {'*' * len(password)}")
    
    # Знаходимо Chrome
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
    ]
    
    chrome_exe = None
    for path in chrome_paths:
        if os.path.exists(path):
            chrome_exe = path
            break
    
    if not chrome_exe:
        print("❌ Chrome не знайдено!")
        return False
    
    # Створюємо тимчасовий профіль
    temp_dir = tempfile.mkdtemp(prefix="andetect_proxy_test_")
    extension_dir = os.path.join(temp_dir, "proxy_auth_extension")
    os.makedirs(extension_dir, exist_ok=True)
    
    print(f"📁 Тимчасовий профіль: {temp_dir}")
    
    # Створюємо розширення для авторизації
    manifest = {
        "manifest_version": 2,
        "name": "Proxy Auth Test",
        "version": "1.0",
        "description": "Test proxy authentication",
        "permissions": [
            "webRequest",
            "webRequestBlocking",
            "<all_urls>",
            "proxy"
        ],
        "background": {
            "scripts": ["background.js"],
            "persistent": True
        }
    }
    
    with open(os.path.join(extension_dir, "manifest.json"), 'w') as f:
        json.dump(manifest, f, indent=2)
    
    background_js = f"""
chrome.webRequest.onAuthRequired.addListener(
    function(details) {{
        console.log('🔐 Proxy auth required for:', details.url);
        console.log('🔑 Using credentials: {username}');
        return {{
            authCredentials: {{
                username: '{username}',
                password: '{password}'
            }}
        }};
    }},
    {{urls: ["<all_urls>"]}},
    ["blocking"]
);

console.log('✅ Proxy Auth Extension loaded');
console.log('🌐 Ready for proxy: {host}:{port}');
"""
    
    with open(os.path.join(extension_dir, "background.js"), 'w') as f:
        f.write(background_js)
    
    # Флаги Chrome
    flags = [
        f"--user-data-dir={temp_dir}",
        "--no-first-run",
        "--no-default-browser-check",
        f"--proxy-server=http://{host}:{port}",
        f"--load-extension={extension_dir}",
        "--disable-extensions-except=" + extension_dir,
        "https://httpbin.org/ip"  # Сайт для перевірки IP
    ]
    
    print(f"🚀 Запуск Chrome з проксі...")
    print(f"Команда: {chrome_exe} {' '.join(flags[:5])}...")
    
    try:
        process = subprocess.Popen([chrome_exe] + flags)
        print(f"✅ Chrome запущено! PID: {process.pid}")
        print("🔍 Перевірте в браузері:")
        print("   1. Відкрилася сторінка httpbin.org/ip")
        print(f"   2. IP-адреса відповідає проксі: {host}")
        print("   3. Немає запитів на авторизацію")
        return True
        
    except Exception as e:
        print(f"❌ Помилка запуску Chrome: {e}")
        return False

def main():
    print("=" * 60)
    print("        Тест проксі з авторизацією для AnDetect")
    print("=" * 60)
    print()
    
    proxy_example = "45.158.61.63:46130:RQQ6C0VF:MZH4VXZU"
    proxy_input = input(f"Введіть проксі у форматі IP:PORT:USER:PASS\n(натисніть Enter для тесту з прикладом):\n> ").strip()
    
    if not proxy_input:
        proxy_input = proxy_example
        print(f"📝 Використовую приклад: {proxy_input}")
    
    print()
    if test_proxy_with_auth(proxy_input):
        print()
        print("✅ Тест запущено! Якщо все працює правильно:")
        print("   - На сторінці httpbin.org/ip буде показано IP вашого проксі")
        print("   - Не будуть з'являтися діалоги авторизації")
        print("   - У консолі розробника (F12) будуть логи розширення")
    else:
        print()
        print("❌ Тест не вдався. Перевірте:")
        print("   - Правильність формату проксі")
        print("   - Доступність проксі")
        print("   - Правильність логіна/паролю")
    
    input("\nНатисніть Enter для виходу...")

if __name__ == "__main__":
    main()
=======
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестування проксі в форматі IP:PORT:USER:PASS
"""

import subprocess
import os
import tempfile
import json

def test_proxy_with_auth(proxy_string):
    """Тестування проксі з авторизацією"""
    
    parts = proxy_string.split(':')
    if len(parts) != 4:
        print("❌ Невірний формат! Використовуйте: IP:PORT:USER:PASS")
        return False
    
    host, port, username, password = parts
    
    print(f"🔍 Тестування проксі:")
    print(f"   Хост: {host}")
    print(f"   Порт: {port}")
    print(f"   Логін: {username}")
    print(f"   Пароль: {'*' * len(password)}")
    
    # Знаходимо Chrome
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
    ]
    
    chrome_exe = None
    for path in chrome_paths:
        if os.path.exists(path):
            chrome_exe = path
            break
    
    if not chrome_exe:
        print("❌ Chrome не знайдено!")
        return False
    
    # Створюємо тимчасовий профіль
    temp_dir = tempfile.mkdtemp(prefix="andetect_proxy_test_")
    extension_dir = os.path.join(temp_dir, "proxy_auth_extension")
    os.makedirs(extension_dir, exist_ok=True)
    
    print(f"📁 Тимчасовий профіль: {temp_dir}")
    
    # Створюємо розширення для авторизації
    manifest = {
        "manifest_version": 2,
        "name": "Proxy Auth Test",
        "version": "1.0",
        "description": "Test proxy authentication",
        "permissions": [
            "webRequest",
            "webRequestBlocking",
            "<all_urls>",
            "proxy"
        ],
        "background": {
            "scripts": ["background.js"],
            "persistent": True
        }
    }
    
    with open(os.path.join(extension_dir, "manifest.json"), 'w') as f:
        json.dump(manifest, f, indent=2)
    
    background_js = f"""
chrome.webRequest.onAuthRequired.addListener(
    function(details) {{
        console.log('🔐 Proxy auth required for:', details.url);
        console.log('🔑 Using credentials: {username}');
        return {{
            authCredentials: {{
                username: '{username}',
                password: '{password}'
            }}
        }};
    }},
    {{urls: ["<all_urls>"]}},
    ["blocking"]
);

console.log('✅ Proxy Auth Extension loaded');
console.log('🌐 Ready for proxy: {host}:{port}');
"""
    
    with open(os.path.join(extension_dir, "background.js"), 'w') as f:
        f.write(background_js)
    
    # Флаги Chrome
    flags = [
        f"--user-data-dir={temp_dir}",
        "--no-first-run",
        "--no-default-browser-check",
        f"--proxy-server=http://{host}:{port}",
        f"--load-extension={extension_dir}",
        "--disable-extensions-except=" + extension_dir,
        "https://httpbin.org/ip"  # Сайт для перевірки IP
    ]
    
    print(f"🚀 Запуск Chrome з проксі...")
    print(f"Команда: {chrome_exe} {' '.join(flags[:5])}...")
    
    try:
        process = subprocess.Popen([chrome_exe] + flags)
        print(f"✅ Chrome запущено! PID: {process.pid}")
        print("🔍 Перевірте в браузері:")
        print("   1. Відкрилася сторінка httpbin.org/ip")
        print(f"   2. IP-адреса відповідає проксі: {host}")
        print("   3. Немає запитів на авторизацію")
        return True
        
    except Exception as e:
        print(f"❌ Помилка запуску Chrome: {e}")
        return False

def main():
    print("=" * 60)
    print("        Тест проксі з авторизацією для AnDetect")
    print("=" * 60)
    print()
    
    proxy_example = "45.158.61.63:46130:RQQ6C0VF:MZH4VXZU"
    proxy_input = input(f"Введіть проксі у форматі IP:PORT:USER:PASS\n(натисніть Enter для тесту з прикладом):\n> ").strip()
    
    if not proxy_input:
        proxy_input = proxy_example
        print(f"📝 Використовую приклад: {proxy_input}")
    
    print()
    if test_proxy_with_auth(proxy_input):
        print()
        print("✅ Тест запущено! Якщо все працює правильно:")
        print("   - На сторінці httpbin.org/ip буде показано IP вашого проксі")
        print("   - Не будуть з'являтися діалоги авторизації")
        print("   - У консолі розробника (F12) будуть логи розширення")
    else:
        print()
        print("❌ Тест не вдався. Перевірте:")
        print("   - Правильність формату проксі")
        print("   - Доступність проксі")
        print("   - Правильність логіна/паролю")
    
    input("\nНатисніть Enter для виходу...")

if __name__ == "__main__":
    main()
>>>>>>> 5a38118ad408679126e5a17483fa7875264c621b

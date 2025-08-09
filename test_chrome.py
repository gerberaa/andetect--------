#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Тестування запуску Chrome з мінімальними флагами
"""

import subprocess
import sys
import os
import tempfile

def test_chrome_launch():
    """Тестування запуску Chrome"""
    
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
    
    print(f"✅ Chrome знайдено: {chrome_exe}")
    
    # Створюємо тимчасову директорію для профілю
    temp_dir = tempfile.mkdtemp(prefix="andetect_test_")
    print(f"📁 Тимчасова директорія: {temp_dir}")
    
    # Мінімальні флаги для тестування
    flags = [
        f"--user-data-dir={temp_dir}",
        "--no-first-run",
        "--no-default-browser-check",
        "https://www.google.com"
    ]
    
    print("🚀 Запуск Chrome з мінімальними флагами...")
    print(f"Команда: {chrome_exe} {' '.join(flags)}")
    
    try:
        # Запускаємо Chrome
        process = subprocess.Popen([chrome_exe] + flags)
        print(f"✅ Chrome запущено! PID: {process.pid}")
        print("🔍 Перевірте чи відкрилося вікно Chrome з Google")
        print("💡 Якщо вікно чорне, проблема в драйверах відеокарти або системних налаштуваннях")
        
        return True
        
    except Exception as e:
        print(f"❌ Помилка запуску Chrome: {e}")
        return False

def main():
    print("=" * 60)
    print("          Тест запуску Chrome для AnDetect")
    print("=" * 60)
    print()
    
    if test_chrome_launch():
        print()
        print("✅ Тест пройдено! Chrome запускається.")
        print("Якщо вікно чорне, спробуйте:")
        print("1. Оновити драйвери відеокарти")
        print("2. Запустити з правами адміністратора")
        print("3. Вимкнути антивірус тимчасово")
        print("4. Перевірити налаштування Windows Defender")
    else:
        print()
        print("❌ Тест не пройдено. Перевірте установку Chrome.")
    
    input("\nНатисніть Enter для виходу...")

if __name__ == "__main__":
    main()

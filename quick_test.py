<<<<<<< HEAD
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Швидкий тест для перевірки чи вирішена проблема з чорним екраном
"""

import subprocess
import os
import tempfile

def quick_chrome_test():
    """Швидкий тест Chrome"""
    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    
    if not os.path.exists(chrome_path):
        chrome_path = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
    
    if not os.path.exists(chrome_path):
        print("Chrome не знайдено!")
        return
    
    temp_dir = tempfile.mkdtemp()
    print(f"Запуск Chrome з профілем: {temp_dir}")
    
    # Мінімальні флаги
    cmd = [
        chrome_path,
        f"--user-data-dir={temp_dir}",
        "--no-first-run",
        "--no-default-browser-check",
        "https://www.google.com"
    ]
    
    print("Команда:", " ".join(cmd))
    subprocess.Popen(cmd)
    print("Chrome запущено! Перевірте чи сторінка завантажується нормально.")

if __name__ == "__main__":
    quick_chrome_test()
=======
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Швидкий тест для перевірки чи вирішена проблема з чорним екраном
"""

import subprocess
import os
import tempfile

def quick_chrome_test():
    """Швидкий тест Chrome"""
    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    
    if not os.path.exists(chrome_path):
        chrome_path = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
    
    if not os.path.exists(chrome_path):
        print("Chrome не знайдено!")
        return
    
    temp_dir = tempfile.mkdtemp()
    print(f"Запуск Chrome з профілем: {temp_dir}")
    
    # Мінімальні флаги
    cmd = [
        chrome_path,
        f"--user-data-dir={temp_dir}",
        "--no-first-run",
        "--no-default-browser-check",
        "https://www.google.com"
    ]
    
    print("Команда:", " ".join(cmd))
    subprocess.Popen(cmd)
    print("Chrome запущено! Перевірте чи сторінка завантажується нормально.")

if __name__ == "__main__":
    quick_chrome_test()
>>>>>>> 5a38118ad408679126e5a17483fa7875264c621b

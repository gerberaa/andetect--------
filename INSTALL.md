# Інструкція з встановлення AnDetect Browser

## 📋 Передумови

### Системні вимоги
- **OS**: Windows 10/11 (64-bit) - основна підтримка
- **Python**: 3.8+ (рекомендовано 3.10+)
- **RAM**: Мінімум 4GB, рекомендовано 8GB+
- **Дисковий простір**: 1GB вільного місця
- **Мережа**: Доступ до інтернету для завантаження залежностей

### Необхідні права
- Права адміністратора для встановлення деяких компонентів
- Доступ до мережевих налаштувань
- Можливість запуску програм із зовнішніх джерел

## 🔧 Крок 1: Встановлення Python

### Автоматичне встановлення (рекомендовано)
```bash
# Завантажте з офіційного сайту
https://www.python.org/downloads/windows/

# Або через winget
winget install Python.Python.3.11
```

### Перевірка встановлення
```bash
python --version
pip --version
```

### Налаштування змінних середовища
Переконайтесь, що Python додано до PATH:
```bash
# Перевірка PATH
echo %PATH%

# Додавання вручну (якщо потрібно)
setx PATH "%PATH%;C:\Python311;C:\Python311\Scripts"
```

## 📥 Крок 2: Отримання коду

### Через Git (рекомендовано)
```bash
# Клонування репозиторію
git clone https://github.com/your-username/andetect-browser.git
cd andetect-browser

# Перевірка статусу
git status
```

### Через завантаження ZIP
1. Відкрийте GitHub репозиторій
2. Натисніть "Code" → "Download ZIP"
3. Розпакуйте архів у бажану директорію

## 🔨 Крок 3: Встановлення залежностей

### Створення віртуального середовища (рекомендовано)
```bash
# Створення venv
python -m venv andetect_env

# Активація (Windows)
andetect_env\Scripts\activate

# Активація (PowerShell)
andetect_env\Scripts\Activate.ps1
```

### Встановлення основних залежностей
```bash
# Оновлення pip
python -m pip install --upgrade pip

# Встановлення залежностей
pip install -r requirements.txt

# Перевірка встановлення
pip list
```

### Вирішення проблем із залежностями

#### PyQt5 проблеми
```bash
# Якщо виникають помилки з PyQt5
pip uninstall PyQt5 PyQtWebEngine
pip install PyQt5==5.15.9 PyQtWebEngine==5.15.6 --force-reinstall

# Альтернативний метод
pip install --find-links https://download.qt.io/snapshots/ci/pyqt/5.15/PyQt5/ PyQt5
```

#### Проблеми з криптографією
```bash
# Встановлення Visual C++ Build Tools (якщо потрібно)
# Завантажте з: https://visualstudio.microsoft.com/visual-cpp-build-tools/

# Або використовуйте pre-compiled wheels
pip install --only-binary=cryptography cryptography
```

## 🌐 Крок 4: Встановлення Tor (опціонально)

### Автоматичне встановлення
```bash
# Завантаження Tor Browser
https://www.torproject.org/download/

# Встановлення у стандартну директорію
C:\Program Files\Tor Browser\
```

### Налаштування шляхів
```bash
# Додавання змінної середовища
setx TOR_PATH "C:\Program Files\Tor Browser\Browser\TorBrowser\Tor\tor.exe"

# Або встановлення portable версії
mkdir C:\andetect\tor
# Розпакуйте tor.exe у цю директорію
```

### Перевірка роботи Tor
```bash
# Тест підключення (опціонально)
"C:\Program Files\Tor Browser\Browser\TorBrowser\Tor\tor.exe" --version
```

## ⚙️ Крок 5: Конфігурація

### Створення файлу налаштувань
```bash
# Створіть andetect_settings.json
copy nul andetect_settings.json
```

### Базова конфігурація
```json
{
  "tor_enabled": false,
  "proxy_enabled": false,
  "anti_fingerprint": true,
  "clear_on_exit": true,
  "block_webrtc": true,
  "spoof_canvas": true,
  "randomize_user_agent": true,
  "proxy_host": "127.0.0.1",
  "proxy_port": 9050,
  "tor_port": 9051
}
```

### Налаштування брандмауера
```bash
# Додавання правил брандмауера (як адміністратор)
netsh advfirewall firewall add rule name="AnDetect Browser" dir=in action=allow protocol=TCP localport=9050,9051
netsh advfirewall firewall add rule name="AnDetect Browser Out" dir=out action=allow protocol=TCP localport=9050,9051
```

## 🚀 Крок 6: Перший запуск

### Тестовий запуск
```bash
# Базовий запуск
python andetect_browser.py

# Запуск з налагодженням
python andetect_browser.py --debug

# Запуск з Tor (якщо встановлено)
python andetect_browser.py --tor
```

### Перевірка функціональності
1. **Інтерфейс**: Перевірте чи відкривається головне вікно
2. **Навігація**: Спробуйте відкрити веб-сайт
3. **Налаштування**: Відкрийте меню налаштувань
4. **Приватність**: Перевірте статус анонімності

## 🛠️ Крок 7: Створення ярлика

### Ярлик на робочому столі
```bash
# Створіть .bat файл
echo @echo off > start_andetect.bat
echo cd /d "C:\path\to\andetect-browser" >> start_andetect.bat
echo andetect_env\Scripts\activate >> start_andetect.bat
echo python andetect_browser.py >> start_andetect.bat
echo pause >> start_andetect.bat
```

### Ярлик з іконкою (опціонально)
1. Створіть .lnk файл через Properties
2. Встановіть Target: `C:\path\to\start_andetect.bat`
3. Додайте іконку (якщо є)

## 🔍 Перевірка встановлення

### Команди діагностики
```bash
# Перевірка Python модулів
python -c "import PyQt5; print('PyQt5 OK')"
python -c "import socks; print('PySocks OK')"
python -c "import requests; print('Requests OK')"

# Перевірка файлів
dir andetect_browser.py
dir privacy_protection.py
dir tor_integration.py

# Тест імпортів
python -c "from andetect_browser import AnDetectBrowser; print('Main module OK')"
```

### Лог файли
```bash
# Перевірка логів (якщо є)
type andetect.log
type tor.log
```

## 🐛 Усунення проблем

### Поширені помилки

#### "No module named 'PyQt5'"
```bash
pip install PyQt5==5.15.9 PyQtWebEngine==5.15.6
```

#### "Tor executable not found"
```bash
# Перевірте шлях до Tor
where tor.exe
setx TOR_PATH "правильний\шлях\до\tor.exe"
```

#### "Permission denied"
```bash
# Запустіть як адміністратор або змініть права
icacls "C:\path\to\andetect-browser" /grant Users:F /T
```

#### "Port already in use"
```bash
# Перевірте які процеси використовують порти
netstat -ano | findstr :9050
netstat -ano | findstr :9051

# Завершіть конфліктуючі процеси
taskkill /PID <process_id> /F
```

### Діагностичні команди
```bash
# Системна інформація
systeminfo | findstr "OS Name"
python -m site

# Мережеві налаштування
ipconfig /all
netsh interface show interface

# Права доступу
whoami /groups
```

## 📊 Моніторинг

### Перевірка роботи
```bash
# Перевірка процесів
tasklist | findstr python
tasklist | findstr tor

# Мережеві з'єднання
netstat -ano | findstr python
```

### Логування
Створіть файл логування для моніторингу:
```python
import logging
logging.basicConfig(
    filename='andetect.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
```

## 🔄 Автоматичне оновлення

### Скрипт оновлення
```bash
# update.bat
@echo off
cd /d "C:\path\to\andetect-browser"
git pull origin main
andetect_env\Scripts\activate
pip install -r requirements.txt --upgrade
echo Update completed!
pause
```

### Планування оновлень
Використовуйте Task Scheduler для автоматичних оновлень:
1. Відкрийте Task Scheduler
2. Створіть базову задачу
3. Встановіть розклад
4. Додайте дію запуску update.bat

## ✅ Завершення встановлення

Після успішного встановлення ви повинні мати:
- ✅ Працюючий AnDetect Browser
- ✅ Налаштовані залежності
- ✅ Опціонально: інтеграцію з Tor
- ✅ Файл конфігурації
- ✅ Ярлик для запуску

## 📞 Підтримка

Якщо виникають проблеми:
1. Перевірте [Issues](https://github.com/your-username/andetect-browser/issues)
2. Створіть новий issue з деталями помилки
3. Додайте лог файли та системну інформацію

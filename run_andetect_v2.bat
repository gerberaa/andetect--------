@echo off
chcp 65001 >nul
cls

echo.
echo ========================================
echo   🛡️ AnDetect Profile Manager v2.0 🛡️
echo ========================================
echo.
echo 🎨 Розширена версія з іконками та мітками
echo 🌍 Підтримка прапорців країн
echo 🔐 Автоматична авторизація проксі
echo 📊 Статистика використання
echo 🎯 Розширені фільтри
echo.

REM Перевірка Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python не знайдено!
    echo Будь ласка, встановіть Python з https://python.org
    pause
    exit /b 1
)

echo ✅ Python знайдено

REM Перевірка PyQt5
python -c "import PyQt5" >nul 2>&1
if %errorlevel% neq 0 (
    echo ⏳ Встановлення PyQt5...
    python -m pip install PyQt5 PyQtWebEngine
)

echo ✅ Залежності готові

REM Перевірка logo.png
if exist "logo.png" (
    echo ✅ Логотип знайдено
) else (
    echo ⚠️  Логотип не знайдено, використовується стандартна іконка
)

echo.
echo 🚀 Запуск AnDetect Profile Manager v2.0...
echo.

python profile_manager_v2.py

if %errorlevel% neq 0 (
    echo.
    echo ❌ Помилка при запуску програми
    echo Перевірте чи встановлені всі залежності
    pause
)

echo.
echo 👋 Дякуємо за використання AnDetect!

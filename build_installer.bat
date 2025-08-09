@echo off
title AnDetect Profile Manager - Збірка установщика
echo.
echo ========================================
echo   AnDetect Profile Manager v1.0
echo   Збірка установщика
echo ========================================
echo.

REM Перевірка наявності Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ПОМИЛКА: Python не встановлено!
    echo Будь ласка, встановіть Python 3.8 або вище з https://python.org
    pause
    exit /b 1
)

echo ✅ Python знайдено

REM Створення іконки
echo.
echo 📄 Створення іконки...
python create_icon.py

REM Перевірка та встановлення залежностей
echo.
echo 📦 Перевірка залежностей...
python -c "import PyQt5" >nul 2>&1
if %errorlevel% neq 0 (
    echo 📥 Встановлення залежностей...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo ❌ ПОМИЛКА: Не вдалося встановити залежності!
        pause
        exit /b 1
    )
)

echo ✅ Залежності готові

REM Запуск збірки
echo.
echo 🔨 Початок збірки...
echo Це може зайняти кілька хвилин...
echo.

python setup.py

echo.
if %errorlevel% equ 0 (
    echo ========================================
    echo ✅ ЗБІРКА ЗАВЕРШЕНА УСПІШНО!
    echo ========================================
    echo.
    echo 📁 Файли знаходяться в:
    echo    dist\AnDetectProfileManager.exe
    echo.
    echo 🎯 Тестування:
    echo    cd dist
    echo    AnDetectProfileManager.exe
    echo.
    echo 📦 Установщик (якщо є NSIS):
    echo    installer.nsi
    echo.
) else (
    echo ========================================
    echo ❌ ПОМИЛКА ЗБІРКИ!
    echo ========================================
    echo.
    echo 🔍 Перевірте:
    echo    - Всі файли на місці
    echo    - Python залежності встановлені
    echo    - Достатньо місця на диску
    echo.
)

echo Натисніть будь-яку клавішу для виходу...
pause >nul

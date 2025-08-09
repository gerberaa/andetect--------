@echo off
chcp 65001 >nul
cls

echo.
echo ========================================
echo   🛡️ AnDetect Profile Manager v2.0 🛡️
echo       Збірка установщика
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

REM Перевірка основних файлів
if not exist "profile_manager_v2.py" (
    echo ❌ Основний файл profile_manager_v2.py не знайдено!
    pause
    exit /b 1
)

if not exist "browser\profile_manager.py" (
    echo ❌ Модуль browser\profile_manager.py не знайдено!
    pause
    exit /b 1
)

if not exist "profile_icons.py" (
    echo ❌ Модуль profile_icons.py не знайдено!
    pause
    exit /b 1
)

if not exist "user_agents.py" (
    echo ❌ Модуль user_agents.py не знайдено!
    pause
    exit /b 1
)

echo ✅ Основні файли знайдено

REM Створення іконки якщо не існує
if not exist "logo.png" (
    if not exist "icon.ico" (
        echo 🎨 Створення іконки...
        python create_icon.py
        if exist "icon.ico" (
            echo ✅ Іконку створено: icon.ico
        ) else (
            echo ⚠️  Не вдалося створити іконку
        )
    ) else (
        echo ✅ Іконку знайдено: icon.ico
    )
) else (
    echo ✅ Логотип знайдено: logo.png
)

echo.
echo 🚀 Початок збірки...
echo Це може зайняти кілька хвилин...
echo.

REM Запуск збірки
python setup_v2.py

if %errorlevel% neq 0 (
    echo.
    echo ❌ Помилка при збірці установщика
    echo Перевірте повідомлення про помилки вище
    pause
    exit /b 1
)

echo.
echo ✅ Збірка завершена!

REM Перевірка результатів
if exist "dist\AnDetectProfileManager.exe" (
    echo 📦 Виконуваний файл: dist\AnDetectProfileManager.exe
    
    REM Розмір файлу
    for %%i in ("dist\AnDetectProfileManager.exe") do (
        set /a size=%%~zi/1024/1024
        echo 📏 Розмір: !size! MB
    )
)

if exist "AnDetectProfileManager_v2.0.0_Setup.exe" (
    echo 💿 Інсталятор: AnDetectProfileManager_v2.0.0_Setup.exe
    
    REM Розмір інсталятора
    for %%i in ("AnDetectProfileManager_v2.0.0_Setup.exe") do (
        set /a size=%%~zi/1024/1024
        echo 📏 Розмір: !size! MB
    )
    
    echo.
    echo 🎉 Установщик готовий до розповсюдження!
    echo.
    echo 💡 Рекомендації:
    echo   • Протестуйте інсталятор на чистій системі
    echo   • Перевірте всі функції після встановлення
    echo   • Створіть резервну копію збірки
) else (
    echo ⚠️  Інсталятор не створено (можливо, NSIS не встановлено)
    echo 💡 Завантажте NSIS з https://nsis.sourceforge.io/
)

echo.
echo 📋 Вміст директорії dist:
if exist "dist" (
    dir /b dist
) else (
    echo   (директорія dist не існує)
)

echo.
echo 👋 Дякуємо за використання AnDetect Profile Manager!
pause

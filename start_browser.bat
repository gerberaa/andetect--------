@echo off
echo AnDetect Browser - Антитрекінг браузер для Windows
echo.

REM Перевірка Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ПОМИЛКА: Python не встановлено!
    echo Завантажте Python з https://python.org/downloads/
    pause
    exit /b 1
)

REM Перевірка залежностей
echo Перевірка залежностей...
python -c "import PyQt5; from PyQt5.QtWebEngineWidgets import QWebEngineView" >nul 2>&1
if errorlevel 1 (
    echo Встановлення залежностей...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo ПОМИЛКА: Не вдалося встановити залежності!
        echo Спробуйте запустити: pip install PyQt5 PyQtWebEngine
        echo.
        echo Запуск спрощеної версії...
        python simple_browser.py
        pause
        exit /b 1
    )
)

REM Спроба запуску повної версії
echo Запуск AnDetect Browser...
python andetect_browser.py
if errorlevel 1 (
    echo.
    echo Помилка запуску повної версії. Запуск спрощеної версії...
    python simple_browser.py
)

pause

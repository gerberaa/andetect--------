<<<<<<< HEAD
@echo off
title AnDetect Profile Manager
echo.
echo ================================
echo   AnDetect Profile Manager v1.0
echo ================================
echo.
echo Програма керування профілями браузера
echo Запускає окремі екземпляри Chrome з налаштованими профілями
echo.

REM Перевірка наявності Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ПОМИЛКА: Python не встановлено!
    echo Будь ласка, встановіть Python 3.8 або вище з https://python.org
    pause
    exit /b 1
)

REM Перевірка наявності Chrome
set CHROME_FOUND=0
if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" set CHROME_FOUND=1
if exist "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" set CHROME_FOUND=1

if %CHROME_FOUND%==0 (
    echo.
    echo УВАГА: Google Chrome не знайдено!
    echo Будь ласка, встановіть Google Chrome з https://chrome.google.com
    echo Або встановіть Chromium з https://chromium.org
    echo.
    echo Програма все одно запуститься, але не зможе запускати профілі.
    echo.
    pause
)

REM Перевірка наявності залежностей
echo Перевірка залежностей...
python -c "import PyQt5" >nul 2>&1
if %errorlevel% neq 0 (
    echo Встановлення залежностей...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo ПОМИЛКА: Не вдалося встановити залежності!
        pause
        exit /b 1
    )
)

REM Запуск менеджера профілів
echo.
echo Запуск AnDetect Profile Manager...
echo.
python profile_manager_app.py

REM Пауза перед закриттям
if %errorlevel% neq 0 (
    echo.
    echo Програма завершилася з помилкою.
    pause
)
=======
@echo off
title AnDetect Profile Manager
echo.
echo ================================
echo   AnDetect Profile Manager v1.0
echo ================================
echo.
echo Програма керування профілями браузера
echo Запускає окремі екземпляри Chrome з налаштованими профілями
echo.

REM Перевірка наявності Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ПОМИЛКА: Python не встановлено!
    echo Будь ласка, встановіть Python 3.8 або вище з https://python.org
    pause
    exit /b 1
)

REM Перевірка наявності Chrome
set CHROME_FOUND=0
if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" set CHROME_FOUND=1
if exist "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" set CHROME_FOUND=1

if %CHROME_FOUND%==0 (
    echo.
    echo УВАГА: Google Chrome не знайдено!
    echo Будь ласка, встановіть Google Chrome з https://chrome.google.com
    echo Або встановіть Chromium з https://chromium.org
    echo.
    echo Програма все одно запуститься, але не зможе запускати профілі.
    echo.
    pause
)

REM Перевірка наявності залежностей
echo Перевірка залежностей...
python -c "import PyQt5" >nul 2>&1
if %errorlevel% neq 0 (
    echo Встановлення залежностей...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo ПОМИЛКА: Не вдалося встановити залежності!
        pause
        exit /b 1
    )
)

REM Запуск менеджера профілів
echo.
echo Запуск AnDetect Profile Manager...
echo.
python profile_manager_app.py

REM Пауза перед закриттям
if %errorlevel% neq 0 (
    echo.
    echo Програма завершилася з помилкою.
    pause
)
>>>>>>> 5a38118ad408679126e5a17483fa7875264c621b

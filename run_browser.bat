<<<<<<< HEAD
@echo off
title AnDetect Browser
echo.
echo ================================
echo   AnDetect Browser v1.0
echo ================================
echo.
echo Запуск браузера...
echo.

REM Перевірка наявності Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ПОМИЛКА: Python не встановлено!
    echo Будь ласка, встановіть Python 3.8 або вище з https://python.org
    pause
    exit /b 1
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

REM Запуск браузера
echo Запуск AnDetect Browser...
python main.py

REM Пауза перед закриттям
if %errorlevel% neq 0 (
    echo.
    echo Браузер завершився з помилкою.
    pause
)
=======
@echo off
title AnDetect Browser
echo.
echo ================================
echo   AnDetect Browser v1.0
echo ================================
echo.
echo Запуск браузера...
echo.

REM Перевірка наявності Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ПОМИЛКА: Python не встановлено!
    echo Будь ласка, встановіть Python 3.8 або вище з https://python.org
    pause
    exit /b 1
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

REM Запуск браузера
echo Запуск AnDetect Browser...
python main.py

REM Пауза перед закриттям
if %errorlevel% neq 0 (
    echo.
    echo Браузер завершився з помилкою.
    pause
)
>>>>>>> 5a38118ad408679126e5a17483fa7875264c621b

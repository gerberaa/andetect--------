<<<<<<< HEAD
@echo off
title Test Proxy with Auth
echo.
echo ================================
echo   Тест проксі з авторизацією
echo ================================
echo.

REM Перевірка наявності Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ПОМИЛКА: Python не встановлено!
    pause
    exit /b 1
)

echo Запуск тесту проксі...
python test_proxy.py

pause
=======
@echo off
title Test Proxy with Auth
echo.
echo ================================
echo   Тест проксі з авторизацією
echo ================================
echo.

REM Перевірка наявності Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ПОМИЛКА: Python не встановлено!
    pause
    exit /b 1
)

echo Запуск тесту проксі...
python test_proxy.py

pause
>>>>>>> 5a38118ad408679126e5a17483fa7875264c621b

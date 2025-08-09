#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт збірки AnDetect Profile Manager v2.0
Створює виконуваний файл та інсталятор з розширеним функціоналом
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

# Конфігурація
APP_NAME = "AnDetectProfileManager"
APP_VERSION = "2.0.0"
APP_DESCRIPTION = "Розширений менеджер профілів браузера з іконками та мітками"
APP_AUTHOR = "AnDetect Team"
MAIN_SCRIPT = "profile_manager_v2.py"

def check_dependencies():
    """Перевірка та встановлення залежностей"""
    print("🔍 Перевірка залежностей...")
    
    required_packages = [
        'PyQt5>=5.15.0',
        'PyQtWebEngine>=5.15.0', 
        'PySocks>=1.7.0',
        'requests>=2.31.0',
        'cryptography>=41.0.0',
        'pyinstaller>=6.0.0'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package.startswith('pyinstaller'):
                import PyInstaller
            elif package.startswith('PyQt5'):
                import PyQt5
            elif package.startswith('PyQtWebEngine'):
                import PyQtWebEngine
            elif package.startswith('PySocks'):
                import socks
            elif package.startswith('requests'):
                import requests
            elif package.startswith('cryptography'):
                import cryptography
            print(f"✅ {package.split('>=')[0]} знайдено")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package.split('>=')[0]} не знайдено")
    
    if missing_packages:
        print(f"\n📦 Встановлення {len(missing_packages)} пакетів...")
        for package in missing_packages:
            print(f"⏳ Встановлення {package}...")
            result = subprocess.run([sys.executable, '-m', 'pip', 'install', package], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ {package} встановлено")
            else:
                print(f"❌ Помилка встановлення {package}: {result.stderr}")
                return False
    
    return True

def create_spec_file():
    """Створення .spec файлу для PyInstaller"""
    print("📝 Створення .spec файлу...")
    
    spec_content = f'''# -*- mode: python ; coding: utf-8 -*-
import sys
import os
from PyInstaller.utils.hooks import collect_all

# Збираємо всі модулі PyQt5
datas = []
binaries = []
hiddenimports = []

# PyQt5 модулі
qt_modules = [
    'PyQt5.QtCore',
    'PyQt5.QtGui', 
    'PyQt5.QtWidgets',
    'PyQt5.QtWebEngine',
    'PyQt5.QtWebEngineWidgets',
    'PyQt5.QtNetwork',
    'PyQt5.QtPrintSupport'
]

for module in qt_modules:
    try:
        tmp_ret = collect_all(module)
        datas += tmp_ret[0]
        binaries += tmp_ret[1] 
        hiddenimports += tmp_ret[2]
    except:
        pass

# Додаткові файли
datas += [
    ('browser', 'browser'),
    ('user_agents.py', '.'),
    ('profile_icons.py', '.'),
    ('profile_dialog_v2.py', '.'),
    ('README.md', '.'),
    ('QUICKSTART.md', '.'),
    ('LICENSE', '.'),
]

# Додаємо логотип якщо існує
if os.path.exists('logo.png'):
    datas += [('logo.png', '.')]
elif os.path.exists('icon.ico'):
    datas += [('icon.ico', '.')]

# Налаштування збірки
block_cipher = None

a = Analysis(
    ['{MAIN_SCRIPT}'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports + [
        'cryptography.fernet',
        'sqlite3',
        'json',
        'uuid',
        'datetime',
        'subprocess',
        'shutil',
        'random'
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'matplotlib',
        'numpy',
        'pandas',
        'PIL',
        'cv2'
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='{APP_NAME}',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # GUI додаток
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='logo.png' if os.path.exists('logo.png') else ('icon.ico' if os.path.exists('icon.ico') else None),
    version='version_info.txt'
)
'''
    
    with open(f'{APP_NAME}.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print(f"✅ Створено {APP_NAME}.spec")
    return True

def create_version_info():
    """Створення файлу версії для Windows"""
    print("📋 Створення інформації про версію...")
    
    version_info = f'''# UTF-8
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=({APP_VERSION.replace('.', ', ')}, 0),
    prodvers=({APP_VERSION.replace('.', ', ')}, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
    ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [StringStruct(u'CompanyName', u'{APP_AUTHOR}'),
        StringStruct(u'FileDescription', u'{APP_DESCRIPTION}'),
        StringStruct(u'FileVersion', u'{APP_VERSION}'),
        StringStruct(u'InternalName', u'{APP_NAME}'),
        StringStruct(u'LegalCopyright', u'© 2024 {APP_AUTHOR}'),
        StringStruct(u'OriginalFilename', u'{APP_NAME}.exe'),
        StringStruct(u'ProductName', u'AnDetect Profile Manager v2.0'),
        StringStruct(u'ProductVersion', u'{APP_VERSION}')])
      ]), 
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)'''
    
    with open('version_info.txt', 'w', encoding='utf-8') as f:
        f.write(version_info)
    
    print("✅ Створено version_info.txt")
    return True

def build_executable():
    """Збірка виконуваного файлу"""
    print("🔨 Збірка виконуваного файлу...")
    
    # Очищення попередніх збірок
    for folder in ['build', 'dist']:
        if os.path.exists(folder):
            print(f"🧹 Очищення {folder}/")
            shutil.rmtree(folder)
    
    # Запуск PyInstaller
    cmd = [
        'pyinstaller',
        f'{APP_NAME}.spec',
        '--clean',
        '--noconfirm'
    ]
    
    print(f"⚙️  Виконання: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Збірка завершена успішно")
        
        # Перевірка чи створений файл
        exe_path = f'dist/{APP_NAME}.exe'
        if os.path.exists(exe_path):
            size = os.path.getsize(exe_path) / (1024 * 1024)  # MB
            print(f"📦 Створено: {exe_path} ({size:.1f} MB)")
            return True
        else:
            print("❌ EXE файл не знайдено")
            return False
    else:
        print(f"❌ Помилка збірки: {result.stderr}")
        return False

def create_installer():
    """Створення NSIS інсталятора"""
    print("📦 Створення інсталятора...")
    
    # Перевірка NSIS
    nsis_path = None
    possible_nsis_paths = [
        r"C:\Program Files (x86)\NSIS\makensis.exe",
        r"C:\Program Files\NSIS\makensis.exe",
        "makensis.exe"
    ]
    
    for path in possible_nsis_paths:
        if shutil.which(path) or os.path.exists(path):
            nsis_path = path
            break
    
    if not nsis_path:
        print("⚠️  NSIS не знайдено, пропускаємо створення інсталятора")
        print("💡 Завантажте NSIS з https://nsis.sourceforge.io/")
        return False
    
    print(f"✅ NSIS знайдено: {nsis_path}")
    
    # Створення NSIS скрипту
    nsis_script = f'''!define APP_NAME "{APP_NAME}"
!define APP_VERSION "{APP_VERSION}"
!define APP_DESCRIPTION "{APP_DESCRIPTION}"
!define APP_AUTHOR "{APP_AUTHOR}"

Name "${{APP_NAME}} v${{APP_VERSION}}"
OutFile "{APP_NAME}_v{APP_VERSION}_Setup.exe"
InstallDir "$PROGRAMFILES\\${{APP_NAME}}"

RequestExecutionLevel admin

; Сторінки інсталятора
Page directory
Page instfiles

; Сторінки деінсталятора  
UninstPage uninstConfirm
UninstPage instfiles

Section "Основні файли"
    SetOutPath "$INSTDIR"
    
    ; Основний виконуваний файл
    File "dist\\{APP_NAME}.exe"
    
    ; Документація
    File /nonfatal "README.md"
    File /nonfatal "QUICKSTART.md" 
    File /nonfatal "LICENSE"
    
    ; Іконка
    File /nonfatal "logo.png"
    File /nonfatal "icon.ico"
    
    ; Створення ярликів
    CreateDirectory "$SMPROGRAMS\\${{APP_NAME}}"
    CreateShortCut "$SMPROGRAMS\\${{APP_NAME}}\\${{APP_NAME}}.lnk" "$INSTDIR\\{APP_NAME}.exe"
    CreateShortCut "$SMPROGRAMS\\${{APP_NAME}}\\Видалити ${{APP_NAME}}.lnk" "$INSTDIR\\Uninstall.exe"
    
    ; Ярлик на робочому столі
    CreateShortCut "$DESKTOP\\${{APP_NAME}}.lnk" "$INSTDIR\\{APP_NAME}.exe"
    
    ; Записи в реєстр
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "DisplayName" "${{APP_NAME}} v${{APP_VERSION}}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "UninstallString" "$INSTDIR\\Uninstall.exe"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "DisplayIcon" "$INSTDIR\\{APP_NAME}.exe"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "DisplayVersion" "${{APP_VERSION}}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "Publisher" "${{APP_AUTHOR}}"
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "NoModify" 1
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}" "NoRepair" 1
    
    ; Деінсталятор
    WriteUninstaller "$INSTDIR\\Uninstall.exe"
SectionEnd

; Деінсталятор
Section "Uninstall"
    ; Видалення файлів
    Delete "$INSTDIR\\{APP_NAME}.exe"
    Delete "$INSTDIR\\README.md"
    Delete "$INSTDIR\\QUICKSTART.md"
    Delete "$INSTDIR\\LICENSE"
    Delete "$INSTDIR\\logo.png"
    Delete "$INSTDIR\\icon.ico"
    Delete "$INSTDIR\\Uninstall.exe"
    
    ; Видалення ярликів
    Delete "$SMPROGRAMS\\${{APP_NAME}}\\${{APP_NAME}}.lnk"
    Delete "$SMPROGRAMS\\${{APP_NAME}}\\Видалити ${{APP_NAME}}.lnk"
    RMDir "$SMPROGRAMS\\${{APP_NAME}}"
    Delete "$DESKTOP\\${{APP_NAME}}.lnk"
    
    ; Видалення з реєстру
    DeleteRegKey HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${{APP_NAME}}"
    
    ; Видалення директорії
    RMDir "$INSTDIR"
SectionEnd'''
    
    script_path = f'{APP_NAME}_installer.nsi'
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(nsis_script)
    
    print(f"✅ Створено {script_path}")
    
    # Компіляція інсталятора
    print("🔧 Компіляція інсталятора...")
    result = subprocess.run([nsis_path, script_path], capture_output=True, text=True)
    
    if result.returncode == 0:
        installer_path = f'{APP_NAME}_v{APP_VERSION}_Setup.exe'
        if os.path.exists(installer_path):
            size = os.path.getsize(installer_path) / (1024 * 1024)  # MB
            print(f"✅ Інсталятор створено: {installer_path} ({size:.1f} MB)")
            return True
        else:
            print("❌ Інсталятор не знайдено")
            return False
    else:
        print(f"❌ Помилка створення інсталятора: {result.stderr}")
        return False

def cleanup():
    """Очищення тимчасових файлів"""
    print("🧹 Очищення тимчасових файлів...")
    
    temp_files = [
        f'{APP_NAME}.spec',
        'version_info.txt',
        f'{APP_NAME}_installer.nsi',
        'build'
    ]
    
    for item in temp_files:
        try:
            if os.path.isfile(item):
                os.remove(item)
                print(f"🗑️  Видалено файл: {item}")
            elif os.path.isdir(item):
                shutil.rmtree(item)
                print(f"🗑️  Видалено директорію: {item}")
        except Exception as e:
            print(f"⚠️  Не вдалося видалити {item}: {e}")

def main():
    """Головна функція збірки"""
    print("=" * 60)
    print(f"  🛡️ {APP_NAME} v{APP_VERSION} - Збірка інсталятора")
    print("=" * 60)
    print()
    
    # Перевірка основного файлу
    if not os.path.exists(MAIN_SCRIPT):
        print(f"❌ Основний файл {MAIN_SCRIPT} не знайдено!")
        return False
    
    steps = [
        ("Перевірка залежностей", check_dependencies),
        ("Створення .spec файлу", create_spec_file),
        ("Створення інформації про версію", create_version_info),
        ("Збірка виконуваного файлу", build_executable),
        ("Створення інсталятора", create_installer)
    ]
    
    success_count = 0
    
    for step_name, step_func in steps:
        print(f"\\n⏳ {step_name}...")
        try:
            if step_func():
                success_count += 1
                print(f"✅ {step_name} - успішно")
            else:
                print(f"❌ {step_name} - помилка")
                if step_name in ["Перевірка залежностей", "Збірка виконуваного файлу"]:
                    print("🛑 Критична помилка, зупиняємо збірку")
                    break
        except Exception as e:
            print(f"❌ {step_name} - винятка: {e}")
            if step_name in ["Перевірка залежностей", "Збірка виконуваного файлу"]:
                print("🛑 Критична помилка, зупиняємо збірку")
                break
    
    print("\\n" + "=" * 60)
    print(f"📊 Результат збірки: {success_count}/{len(steps)} етапів успішно")
    
    if success_count >= 4:  # Основні етапи пройшли
        print("🎉 Збірка завершена успішно!")
        print(f"📦 Виконуваний файл: dist/{APP_NAME}.exe")
        
        installer_path = f'{APP_NAME}_v{APP_VERSION}_Setup.exe'
        if os.path.exists(installer_path):
            print(f"💿 Інсталятор: {installer_path}")
        
        print("\\n💡 Рекомендації:")
        print("  • Протестуйте виконуваний файл перед розповсюдженням")
        print("  • Перевірте інсталятор на чистій системі")
        print("  • Створіть резервну копію збірки")
        
        # Опціональне очищення
        cleanup_choice = input("\\n🧹 Очистити тимчасові файли? (y/n): ").lower()
        if cleanup_choice in ['y', 'yes', 'так', 'т']:
            cleanup()
        
        return True
    else:
        print("❌ Збірка не завершена через помилки")
        return False

if __name__ == "__main__":
    try:
        success = main()
        input("\\nНатисніть Enter для виходу...")
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\\n\\n⏹️  Збірка перервана користувачем")
        sys.exit(1)
    except Exception as e:
        print(f"\\n\\n💥 Неочікувана помилка: {e}")
        input("Натисніть Enter для виходу...")
        sys.exit(1)

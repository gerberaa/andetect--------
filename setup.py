#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Установник для AnDetect Browser
Створює виконуваний файл за допомогою PyInstaller
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def check_pyinstaller():
    """Перевірка наявності PyInstaller"""
    try:
        import PyInstaller
        return True
    except ImportError:
        return False


def install_pyinstaller():
    """Встановлення PyInstaller"""
    print("Встановлення PyInstaller...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pyinstaller'])
        return True
    except subprocess.CalledProcessError as e:
        print(f"Помилка встановлення PyInstaller: {e}")
        return False


def create_spec_file():
    """Створення spec файлу для PyInstaller"""
    spec_content = '''
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['profile_manager_app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('browser', 'browser'),
        ('user_agents.py', '.'),
        ('README.md', '.'),
        ('QUICKSTART.md', '.'),
        ('LICENSE', '.'),
    ],
    hiddenimports=[
        'PyQt5.QtCore',
        'PyQt5.QtGui', 
        'PyQt5.QtWidgets',
        'PyQt5.QtWebEngine',
        'PyQt5.QtWebEngineWidgets',
        'PyQt5.QtWebEngineCore',
        'PyQt5.QtNetwork',
        'socks',
        'requests',
        'cryptography',
        'sqlite3',
        'user_agents',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    name='AnDetectProfileManager',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico' if os.path.exists('icon.ico') else None,
    version='version_info.txt' if os.path.exists('version_info.txt') else None,
)
'''
    
    with open('AnDetectProfileManager.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("Створено AnDetectProfileManager.spec")


def create_version_info():
    """Створення файлу з інформацією про версію"""
    version_info = '''
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(1, 0, 0, 0),
    prodvers=(1, 0, 0, 0),
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
        [StringStruct(u'CompanyName', u'AnDetect'),
        StringStruct(u'FileDescription', u'AnDetect Profile Manager - Менеджер профілів браузера'),
        StringStruct(u'FileVersion', u'1.0.0.0'),
        StringStruct(u'InternalName', u'AnDetectProfileManager'),
        StringStruct(u'LegalCopyright', u'Copyright © 2024 AnDetect'),
        StringStruct(u'OriginalFilename', u'AnDetectProfileManager.exe'),
        StringStruct(u'ProductName', u'AnDetect Profile Manager'),
        StringStruct(u'ProductVersion', u'1.0.0.0')])
      ]), 
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
'''
    
    with open('version_info.txt', 'w', encoding='utf-8') as f:
        f.write(version_info)
    
    print("Створено version_info.txt")


def build_executable():
    """Збірка виконуваного файлу"""
    print("Починаємо збірку...")
    
    try:
        # Створюємо spec файл
        create_spec_file()
        create_version_info()
        
        # Запускаємо PyInstaller
        cmd = [
            sys.executable, '-m', 'PyInstaller',
            '--clean',
            '--noconfirm',
            'AnDetectProfileManager.spec'
        ]
        
        subprocess.check_call(cmd)
        
        print("\n✅ Збірка завершена успішно!")
        print("Виконуваний файл: dist/AnDetectProfileManager.exe")
        
        # Очищаємо тимчасові файли
        cleanup_temp_files()
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Помилка збірки: {e}")
        return False


def cleanup_temp_files():
    """Очищення тимчасових файлів"""
    temp_files = ['AnDetectProfileManager.spec', 'version_info.txt']
    temp_dirs = ['build', '__pycache__']
    
    for file in temp_files:
        if os.path.exists(file):
            try:
                os.remove(file)
                print(f"Видалено {file}")
            except Exception as e:
                print(f"Не вдалося видалити {file}: {e}")
    
    for dir_name in temp_dirs:
        if os.path.exists(dir_name):
            try:
                shutil.rmtree(dir_name)
                print(f"Видалено директорію {dir_name}")
            except Exception as e:
                print(f"Не вдалося видалити {dir_name}: {e}")


def create_installer():
    """Створення інсталятора (потребує NSIS)"""
    nsis_script = '''
;AnDetect Browser Installer
;Generated by setup.py

!define APPNAME "AnDetect Browser"
!define COMPANYNAME "AnDetect"
!define DESCRIPTION "Анонімний браузер з підтримкою профілів"
!define VERSIONMAJOR 1
!define VERSIONMINOR 0
!define VERSIONBUILD 0
!define HELPURL "https://github.com/yourusername/andetect-browser"
!define UPDATEURL "https://github.com/yourusername/andetect-browser/releases"
!define ABOUTURL "https://github.com/yourusername/andetect-browser"
!define INSTALLSIZE 50000

RequestExecutionLevel admin
InstallDir "$PROGRAMFILES\\${COMPANYNAME}\\${APPNAME}"
LicenseData "LICENSE"
Name "${APPNAME}"
Icon "icon.ico"
outFile "AnDetectProfileManager_Setup.exe"

!include LogicLib.nsh

page license
page directory
page instfiles

!macro VerifyUserIsAdmin
UserInfo::GetAccountType
pop $0
${If} $0 != "admin"
    messageBox mb_iconstop "Administrator rights required!"
    setErrorLevel 740
    quit
${EndIf}
!macroend

function .onInit
    setShellVarContext all
    !insertmacro VerifyUserIsAdmin
functionEnd

section "install"
    setOutPath $INSTDIR
    file "dist\\AnDetectProfileManager.exe"
    file "README.md"
    file "QUICKSTART.md"
    
    writeUninstaller "$INSTDIR\\uninstall.exe"
    
    createDirectory "$SMPROGRAMS\\${COMPANYNAME}"
    createShortCut "$SMPROGRAMS\\${COMPANYNAME}\\${APPNAME}.lnk" "$INSTDIR\\AnDetectProfileManager.exe"
    createShortCut "$DESKTOP\\${APPNAME}.lnk" "$INSTDIR\\AnDetectProfileManager.exe"
    
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}" "DisplayName" "${APPNAME}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}" "UninstallString" "$INSTDIR\\uninstall.exe"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}" "InstallLocation" "$INSTDIR"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}" "DisplayIcon" "$INSTDIR\\AnDetectProfileManager.exe"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}" "Publisher" "${COMPANYNAME}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}" "HelpLink" "${HELPURL}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}" "URLUpdateInfo" "${UPDATEURL}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}" "URLInfoAbout" "${ABOUTURL}"
    WriteRegStr HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}" "DisplayVersion" "${VERSIONMAJOR}.${VERSIONMINOR}.${VERSIONBUILD}"
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}" "VersionMajor" ${VERSIONMAJOR}
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}" "VersionMinor" ${VERSIONMINOR}
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}" "NoModify" 1
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}" "NoRepair" 1
    WriteRegDWORD HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}" "EstimatedSize" ${INSTALLSIZE}
sectionEnd

section "uninstall"
    delete "$INSTDIR\\AnDetectProfileManager.exe"
    delete "$INSTDIR\\README.md"
    delete "$INSTDIR\\QUICKSTART.md"
    delete "$INSTDIR\\uninstall.exe"
    rmDir "$INSTDIR"
    
    delete "$SMPROGRAMS\\${COMPANYNAME}\\${APPNAME}.lnk"
    rmDir "$SMPROGRAMS\\${COMPANYNAME}"
    delete "$DESKTOP\\${APPNAME}.lnk"
    
    DeleteRegKey HKLM "Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\${APPNAME}"
sectionEnd
'''
    
    with open('installer.nsi', 'w', encoding='utf-8') as f:
        f.write(nsis_script)
    
    print("Створено installer.nsi")
    print("Для створення інсталятора запустіть: makensis installer.nsi")


def main():
    """Головна функція"""
    print("=" * 50)
    print("   AnDetect Browser - Установник")
    print("=" * 50)
    print()
    
    # Перевірка PyInstaller
    if not check_pyinstaller():
        print("PyInstaller не знайдено.")
        if not install_pyinstaller():
            print("❌ Не вдалося встановити PyInstaller")
            sys.exit(1)
    
    print("✅ PyInstaller готовий")
    
    # Перевірка залежностей
    print("Перевірка залежностей...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("✅ Залежності встановлено")
    except subprocess.CalledProcessError:
        print("❌ Помилка встановлення залежностей")
        sys.exit(1)
    
    # Збірка
    if build_executable():
        print("\n🎉 AnDetect Profile Manager успішно зібрано!")
        
        # Створення NSIS скрипта
        create_installer()
        
        print("\nФайли:")
        print("- Виконуваний файл: dist/AnDetectProfileManager.exe")
        print("- NSIS скрипт: installer.nsi")
        print()
        print("Для тестування запустіть: dist/AnDetectProfileManager.exe")
    else:
        print("\n❌ Збірка не вдалася")
        sys.exit(1)


if __name__ == "__main__":
    main()

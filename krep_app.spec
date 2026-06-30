# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec для сборки krep_app в один исполняемый файл.

macOS:  dist/krep_app   (Unix-бинарник)
Windows: dist/krep_app.exe (при запуске pyinstaller на Windows)
"""

from PyInstaller.utils.hooks import collect_all, collect_submodules

# Собираем все данные и скрытые импорты тяжёлых библиотек
pandas_datas, pandas_binaries, pandas_hiddenimports = collect_all('pandas')
openpyxl_datas, openpyxl_binaries, openpyxl_hiddenimports = collect_all('openpyxl')

a = Analysis(
    ['entry.py'],
    pathex=['.'],
    binaries=pandas_binaries + openpyxl_binaries,
    datas=[
        # HTML-шаблон — кладём в корень _MEIPASS/templates/
        ('src/krep_app/templates', 'templates'),
        *pandas_datas,
        *openpyxl_datas,
    ],
    hiddenimports=[
        'flask',
        'jinja2',
        'werkzeug',
        'itsdangerous',
        'click',
        *pandas_hiddenimports,
        *openpyxl_hiddenimports,
        *collect_submodules('dateutil'),
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'scipy', 'PIL', 'IPython', 'jupyter'],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='krep_app',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,   # показывать консоль (там выводится URL сервера)
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

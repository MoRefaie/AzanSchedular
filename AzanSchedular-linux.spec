# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_all

packages = [
    'bs4',
    'pyatv',
    'dateutil',
    'requests',
    'tenacity',
    'fastapi',
    'uvicorn',
    'pillow',
    'aiofiles',
    'python-multipart',
]

all_datas = []
all_binaries = []
all_hiddenimports = []

for pkg in packages:
    datas, binaries, hiddenimports = collect_all(pkg)
    all_datas += datas
    all_binaries += binaries
    all_hiddenimports += hiddenimports

a = Analysis(
    ['AzanSchedular/azan_app.py'],
    pathex=[],
    binaries=all_binaries,
    datas=[
        ('AzanSchedular/*.py', '.'),
        ('config/*', 'config'),
        ('media/*', 'media'),
    ] + all_datas,
    hiddenimports=all_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='AzanSchedular',
    debug=False,
    console=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    disable_windowed_traceback=False,
    icon='media/icon.png',
)

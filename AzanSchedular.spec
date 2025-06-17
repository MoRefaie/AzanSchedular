# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_all

# List of packages to collect for hidden imports, datas, and binaries
packages = [
    'bs4',
    'pyatv',
    'dateutil',
    'requests',
    'tenacity',
    'fastapi',
    'uvicorn',
    'pystray',
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

# Add all config and media files
extra_datas = [
    ('AzanSchedular/*.py', '.'),
    ('config/*', 'config'),
    ('media/*', 'media'),
]

# Analysis
a = Analysis(
    ['AzanSchedular/azan_app.py'],
    pathex=[],
    binaries=all_binaries,
    datas=extra_datas + all_datas,
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
    icon='media/icon.ico',
)

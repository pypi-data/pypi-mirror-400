# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path

block_cipher = None

PROJECT_ROOT = str(Path.cwd())

a = Analysis(
    ['src/esn_tool/cli.py'],
    pathex=[PROJECT_ROOT],
    binaries=[],
    datas=[],
    hiddenimports=[
        'click',
        'rich',
        'httpx',
        'questionary',
        'textual',
        'esn_tool.commands',
        'esn_tool.services',
        'esn_tool.ui',
        'esn_tool.utils',
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
    name='esn',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch='arm64',
    codesign_identity=None,
    entitlements_file=None,
)

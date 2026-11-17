# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# CustomTkinter 데이터 파일 수집
datas = collect_data_files('customtkinter')

# tools 및 assets 번들링 (7z, lz4, zstd, 아이콘 리소스 등 완전 독립 실행 지원)
tools_dir = os.path.abspath('tools')
if os.path.exists(tools_dir):
    datas.append((tools_dir, 'tools'))

assets_dir = os.path.abspath('assets')
if os.path.exists(assets_dir):
    datas.append((assets_dir, 'assets'))

# hidden imports
hiddenimports = [
    'customtkinter',
    'windnd',
    'darkdetect',
    'winreg',
    'ctypes',
    'multiprocessing',
    'zipper9_ui',
    'zipper9_ui.app',
    'zipper9_ui.bridge',
    'zipper9_ui.bridge.worker',
    'zipper9_ui.bridge.context_menu',
    'zipper9_ui.bridge.file_association',
    'zipper9_ui.bridge.instant_ops',
    'zipper9_ui.bridge.settings',
    'zipper9_ui.bridge.i18n',
]
hiddenimports += collect_submodules('customtkinter')
hiddenimports += collect_submodules('zipper9_ui')

root_dir = os.path.abspath('.')

a = Analysis(
    ['main.py'],
    pathex=[root_dir],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
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
    name='zipper9',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

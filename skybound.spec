# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_all

block_cipher = None

# Define all game assets
added_files = [
    ('imgs/*.png', 'imgs'),
    ('imgs/*.json', 'imgs'),
    ('sfxs/*.ogg', 'sfxs'),
    ('font/*.ttf', 'font'),
    ('txts/*.json', 'txts')
]

# Force-collect numpy in full. PyInstaller's static analysis misses some of
# numpy's lazily-imported submodules (e.g. numpy._core._exceptions, pulled in by
# the multiarray C-extension stub), which makes the frozen numpy fail to import
# its C-extensions at runtime. collect_all bundles every submodule, data file,
# and shared library so numpy initializes correctly.
numpy_datas, numpy_binaries, numpy_hiddenimports = collect_all('numpy')

import sys
import sysconfig
import os

# On Linux, PyInstaller needs libpython bundled explicitly.
# Detect dynamically so the spec works on any Python version / arch.
# On Windows, PyInstaller's built-in hooks handle pythonXY.dll automatically.
if sys.platform.startswith('linux'):
    _libdir = sysconfig.get_config_var('LIBDIR') or ''
    _ldlib  = sysconfig.get_config_var('LDLIBRARY') or ''
    _libpath = os.path.join(_libdir, _ldlib)
    libpython_binaries = [(_libpath, '.')] if os.path.isfile(_libpath) else []
else:
    libpython_binaries = []

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=libpython_binaries + numpy_binaries,
    datas=added_files + numpy_datas,
    hiddenimports=['pygame'] + numpy_hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(
    a.pure, 
    a.zipped_data,
    cipher=block_cipher
)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Skybound',
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
    icon='icon.ico',
)

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

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[('/usr/lib/x86_64-linux-gnu/libpython3.12.so.1.0', '.')] + numpy_binaries,
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

# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['finapp.py'],
    pathex=['C:\\project\\python\\finapp2'],
    binaries=[],
    datas=[('style.qss','.'), ('m1.csv','.')],  # Include both trades folder and logo
    hiddenimports=['PyQt5.sip'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tensorflow', 'torch'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None, # chenged from block_cipher
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='finapp',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='finapp',
)

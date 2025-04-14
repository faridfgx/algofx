# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('fxlogo.png', '.'),  # Changed to place in root directory
        ('icons', 'icons'),
        ('fonts', 'fonts'),
    ],
    hiddenimports=[],  # Add specific imports your app needs
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'numpy', 'pandas', 'scipy', 'PIL'],  # Exclude large libraries if not used
    noarchive=False,
    optimize=2,  # Increased optimization level
)

pyz = PYZ(a.pure, optimize=2)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='main',
    debug=False,
    bootloader_ignore_signals=False,
    strip=True,  # Strip symbols to reduce size
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,  # Keep as None for architecture of current Python
    codesign_identity=None,
    entitlements_file=None,
    icon='fxlogo.ico',
    uac_admin=False,  # No admin rights required (better compatibility)
)
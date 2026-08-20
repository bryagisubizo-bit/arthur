# -*- mode: python ; coding: utf-8 -*-


from PyInstaller.utils.hooks import collect_data_files, collect_submodules


openwakeword_datas = collect_data_files("openwakeword")
openwakeword_hiddenimports = collect_submodules("openwakeword") + ["onnxruntime", "sounddevice"]


a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=[('assets/arthur_hawk.svg', 'assets'), ('assets/arthur_hawk.ico', 'assets')] + openwakeword_datas,
    hiddenimports=openwakeword_hiddenimports,
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
    [],
    exclude_binaries=True,
    name='Arthur',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon='assets/arthur_hawk.ico',
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
    name='Arthur',
)

# -*- mode: python ; coding: utf-8 -*-

import os.path

import ase.collections


hiddenimports = []
datas = [
    ('src/molecular_dynamics_toy/data/structures/*', 'molecular_dynamics_toy/data/structures'),
    (os.path.join(os.path.dirname(ase.collections.__file__), 'g2.json'), 'ase/collections'),
    ('ThirdPartyNotices.html', '.'),
    ('LICENSE.txt', '.'),
]
excludes = []

a = Analysis(
    ['src/molecular_dynamics_toy/__main__.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    noarchive=False,
    optimize=1,
	module_collection_mode = {
		'torch_geometric': 'pyz+py',
		'torch_runstats': 'pyz+py',
		'mattersim': 'pyz+py',
		'e3nn': 'pyz+py',
	},
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='MDToy',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
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
    name='MDToy',
)
app = BUNDLE(
    coll,
    name='MDToy.app',
    icon=None,
    bundle_identifier=None,
)

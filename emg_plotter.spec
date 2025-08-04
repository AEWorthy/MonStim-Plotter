# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

# Get the current directory
current_dir = Path.cwd()

# Define the main script
main_script = 'launcher.py'

# Define additional data files to include
added_files = [
    ('Example Data 1.csv', '.'),
    ('Example Data 2.csv', '.'),
    ('Example Data 3.csv', '.'),
    ('README.md', '.'),
    ('README_GUI.md', '.'),
    ('src/icon.png', 'src'),  # Include icon for GUI
    ('src/logo.png', 'src'),  # Include logo
    ('src/icon.ico', 'src'),  # Include logo ICO for Windows
    ('src/info.png', 'src'),  # Include info image
]

# Find all CSV files in CA26 Project folder if it exists
ca26_folder = current_dir / 'CA26 Project'
if ca26_folder.exists():
    for csv_file in ca26_folder.glob('*.csv'):
        added_files.append((str(csv_file), 'CA26 Project'))

block_cipher = None

a = Analysis(
    [main_script],
    pathex=[str(current_dir)],
    binaries=[],
    datas=added_files,
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtGui', 
        'PyQt6.QtWidgets',
        'matplotlib.backends.backend_qt5agg',
        'matplotlib.backends.backend_agg',
        'matplotlib.backends._backend_agg',
        'matplotlib',
        'matplotlib.pyplot',
        'matplotlib.cm',
        'matplotlib.colors',
        'pandas',
        'pandas._libs',
        'pandas._libs.tslibs',
        'numpy',
        'numpy.core',
        'numpy.core._multiarray_umath',
        'numpy.core._multiarray_tests',
        'numpy.linalg._umath_linalg',
        'numpy.random._common',
        'numpy.random.bit_generator',
        'numpy.random._bounded_integers',
        'numpy.random._mt19937',
        'numpy.random.mtrand',
        'numpy.random._philox',
        'numpy.random._pcg64',
        'numpy.random._sfc64',
        'numpy.random._generator',
        'plot_emg',
        'PIL',
        'PIL.Image',
        'PIL._tkinter_finder',
        'argparse',
        'datetime',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'PyQt5',
        'PySide2',
        'PySide6',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
    optimize=0,  # Don't optimize to avoid potential issues
)

# Remove duplicate entries and sort
a.datas = list(set(a.datas))

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='MonStim Plotter',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to True if you want console output for debugging
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='src/icon.ico'
)

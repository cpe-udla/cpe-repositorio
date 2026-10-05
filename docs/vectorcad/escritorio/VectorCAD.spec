# -*- mode: python ; coding: utf-8 -*-
"""
Spec de PyInstaller para VectorCAD (macOS).

    pyinstaller --noconfirm --clean VectorCAD.spec

Produce dist/VectorCAD.app, autónomo: incluye el intérprete de Python y Qt, de
modo que funciona en un Mac sin Python instalado.
"""

import os

ROOT = os.path.abspath(os.getcwd())
ICON = os.path.join(ROOT, "VectorCAD.icns")
if not os.path.exists(ICON):
    ICON = None

DATAS = []
for extra in ("ejemplo.scr", "README.md"):
    p = os.path.join(ROOT, extra)
    if os.path.exists(p):
        DATAS.append((p, "."))

# Módulos que no usa la aplicación: recortarlos reduce el bundle a la mitad.
EXCLUDES = [
    "PyQt5", "PyQt6", "tkinter", "matplotlib", "PIL", "pytest", "IPython",
    "notebook", "pandas", "scipy", "setuptools._distutils",
    "PySide6.QtWebEngineCore", "PySide6.QtWebEngineWidgets", "PySide6.QtWebEngineQuick",
    "PySide6.QtQml", "PySide6.QtQuick", "PySide6.QtQuick3D", "PySide6.QtQuickWidgets",
    "PySide6.Qt3DCore", "PySide6.Qt3DRender", "PySide6.Qt3DAnimation", "PySide6.Qt3DExtras",
    "PySide6.QtMultimedia", "PySide6.QtMultimediaWidgets", "PySide6.QtCharts",
    "PySide6.QtDataVisualization", "PySide6.QtGraphs", "PySide6.QtBluetooth",
    "PySide6.QtNfc", "PySide6.QtPositioning", "PySide6.QtLocation", "PySide6.QtSensors",
    "PySide6.QtSerialPort", "PySide6.QtSql", "PySide6.QtTest", "PySide6.QtDesigner",
    "PySide6.QtHelp", "PySide6.QtRemoteObjects", "PySide6.QtScxml", "PySide6.QtSpatialAudio",
    "PySide6.QtTextToSpeech", "PySide6.QtWebChannel", "PySide6.QtWebSockets",
]

a = Analysis(
    ["vectorcad.py"],
    pathex=[ROOT],
    binaries=[],
    datas=DATAS,
    hiddenimports=["ezdxf", "shapely"],
    hookspath=[],
    runtime_hooks=[],
    excludes=EXCLUDES,
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="VectorCAD",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,         # innecesario: la app atiende QFileOpenEvent en Qt
    target_arch=None,             # None = arquitectura de la máquina que compila
    codesign_identity=None,
    entitlements_file=None,
    icon=ICON,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="VectorCAD",
)

app = BUNDLE(
    coll,
    name="VectorCAD.app",
    icon=ICON,
    bundle_identifier="cl.ceprodep.vectorcad",
    version="5.0",
    info_plist={
        "CFBundleName": "VectorCAD",
        "CFBundleDisplayName": "VectorCAD",
        "CFBundleShortVersionString": "5.0",
        "CFBundleVersion": "5.0",
        "LSMinimumSystemVersion": "11.0",
        "NSHighResolutionCapable": True,
        "NSRequiresAquaSystemAppearance": False,
        "LSApplicationCategoryType": "public.app-category.graphics-design",
        "CFBundleDocumentTypes": [
            {
                "CFBundleTypeName": "Dibujo VectorCAD",
                "CFBundleTypeRole": "Editor",
                "LSHandlerRank": "Owner",
                "CFBundleTypeExtensions": ["vcad"],
            },
            {
                "CFBundleTypeName": "Dibujo DXF",
                "CFBundleTypeRole": "Editor",
                "LSHandlerRank": "Alternate",
                "CFBundleTypeExtensions": ["dxf"],
            },
            {
                "CFBundleTypeName": "Dibujo DWG",
                "CFBundleTypeRole": "Viewer",
                "LSHandlerRank": "Alternate",
                "CFBundleTypeExtensions": ["dwg"],
            },
        ],
    },
)

# -*- mode: python ; coding: utf-8 -*-
import os

# data 디렉토리가 없으면 생성
if not os.path.exists('data'):
    os.makedirs('data')

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('data', 'data'),  # data 디렉토리 포함
        ('image/hshell.ico', 'image'),  # 아이콘 파일 포함
    ],
    hiddenimports=[
        'cryptography',
        'paramiko',
        'PyQt5',
        'pyte',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=2,  # 최적화 레벨 2로 설정
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Hshell',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # GUI 모드
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['image/hshell.ico'],
    version='file_version_info.txt',  # 버전 정보 포함
)

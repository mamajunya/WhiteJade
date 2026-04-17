# -*- mode: python ; coding: utf-8 -*-
# 简化版打包配置 - 减少依赖冲突

block_cipher = None

a = Analysis(
    ['gui_app.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('icon.png', '.'),
        ('environment_checker.py', '.'),
        ('environment_dialog.py', '.'),
        ('model', 'model'),  # 打包整个 model 目录（包含 .h5 模型文件）
    ],
    hiddenimports=[
        'PyQt6.QtCore',
        'PyQt6.QtGui',
        'PyQt6.QtWidgets',
        'pixivpy3',
        'gppt',
        'json',
        'pathlib',
        'pixiv_downloader',
        'pixiv_downloader.pixiv_downloader',
        'image_moderator',
        'image_moderator.deepdanbooru_moderator',
        'deepdanbooru',
        'deepdanbooru.project',
        'deepdanbooru.commands',
        'tensorflow',
        'tensorflow.keras',
        'tensorflow.keras.models',
        'numpy',
        'PIL',
        'PIL.Image',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'pandas',
        'pytest',
        'IPython',
        'jupyter',
        'notebook',
        'tensorboard',
        'jax',
        'torch',
        'torchvision',
        'torchaudio',
        'torch.distributed',
        'torch.nn',
        'torch.optim',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='WhiteJade',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # 临时启用控制台以便调试
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.png',  # 设置 exe 文件图标
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='WhiteJade',
)

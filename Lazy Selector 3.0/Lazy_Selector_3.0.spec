# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['Lazy_Selector_3.0.py'],
             pathex=['C:\\Users\\code\\Desktop\\Third Year\\Codes\\Lazy Selector 3.0'],
             binaries=[],
             datas=[("data","data")],
             hiddenimports=['plyer.platforms.win.notification','plyer.platforms.win.battery'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='Lazy_Selector_3.0',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True , icon='C:\\Users\\code\\Desktop\\Third Year\\Codes\\Lazy Selector 3.0\\data\\musicapp.ico')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='Lazy_Selector_3.0')

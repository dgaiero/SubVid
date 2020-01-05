# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['SubVid.py'],
             pathex=['C:\\Users\\dgaiero\\OneDrive - California Polytechnic State University\\Documents\\projects\\SubVid'],
             binaries=[],
             datas=[('LICENSE.LGPL', '.'), ('COPYING.LESSER', '.')],
             hiddenimports=[],
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
          name='SubVid',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False,
          version='_version.txt',
          icon='default_icon.ico'
         )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='SubVid')

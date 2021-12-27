from datetime import datetime
import os
from platform import version

import PyInstaller.__main__
from dotenv import load_dotenv
from version import Version

VS_VERSION_INFO = """
# UTF-8
#
# For more details about fixed file info 'ffi' see:
# http://msdn.microsoft.com/en-us/library/ms646997.aspx
VSVersionInfo(
    ffi=FixedFileInfo(
        # filevers and prodvers should be always a tuple with four items: (1, 2, 3, 4)
        # Set not needed items to zero 0.
        filevers=({file_vers}),
        prodvers=({prod_vers}),
        # Contains a bitmask that specifies the valid bits 'flags'r
        mask=0x17,
        # Contains a bitmask that specifies the Boolean attributes of the file.
        flags=0x0,
        # The operating system for which this file was designed.
        # 0x4 - NT and there is no need to change it.
        OS=0x4,
        # The general type of file.
        # 0x1 - the file is an application.
        fileType=0x1,
        # The function of the file.
        # 0x0 - the function is not defined for this fileType
        subtype=0x0,
        # Creation date and time stamp.
        date=(0, 0)
    ),
    kids=[
        StringFileInfo(
            [
                StringTable(
                    u'040904b0',
                    [StringStruct(u'CompanyName', u'Firelight'),
                     StringStruct(u'FileDescription', u'SubVideo'),
                     StringStruct(u'FileVersion', u'{file_vers_str}'),
                     StringStruct(u'InternalName', u'subvid_exe'),
                     StringStruct(u'LegalCopyright',
                                  u'Copyright {year} Dominic Gaiero.'),
                     StringStruct(u'OriginalFilename', u'SubVid.exe'),
                     StringStruct(u'ProductName', u'SubVideo'),
                     StringStruct(u'ProductVersion', u'{prod_vers_str}'),
                     StringStruct(u'CompanyShortName', u'Firelight'),
                     StringStruct(u'ProductShortName', u'SubVid')])
            ]),
        VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
    ]
)

"""


def build_executable():
    load_dotenv()
    PyInstaller.__main__.run([
        'SubVid.py',
        '--key', os.environ.get('ENCRYPTION_KEY'),
        '--version-file', 'file_version_info.txt',
        '--noconfirm',
        '--noconsole',
        '--clean',
        '--icon', 'default_icon.ico',
        '--add-data', 'default_icon.ico;.',
        '--add-data', 'LICENSE.LGPL;.',
        '--add-data', 'COPYING.LESSER;.',
        '--add-data', 'file_icon.ico;.'
    ])

def main():
    version_info = Version()
    version_info.read_file()
    version_info.update_version()
    version_info.write_file()
    vs_version_info_vars = {
        'file_vers': f'{version_info.yr}, {version_info.month}, {version_info.day}, {version_info.inc}',
        'prod_vers': f'{version_info.yr}, {version_info.month}, {version_info.day}, {version_info.inc}',
        'file_vers_str': version_info,
        'prod_vers_str': version_info,
        'year': datetime.now().year
    }
    vs_version_info = VS_VERSION_INFO.format(**vs_version_info_vars)
    with open('file_version_info.txt', 'w') as f:
        f.write(vs_version_info)
    build_executable()

if __name__ == "__main__":
    main()

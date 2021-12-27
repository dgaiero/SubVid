import subprocess
from pathlib import Path
from MakeExecutable import main as MakeExecutableFile
from version import Version
import os

install_script_template = Path(os.path.dirname(os.path.realpath(__file__))) / 'template' / 'install_script.iss'
version_info = Version()
version_info.read_file()

with open(install_script_template) as f:
    template_text = f.read()
    template_text = template_text.replace(r'{{AppVersion}}', str(version_info))

with open('install_script_tmp.iss', 'w') as f:
    f.write(template_text)

iss_loc = Path.cwd() / 'install_script_tmp.iss'
compil32_path = Path('C:/Program Files (x86)/Inno Setup 6') / 'iscc'

print('Making Executable')
MakeExecutableFile()
print('Compiling Installer')
subprocess.check_call([compil32_path, '/Qp', str(iss_loc)])

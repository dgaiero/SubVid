import subprocess
from pathlib import Path
from MakeExecutable import main as MakeExecutableFile
from version import Version
import os
import shutil


current_path = Path(os.path.dirname(os.path.realpath(__file__)))
install_script_template = current_path / 'template' / 'install_script.iss'

installer_executable_path = current_path / 'dist' / 'installer'
version_info = Version()
version_info.read_file()

if os.path.exists(installer_executable_path) and os.path.isdir(installer_executable_path):
    print("removing old installers")
    shutil.rmtree(installer_executable_path)

print('Making Executable')
MakeExecutableFile()
version_info.read_file()
print('Compiling Installer')
with open(install_script_template) as f:
    template_text = f.read()
    template_text = template_text.replace(r'{{AppVersion}}', str(version_info))

with open('install_script_tmp.iss', 'w') as f:
    f.write(template_text)

iss_loc = Path.cwd() / 'install_script_tmp.iss'
compil32_path = Path('C:/Program Files (x86)/Inno Setup 6') / 'iscc'
subprocess.check_call([compil32_path, '/Qp', str(iss_loc)])

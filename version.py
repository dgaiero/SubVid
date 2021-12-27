from pathlib import Path
import re
from datetime import datetime

class Version:

    def __init__(self):
        self.reset_date()
        self.inc = 0
        self.isdev = ''

    def read_file(self):
        version_file = Path('_version.py')
        version_pattern = r"(?P<year>\d\d\d\d).(?P<month>\d+).(?P<day>\d+).(?P<inc>\d+)(?P<isdev>\+dev|)"
        if version_file.exists():
            with open('_version.py') as f:
                verion_line = f.readline()
            version_info = re.search(version_pattern, verion_line)
            self.yr = version_info.group('year')
            self.month = version_info.group('month')
            self.day = version_info.group('day')
            self.inc = int(version_info.group('inc'))
            self.isdev = version_info.group('isdev')
        else:
            self.reset_date()
            self.inc = 0
            self.isdev = ''

    def reset_date(self):
        self.yr = datetime.now().year
        self.month = datetime.now().month
        self.day = datetime.now().day

    def write_file(self, isdev=False):
        if isdev:
            self.isdev = '+dev'
        with open('_version.py', 'w') as f:
            f.write(
                f"__version__ = '{self.__repr__()}'\n")

    def __repr__(self) -> str:
        return f'{self.yr}.{self.month}.{self.day}.{self.inc}{self.isdev}'

    def update_version(self):
        version_date = datetime.strptime(f'{self.yr}.{self.month}.{self.day}', r'%Y.%m.%d')
        if version_date.date() < datetime.now().date():
            self.inc = 1
            self.reset_date()
        else:
            self.inc = self.inc + 1

def main():
    version = Version()
    version.read_file()
    version.update_version()
    version.write_file(isdev='+dev')
    print(version)

if __name__ == "__main__":
    main()

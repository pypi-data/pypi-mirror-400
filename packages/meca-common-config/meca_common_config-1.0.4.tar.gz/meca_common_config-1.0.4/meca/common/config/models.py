import os
import sys
from configparser import ConfigParser
from pathlib import Path
from typing import List


class ConfigDict(dict):

    def __init__(self, appname: str, encoding='utf-8'):
        self.appname = appname
        self.name = f'{appname}.ini'
        self.config = ConfigParser()
        self.platform = sys.platform.lower()
        self.__init_paths__()
        self.config.read(self.paths, encoding=encoding)
        super().__init__(**self.config)
        del self['DEFAULT']

    def __init_paths__(self):
        self.__paths: List[Path] = []
        match self.platform:
            case "linux":
                self.paths = Path('/etc/')/self.name
                self.paths = Path(os.environ.get('HOME'))/"etc"/self.name
            case "win32":
                self.paths = Path(os.environ['ProgramData'])/self.name
                self.paths = Path(os.environ['APPDATA'])/self.name
            case _:
                raise NotImplementedError(f'{self.platform}')
        self.paths = Path('etc.ini')

    @property
    def paths(self) -> List[Path]:
        return self.__paths

    @paths.setter
    def paths(self, value):
        self.__paths.append(value)

    def show(self):
        paths = self.paths
        for path in paths:
            print(path.absolute())

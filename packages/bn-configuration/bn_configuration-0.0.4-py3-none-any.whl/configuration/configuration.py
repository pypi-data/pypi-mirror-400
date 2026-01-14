from configparser import ConfigParser
import os
import logging
import sys
from typing import List, Optional, Dict, Any, Union

log = logging.getLogger('config-reader')
logging.basicConfig(level=logging.INFO)

class MyConfig:
    def __init__(
        self,
        section: str,
        options: Optional[List[str]] = None
    ):
        """
        usage examples:
        A/ vrm = MyConfig('vrm', ['url','key','secret']) > vrm.url
        B/ vrm = MyConfig('vrm') > vrm.get('url')
        :param section: required, the section in the inifile; PREFIX_ in env
        :param options: options to be set as attribute
        """
        self.section = section
        self.options = options or []
        self.ini_file_tail = '.ini'
        self._inis = self.parse_ini()
        self.set_options()

    def __repr__(self):
        return f'Config {self.section} {self.options_loaded}'

    @property
    def options_loaded(self):
        return {i: len(self.__getattribute__(i)) > 0 for i in self.options}

    def valid(self):
        return all(self.options_loaded.values())

    def set_options(self):
        for option in self.options:
            self.__setattr__(option, self.get_option(option))

    def get(self, option):
        return self.get_option(self, option)

    def get_option(self, option):
        var = self.env_var(option)
        if var in os.environ:
            return os.environ[var]
        return self._inis.get(option, '')

    def parse_ini(self):
        def find(map):
            for file in os.listdir(map):
                if file.endswith(self.ini_file_tail):
                    yield f'{map}/{file}'

        root = os.path.dirname(os.path.abspath(sys.argv[0]))
        files = [f for f in find(root)]
        results = {}
        if files:
            cp = ConfigParser()
            cp.read(files)
            if self.section in cp:
                results.update({option: cp[self.section][option] for option in cp[self.section]})
        return results

    def env_var(self, option=''):
        return f'{self.section.upper()}_{option.upper()}'
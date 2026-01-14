import shutil
import sys

from ...types.he import He
from ....functions.builtins import terminal
from ....functions.decorators import parse_self_x_item_value_or_set_by_instance_he_by_module_name, \
    parse_self_x_item_value, parse_self_x_item_value_or_set_by_func


class PipPublisher(He):
    def __init__(self, u, name:str):
        super().__init__(u)
        self.configs.name = name
        self.__x__['___version_file___'] = self.__si__.working_folder.child_file('pyproject.vers')
        self.__x__['___project_file___'] = self.__si__.working_folder.child_file('pyproject.toml')
        if self.___version_file___.is_exists():
            v1, v2, v3 = self.___version_file___.read_content().split('.')
            self.configs.version = '.'.join([v1, v2, str(int(v3) + 1)])
        else:
            self.configs.version = '0.0.1'

    @property
    @parse_self_x_item_value_or_set_by_instance_he_by_module_name()
    def configs(self): return

    @property
    @parse_self_x_item_value()
    def ___version_file___(self): return

    @property
    @parse_self_x_item_value()
    def ___project_file___(self): return

    @property
    @parse_self_x_item_value_or_set_by_func()
    def ___dist_folder___(self): return self.__si__.working_folder.child_file('dist')


    def save_peoject_file(self):
        requirements = []
        requirements_file = self.__si__.working_folder.child_file('requirements.txt')
        if requirements_file.is_exists():
            lines = requirements_file.read_lines()
            requirements = [line.strip() for line in lines if line.strip() and not line.strip().startswith("#")]
        requirements_toml = ', '.join(f'"{r}"' for r in requirements)
        d = [
            '[build-system]',
            'requires = ["setuptools>=61.0", "wheel"]',
            'build-backend = "setuptools.build_meta"',
            '[project]',
            f'name = "{self.configs.name}"',
            f'version = "{self.configs.version}"',
            'description = "Hebill"',
            'readme = "README.MD"',
            'requires-python = ">=3.12"',
            'authors = [{ name = "He Bill", email = "hebill@hebill.net" }]',
            'license = "MIT"',
            'license-files = [',
            '    "LICENSE"',
            ']',
            f'dependencies = [{requirements_toml}]',
            '[tool.setuptools]',
            'include-package-data = true',

            '[tool.setuptools.packages.find]',
            'where = ["."]',
            'include = ["hebill", "hebill.*"]',

            '[tool.setuptools.package-data]',
            'hebill = ["**/*"]',
        ]
        self.___project_file___.save_content('\n'.join(d))

    def pack(self):
        self.save_peoject_file()
        self.___version_file___.save_content(self.configs.version)
        if self.___dist_folder___.is_exists():
            shutil.rmtree(self.___dist_folder___)
        cmd = [sys.executable, "-m", "build"]
        self.__sd__.output.info(f'开始执行命令：{' '.join(cmd)}')
        terminal(cmd)
        cmd = [sys.executable, "-m", "twine", "upload", "dist/*"]
        self.__sd__.output.info(f'命令执行完毕，你可以手动执行上传：{' '.join(cmd)}')


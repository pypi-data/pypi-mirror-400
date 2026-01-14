import os
import subprocess
from ..folder import Folder
from ..mod_type import ModType
from ...types.he import He
from ....functions.builtins import HeEro
from ....functions.decorators import parse_self_x_item_value_or_set_by_instance_he_by_module_name


class ExePacker(He):
    def __init__(self, u, mainpy:str, website_module:str=None, one_file:bool=False, one_dir:bool=False, show_console:bool=False, pack_overwrite:bool=False):
        super().__init__(u)
        exename = os.path.splitext(os.path.basename(mainpy))[0]
        if exename.endswith('main.py'): exename = exename.replace('main.py', '.py')
        self.configs.update({
            'mainpy': mainpy,
            'website_module': website_module,
            'exe_name': (exename:=os.path.splitext(os.path.basename(mainpy))[0]),
            'one_file': one_file,
            'one_dir': one_dir,
            'show_console': show_console,
            'pack_overwrite': pack_overwrite,
            'root_folders': [self.__si__.hebill_folder],
            'root_modules': [],
            'dist_path': (pkgdir:=self.__si__.working_folder.child_folder('.packages').child_folder(exename)).child_folder('dist'),
            'build_path': pkgdir.child_folder(exename).child_folder('build'),
            'spec_path': pkgdir.child_folder(exename),
            'comd_path': pkgdir.child_folder(exename),
        })

    @property
    @parse_self_x_item_value_or_set_by_instance_he_by_module_name()
    def configs(self): return

    def add_root_folder(self, folder):
        if folder:
            if not isinstance(folder, Folder): folder = self.__s__.components.folder(folder)
            self.configs.root_folders.append(folder)
    def ___check_root_module___(self, module):
        if module:
            ero = HeEro(ExePacker, '___check_root_module___', '检验根模块')
            if not isinstance(module, ModType):
                try: return self.__s__.components.mod_path(module).mod_type
                except Exception as e: raise (ero.add(f'无法导入根模块：{module}', e))
        return None

    def add_root_module(self, module):
        if module:=self.___check_root_module___(module):
            self.configs.root_folders.append(module.folder)
            self.configs.root_modules.append(module)

    def __output_commands__(self) -> list[str]:
        website_module = self.___check_root_module___(self.configs.website_module)
        cmd = ['PyInstaller', '--clean']
        # --name 必须拆开
        cmd.extend(['--name', self.configs.exe_name])
        if self.configs.one_dir: cmd.append('--onedir')
        elif self.configs.one_file: cmd.append('--onefile')
        if not self.configs.show_console: cmd.append('--windowed')
        if self.configs.pack_overwrite: cmd.append('--noconfirm')
        if self.configs.dist_path: cmd.extend(['--distpath', self.configs.dist_path])
        if self.configs.build_path: cmd.extend(['--workpath', self.configs.build_path])
        if self.configs.spec_path: cmd.extend(['--specpath', self.configs.spec_path])
        ico_added = False
        if self.configs.icon_file:
            ico_added = True
            cmd.extend(['--icon', self.configs.icon_file])
        if not ico_added:
            if website_module:
                ico = website_module.folder.child_file('logo.ico')
                if ico.is_exists():
                    ico_added = True
                    cmd.extend(['--icon', ico])
        if not ico_added:
            ico = self.__si__.hebill_folder.child_file('logo.ico')
            if ico.is_exists():
                cmd.extend(['--icon', ico])

        if self.configs.version_file: cmd.extend(['--version-file', self.configs.version_file])
        if not self.__si__.is_pip_installed(): cmd.extend(['--collect-submodules', 'hebill'])
        for pkg in self.configs.root_modules: cmd.extend(['--collect-submodules', pkg])
        if website_module: cmd.extend(['--collect-submodules', website_module])
        def collect(fd: Folder):
            if fd.is_exists():
                cmd.extend(['--add-data', f'{fd};{os.path.basename(fd)}'])
                """for dirpath, _, filenames in os.walk(fd):
                    for file in filenames:
                        if file.endswith(('.py', '.pyc', '.pyi')):continue
                        src = os.path.join(dirpath, file)
                        dst = os.path.relpath(src, self.__si__.working_folder)
                        # --add-data 也必须拆开
                        cmd.extend(['--add-data', f'{src};{dst}'])"""
        if not self.__si__.is_pip_installed(): collect(self.__si__.folder)
        for folder in self.configs.root_folders: collect(folder)
        if website_module: collect(website_module.folder)

        cmd.append(self.configs.mainpy)
        return cmd

    def pack(self):
        if self.configs.comd_path:
            cmd = self.__output_commands__()
            lines = [cmd[0] + ' ^']
            for arg in cmd[1:-1]: lines.append(f'  {arg} ^')
            lines.append(f'  {cmd[-1]}')
            self.configs.comd_path.child_file(f'{self.configs.exe_name}.cmd').save_content('\n'.join(lines))
        subprocess.run(self.__output_commands__(), check=True)

    def output_command(self) -> str: # 仅用于“显示”，不是执行
        return ' '.join(f'"{c}"' if ' ' in c else c for c in self.__output_commands__())

    def save_command(self, file=None):
        if not file: file = self.configs.exe_name + '.cmd'
        if isinstance(file, str): file = self.__sm__.file(file)
        cmd = self.__output_commands__()
        lines = [cmd[0] + ' ^']
        for arg in cmd[1:-1]: lines.append(f'  {arg} ^')
        lines.append(f'  {cmd[-1]}')
        file.save_content('\n'.join(lines))

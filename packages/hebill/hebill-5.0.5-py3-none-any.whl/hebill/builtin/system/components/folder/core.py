import os.path

from hebill.builtin.functions.builtins import HeEro
from ..file_folder import FileFolder


class Folder(FileFolder):
    def __init__(self, u, path: str):
        super().__init__(u, path)

    def is_exists(self): return os.path.isdir(self)
    def is_unexists(self): return not self.is_exists()
    def create(self): return os.makedirs(self, exist_ok=True)

    def child_file(self, name: str | list[str]): return self.__sm__.file(os.path.join(self, *(name if isinstance(name, list) else [name])))
    def child_folder(self, name: str | list[str]): return self.__sm__.folder(os.path.join(self, *(name if isinstance(name, list) else [name])))
    def search_children_names(self): return os.listdir(self) if self.is_exists() else []
    def search_children_file_names(self): return [name for name in self.search_children_names() if os.path.isfile(os.path.join(self, name))]
    def search_children_folder_names(self): return [name for name in self.search_children_names() if os.path.isdir(os.path.join(self, name))]
    def search_usable_children_names(self): return [name for name in self.search_children_names() if not name.startswith('.') and not name.startswith('_')]
    def search_usable_children_file_names(self): return [name for name in self.search_children_file_names() if not name.startswith('.') and not name.startswith('_')]
    def search_usable_children_folder_names(self): return [name for name in self.search_children_folder_names() if not name.startswith('.') and not name.startswith('_')]

    def search_children_paths(self): return [os.path.join(self, name) for name in self.search_children_names()]
    def search_children_file_paths(self): return [os.path.join(self, name) for name in self.search_children_file_names()]
    def search_children_folder_paths(self): return [os.path.join(self, name) for name in self.search_children_folder_names()]
    def search_usable_children_paths(self): return [os.path.join(self, name) for name in self.search_usable_children_names()]
    def search_usable_children_file_paths(self): return [os.path.join(self, name) for name in self.search_usable_children_file_names()]
    def search_usable_children_folder_paths(self): return [os.path.join(self, name) for name in self.search_usable_children_folder_names()]

    def search_children_files(self): return [self.child_file(name) for name in self.search_children_file_names()]
    def search_children_folders(self): return [self.child_folder(name) for name in self.search_children_folder_names()]
    def search_usable_children_files(self): return [self.child_file(name) for name in self.search_usable_children_file_names()]
    def search_usable_children_folders(self): return [self.child_folder(name) for name in self.search_usable_children_folder_names()]
    def search_children(self): return self.search_children_files() + self.search_children_folders()
    def search_usable_children(self): return self.search_usable_children_files() + self.search_usable_children_folders()

    def copyto(self, target_folder):
        e = HeEro(self, self.copyto, '将目录目录复制到指定目录。')
        if not isinstance(target_folder, Folder): target_folder = FileFolder(self.__s__, target_folder)
        if target_folder.is_exists(): raise e.add(f'目录：{target_folder} 已经存在！')
        target_folder.create()
        import shutil
        from pathlib import Path
        src = Path(self)
        dst = Path(target_folder)
        # 复制“目录内部内容”
        for item in src.iterdir():
            target = dst / item.name
            if item.is_dir(): shutil.copytree(item, target)
            else: shutil.copy2(item, target)

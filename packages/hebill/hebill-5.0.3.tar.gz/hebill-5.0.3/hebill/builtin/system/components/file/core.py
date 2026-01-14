import os.path
from ..file_folder import FileFolder


class File(FileFolder):
    def __init__(self, u, path: str):
        super().__init__(u, path)

    @property
    def base_name(self): return self.name.rsplit('.', 1)[0]

    @property
    def extension_name(self): return self.name.rsplit('.', 1)[1] if '.' in self.name else ''

    def is_exists(self): return os.path.isfile(self)
    def is_unexists(self): return not self.is_exists()
    def parse_json(self):
        import json
        try:
            with open(self, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return None

    def read_content(self):
        try:
            with open(self, 'r', encoding='utf-8') as file: return file.read()
        except Exception: return None

    def read_lines(self):
        result = []
        try:
            with open(self, 'r', encoding='utf-8') as file:
                for line in file: result.append(line)
            return result
        except Exception: return None

    def save_content(self, content: str):
        try:
            with open(self, 'w', encoding='utf-8') as file: return file.write(content)
        except Exception: return False

    def read_bytes(self):
        try:
            with open(self, 'rb') as file: return file.read()
        except Exception: return None

    def save_json(self, data: dict):
        import json
        try:
            with open(self, 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
                return True
        except Exception: return False

    def copy_to(self, path):
        if isinstance(path, File): file = path
        elif isinstance(path, str): file = self.__s__.components.file(path)
        else: return False
        if self != file and self.is_exists():
            try:
                import shutil
                shutil.copy(self, file)
                return True
            except Exception: return False
        return False

    def copy_from(self, path):
        if isinstance(path, str):
            file = self.__s__.components.file(path)
        elif isinstance(path, File):
            file = path
        else:
            return False
        return file.copy_to(self)

    def save_io(self, bytes_io):
        # 确保 io 的指针在开头
        try:
            bytes_io.seek(0)
            with open(self, "wb") as f: f.write(bytes_io.read())
            return True
        except Exception: return False


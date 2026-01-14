from .. import He
from ....components.cls_type import ClsType
from ....components.folder import Folder
from ....components.mod_path import ModPath
from ....components.mod_type import ModType
from ....components.obj_type import ObjType


class I:
    def __init__(self, he):
        self.__x: dict = ...

    @property
    def __he__(self)-> He: ...
    @property
    def __x__(self)-> dict: ...

    @property
    def id(self)-> int: ...
    @property
    def mod_path(self)-> ModPath: ...
    @property
    def mod_type(self)-> ModType: ...
    @property
    def cls_type(self)-> ClsType: ...
    @property
    def obj_type(self)-> ObjType: ...

    @property
    def folder(self)-> Folder: ...

from .....functions.decorators import parse_self_x_item_value, parse_self_x_item_value_or_set_by_func, \
    instance_he_by_module_name, set_self_x_item_value_by_setter_with_agr
from ....types.he import He


class Node(He):
    def __init__(self, u):
        super().__init__(u)
        if type(self) is Node: raise TypeError("Node 不能直接实例化，只能由子类调用。")
        from ..nodes.wrap import Wrap
        from .. import Htmdoc
        if isinstance(u, Htmdoc):
            super().__init__(u)
            self.__x__['document'] = u
        elif isinstance(u, Wrap):
            super().__init__(u.document)
            self.__x__['document'] = u.document
            self.__x__['senior'] = u
            self.senior.juniors[self.__id__] = self
        else:
            raise TypeError(f'Node __init__ 参数 u {type(u)} 只能是 Htmldoc 或者 Wrap。')
        self.document.elements[self.__id__] = self

    def ___senior___(self, senior=None):
        if senior is None:
            if self.has_senior():
                del self.senior.juniors[self.__id__]
                del self.__x__['senior']
                return True
            return False
        from..nodes.wrap import Wrap
        if not isinstance(self.senior, Wrap): raise TypeError(f'Node 的父节点只能是 Wrap。')
        if self.has_senior(): self.___senior___()
        senior.juniors[self.__id__] = self
        self.__x__['senior'] = senior
        return True

    @property
    @parse_self_x_item_value()
    def document(self): return
    @property
    @parse_self_x_item_value()
    def senior(self): return
    def has_senior(self): return self.__x__.get('senior', None) is not None

    @staticmethod
    def is_comment(): return False
    @staticmethod
    def is_script(): return False
    @staticmethod
    def is_tag(): return False
    @staticmethod
    def is_text(): return False
    @staticmethod
    def is_wrap(): return False

    @property
    @parse_self_x_item_value()
    def ___anchored_to___(self): return
    def ___anchor_to___(self, node): self.__x__['___anchored_to___'] = node
    def ___is_anchored_to___(self): return self.__x__.get('___anchored_to___', None) is not None
    @property
    @parse_self_x_item_value_or_set_by_func()
    def ___anchors___(self): return {}
    def ___anchor___(self, sn:int):
        if sn == 0: raise RuntimeError('锚点位置不支持参数 sn = 0')
        if sn not in self.___anchors___:
            self.___anchors___[sn] = self.document.wrap()
            self.___anchors___[sn].___anchor_to___(self)
        return self.___anchors___[sn].___anchor_to___(self)
    def before(self, sn:int): return self.___anchor___(sn or -sn)
    @property
    def before1(self): return self.___anchor___(1)
    @property
    def before2(self): return self.___anchor___(2)
    @property
    def before3(self): return self.___anchor___(3)
    @property
    def before4(self): return self.___anchor___(4)
    @property
    def before5(self): return self.___anchor___(5)
    def after(self, sn:int): return self.___anchor___(-sn or sn)
    @property
    def after1(self): return self.___anchor___(-1)
    @property
    def after2(self): return self.___anchor___(-2)
    @property
    def after3(self): return self.___anchor___(-3)
    @property
    def after4(self): return self.___anchor___(-4)
    @property
    def after5(self): return self.___anchor___(-5)
    ####################################################################################################
    # Content 专用
    @property
    @parse_self_x_item_value()
    def ___content___(self): return
    @___content___.setter
    @set_self_x_item_value_by_setter_with_agr()
    def ___content___(self, content: str): return
    ####################################################################################################
    # Wrap 专用
    @property
    @parse_self_x_item_value_or_set_by_func()
    def ___juniors___(self): return {}

    @instance_he_by_module_name(module_name='.nodes#', module_name_striped=True)
    def ___comment___(self, content: str = None): return
    @instance_he_by_module_name(module_name='.nodes#', module_name_striped=True)
    def ___script___(self, content: str = None): return
    @instance_he_by_module_name(module_name='.nodes#', module_name_striped=True)
    def ___text___(self, content: str = None): return
    @instance_he_by_module_name(module_name='.nodes#', module_name_striped=True)
    def ___wrap___(self, content=None): return

    def ___append___(self, element=None):
        if isinstance(element, list):
            return [self.___append___(e) for e in element]
        if isinstance(element, str|float|int):
            return self.___text___(element)
        if isinstance(element, Node):
            element.___senior___(self)
            return element
        return None
    ####################################################################################################
    # Tag 专用
    @property
    @parse_self_x_item_value()
    def ___name___(self): return
    @___name___.setter
    @set_self_x_item_value_by_setter_with_agr()
    def ___name___(self, name: str): return
    @property
    @parse_self_x_item_value_or_set_by_func()
    def ___attributes___(self): return {}

    @property
    @parse_self_x_item_value()
    def ___inner_anchored_to___(self): return
    def ___inner_anchor_to___(self, node): self.__x__['___inner_anchored_to___'] = node
    def ___is_inner_anchored_to___(self): return self.__x__.get('___inner_anchored_to___', None) is not None
    @property
    @parse_self_x_item_value_or_set_by_func()
    def ___inner_anchors___(self): return {}
    def ___inner_anchor___(self, sn:int):
        if sn == 0: raise RuntimeError('锚点位置不支持参数 sn = 0')
        if sn not in self.___inner_anchors___:
            self.___inner_anchors___[sn] = self.document.wrap()
            self.___inner_anchors___[sn].___inner_anchor_to___(self)
        return self.___inner_anchors___[sn].___inner_anchor_to___(self)
    def ___inner_before___(self, sn:int): return self.___inner_anchor___(sn)
    @property
    def ___inner_before1___(self): return self.___inner_anchor___(1)
    @property
    def ___inner_before2___(self): return self.___inner_anchor___(2)
    @property
    def ___inner_before3___(self): return self.___inner_anchor___(3)
    @property
    def ___inner_before4___(self): return self.___inner_anchor___(4)
    @property
    def ___inner_before5___(self): return self.___inner_anchor___(5)
    def ___inner_after___(self, sn:int): return self.___inner_anchor___(sn)
    @property
    def ___inner_after1___(self): return self.___inner_anchor___(-1)
    @property
    def ___inner_after2___(self): return self.___inner_anchor___(-2)
    @property
    def ___inner_after3___(self): return self.___inner_anchor___(-3)
    @property
    def ___inner_after4___(self): return self.___inner_anchor___(-4)
    @property
    def ___inner_after5___(self): return self.___inner_anchor___(-5)

    @property
    @parse_self_x_item_value_or_set_by_func()
    def ___output_pairable___(self): return True
    @___output_pairable___.setter
    @set_self_x_item_value_by_setter_with_agr()
    def ___output_pairable___(self, pairable: bool): return
    @property
    @parse_self_x_item_value_or_set_by_func()
    def ___output_brealable___(self): return True
    @___output_brealable___.setter
    @set_self_x_item_value_by_setter_with_agr()
    def ___output_brealable___(self, brealable: bool): return
    ####################################################################################################

    @property
    @parse_self_x_item_value_or_set_by_func()
    def ___level___(self):
        if self.is_wrap():
            if self.___is_anchored_to___():
                return self.___anchored_to___.___level___
            if self.___is_inner_anchored_to___():
                return self.___inner_anchored_to___.___level___ + 1
        if self.has_senior():
            return self.senior.___output_level___ + 1
        return 0

    @property
    @parse_self_x_item_value_or_set_by_func()
    def ___output_level___(self):
        if self.is_wrap():
            if self.___is_anchored_to___():
                return self.___anchored_to___.___output_level___
            if self.___is_inner_anchored_to___():
                return self.___inner_anchored_to___.___output_level___ + 1
        if self.has_senior():
            if self.is_wrap():
                return self.senior.___output_level___
            return self.senior.___output_level___ + 1
        return 0

    def __str__(self):
        rs = []
        # 输出前置锚点
        rs.extend(str(self.___anchors___[k]) for k in sorted((k for k in self.___anchors___ if k > 0), reverse=True))
        rs.append(f'{self.___level___ * '\t'}<{self.__class__.__name__}'
                  f' level={self.___level___}'
                  f' id={self.__id__}'
                  f' senior="{f'{type(s:=self.senior if self.has_senior() else self.document).__name__}@{id(s)}'}"'
                  f' juniors="{','.join([f'{type(i).__name__}@{id(i)}' for i in self.___juniors___.values()])}"'
                  f' class="{'.'.join([c.__name__ for c in self.__class__.__mro__ if issubclass(c, Node)].__reversed__())}"'
                  f' output_level={self.___output_level___}'
                  f'>'
                  )
        if self.is_wrap() or self.is_tag():
            # 输出内部前置锚点
            if self.is_tag(): rs.extend(i.__str__() for k, i in sorted(((k, v) for k, v in self.___inner_anchors___.items() if k > 0), key=lambda x: x[0], reverse=True))
            for i in self.___juniors___.values(): rs.append(i.__str__())
            # 输出内部前置锚点
            if self.is_tag(): rs.extend(i.__str__() for k, i in sorted(((k, v) for k, v in self.___inner_anchors___.items() if k > 0), key=lambda x: x[0], reverse=True))
        # 输出后置锚点
        rs.extend(str(self.___anchors___[k]) for k in sorted((k for k in self.___anchors___ if k < 0), reverse=True))
        return '\n'.join(r for r in rs if r)

    def output(self):
        mini = self.document.configs.output_minimized
        rs = []
        # 输出前置锚点
        rs.extend(self.___anchors___[k].output() for k in sorted((k for k in self.___anchors___ if k > 0), reverse=True))
        if self.is_comment():
            if not self.document.configs.output_minimized and self.document.configs.output_comments:
                self.document.___output_next_break___ = True
                rs.extend((
                    '\n' + self.document.configs.output_indentation * self.___output_level___,
                    f'<!--[{self.___content___.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')}]-->'
                ))
        if self.is_script():
            self.document.___output_next_break___ = False
            rs.append(self.___content___)
        if self.is_tag():
            remove_space = not mini and self.___output_level___ > 0 and self.document.configs.output_unspaced
            if not mini:
                if self.document.___output_next_break___:
                    if remove_space: rs.append('<!--')
                    rs.append('\n' + self.document.configs.output_indentation * self.___output_level___)
                    if remove_space: rs.append('-->')
            ##################################################
            # Attributes:
            rs.append(f'<{self.___name___}')
            for k, v in self.___attributes___.items():
                if v is None: rs.append(f' {k}')
                else: rs.append(f' {k}="{v}"')
            if not self.___output_pairable___:
                rs.append(' />')
            else:
                rs.append('>')
                self.document.___output_next_break___ = True
                ##################################################
                # 输出内部前置锚点
                rs.extend(self.___inner_anchors___[k].output() for k in sorted((k for k in self.___inner_anchors___ if k > 0), reverse=True))
                ##################################################
                # Inner Main
                ris = [r for i in self.___juniors___.values() if (r:=i.output())]
                rs.extend(ris)
                if not mini:
                    if self.document.___output_next_break___ and ris:
                        rs.append("\n" + self.document.configs.output_indentation * self.___output_level___)
                rs.append('</' + self.___name___ + '>')
                self.document.___output_next_break___ = self.___output_brealable___
                ##################################################
                # 输出内部后置锚点
                rs.extend(self.___inner_anchors___[k].output() for k in sorted((k for k in self.___inner_anchors___ if k < 0), reverse=True))
        if self.is_text():
            self.document.___output_next_break___ = False
            rs.append(self.___content___.replace('<', '&lt;').replace('>', '&gt;'))
        if self.is_wrap():
            rs.extend(i.output() for i in self.___juniors___.values())
        # 输出后置锚点
        rs.extend(self.___anchors___[k].output() for k in sorted((k for k in self.___anchors___ if k < 0), reverse=True))
        return ''.join(rs)
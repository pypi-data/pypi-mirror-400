from ....functions.builtins import instance_pyobj_by_mod_path
from ....functions.decorators import instance_he_by_module_name, \
    parse_self_x_item_value_or_set_by_instance_he_by_module_name, set_self_x_item_value_by_setter_with_agr, \
    parse_self_x_item_value_or_set_by_func
from ...types.he import He


class Htmdoc(He):
    def __init__(self, u, configs:dict=None):
        He.__init__(self, u)
        self.configs.update(configs)

    @property
    @parse_self_x_item_value_or_set_by_func()
    def elements(self): return {}

    @property
    @parse_self_x_item_value_or_set_by_instance_he_by_module_name()
    def configs(self): return

    @property
    @parse_self_x_item_value_or_set_by_instance_he_by_module_name(module_name='tags.html')
    def root(self): return

    @instance_he_by_module_name(module_name='nodes#')
    def comment(self, content: str = None): return
    @instance_he_by_module_name(module_name='nodes#')
    def script(self, content: str = None): return
    @instance_he_by_module_name(module_name='nodes#')
    def text(self, content: str = None): return
    @instance_he_by_module_name(module_name='nodes#')
    def wrap(self, content=None): return

    @staticmethod
    def ___auto_create_tag___(u, name:str, args:tuple|list, kwargs:dict):
        # return self.__b__.pyobj_by_modnam(f'{Htmdoc.__module__.rsplit('.', 1)[0]}.tags.{name.lower()}', [u, *args], kwargs)
        try: return instance_pyobj_by_mod_path(f'{Htmdoc.__module__.rsplit('.', 1)[0]}.tags.{name.lower()}', [u, *args], kwargs)
        except: return instance_pyobj_by_mod_path(f'{Htmdoc.__module__.rsplit('.', 1)[0]}.nodes.tag', [u, name.lower(), *args], kwargs)


    def __getattribute__(self, name:str):
        def handler(*args, **kwargs):
            return self.___auto_create_tag___(self, name, args, kwargs)
        if name and name[0].isupper():
            return handler
        return super().__getattribute__(name)

    """def __getattr__(self, name:str):
        # 当访问不存在的属性或方法时触发
        def handler(*args, **kwargs): return self.___auto_create_tag___(self, name, args, kwargs)
        return handler"""

    @property
    @parse_self_x_item_value_or_set_by_func()
    def ___output_next_break___(self): return False
    @___output_next_break___.setter
    @set_self_x_item_value_by_setter_with_agr(value_type='bol')
    def ___output_next_break___(self, value): pass

    def output(self):
        """s = '['
        elements = self.elements
        for k, v in elements.items(): s += f'\n\t{k}: {v}'
        s += ']'
        s += '\n' + str(self)
        return s"""
        return self.root.output()
    def __str__(self):
        return self.root.__str__()


    @property
    @parse_self_x_item_value_or_set_by_func()
    def ___css_links___(self): return []
    @property
    @parse_self_x_item_value_or_set_by_func()
    def ___js_links___(self): return []
    @property
    @parse_self_x_item_value_or_set_by_func()
    def ___css_scripts___(self): return []
    @property
    @parse_self_x_item_value_or_set_by_func()
    def ___js_scripts___(self): return []

    def add_css_link(self, url):
        if url not in self.___css_links___: self.___css_links___.append(url)
    def add_js_link(self, url):
        if url not in self.___js_links___:
            self.___js_links___.append(url)
    def add_css_code(self, code): self.___css_scripts___.append(code)
    def add_js_code(self, code): self.___js_scripts___.append(code)

    """def add_library_css_link(self, *names): self.add_css_link(self.library_file_url(*names))
    def add_library_js_link(self, *names):self.add_js_link(self.library_file_url(*names))

    def library_file_url(self, *names): return self.__b__.join_url(self.configs.library_url_root, *names)
    def library_file(self, *names): return self.__s__.modules.file(str(os.path.join(os.path.dirname(__file__), 'library', *names)))"""

    def add_css_link_node(self, url: str):
        n = self.root.head.inner_after(-100).Link(url)
        n.attributes['rel'] = 'stylesheet'
        n.attributes['type'] = 'text/css'
        n.attributes['crossorigin'] = 'anonymous'
        return n
    def add_js_link_node(self, url: str):
        n = self.root.body.after(-1000).Script()
        n.attributes['src'] = url
        n.attributes['type'] = 'text/javascript'
        return n
    def add_css_script_node(self, script: str):
        return self.root.head.after(-100).Style(script)
    def add_js_script_node(self, script: str):
        n = self.root.body.after(-1000).Script()
        n.script(script)
        n.attributes['type'] = 'text/javascript'
        return n

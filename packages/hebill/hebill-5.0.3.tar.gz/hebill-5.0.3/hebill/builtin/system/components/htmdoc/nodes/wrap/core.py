from ...node import Node


class Wrap(Node):
    def __init__(self, u, content=None):
        super().__init__(u)
        self.append(content)

    @property
    def juniors(self): return self.___juniors___

    @staticmethod
    def is_wrap(): return True

    def comment(self, content: str = None): return self.___comment___(content)
    def script(self, content: str = None): return self.___script___(content)
    def text(self, content: str = None): return self.___text___(content)
    def wrap(self, content=None): return self.___wrap___(content)

    def append(self, element=None): return self.___append___(element)

    def __getattr__(self, name:str):
        if name and name[0].isupper():
            def handler(*args, **kwargs):
                return self.document.___auto_create_tag___(self, name, args, kwargs)
            return handler
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

    @property
    def anchored(self): return self.___anchored_to___
    def is_anchored(self): return self.___is_anchored_to___()

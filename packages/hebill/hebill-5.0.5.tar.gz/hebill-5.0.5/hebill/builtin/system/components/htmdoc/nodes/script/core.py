from ...node import Node


class Script(Node):
    def __init__(self, u, content:str=None):
        super().__init__(u)
        self.___content___ = content or ''

    @property
    def content(self): return self.___content___

    def output(self):
        self.document.___output_next_break___ = False
        return self.content

    @staticmethod
    def is_script(): return True
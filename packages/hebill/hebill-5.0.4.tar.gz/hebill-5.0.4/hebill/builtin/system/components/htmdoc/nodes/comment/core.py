from ...node import Node


class Comment(Node):
    def __init__(self, u, content:str=None):
        super().__init__(u)
        self.___content___ = content or ''

    @property
    def content(self): return self.___content___

    @staticmethod
    def is_comment(): return True

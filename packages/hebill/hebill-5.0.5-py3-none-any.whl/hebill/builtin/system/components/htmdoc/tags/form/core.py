from ...nodes.tag import Tag


class Form(Tag):
    def __init__(self, u, action: str = None, attributes:dict[str, str|int|float|None]=None):
        if isinstance(attributes, dict):
            if action: attributes['action'] = action
        else:
            if action: attributes = {'action': action}
        Tag.__init__(self, u, None, attributes)
        if not self.attributes.get('method'): self.attributes['method'] = 'POST'

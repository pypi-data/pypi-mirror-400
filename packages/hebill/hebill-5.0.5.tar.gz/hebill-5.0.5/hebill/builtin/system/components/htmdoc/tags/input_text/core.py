from ..input import Input


class InputText(Input):
    def __init__(self, u, name: str = None, value: str = None, placeholder:str=None, attributes:dict[str, str|int|float|None]=None):
        if placeholder:
            if isinstance(attributes, dict):
                attributes['placeholder'] = placeholder
            else:
                attributes = {'placeholder': placeholder}
        Input.__init__(self, u, name, value, attributes)


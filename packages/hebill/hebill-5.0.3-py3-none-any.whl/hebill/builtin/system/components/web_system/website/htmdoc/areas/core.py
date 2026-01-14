from .......functions.decorators import parse_self_x_item_value_or_set_by_func
from ......types.hd import Hd


class Areas(Hd):
    @property
    def __document__(self): return self.__u__

    def add(self, name, area): self[name] = area

    @property
    @parse_self_x_item_value_or_set_by_func()
    def navbar(self): return self.__document__.root.body.inner_before(100)
    @navbar.setter
    def navbar(self, area): area.append(self.navbar)

    @property
    @parse_self_x_item_value_or_set_by_func()
    def breadcrumb(self): return self.__document__.root.body.inner_before(90)
    @breadcrumb.setter
    def breadcrumb(self, area): area.append(self.breadcrumb)

    @property
    @parse_self_x_item_value_or_set_by_func()
    def navigations(self): return self.__document__.root.body.inner_before(80)
    @navigations.setter
    def navigations(self, area): area.append(self.navigations)

    @property
    @parse_self_x_item_value_or_set_by_func()
    def messages(self): return self.__document__.root.body.inner_before(70)
    @messages.setter
    def messages(self, area): area.append(self.messages)

    @property
    @parse_self_x_item_value_or_set_by_func()
    def content(self): return self.__document__.root.body
    @content.setter
    def content(self, area): area.append(self.content)

    @property
    @parse_self_x_item_value_or_set_by_func()
    def footer(self): return self.__document__.root.body.after(-50)
    @footer.setter
    def footer(self, area): area.append(self.footer)

    @property
    @parse_self_x_item_value_or_set_by_func()
    def debugs(self): return self.__document__.root.body.after(-100)
    @debugs.setter
    def debugs(self, area): area.append(self.debugs)

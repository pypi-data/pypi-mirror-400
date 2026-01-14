from colorama import Fore, Style
from ....types.he import He


class Input(He):
    def input(self, label=None, prefix=None, color=None, bgcolor=None, bright=None):
        text = Fore.BLUE + self.__u__.make_prefix(prefix)
        if label:
            text += f'{label}'
        text += ': '
        if bgcolor:
            text += bgcolor
        if color:
            text += color
        if bright:
            text += Style.BRIGHT
        text += Style.RESET_ALL
        return input(text)

    def primary(self, label=None, prefix=None): return self.input(label, prefix, Fore.WHITE)
    def secondary(self, label=None, prefix=None): return self.input(label, prefix, Fore.BLUE)
    def success(self, label=None, prefix=None): return self.input(label, prefix, Fore.GREEN)
    def warning(self, label=None, prefix=None): return self.input(label, prefix, Fore.YELLOW)
    def danger(self, label=None, prefix=None): return self.input(label, prefix, Fore.RED)
    def info(self, label=None, prefix=None): return self.input(label, prefix, Fore.CYAN)
    def comment(self, label=None, prefix=None): return self.input(label, prefix, Fore.BLACK)

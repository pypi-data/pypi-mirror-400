from hebill import Hebill

if __name__ == '__main__':
    he = Hebill()
    cm = he.components.css_maker('css.css')

    from dev.colors import assemble
    assemble(cm)

    from dev.container import assemble
    assemble(cm)

    from dev.grid import assemble
    assemble(cm)

    # container 响应宽度
    cm.save(True)
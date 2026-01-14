from hebill.builtin.system.components.css_maker import CssMaker

breakpoints = {
    "sm": 576,
    "md": 768,
    "lg": 992,
    "xl": 1200,
    "xx": 1440
}
col_qn = 12
col_ws = [f"{i/col_qn*100:.6f}%" for i in range(1, col_qn+1)]

def assemble(css_maker: CssMaker):
    # Grid 基础变量
    css_maker.cls_root.atr('--row-gap', '15px')
    css_maker.cls_root.atr('--cell-gap', '15px')

    # .grid 容器
    c = css_maker.cls('.grid')
    c.atr('width', '100%')

    # .row
    r = css_maker.cls('.row')
    r.atr('display', 'flex')
    r.atr('flex-wrap', 'wrap')
    r.atr('margin-left', 'calc(-1 * var(--cell-gap))')
    r.atr('margin-right', 'calc(-1 * var(--cell-gap))')
    r.atr('row-gap', 'var(--row-gap)')

    # .cell
    cell = css_maker.cls('.cell')
    cell.atr('padding-left', 'var(--cell-gap)')
    cell.atr('padding-right', 'var(--cell-gap)')
    cell.atr('box-sizing', 'border-box')
    cell.atr('flex', '0 0 auto')

    # 默认列宽
    for i, w in enumerate(col_ws, 1):
        c = css_maker.cls(f'.cell-{i}')
        c.atr('flex-basis', w)
        c.atr('max-width', w)

    # 响应式列
    for bp_name, bp_width in breakpoints.items():
        m = css_maker.med(media_min_width=bp_width)
        for i, w in enumerate(col_ws, 1):
            c = m.cls(f'.{bp_name}\\:cell-{i}')
            c.atr('flex-basis', w)
            c.atr('max-width', w)

    # 响应式 row-gap / cell-gap（可选）
    for bp_name, bp_width in breakpoints.items():
        m = css_maker.med(media_min_width=bp_width)
        r = m.cls('.row')
        r.atr('--row-gap', '15px')   # 可按断点调整
        r.atr('--cell-gap', '15px')  # 可按断点调整

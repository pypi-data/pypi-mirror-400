# 定义断点
from hebill.builtin.system.components.css_maker import CssMaker
# 定义断点
breakpoints = {
    "sm": 576,
    "md": 768,
    "lg": 992,
    "xl": 1200,
    "xx": 1440
}
# 对应 max-width
max_widths = {
    "sm": 540,
    "md": 720,
    "lg": 960,
    "xl": 1140,
    "xx": 1408
}

prefix = 'container'
names = ['', 'sm', 'md', 'lg', 'xl', 'xx']
root_attrs = {
    '--container-padding': '15px'
}
base_attrs = {
    'width': '100%',
    'margin-left': 'auto',
    'margin-right': 'auto',
    'padding-left': 'var(--container-padding, 15px)',
    'padding-right': 'var(--container-padding, 15px)',
}

def assemble(cm: CssMaker):
    # 常量定义
    for k, v in root_attrs.items():
        cm.cls_root.atr(k, v)
    # 基础式样
    c = cm.cls(', '.join([f'.{prefix}{'-' if n else ''}{n}' for n in names]) + f', .{prefix}-fd')
    for k, v in base_attrs.items():
        c.atr(k, v)
    # 循环生成 media 规则
    for s, w in breakpoints.items():
        # 哪些 container 类适用当前断点
        idx = list(breakpoints.keys()).index(s) + 1
        aps = [f'.{prefix}{("-" + n) if n else ""}' for n in names[:idx + 1]]
        sts = ",".join(aps)
        m = cm.med(media_min_width=w)
        c = m.cls(sts)
        c.atr_px('max-width', max_widths[s])
    c = cm.cls(f'.{prefix}-fd')
    c.atr('max-width', '100%')

"""Regenerate the site's vector tables and cross-focal plot from the supplied LaTeX.

Run: MPLCONFIGDIR=/tmp/monoben-matplotlib python static/tabels/render_assets.py
Only the plot requires matplotlib; table SVGs retain selectable 15 px text.
"""
from pathlib import Path
from html import escape
import re

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'static/images'


def rows_from_tex(name):
    source = (Path(__file__).parent / name).read_text()
    body = source.split(r'\begin{tabular}', 1)[1]
    rows = []
    for row in body.split(r'\\'):
        row = row.replace(r'\hline', '').strip()
        if not re.match(r'(?:Mono|Occupancy|OPA|\\textbf\{Mono)', row):
            continue
        cells = [re.sub(r'\s*\\cite\{[^}]+\}', '', c).strip() for c in row.split('&')]
        rows.append(cells)
    return rows


def plain(cell):
    return re.sub(r'\\(?:textbf|underline)\{([^}]+)\}', r'\1', cell).replace(r'$^\dagger$', '†').replace(r'$\dagger$', '†').replace('--', '–')


def table_svg(rows, kind, columns_per_panel, width, method_width, extra_width=0):
    count = len(rows[0]) - (2 if kind == 'kitti' else 1)
    panels = [list(range(i, min(i + columns_per_panel, count))) for i in range(0, count, columns_per_panel)]
    row_height, header_height, gap = 40, 88, 28
    panel_height = header_height + len(rows) * row_height
    height = len(panels) * (panel_height + gap) - gap + 2
    svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
           '<rect width="100%" height="100%" fill="white"/>',
           '<g font-family="Times New Roman, Nimbus Roman, Times, serif" font-size="15" fill="#111">']

    def text(x, y, value, anchor='middle', bold=False, underline=False):
        style = ' font-weight="bold"' if bold else ''
        if value in ('AP3D ↑', 'APBEV ↑'):
            subscript = '3D' if value == 'AP3D ↑' else 'BEV'
            content = f'AP<tspan baseline-shift="sub" font-size="11">{subscript}</tspan> ↑'
        else:
            content = escape(value)
        svg.append(f'<text x="{x:g}" y="{y:g}" text-anchor="{anchor}"{style}>{content}</text>')
        if underline:
            half = sum(3.75 if c == '.' else 7.5 for c in value) / 2
            svg.append(f'<path d="M{x-half:g} {y+2.5:g}H{x+half:g}" stroke="#111" stroke-width="0.7"/>')

    def line(x1, y1, x2, y2, weight=0.65):
        svg.append(f'<path d="M{x1:g} {y1:g}H{x2:g}" stroke="#111" stroke-width="{weight}"/>' if y1 == y2 else f'<path d="M{x1:g} {y1:g}V{y2:g}" stroke="#111" stroke-width="{weight}"/>')

    focal = list(range(600, 1401, 50)) + ['Avg']
    for p, columns in enumerate(panels):
        top = p * (panel_height + gap) + 1
        start = method_width + extra_width
        cw = (width - start) / len(columns)
        line(0, top, width, top, 1.4)
        text(8, top + 48, 'Method', 'start')
        if kind == 'kitti' and not extra_width:
            text(8, top + 67, '(extra data)', 'start')
        line(method_width, top, method_width, top + panel_height)
        if kind == 'kitti' and extra_width:
            text(method_width + extra_width / 2, top + 37, 'Extra')
            text(method_width + extra_width / 2, top + 55, 'Data')
            line(start, top, start, top + panel_height)
        groups = []
        for index in columns:
            if kind == 'focal':
                group = 'Avg' if index == 17 else ('Unseen Focals' if index < 2 or index > 14 else 'Seen Focals')
            else:
                group = ('KITTI Test' if index < 6 else 'KITTI Val') + (' · AP3D ↑' if index % 6 < 3 else ' · APBEV ↑')
            if groups and groups[-1][0] == group:
                groups[-1][2] += 1
            else:
                groups.append([group, columns.index(index), 1])
        for group, first, length in groups:
            center = start + (first + length / 2) * cw
            if kind == 'focal':
                if length * cw < 110 and group != 'Avg':
                    text(center, top + 16, group.split()[0])
                    text(center, top + 33, 'Focals')
                    text(center, top + 49, '(px)')
                else:
                    text(center, top + 25, group)
                    if group != 'Avg':
                        text(center, top + 44, '(px)')
            else:
                dataset, metric = group.split(' · ')
                if length * cw < 90:
                    text(center, top + 16, 'KITTI')
                    text(center, top + 33, dataset.split()[1])
                    text(center, top + 49, metric)
                else:
                    text(center, top + 25, dataset)
                    text(center, top + 44, metric)
            if first:
                line(start + first * cw, top, start + first * cw, top + panel_height)
        line(start, top + 53, width, top + 53)
        for j, index in enumerate(columns):
            x = start + (j + 0.5) * cw
            if kind == 'focal':
                label = str(focal[index]) if index != 17 else ''
                color = '#ffe1c8' if index < 2 or 14 < index < 17 else '#d2f5d7' if index in (2, 6, 10, 14) else '#c8e1ff'
                if label:
                    svg.append(f'<rect x="{x-22:g}" y="{top+61}" width="44" height="20" fill="{color}"/>')
            else:
                label = ['Easy', 'Mod.', 'Hard'][index % 3]
            text(x, top + 76, label)
        line(0, top + header_height, width, top + header_height, 1)
        for r, row in enumerate(rows):
            y = top + header_height + r * row_height + 25
            method = plain(row[0])
            if kind == 'kitti' and not extra_width:
                text(8, y - 9, method, 'start', r'\textbf' in row[0])
                text(8, y + 9, 'Extra: ' + plain(row[1]), 'start')
            elif '(Reproduced)' in method:
                text(8, y - 9, 'MonoIA†', 'start')
                text(8, y + 9, '(Reproduced)', 'start')
            else:
                text(8, y, method, 'start', r'\textbf' in row[0])
            if kind == 'kitti':
                if extra_width:
                    text(method_width + extra_width / 2, y, plain(row[1]))
                if r == 3:
                    line(0, top + header_height + r * row_height, width, top + header_height + r * row_height)
            for j, index in enumerate(columns):
                cell = row[index + (2 if kind == 'kitti' else 1)]
                text(start + (j + 0.5) * cw, y, plain(cell), bold=r'\textbf' in cell, underline=r'\underline' in cell)
        line(0, top + panel_height, width, top + panel_height, 1.4)
    svg.append('</g></svg>')
    return '\n'.join(svg)


def main():
    focal = rows_from_tex('focal_gen.tex')
    kitti = rows_from_tex('kitti_main_result.tex')
    assert len(focal) == 6 and all(len(r) == 19 for r in focal)
    assert len(kitti) == 11 and all(len(r) == 14 for r in kitti)
    for name, rows, kind, variants in [
        ('focal_table', focal, 'focal', [(18, 1080, 180, 0), (7, 580, 160, 0), (2, 280, 160, 0)]),
        ('kitti_table', kitti, 'kitti', [(12, 1080, 180, 72), (6, 580, 160, 60), (3, 280, 136, 0)]),
    ]:
        for suffix, args in zip(('wide', 'medium', 'small'), variants):
            (OUT / f'{name}_{suffix}.svg').write_text(table_svg(rows, kind, *args))

    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Patch
    matplotlib.rcParams.update({'font.family': 'DejaVu Serif', 'font.size': 13, 'svg.fonttype': 'path'})
    chosen = [focal[i] for i in (0, 1, 2, 3, 5)]
    # 600 px is column 1: 850 px -> column 6, 1400 px -> column 17.
    seen = [float(plain(row[6])) for row in chosen]
    unseen = [float(plain(row[17])) for row in chosen]
    fig, ax = plt.subplots(figsize=(10.8, 4.5), layout='constrained')
    dark = ['#78849c', '#57a78c', '#9a5c8c', '#be9826', '#4a7fb5']
    light = ['#d7dce4', '#c2e2d5', '#dcbdd5', '#f0cd5e', '#b7cfe8']
    ax.axvspan(3.5, 4.5, color='#fdf6e3', zorder=0)
    a = ax.bar([i-.19 for i in range(5)], seen, .34, color=dark, edgecolor='#222', hatch='///', zorder=3)
    b = ax.bar([i+.19 for i in range(5)], unseen, .34, color=light, edgecolor='#777', zorder=3)
    ax.bar_label(a, fmt='%.2f', padding=5, fontsize=12)
    ax.bar_label(b, fmt='%.2f', padding=5, fontsize=12)
    ax.set(ylim=(0, 28), xlim=(-.6, 4.6), ylabel='AP$_{3D}$ (IoU ≥ 0.7) ↑', xticks=range(5),
           xticklabels=['MonoDETR', 'MonoDGP', 'MonoCoP', 'MonoIA\n(Paper)', 'MonoBEN\n(Ours)'])
    ax.get_xticklabels()[-1].set_fontweight('bold')
    ax.set_axisbelow(True)
    ax.grid(axis='y', linestyle='--', alpha=.4)
    ax.spines[['top', 'right']].set_visible(False)
    ax.legend(handles=[Patch(facecolor='#78849c', edgecolor='#222', hatch='///', label='Seen focal · 850 px'),
                       Patch(facecolor='#d7dce4', edgecolor='#777', label='Unseen focal · 1400 px')],
              loc='lower center', bbox_to_anchor=(.5, 1.02), ncol=2, frameon=False)
    for extension in ('svg', 'png'):
        fig.savefig(OUT / f'cross_focal_performance.{extension}', dpi=200)
    plt.close(fig)
    print('850 px:', seen)
    print('1400 px:', unseen)


if __name__ == '__main__':
    main()

import argparse
# use pathlib instead of os
from scipy import stats
from pathlib import Path
import numpy as np
from Bio import Phylo
from Bio.Phylo import BaseTree
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import matplotlib

from ellishape_cli.tree import read_csv

# 使用非交互式后端
matplotlib.use('Agg')


def load_and_preprocess_tree(newick_file):
    """加载Newick文件并预处理树结构"""
    tree = Phylo.read(newick_file, 'newick')
    return tree


def get_terminales(tree) -> set:
    """识别异常（分支超长）与正常的叶节点集合"""
    z_score_limit = 3
    name = []
    length = []
    long_terminal = set()
    normal_terminal_len = []
    normal_terminal = []
    for i in tree.get_terminals():
        name.append(i.name)
        # 某些newick没有branch_length，这里容错为0
        length.append(i.branch_length if i.branch_length is not None else 0.0)
    if len(length) == 0:
        return set(), []
    z_score = stats.zscore(length)
    for index, score in enumerate(z_score):
        if np.abs(score) >= z_score_limit:
            long_terminal.add(name[index])
        else:
            normal_terminal_len.append((name[index], length[index]))
    # sort by length and select represents
    normal_terminal_len.sort(key=lambda x: x[1])
    if len(long_terminal) == 0 and len(normal_terminal_len) > 0:
        normal_terminal = [normal_terminal_len[0][0]]
    else:
        step = max(1, len(length) // max(1, len(long_terminal)))
        for i in range(0, len(normal_terminal_len), step):
            normal_terminal.append(normal_terminal_len[i][0])
    return long_terminal, normal_terminal


def draw_figure(long_terminal, normal_terminal, output):
    """输出 bad(上排)/good(下排) 的形状对比拼图"""
    n_cols = max(1, len(long_terminal))
    figsize = (n_cols * 5, 10)
    long_imgs = [Path(i + '.png') for i in long_terminal]
    normal_imgs = [Path(i + '.png') for i in normal_terminal]

    fig, axes = plt.subplots(2, n_cols, figsize=figsize)
    if n_cols == 1:
        axes = axes.reshape(2, 1)

    for i, img_path in enumerate(long_imgs):
        if i >= n_cols:
            break
        if img_path.exists():
            img = mpimg.imread(img_path)
            axes[0, i].imshow(img)
        axes[0, i].set_title(img_path.stem + ' bad')
        axes[0, i].axis('off')

    for i, img_path in enumerate(normal_imgs[:n_cols]):
        if img_path.exists():
            img = mpimg.imread(img_path)
            axes[1, i].imshow(img)
        axes[1, i].set_title(img_path.stem)
        axes[1, i].axis('off')

    print('Up: bad Down: good')
    plt.tight_layout()
    plt.savefig(output)
    plt.close(fig)


def sort_tree_by_leaf_count(tree: BaseTree.Tree):
    """按叶子节点数量对树进行排序（影响绘制时分支顺序）"""
    def sort_clades(clade):
        if clade.is_terminal():
            return 1
        else:
            return sum(sort_clades(child) for child in clade.clades)

    def apply_sorting(clade):
        if not clade.is_terminal():
            clade.clades.sort(key=sort_clades)
            for child in clade.clades:
                apply_sorting(child)

    apply_sorting(tree.root)
    return tree


def draw_leaf(name, dots, terminals, tree):
    """根据 .dot.csv 中的坐标为指定叶节点输出单体形状图 (name.png)。"""
    for leaf in tree.get_terminals():
        if leaf.name in terminals:
            # 兼容无扩展名：优先用 <name>.png
            image_path = Path(f"{leaf.name}.png")
            x_idx = np.argwhere(name == leaf.name)
            if x_idx.size == 0:
                continue
            leaf_dot = dots[x_idx[0, 0]].reshape(-1, 2)
            fig2, ax2 = plt.subplots(figsize=(8, 8))
            ax2.plot(leaf_dot[:, 0], leaf_dot[:, 1], 'b', linewidth=3)
            ax2.plot(leaf_dot[0, 0], leaf_dot[0, 1], 'co', linewidth=1, alpha=0.5)
            ax2.axis('equal')
            ax2.axis('off')
            plt.savefig(image_path)
            plt.close(fig2)
    return


# =============================
#  使用 Bio.Phylo.draw 绘树（支持标红 + 画布自适应）
# =============================

def _compute_figsize_by_leaves(n_leaves: int, base_size: int = 25):
    """根据叶子数目调整画布大小。
    <200: 1x, 200-399: 2x, >=400: 4x
    返回 (w, h)
    """
    if n_leaves < 200:
        mul = 1
    elif n_leaves < 400:
        mul = 3
    elif n_leaves < 800:
        mul = 6
    elif n_leaves < 1600:
        mul = 12
    else:
        mul = 20
    return (base_size * mul, base_size * mul)


def _compute_depths(tree: BaseTree.Tree):
    """计算每个clade到根的累积距离（None分支长按1处理），返回dict{clade: x}"""
    depths = {tree.root: 0.0}
    def rec(clade):
        x = depths[clade]
        for ch in clade.clades:
            bl = ch.branch_length if ch.branch_length is not None else 1.0
            depths[ch] = x + bl
            rec(ch)
    rec(tree.root)
    return depths


def _compute_ypos(tree: BaseTree.Tree):
    """给每个clade分配y坐标：叶子按遍历顺序1,2,...；内部为子女y的平均"""
    y = {}
    counter = [0]
    def rec(clade):
        if clade.is_terminal():
            counter[0] += 1
            y[clade] = float(counter[0])
        else:
            for ch in clade.clades:
                rec(ch)
            y[clade] = float(np.mean([y[ch] for ch in clade.clades]))
    rec(tree.root)
    return y


def _find_parent(tree: BaseTree.Tree, target):
    """寻找某个clade的父节点（Biopython默认不保存parent指针）"""
    for cl in tree.find_clades(order='level'):
        for ch in cl.clades:
            if ch is target:
                return cl
    return None


def draw_tree_biophylo(tree: BaseTree.Tree, output_file: Path, text_size: int, long_terminal: set):
    """使用 Bio.Phylo.draw 绘制进化树，并将异常长分支（long_terminal）标签+父→叶末端线段高亮为红色。"""
    n_leaves = len(list(tree.get_terminals()))
    figsize = _compute_figsize_by_leaves(n_leaves, base_size=24)

    # 为需要标红的叶子构造颜色映射（label -> color）
    label_colors = {label: 'red' for label in long_terminal}

    fig, ax = plt.subplots(figsize=figsize)

    # 先用 Biopython 绘树
    Phylo.draw(
        tree,
        axes=ax,
        do_show=False,
        label_func=lambda x: getattr(x, 'name', ''),
        label_colors=label_colors,
    )

    # 统一文字字号
    for txt in ax.texts:
        try:
            txt.set_fontsize(text_size)
        except Exception:
            pass

    # —— 计算与 Biopython 一致的坐标，并覆盖绘制“父→叶”末端两段线（红色） ——
    xmap = _compute_depths(tree)  # clade -> x
    ymap = _compute_ypos(tree)    # clade -> y

    def hi_line(x1, y1, x2, y2, color='red', lw=2.5):
        ax.plot([x1, x2], [y1, y2], color=color, linewidth=lw, solid_capstyle='round')

    for leaf in tree.get_terminals():
        if leaf.name not in long_terminal:
            continue
        parent = _find_parent(tree, leaf)
        if parent is None:
            continue
        # 末端竖直段：x = x_parent, y: y_parent -> y_leaf
        x_p = xmap[parent]
        y_p = ymap[parent]
        x_l = xmap[leaf]
        y_l = ymap[leaf]
        hi_line(x_p, y_p, x_p, y_l, color='red', lw=3.0)   # 竖直
        hi_line(x_p, y_l, x_l, y_l, color='red', lw=3.0)   # 水平

    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f"进化树已保存至：{output_file} (leaves={n_leaves}, figsize={figsize})")


def parse_args():
    parser = argparse.ArgumentParser(description="生成进化树可视化（使用 Bio.Phylo.draw）并输出形状对比")
    parser.add_argument("newick_file", help="输入Newick格式的进化树文件")
    parser.add_argument('-dot', required=True, help='.dot.csv文件（每个叶节点的二维形状坐标）')
    parser.add_argument("-o", "--output", default="tree.png", help="输出图片文件名（默认：tree.png）")
    parser.add_argument("-w", "--img_width", type=int, default=100, help="（保留参数，占位用）")
    parser.add_argument("-t", "--text_size", type=int, default=10, help="文字大小（默认：10）")
    args = parser.parse_args()
    return args


def init_args(arg):
    # init paths
    arg.newick_file = Path(arg.newick_file).resolve()
    assert arg.newick_file.exists()
    arg.dot = Path(arg.dot).resolve()
    assert arg.dot.exists()
    arg.output = Path(arg.output).resolve()
    return arg


def main():
    """主函数：读取树与形状数据，生成可视化结果（Biopython 绘树 + 形状拼图）"""
    arg = parse_args()
    arg = init_args(arg)
    name, data = read_csv(arg.dot)

    # 兼容 Windows 路径分隔符（修正反斜杠转义）
    name = [i.split('\\')[-1] for i in name]
    name = np.array(name, dtype=np.str_)
    a, b = data.shape
    dots = data.reshape(a, b // 2, 2)

    tree = load_and_preprocess_tree(arg.newick_file)
    long_terminal, normal_terminal = get_terminales(tree)

    # 对树进行简单排序（可选，便于美观）
    tree = sort_tree_by_leaf_count(tree)

    # 为 long / normal 叶节点绘制单体形状
    draw_leaf(name, dots, long_terminal, tree)
    draw_leaf(name, dots, normal_terminal, tree)

    # 形状对比拼图
    draw_figure(long_terminal, normal_terminal, arg.output.with_name('compare.png'))

    # 使用 Biopython 自带的绘图接口绘树（带标红与画布自适应）
    draw_tree_biophylo(tree, arg.output, arg.text_size, long_terminal)


if __name__ == "__main__":
    main()
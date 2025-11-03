#!/usr/bin/env python3
"""
list_dir_min.py
纯树状结构，不打印环境/绝对路径
"""
import sys
from pathlib import Path


def tree(path: Path, prefix: str = ''):
    try:
        entries = sorted(path.iterdir(), key=lambda p: (p.is_file(), p.name.lower()))
    except PermissionError:
        print(prefix + "└─ [权限拒绝]")
        return

    pointers = ['├─ '] * (len(entries) - 1) + ['└─ ']
    for pointer, entry in zip(pointers, entries):
        print(prefix + pointer + entry.name)
        if entry.is_dir():
            extension = '│  ' if pointer == '├─ ' else '   '
            tree(entry, prefix + extension)


if __name__ == '__main__':
    # 修复：使用当前目录作为默认路径，而不是那个可能不存在的长路径
    if len(sys.argv) > 1:
        root = Path(sys.argv[1])
    else:
        root = Path('.')  # 使用当前目录

    if not root.exists():
        sys.exit(f'路径不存在: {root}')

    print(f"目录树: {root.name}")  # 只显示目录名
    tree(root)
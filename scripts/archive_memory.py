#!/usr/bin/env python3
"""archive_memory.py — 记忆文档归档

每轮迭代结束，把过程文档按"修改月份"归入 存档-YYYY-MM/<来源目录名>/，
生成归档清单（manifest），不覆盖已有文件（冲突自动加序号后缀）。

用法:
    python archive_memory.py <源目录> [--into <归档根目录>] [--dry-run] [--keep-glob "*.md"]

默认归档根目录 = 源目录下的 存档/；默认只归档文本类过程文档
（*.md / *.txt / *.json / *.html / *.py），目录会递归处理。
源目录本身不被修改（只复制，不移动），确认清单无误后可自行删除原件。

退出码: 0 = 成功; 2 = 参数错误。
"""

import argparse
import shutil
import sys
from datetime import datetime
from pathlib import Path

DEFAULT_GLOBS = ("*.md", "*.txt", "*.json", "*.html", "*.py")


def pick_files(src, globs):
    files = []
    for g in globs:
        files.extend(src.rglob(g))
    # 排除归档根目录内部，防止重复归档
    return sorted({f for f in files if f.is_file()})


def unique_target(target):
    if not target.exists():
        return target
    for i in range(2, 1000):
        cand = target.with_name(f"{target.stem}-{i}{target.suffix}")
        if not cand.exists():
            return cand
    raise RuntimeError(f"无法为 {target} 生成不重名目标")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src", help="源目录（如 进度/）")
    ap.add_argument("--into", default=None, help="归档根目录（默认 <源目录>/存档/）")
    ap.add_argument("--dry-run", action="store_true", help="只打印计划，不实际复制")
    ap.add_argument("--keep-glob", action="append", default=None,
                    help="只归档匹配的文件（可多次指定，默认常见文档扩展名）")
    args = ap.parse_args()

    src = Path(args.src)
    if not src.is_dir():
        print(f"[ERROR] 源目录不存在: {src}")
        return 2
    into = Path(args.into) if args.into else src / "存档"
    globs = tuple(args.keep_glob) if args.keep_glob else DEFAULT_GLOBS

    files = [f for f in pick_files(src, globs) if into not in f.parents]
    if not files:
        print(f"[INFO] {src} 下没有可归档的文档（匹配: {globs}）")
        return 0

    manifest = []
    for f in files:
        mtime = datetime.fromtimestamp(f.stat().st_mtime)
        month_dir = into / f"存档-{mtime:%Y-%m}" / src.name
        target = unique_target(month_dir / f.name)
        manifest.append((f, target, mtime, f.stat().st_size))
        if not args.dry_run:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, target)

    verb = "计划归档" if args.dry_run else "已归档"
    print(f"{verb} {len(manifest)} 个文件 → {into}\n")
    for f, target, mtime, size in manifest:
        print(f"  [{mtime:%Y-%m-%d}] {f}  ({size} B)")
        print(f"      -> {target}")

    manifest_path = into / "manifest.md"
    if not args.dry_run:
        lines = ["# 归档清单", "",
                 f"> 生成时间: {datetime.now():%Y-%m-%d %H:%M:%S}　来源: {src.resolve()}", "",
                 "| 归档时间 | 原路径 | 归档路径 | 大小 |", "| --- | --- | --- | --- |"]
        for f, target, mtime, size in manifest:
            lines.append(f"| {mtime:%Y-%m-%d} | {f} | {target} | {size} B |")
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"\n清单已写入: {manifest_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

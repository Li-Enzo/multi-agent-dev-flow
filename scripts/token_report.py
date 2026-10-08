#!/usr/bin/env python3
"""token_report.py — 文档体量统计与归档/转 references 建议

配合 token-saving 范式（references/token-saving.md）：定期盘点文档体量，
找出"每次会话都被动读到、其实不常改"的大文档与过期过程文档，给出处置建议：
  - 字数 ≥ 阈值（默认 20000）→ 建议转 references/（按需加载，不进活上下文）；
  - 最后修改距今 ≥ 阈值天数（默认 90）→ 建议归档（scripts/archive_memory.py）。

用法:
    python token_report.py <目录...> [--glob "<模式>"] [--top N] [--threshold 字数] [--age 天数]

退出码: 0 = 成功; 2 = 参数错误。
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

DEFAULT_GLOBS = ("*.md", "*.txt")
CHAR_THRESHOLD = 20000
AGE_DAYS = 90


def collect_files(paths, globs):
    files = set()
    for p in paths:
        p = Path(p)
        if p.is_file():
            files.add(p)
        elif p.is_dir():
            for g in globs:
                files.update(f for f in p.rglob(g) if f.is_file())
        else:
            print(f"[ERROR] 路径不存在: {p}")
            return None
    return sorted(files)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src", nargs="+", help="要统计的文件/目录（目录递归处理）")
    ap.add_argument("--glob", dest="globs", action="append", default=None,
                    help="只统计匹配的文件（可多次指定，默认 *.md / *.txt）")
    ap.add_argument("--top", type=int, default=0, help="只显示字数前 N 大的文件（默认全部）")
    ap.add_argument("--threshold", type=int, default=CHAR_THRESHOLD,
                    help=f"转 references 建议阈值，字数 ≥ 此值触发（默认 {CHAR_THRESHOLD}）")
    ap.add_argument("--age", type=int, default=AGE_DAYS,
                    help=f"归档建议阈值，最后修改距今 ≥ 此天数触发（默认 {AGE_DAYS}）")
    args = ap.parse_args()

    globs = tuple(args.globs) if args.globs else DEFAULT_GLOBS
    files = collect_files(args.src, globs)
    if files is None:
        return 2
    if not files:
        print(f"[INFO] 没有匹配 {globs} 的文档")
        return 0

    now = datetime.now().timestamp()
    rows = []
    for f in files:
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            print(f"[WARN] 读取失败，跳过 {f}: {exc}")
            continue
        mtime = f.stat().st_mtime
        rows.append({
            "path": f,
            "lines": len(text.splitlines()),
            "chars": len(text),
            "bytes": f.stat().st_size,
            "mtime": mtime,
            "age_days": (now - mtime) / 86400,
        })

    rows.sort(key=lambda r: r["chars"], reverse=True)
    shown = rows[:args.top] if args.top > 0 else rows

    top_note = f"，仅前 {args.top} 名" if args.top > 0 else ""
    print(f"统计 {len(rows)} 个文档（按字数降序{top_note}）\n")
    header = f"{'文件':<50} {'行数':>6} {'字数':>8} {'大小':>9} {'修改日期':>10}  建议"
    print(header)
    print("-" * len(header) + "----------")
    n_big = n_old = 0
    for r in shown:
        tips = []
        if r["chars"] >= args.threshold:
            tips.append("转 references")
            n_big += 1
        if r["age_days"] >= args.age:
            tips.append("归档")
            n_old += 1
        print(f"{str(r['path']):<50} {r['lines']:>6} {r['chars']:>8} {r['bytes']:>8} B"
              f" {datetime.fromtimestamp(r['mtime']):%Y-%m-%d} {('/'.join(tips)) if tips else '-'}")

    total_lines = sum(r["lines"] for r in rows)
    total_chars = sum(r["chars"] for r in rows)
    print(f"\n合计: {len(rows)} 个文档，{total_lines} 行，约 {total_chars} 字（{total_chars / 1000:.1f} K 字符）")
    print(f"触发建议: 转 references {n_big} 个（≥{args.threshold} 字）; 归档 {n_old} 个（≥{args.age} 天未改）")
    return 0


if __name__ == "__main__":
    sys.exit(main())

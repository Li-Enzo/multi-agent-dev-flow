#!/usr/bin/env python3
"""changelog_check.py — 契约变更同步硬规则的守门员

硬规则：接口契约文档发生任何变更，当次交付必须同步写 CHANGELOG。
本脚本比较契约文件的修改时间与 CHANGELOG 最新条目的日期：
  - 契约 mtime 的日期 > CHANGELOG 最新条目日期  → 报警（契约改了，CHANGELOG 没跟上）
  - 否则通过。

用法:
    python changelog_check.py <契约文档.md> <CHANGELOG.md>

退出码: 0 = 同步; 1 = 契约新于 CHANGELOG（违反硬规则）; 2 = 文件错误。
"""

import re
import sys
from datetime import datetime
from pathlib import Path

DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")


def latest_changelog_date(changelog_path):
    """从 CHANGELOG 中提取最新条目的日期（按文件中出现顺序取第一个日期）。"""
    text = changelog_path.read_text(encoding="utf-8")
    # 条目标题形如 "## V2.4.2 · 2026-10-03（...）"
    # 约定 CHANGELOG 最新条目在前；但无论正序倒序，取所有条目标题中的最大日期，
    # 避免"条目追加在文件尾"的写法导致误判
    dates = []
    for line in text.splitlines():
        if line.lstrip().startswith("#"):
            m = DATE_RE.search(line)
            if m:
                dates.append(datetime.strptime(m.group(1), "%Y-%m-%d"))
    if dates:
        return max(dates)
    # 退化：全文第一个日期
    m = DATE_RE.search(text)
    if m:
        return datetime.strptime(m.group(1), "%Y-%m-%d")
    return None


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        return 2
    contract = Path(sys.argv[1])
    changelog = Path(sys.argv[2])
    for p in (contract, changelog):
        if not p.is_file():
            print(f"[ERROR] 文件不存在: {p}")
            return 2

    contract_mtime = datetime.fromtimestamp(contract.stat().st_mtime)
    cl_date = latest_changelog_date(changelog)
    if cl_date is None:
        print(f"[ERROR] 未能在 {changelog} 中找到任何日期条目")
        return 2

    print(f"契约最后修改 : {contract_mtime:%Y-%m-%d %H:%M:%S}")
    print(f"CHANGELOG 最新条目日期 : {cl_date:%Y-%m-%d}")

    if contract_mtime.date() > cl_date.date():
        print("\n[FAIL] 契约修改时间晚于 CHANGELOG 最新条目 → 违反硬规则：")
        print("       本次交付必须补充 CHANGELOG 条目并重打包文档包后，才能算交付完成。")
        return 1
    print("\n[ OK ] 契约与 CHANGELOG 同步")
    return 0


if __name__ == "__main__":
    sys.exit(main())

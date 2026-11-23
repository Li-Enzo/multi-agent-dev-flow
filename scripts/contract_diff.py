#!/usr/bin/env python3
"""contract_diff.py — 契约破坏性变更检测

对比两版契约文档（旧 vs 新），识别会破坏调用方的变更（防并行 agent 改崩调用方）：
  1. 接口删除：旧版存在的 action 在新版消失
  2. 字段删除：入参/出参表中的既有字段被移除
  3. 类型变更：已存字段的类型收窄或改变（一律判破坏， widening 也应走评审）
  4. 必填加强：入参新增必填字段，或既有选填入参改为必填
  5. 必有降级：出参「必有」字段变为可选（调用方按必有读取会拿到缺字段）

非破坏性变更仅 INFO 提示，不影响退出码：
  新增接口 / 新增可选入参 / 新增出参字段 / 必填放宽为选填 / 出参可选提为必有。

用法:
    python contract_diff.py <旧契约.md> <新契约.md>

退出码: 0 = 无破坏性变更; 1 = 存在破坏性变更; 2 = 文件/结构错误。
"""

import re
import sys
from pathlib import Path

from contract_lint import HEADING_RE, TABLE_ROW_RE, is_separator_row, parse_interfaces

ACTION_RE = re.compile(r"\|\s*action\s*\|\s*`([^`]+)`", re.I)


def _norm_type(cell: str) -> str:
    """类型单元格归一化：去反引号、压缩空白（`list<string>` 与 list < string > 视为同型）。"""
    return " ".join(cell.strip().strip("`").split())


def parse_field_table(body, keyword: str, required_col: str):
    """解析 body 中 keyword 标题行后的首个字段表。

    返回 {字段名: {"type": 类型, "required": bool}}；找不到表或缺关键列返回 None。
    required_col：入参表为「必填」，出参表为「必有」。
    """
    for i, line in enumerate(body):
        if keyword not in line:
            continue
        rows = []
        for j in range(i + 1, len(body)):
            if TABLE_ROW_RE.match(body[j]):
                rows.append(body[j])
            elif rows or HEADING_RE.match(body[j]):
                break
        if not rows:
            return None
        header = [c.strip() for c in rows[0].strip().strip("|").split("|")]
        try:
            fi, ti = header.index("字段"), header.index("类型")
            ri = header.index(required_col)
        except ValueError:
            return None
        fields = {}
        for row in rows[1:]:
            cells = [c.strip() for c in row.strip().strip("|").split("|")]
            if is_separator_row(cells) or len(cells) <= max(fi, ti, ri):
                continue
            name = cells[fi].strip("`")
            if not name:
                continue
            fields[name] = {
                "type": _norm_type(cells[ti]),
                "required": cells[ri].strip() == "是",
            }
        return fields
    return None


def parse_contract(text: str):
    """解析契约文档，返回 {action: {"title", "in", "out"}}（按文档顺序）。"""
    interfaces = {}
    for domain, title, body in parse_interfaces(text):
        m = ACTION_RE.search("\n".join(body))
        if not m:
            continue
        interfaces[m.group(1)] = {
            "title": f"{domain} > {title}",
            "in": parse_field_table(body, "入参", "必填") or {},
            "out": parse_field_table(body, "出参", "必有") or {},
        }
    return interfaces


def diff_contracts(old: dict, new: dict):
    """对比两版契约模型，返回 (breaking, info)，元素为 (接口标签, 问题描述)。"""
    breaking, info = [], []
    for action, o in old.items():
        label = f"`{action}`（{o['title']}）"
        n = new.get(action)
        if n is None:
            breaking.append((label, f"接口 `{action}` 在新版中被删除"))
            continue
        for direction, human in (("in", "入参"), ("out", "出参")):
            of, nf = o[direction], n[direction]
            for name, meta in of.items():
                cur = nf.get(name)
                if cur is None:
                    breaking.append((label, f"{human}字段 `{name}` 被删除"))
                elif meta["type"] != cur["type"]:
                    breaking.append((label, f"{human}字段 `{name}` 类型变更 "
                                            f"`{meta['type']}` → `{cur['type']}`"))
                elif direction == "in" and not meta["required"] and cur["required"]:
                    breaking.append((label, f"入参字段 `{name}` 由选填改为必填"
                                            "（旧版调用方不会传）"))
                elif direction == "out" and meta["required"] and not cur["required"]:
                    breaking.append((label, f"出参字段 `{name}` 由必有降级为可选"
                                            "（调用方按必有读取会拿到缺字段）"))
                elif direction == "in" and meta["required"] and not cur["required"]:
                    info.append((label, f"入参字段 `{name}` 由必填放宽为选填"))
                elif direction == "out" and not meta["required"] and cur["required"]:
                    info.append((label, f"出参字段 `{name}` 由可选提升为必有"))
            for name, meta in nf.items():
                if name in of:
                    continue
                if direction == "in" and meta["required"]:
                    breaking.append((label, f"新增必填入参 `{name}`（旧版调用方不会传）"))
                else:
                    info.append((label, f"新增{human}字段 `{name}`"))
    for action, n in new.items():
        if action not in old:
            info.append((f"`{action}`（{n['title']}）", "新增接口（向后兼容）"))
    return breaking, info


def main():
    if len(sys.argv) != 3 or sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        return 0 if len(sys.argv) >= 2 else 2
    old_path, new_path = Path(sys.argv[1]), Path(sys.argv[2])
    for p in (old_path, new_path):
        if not p.is_file():
            print(f"[ERROR] 文件不存在: {p}")
            return 2
    old = parse_contract(old_path.read_text(encoding="utf-8"))
    new = parse_contract(new_path.read_text(encoding="utf-8"))
    for p, model in ((old_path, old), (new_path, new)):
        if not model:
            print(f"[ERROR] 未在 {p} 中解析到任何接口块（需含 '| action |' 元信息表）")
            return 2

    breaking, info = diff_contracts(old, new)

    # 按接口分组输出，保持文档顺序；无破坏性变更的旧接口标 [ OK ]
    labels = [f"`{a}`（{m['title']}）" for a, m in old.items()]
    for label in labels:
        problems = [msg for lb, msg in breaking if lb == label]
        notes = [msg for lb, msg in info if lb == label]
        tag = "FAIL" if problems else " OK "
        print(f"[{tag}] {label}")
        for msg in problems:
            print(f"       - {msg}")
        for msg in notes:
            print(f"       (info) {msg}")
    for lb, msg in info:
        if lb not in labels:  # 新增接口
            print(f"[INFO] {lb}")
            print(f"       (info) {msg}")

    added = sum(1 for a in new if a not in old)
    print(f"\n共对比 {len(old)} 个接口（新增 {added} 个），"
          f"破坏性变更 {len(breaking)} 个")
    return 1 if breaking else 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""contract_lint.py — 接口契约文档完整性检查

代替 AI 逐行人工审查契约文档。检查每个接口小节是否具备：
  1. action 元信息表（含 action 名与鉴权行）
  2. 入参表（表头须含 字段/类型/必填）
  3. 出参表（表头须含 字段/类型）
  4. 错误码小节

用法:
    python contract_lint.py <契约文档.md> [--strict]

退出码: 0 = 全部通过; 1 = 存在缺项; 2 = 文件/结构错误。
"""

import re
import sys
from pathlib import Path

HEADING_RE = re.compile(r"^(#{2,3})\s+(.*)$")
TABLE_ROW_RE = re.compile(r"^\s*\|.*\|\s*$")


def parse_interfaces(text):
    """按章节切分，返回 [(编号, 标题, 块文本)]，仅保留含 action 元信息表的块。"""
    lines = text.splitlines()
    blocks = []
    current = None  # (level, title, [lines])

    def flush():
        if current is not None:
            blocks.append(current)

    for line in lines:
        m = HEADING_RE.match(line)
        if m:
            flush()
            level = len(m.group(1))
            # 新的 ## 或 ### 开始新块；## 会终结其下所有 ###
            if blocks and level <= blocks[-1][0]:
                pass
            current = (level, m.group(2).strip(), [])
        else:
            if current is None:
                current = (0, "<文件头>", [])
            current[2].append(line)
    flush()

    # 归并：把 ### 块挂在所属 ## 域下，再筛出含 "| action |" 的接口块
    interfaces = []
    domain = ""
    for level, title, body in blocks:
        if level == 2:
            domain = title
        block_text = "\n".join(body)
        if "| action |" in block_text.lower():
            interfaces.append((domain, title, body))
    return interfaces


def table_headers_after(body, keyword):
    """在 body 中找到 keyword 标题行，返回其后第一个表格的表头单元格列表。"""
    for i, line in enumerate(body):
        if keyword in line:
            for j in range(i + 1, len(body)):
                if TABLE_ROW_RE.match(body[j]):
                    cells = [c.strip() for c in body[j].strip().strip("|").split("|")]
                    return cells
                if HEADING_RE.match(body[j]):
                    return None
    return None


def lint_block(domain, title, body):
    problems = []
    text = "\n".join(body)
    if not re.search(r"\|\s*action\s*\|\s*`[^`]+`", text, re.I):
        problems.append("action 元信息表缺少具体的 action 名（应形如 | action | `xxx` |）")
    if not re.search(r"\|\s*鉴权\s*\|", text):
        problems.append("缺少鉴权行（| 鉴权 | 公开/需登录/需权限点 |）")

    in_headers = table_headers_after(body, "入参")
    if in_headers is None:
        problems.append("缺少入参表")
    elif not ({"字段", "类型", "必填"} <= set(in_headers)):
        problems.append(f"入参表表头缺列（应为 字段/类型/必填/含义/示例，实际：{in_headers}）")

    out_headers = table_headers_after(body, "出参")
    if out_headers is None:
        problems.append("缺少出参表")
    elif not ({"字段", "类型"} <= set(out_headers)):
        problems.append(f"出参表表头缺列（实际：{out_headers}）")

    if "错误码" not in text:
        problems.append("缺少错误码小节")
    return problems


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        return 0 if len(sys.argv) >= 2 else 2
    path = Path(sys.argv[1])
    if not path.is_file():
        print(f"[ERROR] 文件不存在: {path}")
        return 2
    text = path.read_text(encoding="utf-8")
    interfaces = parse_interfaces(text)
    if not interfaces:
        print(f"[ERROR] 未在 {path} 中解析到任何接口块（需含 '| action |' 元信息表）")
        return 2

    total_problems = 0
    for domain, title, body in interfaces:
        problems = lint_block(domain, title, body)
        if problems:
            total_problems += len(problems)
            print(f"[FAIL] {domain} > {title}")
            for p in problems:
                print(f"       - {p}")
        else:
            print(f"[ OK ] {domain} > {title}")

    print(f"\n共检查 {len(interfaces)} 个接口，问题 {total_problems} 个")
    return 1 if total_problems else 0


if __name__ == "__main__":
    sys.exit(main())

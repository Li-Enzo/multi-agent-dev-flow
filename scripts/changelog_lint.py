#!/usr/bin/env python3
"""changelog_lint.py — CHANGELOG 与 commit message 范式守门

两项检查（可任意组合，至少一项）：
  1. CHANGELOG「## Unreleased」章节非空：必须存在且至少有一条非空条目
     （防止"代码变了、日志没记"）；
  2. commit message 范式：首行必须匹配 `type(scope): 简述`，
     type ∈ feat/fix/docs/refactor/test/chore，scope 必填，简述非空。
     消息来源三选一：--msg 内联 / --msg-file 文件 / --git-range A..B（git log）。

用法:
    python changelog_lint.py <CHANGELOG路径>
    python changelog_lint.py <CHANGELOG路径> --git-range HEAD~3..HEAD
    python changelog_lint.py --msg "feat(scripts): 新增 xxx"          # 仅查消息
    python changelog_lint.py --msg-file .git/COMMIT_EDITMSG           # commit-msg 钩子

退出码: 0 = 全部通过; 1 = 存在违规; 2 = 参数/IO/环境错误。
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

TYPES = ("feat", "fix", "docs", "refactor", "test", "chore")
MSG_RE = re.compile(
    r"^(?P<type>" + "|".join(TYPES) + r")"
    r"\((?P<scope>[a-z0-9_/-]+)\)"
    r": (?P<summary>\S.*)$"
)
UNRELEASED_RE = re.compile(r"^##\s+Unreleased\b", re.I)
BULLET_RE = re.compile(r"^\s*[-*]\s+\S")


def check_unreleased(text: str):
    """返回问题描述或 None：Unreleased 章节必须存在且含至少一条非空条目。"""
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if UNRELEASED_RE.match(line):
            body = []
            for rest in lines[i + 1:]:
                if rest.startswith("## "):
                    break
                body.append(rest)
            if not any(BULLET_RE.match(l) for l in body):
                return "「## Unreleased」章节没有任何条目（代码变了，日志没记）"
            return None
    return "未找到「## Unreleased」章节"


def check_message(msg: str):
    """校验单条 commit message 首行范式，返回问题描述或 None。"""
    subject = msg.splitlines()[0].strip() if msg.strip() else ""
    if not subject:
        return "空 commit message"
    m = MSG_RE.match(subject)
    if m:
        return None
    head = subject.split("(", 1)[0].split(":", 1)[0].strip()
    if head in TYPES and "(" not in subject.split(":", 1)[0]:
        return f"缺少 scope（应为 `{head}(scope): 简述`）: {subject!r}"
    return f"不符合 `type(scope): 简述`（type ∈ {'/'.join(TYPES)}）: {subject!r}"


def git_subjects(rng: str, cwd: Path):
    """git log 取范围内每条提交的首行；返回 (subjects, 错误描述)。"""
    try:
        r = subprocess.run(
            ["git", "log", "--format=%s", rng],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            cwd=str(cwd),
        )
    except OSError as exc:
        return None, f"无法执行 git: {exc}"
    if r.returncode != 0:
        return None, f"git log {rng} 失败: {r.stderr.strip()}"
    return [l for l in r.stdout.splitlines() if l.strip()], None


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("changelog", nargs="?", default=None,
                    help="CHANGELOG.md 路径（省略则只查 commit message）")
    ap.add_argument("--msg", default=None, help="内联单条 commit message")
    ap.add_argument("--msg-file", default=None, help="commit message 文件（如 commit-msg 钩子）")
    ap.add_argument("--git-range", metavar="A..B", default=None,
                    help="git 提交范围，逐条校验首行（git 在 CHANGELOG 所在目录执行）")
    args = ap.parse_args()

    if args.changelog is None and not (args.msg or args.msg_file or args.git_range):
        print("[ERROR] 至少给一项检查：CHANGELOG 路径 / --msg / --msg-file / --git-range")
        return 2

    problems = 0

    if args.changelog is not None:
        path = Path(args.changelog)
        if not path.is_file():
            print(f"[ERROR] 文件不存在: {path}")
            return 2
        problem = check_unreleased(path.read_text(encoding="utf-8"))
        if problem:
            problems += 1
            print(f"[FAIL] {path}")
            print(f"       - {problem}")
        else:
            print(f"[ OK ] {path}（Unreleased 非空）")

    # 收集待校验的 commit message
    messages = []  # (来源标签, message)
    if args.msg is not None:
        messages.append(("--msg", args.msg))
    if args.msg_file is not None:
        msg_path = Path(args.msg_file)
        if not msg_path.is_file():
            print(f"[ERROR] 文件不存在: {msg_path}")
            return 2
        messages.append((str(msg_path), msg_path.read_text(encoding="utf-8")))
    if args.git_range is not None:
        cwd = Path(args.changelog).resolve().parent if args.changelog else Path.cwd()
        subjects, error = git_subjects(args.git_range, cwd)
        if error:
            print(f"[ERROR] {error}")
            return 2
        for s in subjects:
            messages.append((f"git {args.git_range}", s))

    bad = [(src, m, check_message(m)) for src, m in messages]
    bad = [(src, m, p) for src, m, p in bad if p]
    for src, m, p in bad:
        problems += 1
        print(f"[FAIL] {src}")
        print(f"       - {p}")
    ok_count = len(messages) - len(bad)
    if messages:
        print(f"[ OK ] commit message 范式通过 {ok_count}/{len(messages)} 条")

    print(f"\n检查完成，问题 {problems} 个")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""doc_pack.py — 文档包一键打包与硬规则校验

把"契约变更硬规则"（references/agent-collab.md §5）做成工具：
  1. 打包：把指定文档打成 versioned zip 包；
  2. 版本号连续不跳号：扫描输出目录已有 <name>-v<N>.zip，新版本 = 最大版本 + 1；
  3. 字节一致校验：打包后重开包，包内每个成员与磁盘文件逐字节比对；
  4. 时序校验：包文件 mtime 晚于所有源文件的最后修改时间；
  5. 旧包移入存档目录。

用法:
    python doc_pack.py [源路径...] [-o <输出目录>] [--name <包名前缀>] [--archive <存档目录>] [--dry-run]

源路径缺省为 docs/；目录会递归收集 *.md / *.txt / *.json。
默认输出目录为 文档包/，存档目录为 文档包/存档/。

退出码: 0 = 打包并校验通过; 1 = 字节/时序校验失败; 2 = 参数/IO 错误。
"""

import argparse
import os
import re
import shutil
import sys
import zipfile
from datetime import datetime
from pathlib import Path

DEFAULT_GLOBS = ("*.md", "*.txt", "*.json")
VERSION_RE = re.compile(r"^(?P<name>.+)-v(?P<ver>\d+)\.zip$")


def collect_sources(paths, globs):
    """把文件/目录参数展开为去重排序后的文件列表。"""
    files = set()
    for p in paths:
        p = Path(p)
        if p.is_file():
            files.add(p)
        elif p.is_dir():
            for g in globs:
                files.update(f for f in p.rglob(g) if f.is_file())
        else:
            print(f"[ERROR] 源路径不存在: {p}")
            return None
    return sorted(files)


def list_packs(out_dir, name):
    """返回输出目录下 <name>-v<N>.zip 的 [(版本号, 路径)]，按版本升序。"""
    packs = []
    if not out_dir.is_dir():
        return packs
    for f in out_dir.glob(f"{name}-v*.zip"):
        m = VERSION_RE.match(f.name)
        if m and m.group("name") == name:
            packs.append((int(m.group("ver")), f))
    return sorted(packs)


def make_members(sources):
    """为每个源文件计算包内成员名：相对公共根的 posix 相对路径（绝对路径不进包）。"""
    common = Path(os.path.commonpath([str(f) for f in sources]))
    if not common.is_dir():
        common = common.parent
    return [(str(f.relative_to(common)).replace("\\", "/"), f) for f in sources]


def verify_pack(pack, members):
    """硬规则校验：包内成员与磁盘逐字节一致；包 mtime 晚于所有源文件 mtime。"""
    problems = []
    disk = dict(members)
    with zipfile.ZipFile(pack) as zf:
        names = [n for n in zf.namelist() if not n.endswith("/")]
        if set(names) != set(disk):
            missing = sorted(set(disk) - set(names))
            extra = sorted(set(names) - set(disk))
            if missing:
                problems.append(f"包内缺少成员: {missing}")
            if extra:
                problems.append(f"包内多出成员: {extra}")
        for n in names:
            if n in disk:
                if zf.read(n) != disk[n].read_bytes():
                    problems.append(f"字节不一致: {n}（包内与磁盘不同）")
    src_mtime = max(f.stat().st_mtime for _, f in members)
    if pack.stat().st_mtime < src_mtime:
        problems.append(
            f"包 mtime 早于源文件最后修改（{datetime.fromtimestamp(pack.stat().st_mtime):%Y-%m-%d %H:%M:%S}"
            f" < {datetime.fromtimestamp(src_mtime):%Y-%m-%d %H:%M:%S}）")
    return problems


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("src", nargs="*", default=None, help="源文件/目录（缺省 docs/）")
    ap.add_argument("-o", "--out", default="文档包", help="输出目录（默认 文档包/）")
    ap.add_argument("--name", default="docpack", help="包名前缀（默认 docpack）")
    ap.add_argument("--archive", default=None, help="旧包存档目录（默认 <输出目录>/存档/）")
    ap.add_argument("--dry-run", action="store_true", help="只打印计划，不实际打包")
    args = ap.parse_args()

    out_dir = Path(args.out)
    archive_dir = Path(args.archive) if args.archive else out_dir / "存档"
    src_paths = args.src if args.src else ["docs"]
    sources = collect_sources(src_paths, DEFAULT_GLOBS)
    if sources is None:
        return 2
    # 排除输出/存档目录，防止把旧包打进新包
    sources = [f for f in sources if out_dir not in f.parents and archive_dir not in f.parents]
    if not sources:
        print("[ERROR] 没有可打包的文档")
        return 2
    members = make_members(sources)

    packs = list_packs(out_dir, args.name)
    new_ver = (packs[-1][0] + 1) if packs else 1
    new_pack = out_dir / f"{args.name}-v{new_ver}.zip"

    print(f"源文件 {len(sources)} 个（最新修改: {datetime.fromtimestamp(max(f.stat().st_mtime for f in sources)):%Y-%m-%d %H:%M:%S}）")
    print(f"版本接续: {packs[-1][0] if packs else 0} → {new_ver}　输出: {new_pack}\n")
    for f in sources:
        print(f"  {f}　({f.stat().st_size} B)")

    if args.dry_run:
        print("\n[INFO] dry-run：以上仅为打包计划")
        return 0

    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(new_pack, "w", zipfile.ZIP_DEFLATED) as zf:
            for arcname, f in members:
                zf.write(f, arcname=arcname)
    except OSError as exc:
        print(f"\n[ERROR] 打包失败: {exc}")
        return 2

    problems = verify_pack(new_pack, members)
    if problems:
        print(f"\n[FAIL] 文档包 v{new_ver} 未通过硬规则校验:")
        for p in problems:
            print(f"       - {p}")
        new_pack.unlink(missing_ok=True)
        return 1
    print(f"\n[ OK ] 字节一致校验通过：{len(sources)} 个成员与磁盘逐字节相同")
    print(f"[ OK ] 时序校验通过：包 mtime 晚于所有源文件")

    moved = []
    if packs:
        archive_dir.mkdir(parents=True, exist_ok=True)
        for _, old in packs:
            target = archive_dir / old.name
            if target.exists():
                print(f"[ERROR] 存档目录已存在同名旧包: {target}（跳过移动，请人工处理）")
                continue
            shutil.move(str(old), str(target))
            moved.append(target)
        print(f"[ OK ] 旧包 {len(moved)} 个已移入存档: {archive_dir}")
    print(f"\n文档包 v{new_ver} 打包完成: {new_pack}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

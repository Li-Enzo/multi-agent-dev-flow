"""token_report.py 回归用例：体量统计、归档/转 references 建议、错误路径。"""
import os
import time


def test_stats_and_suggestions(run_script, tmp_path):
    (tmp_path / "active.md").write_text("# 活跃\n短内容。\n", encoding="utf-8")
    big = tmp_path / "big.md"
    big.write_text("# 大文档\n" + "每行约二十个汉字用于填充体量统计。\n" * 1200, encoding="utf-8")
    old = tmp_path / "old.md"
    old.write_text("# 旧文档\n", encoding="utf-8")
    old_ts = time.time() - 400 * 86400
    os.utime(old, (old_ts, old_ts))

    r = run_script("token_report.py", tmp_path)
    assert r.returncode == 0
    assert "big.md" in r.stdout and "转 references" in r.stdout
    assert "old.md" in r.stdout and "归档" in r.stdout
    assert "active.md" in r.stdout
    assert "合计" in r.stdout


def test_top_n(run_script, tmp_path):
    for i in range(5):
        (tmp_path / f"f{i}.md").write_text("# x\n" + "字" * (i * 100), encoding="utf-8")
    r = run_script("token_report.py", tmp_path, "--top", "2")
    assert r.returncode == 0
    assert "仅前 2 名" in r.stdout
    assert "f4.md" in r.stdout and "f0.md" not in r.stdout


def test_custom_thresholds(run_script, tmp_path):
    (tmp_path / "a.md").write_text("# x\n" + "字" * 50, encoding="utf-8")
    r = run_script("token_report.py", tmp_path, "--threshold", "10", "--age", "30")
    assert r.returncode == 0
    assert "转 references 1 个（≥10 字）" in r.stdout


def test_missing_path_exit_2(run_script, tmp_path):
    r = run_script("token_report.py", tmp_path / "none")
    assert r.returncode == 2


def test_repo_docs_run_clean(run_script):
    from conftest import REPO_ROOT
    r = run_script("token_report.py", REPO_ROOT / "references", REPO_ROOT / "docs")
    assert r.returncode == 0
    assert "合计" in r.stdout

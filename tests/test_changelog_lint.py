"""changelog_lint.py 回归用例：Unreleased 非空校验 + commit message 范式检查。"""
import pytest

VALID_CHANGELOG = """# CHANGELOG

## Unreleased

- feat(scripts): 新增某脚本。

## v1.1.0 — 2026-10-09

- 历史条目。
"""

EMPTY_UNRELEASED = """# CHANGELOG

## Unreleased

## v1.1.0 — 2026-10-09

- 历史条目。
"""


def _write(tmp_path, text):
    p = tmp_path / "CHANGELOG.md"
    p.write_text(text, encoding="utf-8")
    return p


def test_repo_changelog_passes(run_script):
    from conftest import REPO_ROOT
    r = run_script("changelog_lint.py", REPO_ROOT / "CHANGELOG.md")
    assert r.returncode == 0
    assert "Unreleased 非空" in r.stdout


def test_valid_unreleased_passes(run_script, tmp_path):
    r = run_script("changelog_lint.py", _write(tmp_path, VALID_CHANGELOG))
    assert r.returncode == 0


def test_empty_unreleased_fails(run_script, tmp_path):
    r = run_script("changelog_lint.py", _write(tmp_path, EMPTY_UNRELEASED))
    assert r.returncode == 1
    assert "没有任何条目" in r.stdout


def test_missing_unreleased_section_fails(run_script, tmp_path):
    r = run_script("changelog_lint.py", _write(tmp_path, "# CHANGELOG\n\n## v1.0.0\n\n- x\n"))
    assert r.returncode == 1
    assert "未找到" in r.stdout


def test_missing_file_exit_2(run_script, tmp_path):
    r = run_script("changelog_lint.py", tmp_path / "nope.md")
    assert r.returncode == 2


@pytest.mark.parametrize("msg", [
    "feat(scripts): 新增 changelog_lint",
    "docs(changelog): 补条目",
    "fix(api): 修复边界条件",
    "chore(ci): 接入门禁",
])
def test_good_commit_messages_pass(run_script, msg):
    r = run_script("changelog_lint.py", "--msg", msg)
    assert r.returncode == 0


@pytest.mark.parametrize("msg", [
    "新增 changelog_lint",               # 无 type/scope
    "feat: 缺少 scope",                  # 无 scope
    "wip(scripts): 非法 type",           # type 不在表内
    "feat(scripts):",                    # 缺简述
    "feat(scripts): ",                   # 简述为空白
])
def test_bad_commit_messages_fail(run_script, msg):
    r = run_script("changelog_lint.py", "--msg", msg)
    assert r.returncode == 1
    assert "[FAIL]" in r.stdout


def test_missing_scope_diagnostic(run_script):
    r = run_script("changelog_lint.py", "--msg", "feat: 缺少 scope")
    assert r.returncode == 1
    assert "缺少 scope" in r.stdout


def test_msg_file(run_script, tmp_path):
    f = tmp_path / "COMMIT_EDITMSG"
    f.write_text("refactor(store): 拆分解耦\n\n正文随意\n", encoding="utf-8")
    r = run_script("changelog_lint.py", "--msg-file", f)
    assert r.returncode == 0


def test_no_check_given_exit_2(run_script):
    r = run_script("changelog_lint.py")
    assert r.returncode == 2


@pytest.mark.skipif(not (__import__("pathlib").Path(__file__).resolve().parent.parent / ".git").exists(),
                    reason="非 git 环境（源码包）跳过 git-range 用例")
def test_git_range_against_repo_history(run_script):
    # 本仓库自身历史即范式样本：最近若干提交必须全部合规
    r = run_script("changelog_lint.py", "--git-range", "HEAD~5..HEAD")
    assert r.returncode == 0
    assert "范式通过" in r.stdout


def test_git_range_bad_revision_exit_2(run_script, tmp_path):
    r = run_script("changelog_lint.py", _write(tmp_path, VALID_CHANGELOG),
                   "--git-range", "no-such-ref..HEAD")
    assert r.returncode == 2

"""doc_pack.py 回归用例：打包、版本接续、字节一致校验、旧包存档。"""
import zipfile

import doc_pack


def _make_docs(tmp_path):
    docs = tmp_path / "docs"
    (docs / "sub").mkdir(parents=True)
    (docs / "api-contract.md").write_text("# 契约\n", encoding="utf-8")
    (docs / "sub" / "config.json").write_text('{"action": "x"}', encoding="utf-8")
    return docs


def test_pack_first_version(run_script, tmp_path):
    docs = _make_docs(tmp_path)
    r = run_script("doc_pack.py", docs, "-o", tmp_path / "包")
    assert r.returncode == 0
    assert (tmp_path / "包" / "docpack-v1.zip").is_file()
    assert "字节一致校验通过" in r.stdout


def test_version_sequence_and_archive(run_script, tmp_path):
    docs = _make_docs(tmp_path)
    out = tmp_path / "包"
    assert run_script("doc_pack.py", docs, "-o", out).returncode == 0
    r = run_script("doc_pack.py", docs, "-o", out)
    assert r.returncode == 0
    assert (out / "docpack-v2.zip").is_file()
    assert (out / "存档" / "docpack-v1.zip").is_file()
    assert not (out / "docpack-v1.zip").exists()


def test_dry_run_creates_nothing(run_script, tmp_path):
    docs = _make_docs(tmp_path)
    r = run_script("doc_pack.py", docs, "-o", tmp_path / "包", "--dry-run")
    assert r.returncode == 0
    assert not (tmp_path / "包").exists()


def test_verify_pack_detects_tampered_bytes(tmp_path):
    docs = _make_docs(tmp_path)
    src = docs / "api-contract.md"
    bad = tmp_path / "bad.zip"
    with zipfile.ZipFile(bad, "w") as zf:
        zf.writestr("api-contract.md", "被篡改的内容")
    problems = doc_pack.verify_pack(bad, [("api-contract.md", src)])
    assert any("字节不一致" in p for p in problems)


def test_verify_pack_detects_missing_member(tmp_path):
    docs = _make_docs(tmp_path)
    src = docs / "api-contract.md"
    bad = tmp_path / "bad.zip"
    with zipfile.ZipFile(bad, "w") as zf:
        zf.writestr("other.md", "# 别的文件\n")
    problems = doc_pack.verify_pack(bad, [("api-contract.md", src)])
    assert any("缺少成员" in p for p in problems)


def test_missing_source_path_exit_2(run_script, tmp_path):
    r = run_script("doc_pack.py", tmp_path / "none", "-o", tmp_path / "包")
    assert r.returncode == 2


def test_empty_docs_exit_2(run_script, tmp_path):
    empty = tmp_path / "empty"
    empty.mkdir()
    r = run_script("doc_pack.py", empty, "-o", tmp_path / "包")
    assert r.returncode == 2

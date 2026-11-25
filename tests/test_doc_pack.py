"""doc_pack.py 回归用例：打包、版本接续、字节一致校验、旧包存档、manifest 完整性自检。"""
import hashlib
import json
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


# ---- manifest.json 完整性清单（打包生成 + 解包侧 --verify 自检）----

def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def test_pack_writes_manifest_with_sha256(run_script, tmp_path):
    docs = _make_docs(tmp_path)
    r = run_script("doc_pack.py", docs, "-o", tmp_path / "包", "--name", "api-docs")
    assert r.returncode == 0
    assert "完整性清单" in r.stdout
    pack = tmp_path / "包" / "api-docs-v1.zip"
    with zipfile.ZipFile(pack) as zf:
        assert zf.namelist()[0] == "manifest.json"  # 首成员
        manifest = json.loads(zf.read("manifest.json").decode("utf-8"))
    assert manifest["name"] == "api-docs"
    assert manifest["version"] == 1
    listed = {e["path"]: e for e in manifest["files"]}
    assert set(listed) == {"api-contract.md", "sub/config.json"}
    for arcname, entry in listed.items():
        data = (docs / arcname).read_bytes()
        assert entry["sha256"] == _sha(data)
        assert entry["size"] == len(data)


def test_verify_mode_ok(run_script, tmp_path):
    docs = _make_docs(tmp_path)
    out = tmp_path / "包"
    run_script("doc_pack.py", docs, "-o", out)
    r = run_script("doc_pack.py", "--verify", out / "docpack-v1.zip")
    assert r.returncode == 0
    assert "完整性自检通过" in r.stdout


def test_verify_mode_detects_tampered_member(run_script, tmp_path):
    bad = tmp_path / "tampered.zip"
    with zipfile.ZipFile(bad, "w") as zf:
        zf.writestr("manifest.json", json.dumps({"files": [
            {"path": "a.md", "sha256": "0" * 64, "size": 3},
        ]}))
        zf.writestr("a.md", "xyz")
    r = run_script("doc_pack.py", "--verify", bad)
    assert r.returncode == 1
    assert "SHA-256 不一致" in r.stdout


def test_verify_mode_detects_extra_and_missing(run_script, tmp_path):
    bad = tmp_path / "extra.zip"
    with zipfile.ZipFile(bad, "w") as zf:
        zf.writestr("manifest.json", json.dumps({"files": [
            {"path": "a.md", "sha256": _sha(b"# a\n"), "size": 4},
            {"path": "gone.md", "sha256": _sha(b"gone"), "size": 4},
        ]}))
        zf.writestr("a.md", "# a\n")
        zf.writestr("b.md", "清单外成员")
    r = run_script("doc_pack.py", "--verify", bad)
    assert r.returncode == 1
    assert "包内缺失" in r.stdout
    assert "清单外成员" in r.stdout


def test_verify_mode_rejects_pack_without_manifest(run_script, tmp_path):
    legacy = tmp_path / "legacy.zip"
    with zipfile.ZipFile(legacy, "w") as zf:
        zf.writestr("a.md", "# a\n")
    r = run_script("doc_pack.py", "--verify", legacy)
    assert r.returncode == 1
    assert "无法自检" in r.stdout


def test_verify_mode_missing_file_exit_2(run_script, tmp_path):
    r = run_script("doc_pack.py", "--verify", tmp_path / "nope.zip")
    assert r.returncode == 2

"""contract_lint.py 回归用例：完整性检查 + 错误码登记合法性。"""
import pytest

VALID_CONTRACT = """# 示例契约

## 1. 通用约定

### 1.2 统一响应

| code | 含义 |
| --- | --- |
| 0 | 成功 |
| 1001 | 参数错误 |
| 2002 | 重复提交 |
| 5000 | 系统异常 |

## 2. user 域

### 2.1 用户注册

| 项 | 内容 |
| --- | --- |
| action | `user.register` |
| 鉴权 | 公开 |

**入参（data）**

| 字段 | 类型 | 必填 | 含义 | 示例 |
| --- | --- | --- | --- | --- |
| phone | string | 是 | 手机号 | 138 |

**出参（data）**

| 字段 | 类型 | 必有 | 含义 | 示例 |
| --- | --- | --- | --- | --- |

**错误码（本接口特有）**

| code | 触发条件 |
| --- | --- |
| 0 | 成功 |
| 1001 | 参数错误 |
"""


@pytest.fixture()
def contract(tmp_path):
    p = tmp_path / "api-contract.md"
    p.write_text(VALID_CONTRACT, encoding="utf-8")
    return p


def test_valid_contract_pass(run_script, contract):
    r = run_script("contract_lint.py", contract)
    assert r.returncode == 0
    assert "[ OK ]" in r.stdout


def test_unregistered_error_code_fails(run_script, contract):
    text = contract.read_text(encoding="utf-8").replace(
        "| 1001 | 参数错误 |\n\n---", "| 9999 | 业务冲突 |\n\n---")
    # 只改接口错误码表（通用码表保持登记 1001）：把接口表最后一行换成 9999
    text = contract.read_text(encoding="utf-8")
    head, sep, tail = text.rpartition("| 1001 | 参数错误 |")
    text = head + "| 9999 | 业务冲突 |" + tail
    contract.write_text(text, encoding="utf-8")
    r = run_script("contract_lint.py", contract)
    assert r.returncode == 1
    assert "9999" in r.stdout


def test_missing_universal_table_exit_2(run_script, contract):
    text = contract.read_text(encoding="utf-8")
    start = text.index("## 1. 通用约定")
    end = text.index("## 2. user 域")
    contract.write_text(text[:start] + text[end:], encoding="utf-8")
    r = run_script("contract_lint.py", contract)
    assert r.returncode == 2
    assert "通用约定" in r.stdout


def test_missing_required_parts_fails(run_script, tmp_path):
    p = tmp_path / "bad.md"
    p.write_text(VALID_CONTRACT.replace("**入参（data）**", "**参数（data）**"), encoding="utf-8")
    r = run_script("contract_lint.py", p)
    assert r.returncode == 1


def test_repo_template_runs_clean(run_script):
    from conftest import REPO_ROOT
    r = run_script("contract_lint.py", REPO_ROOT / "assets" / "templates" / "api-contract-template.md")
    assert r.returncode == 0

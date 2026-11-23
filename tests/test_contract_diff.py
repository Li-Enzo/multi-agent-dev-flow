"""contract_diff.py 回归用例：破坏性变更检测（字段删除/类型变更/新增必填/必有降级/接口删除）。"""
import pytest

BASE_CONTRACT = """# 示例契约 v1

## 1. 通用约定

### 1.2 统一响应

| code | 含义 |
| --- | --- |
| 0 | 成功 |
| 1001 | 参数错误 |

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
| channel | string | 否 | 来源渠道 | web |

**出参（data）**

| 字段 | 类型 | 必有 | 含义 | 示例 |
| --- | --- | --- | --- | --- |
| userId | string | 是 | 用户 ID | u_1 |
| token | string | 是 | 登录态 | eyJ |
| nickname | string | 否 | 昵称 | 小明 |

**错误码（本接口特有）**

| code | 触发条件 |
| --- | --- |
| 0 | 成功 |

---

### 2.2 用户登录

| 项 | 内容 |
| --- | --- |
| action | `user.login` |
| 鉴权 | 公开 |

**入参（data）**

| 字段 | 类型 | 必填 | 含义 | 示例 |
| --- | --- | --- | --- | --- |
| phone | string | 是 | 手机号 | 138 |

**出参（data）**

| 字段 | 类型 | 必有 | 含义 | 示例 |
| --- | --- | --- | --- | --- |
| userId | string | 是 | 用户 ID | u_1 |

**错误码（本接口特有）**

| code | 触发条件 |
| --- | --- |
| 0 | 成功 |
"""


@pytest.fixture()
def old_contract(tmp_path):
    p = tmp_path / "contract-v1.md"
    p.write_text(BASE_CONTRACT, encoding="utf-8")
    return p


def evolve(tmp_path, *replacements):
    """对 BASE_CONTRACT 依次做字符串替换，写出新版契约文件。"""
    text = BASE_CONTRACT
    for old, new in replacements:
        assert old in text, f"替换源不存在: {old}"
        text = text.replace(old, new)
    p = tmp_path / "api-contract-v2.md"
    p.write_text(text, encoding="utf-8")
    return p


def test_identical_contracts_pass(run_script, old_contract):
    r = run_script("contract_diff.py", old_contract, old_contract)
    assert r.returncode == 0
    assert "[ OK ]" in r.stdout
    assert "破坏性变更 0 个" in r.stdout


def test_removed_output_field_fails(run_script, tmp_path, old_contract):
    new = evolve(tmp_path, ("| nickname | string | 否 | 昵称 | 小明 |\n", ""))
    r = run_script("contract_diff.py", old_contract, new)
    assert r.returncode == 1
    assert "nickname" in r.stdout
    assert "被删除" in r.stdout


def test_type_change_fails(run_script, tmp_path, old_contract):
    new = evolve(tmp_path, ("| phone | string | 是 | 手机号 | 138 |",
                            "| phone | int64 | 是 | 手机号 | 138 |"))
    r = run_script("contract_diff.py", old_contract, new)
    assert r.returncode == 1
    assert "类型变更" in r.stdout
    assert "string" in r.stdout and "int64" in r.stdout


def test_new_required_input_fails(run_script, tmp_path, old_contract):
    new = evolve(tmp_path, ("| channel | string | 否 | 来源渠道 | web |",
                            "| channel | string | 否 | 来源渠道 | web |\n"
                            "| smsCode | string | 是 | 短信验证码 | 483920 |"))
    r = run_script("contract_diff.py", old_contract, new)
    assert r.returncode == 1
    assert "新增必填入参" in r.stdout
    assert "smsCode" in r.stdout


def test_new_optional_input_is_info_only(run_script, tmp_path, old_contract):
    new = evolve(tmp_path, ("| channel | string | 否 | 来源渠道 | web |",
                            "| channel | string | 否 | 来源渠道 | web |\n"
                            "| remark | string | 否 | 备注 | hi |"))
    r = run_script("contract_diff.py", old_contract, new)
    assert r.returncode == 0
    assert "(info)" in r.stdout
    assert "remark" in r.stdout


def test_optional_becomes_required_fails(run_script, tmp_path, old_contract):
    new = evolve(tmp_path, ("| channel | string | 否 | 来源渠道 | web |",
                            "| channel | string | 是 | 来源渠道 | web |"))
    r = run_script("contract_diff.py", old_contract, new)
    assert r.returncode == 1
    assert "由选填改为必填" in r.stdout


def test_required_relaxed_is_info_only(run_script, tmp_path, old_contract):
    new = evolve(tmp_path, ("| phone | string | 是 | 手机号 | 138 |\n| channel",
                            "| phone | string | 否 | 手机号 | 138 |\n| channel"))
    r = run_script("contract_diff.py", old_contract, new)
    assert r.returncode == 0
    assert "由必填放宽为选填" in r.stdout


def test_output_downgraded_to_optional_fails(run_script, tmp_path, old_contract):
    new = evolve(tmp_path, ("| token | string | 是 | 登录态 | eyJ |",
                            "| token | string | 否 | 登录态 | eyJ |"))
    r = run_script("contract_diff.py", old_contract, new)
    assert r.returncode == 1
    assert "由必有降级为可选" in r.stdout


def test_removed_interface_fails(run_script, tmp_path, old_contract):
    start = BASE_CONTRACT.index("### 2.2 用户登录")
    new_text = BASE_CONTRACT[:start].rstrip() + "\n"
    p = tmp_path / "api-contract-v2.md"
    p.write_text(new_text, encoding="utf-8")
    r = run_script("contract_diff.py", old_contract, p)
    assert r.returncode == 1
    assert "user.login" in r.stdout
    assert "被删除" in r.stdout


def test_new_interface_is_info_only(run_script, tmp_path, old_contract):
    extra = """
---

### 2.3 用户注销

| 项 | 内容 |
| --- | --- |
| action | `user.delete` |
| 鉴权 | 需登录 |

**入参（data）**

| 字段 | 类型 | 必填 | 含义 | 示例 |
| --- | --- | --- | --- | --- |
| userId | string | 是 | 用户 ID | u_1 |

**出参（data）**

| 字段 | 类型 | 必有 | 含义 | 示例 |
| --- | --- | --- | --- | --- |
| ok | bool | 是 | 是否成功 | true |

**错误码（本接口特有）**

| code | 触发条件 |
| --- | --- |
| 0 | 成功 |
"""
    p = tmp_path / "api-contract-v2.md"
    p.write_text(BASE_CONTRACT.rstrip() + "\n" + extra, encoding="utf-8")
    r = run_script("contract_diff.py", old_contract, p)
    assert r.returncode == 0
    assert "新增接口" in r.stdout
    assert "user.delete" in r.stdout


def test_missing_file_exit_2(run_script, tmp_path, old_contract):
    r = run_script("contract_diff.py", old_contract, tmp_path / "nope.md")
    assert r.returncode == 2
    assert "文件不存在" in r.stdout


def test_repo_example_against_itself_passes(run_script):
    from conftest import REPO_ROOT
    example = REPO_ROOT / "examples" / "api-contract.example.md"
    r = run_script("contract_diff.py", example, example)
    assert r.returncode == 0
    assert "user.register" in r.stdout
    assert "user.login" in r.stdout

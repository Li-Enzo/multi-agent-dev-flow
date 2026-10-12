# examples/ — 模板套用示例

> 本目录演示「文档模板如何落地为真实项目文档」：拿 `assets/templates/` 的空模板，填出 demo 项目「示例商城」的完整契约与测试用例，并通过脚本守门证明。

## 文件

| 文件 | 套用的模板 | 内容 |
| --- | --- | --- |
| `api-contract.example.md` | `assets/templates/api-contract-template.md` | 完整接口契约：通用约定（错误码表/字段约定）+ user 域 2 个接口（`user.register` / `user.login`），含元信息表、入参表、出参表、接口错误码表 |
| `test-cases.example.md` | `assets/templates/test-cases-template.md` | 与契约逐条对应的测试用例：核心链路 A01–A07（含幂等重放、防枚举分支）、登录态鉴权 B01–B03、后台 C01–C02、验收集与性能门槛 |

## 套用要点（从空模板到本文档做了什么）

1. 填「通用约定」：错误码表**原样保留** 8 个通用码，项目需要新增码时先登记进这张表（`contract_lint.py` 会强制检查接口错误码 ⊆ 通用码表）。
2. 每个接口抄模板四件套：元信息表（action 用反引号包具体名）→ 入参表（表头必有 字段/类型/必填）→ 出参表（表头必有 字段/类型）→ 错误码小节。
3. 幂等写接口的 `idempotencyKey` 入参标必填，并在错误码里声明 2002 命中语义（见 §1.3 与 A04 用例的对应）。
4. 用例文档与契约字段逐条对齐：用例编号 ↔ 错误码分支，动态值（验证码/时间窗）不硬编码。

## lint 证明

示例契约通过 `scripts/contract_lint.py` 全项检查（含错误码登记合法性）。复现命令与输出：

```
$ python scripts/contract_lint.py examples/api-contract.example.md
[ OK ] 2. user 域 > 2.1 用户注册
[ OK ] 2. user 域 > 2.2 用户登录

共检查 2 个接口，问题 0 个
（退出码 0）
```

> 本证明为 2026-10-09 实测输出；修改示例契约后请重新运行该命令并同步更新本节。

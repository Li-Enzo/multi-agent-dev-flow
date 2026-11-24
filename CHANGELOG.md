# CHANGELOG

> 本仓库自身的变更日志。版本号与 git tag 同步；每条注明关联 commit。
> 遵循仓库 commit 范式 `type(scope): 简述`，type ∈ feat/fix/docs/refactor/test/chore。

## Unreleased

- feat(scripts)：`probe_api.py` 支持 PUT 写操作探测（与 POST 同构发 JSON body，`-m POST|PUT|GET`）并补齐自定义请求头能力说明——`-H` 此前已实装但未入文档与回归；`tests/test_probe_api.py` 新增 6 例（PUT 正常/错误码、鉴权头通过与缺失拒绝、畸形头拒参），测试夹具加鉴权端点模拟（`/api/secure` 前缀校验 Authorization）。SKILL.md 与 README 用法同步。(c299eb0)
- feat(scripts)：新增 `contract_diff.py` 契约破坏性变更检测——对比两版契约文档（旧 vs 新），接口删除/字段删除/类型变更/新增必填入参/选填改必填/出参必有降级即 FAIL，新增接口与可选字段等兼容变更仅 INFO；复用 contract_lint 解析器，退出码 0/1/2 与 lint 系一致。`tests/` 固化 12 个回归用例（含仓库示例自比对）；README/SKILL 脚本清单同步补齐（含此前遗漏的 doc_pack/token_report，脚本数更正为七）。(903a69c)
- chore(roadmap)：任务池补充 6 项——`contract_diff.py` 契约破坏性变更检测、`probe_api.py` 写操作与自定义请求头、`doc_pack.py` manifest 完整性清单、契约版本演进指南、「契约破坏事件」复盘模板、`changelog_lint.py` 范式检查接 CI。(6257d72)

## v1.1.0 — 2026-10-09

> 主题：脚本工具链补全 + 文档体系扩展（对应 ROADMAP「脚本增强」「文档与模板」两节）。

### feat(scripts)

- `probe_api.py` 支持 GET 请求（action 与 data 拼 query string），并支持从环境变量 `PROBE_API_BASE` 读取 base URL（相对路径拼接 / 省略 `-u`）。(2b121b6)
- `contract_lint.py` 新增第 5 项检查：接口声明的错误码必须登记在「通用约定」码表中，未登记即 FAIL；缺通用码表报结构错误。(e94a430)
- 新增 `doc_pack.py`：文档包一键打包，落实契约变更硬规则——版本号连续不跳号、包内字节与磁盘逐字节校验、包 mtime 晚于源文件、旧包自动入存档。(fda1e73)
- 新增 `token_report.py`：统计文档行数/字数，超过阈值给出「转 references / 归档」建议，配合 token-saving 范式。(349ba60)

### test(scripts)

- 新增 `tests/`：为 probe_api / contract_lint / doc_pack / token_report 四个脚本固化 25 个 pytest 回归用例（含本地 HTTP 服务夹具），替代手工实测。(ade200d)

### docs

- `references/backend-paradigm.md` 新增 §8「消息推送接收端」：验签 + AES 解密 + 幂等落库完整流水线与真实事故易错清单。(3f360c8)
- `references/agent-collab.md` 新增 §7「配置漂移防护」：多环境部署前/中/后复读核对清单与漂移处置流程。(9255c20)
- 接口契约模板新增英文版 `assets/templates/api-contract-template.en.md`，与中文版逐节对应。(ab4c671)
- 新增 `examples/`：示例商城完整契约 + 配套测试用例 + 通过 contract_lint 的证明，演示模板套用。(796912d)
- README 增加徽章（MIT license、Python ≥3.8、last commit）。(64fee52)

## v1.0.0 — 2026-10-04

> 主题：多 Agent 协作全栈开发流程 Skill 初版。

- 初始版本：SKILL.md 主文件 + 7 份范式文档（workflow / 前后端 / 数据库 / 美术 / 协作 / token-saving）+ 5 套文档模板 + 4 个零依赖本地脚本（contract_lint / changelog_check / archive_memory / probe_api）。
- 附带 Skill 作用说明与实验报告（`docs/skill-guide-and-experiments.md`）。
- 建立仓库改进任务池 ROADMAP.md。(cad281c, daf0f04, 1070a07)

# CHANGELOG

> 本仓库自身的变更日志。版本号与 git tag 同步；每条注明关联 commit。
> 遵循仓库 commit 范式 `type(scope): 简述`，type ∈ feat/fix/docs/refactor/test/chore。

## Unreleased

- 新增新产品设计构想 `docs/human-loop-test-platform.md`：MCP 原生真人众测平台（AI 编程工作流的人类在环插件）——定位、闭环、架构原则、双轨测试者经济、两周验证路径与落地顺序。
- ROADMAP.md 新增「新产品：MCP 原生真人众测平台」任务池 15 项（验证期 / 平台基建 / MCP 层 / 运营与风控）。

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

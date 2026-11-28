# CHANGELOG

> 本仓库自身的变更日志。版本号与 git tag 同步；每条注明关联 commit。
> 遵循仓库 commit 范式 `type(scope): 简述`，type ∈ feat/fix/docs/refactor/test/chore。

## Unreleased

- feat(scripts)：新增 `changelog_lint.py`——CHANGELOG「## Unreleased」非空校验（缺章节/零条目即 FAIL）+ commit message `type(scope): 简述` 范式检查（type 六类白名单、scope 必填、简述非空；消息来源支持 --msg / --msg-file / --git-range，git 输出强制 UTF-8 解码防 Windows GBK 炸）。接入 CI：push/PR 全量跑 Unreleased 校验，push 事件逐条校验当次推送提交。`tests/test_changelog_lint.py` 固化 19 个用例（含仓库自身 CHANGELOG 与近 5 条历史提交作为活体样本）。README/SKILL 脚本清单同步（更正为八个）。(2b7e03e)
- docs(references)：`agent-collab.md` 新增 §8「契约破坏事件复盘模板」——触发条件三条（diff FAIL 漏网/联调回溯确认暗改/私下兼容）、可复制模板（事件线时间线表、影响面三问、根因五类勾选、防再发措施含验证方式列）、写完后三个闭环动作（措施落地验证/CHANGELOG 留指针/规则反哺工具库）；§5 加指针串联演进指南与复盘入口。SKILL.md 与 README 描述行同步。(c512377)
- docs(references)：新增 `references/contract-evolution.md` 契约版本演进指南——只加不改原则（允许/禁止对照表）、破坏性判定与 `contract_diff.py` 五类 FAIL 口径对齐、字段废弃标记约定（删除线 + 迁移指引格式与示例）、版本号与并行期纪律（内部 2 周/外部 1 季度、双写双读、流量归零才移除）、可复制下线公告模板、四道工具守门流程表。README/SKILL 目录与 `agent-collab.md` §5 交叉引用同步（范式文档更正为八份）。(35af350)
- feat(scripts)：`doc_pack.py` 打包生成包内 `manifest.json` 完整性清单（每个成员的路径/SHA-256/大小 + 包名/版本/打包时间，首成员入包），新增 `--verify <包.zip>` 解包侧自检模式（成员缺失/多出/摘要或大小不一致即 FAIL；无 manifest 的老包明确报「无法自检」）；打包期字节校验相应跳过清单成员。`tests/test_doc_pack.py` 新增 6 例（清单内容与磁盘 SHA-256 逐文件一致、首成员位置、自检通过/篡改/多出/缺失/无清单/包不存在）。SKILL.md 与 README 脚本说明同步。(0dc9f60)
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

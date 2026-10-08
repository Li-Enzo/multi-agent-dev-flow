# 仓库改进任务池（ROADMAP）

> 维护规则：每次迭代取**最上方未完成**的任务；完成后勾选、写仓库 CHANGELOG、提交并推送。
> 所有任务必须是真实可验证的工作，禁止空提交。

## 脚本增强

- [x] `scripts/probe_api.py`：支持 GET 请求与从环境变量读取 base URL（`PROBE_API_BASE`）
- [x] `scripts/contract_lint.py`：增加错误码合法性检查——接口错误码必须出现在通用约定码表中
- [x] `scripts/doc_pack.py`（新增）：文档包一键打包 + 包内契约与磁盘字节一致性校验（把"文档包硬规则"做成工具）
- [x] `scripts/token_report.py`（新增）：统计指定目录文档字数/行数，辅助决定哪些文档应归档或转 references（配合 token-saving 范式）
- [ ] 为 4 个脚本补充 `tests/` 下的 pytest 用例（当前为手工实测，需固化成回归）

## 文档与模板

- [ ] `references/backend-paradigm.md` 补充「消息推送接收端」章节（验签 + AES 解密 + 幂等落库的真实案例）
- [ ] `references/agent-collab.md` 补充「配置漂移防护」清单（多环境部署复读核对流程）
- [ ] 接口契约模板增加英文版 `api-contract-template.en.md`
- [ ] `examples/`（新增）：一份完整的示例契约 + 对应测试用例 + 通过 contract_lint 的证明，演示模板如何套用
- [ ] README 增加徽章（MIT license、Python 版本、最后提交）

## 工程化

- [ ] 仓库自身引入 CHANGELOG.md 并打 `v1.1.0` tag
- [ ] GitHub Actions（可选）：push 时自动跑 scripts 的 pytest

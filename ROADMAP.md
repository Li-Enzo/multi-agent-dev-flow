# 仓库改进任务池（ROADMAP）

> 维护规则：每次迭代取**最上方未完成**的任务；完成后勾选、写仓库 CHANGELOG、提交并推送。
> 所有任务必须是真实可验证的工作，禁止空提交。

## 脚本增强

- [x] `scripts/probe_api.py`：支持 GET 请求与从环境变量读取 base URL（`PROBE_API_BASE`）
- [x] `scripts/contract_lint.py`：增加错误码合法性检查——接口错误码必须出现在通用约定码表中
- [x] `scripts/doc_pack.py`（新增）：文档包一键打包 + 包内契约与磁盘字节一致性校验（把"文档包硬规则"做成工具）
- [x] `scripts/token_report.py`（新增）：统计指定目录文档字数/行数，辅助决定哪些文档应归档或转 references（配合 token-saving 范式）
- [x] 为 4 个脚本补充 `tests/` 下的 pytest 用例（当前为手工实测，需固化成回归）

## 文档与模板

- [x] `references/backend-paradigm.md` 补充「消息推送接收端」章节（验签 + AES 解密 + 幂等落库的真实案例）
- [x] `references/agent-collab.md` 补充「配置漂移防护」清单（多环境部署复读核对流程）
- [x] 接口契约模板增加英文版 `api-contract-template.en.md`
- [x] `examples/`（新增）：一份完整的示例契约 + 对应测试用例 + 通过 contract_lint 的证明，演示模板如何套用
- [x] README 增加徽章（MIT license、Python 版本、最后提交）

## 工程化

- [x] 仓库自身引入 CHANGELOG.md 并打 `v1.1.0` tag
- [x] GitHub Actions（可选）：push 时自动跑 scripts 的 pytest

## 新产品：MCP 原生真人众测平台（human-loop-test-platform）

> 设计构想见 `docs/human-loop-test-platform.md`。本节任务按落地顺序排列：先验证假设，再建平台。
> 企划成败取决于两个未验证假设（开发者付费复购意愿 / AI 合成报告毛利做正），验证期任务优先于一切平台开发。

### 验证期（两周，零平台成本）

- [ ] 人工撮合验证：在 vibe coding 社区（v2ex/即刻/小红书/Cursor 中文群）找 5-10 个开发者，组织 15 人测试 + 人工合成报告 + 收 50 元/单，记录**复购率**与**报告被采纳修改比例**两个数字
- [ ] 写结构化报告模板 schema（复现步骤/环境/期望行为/截图证据/可附修复建议），作为报告合成链路的输入格式约定
- [ ] 验证期复盘：两个数字达标 → 进入平台期；不达标 → 记录 pivot 方向（官方测试插件 / 互测积分社区）

### 平台基建（REST 为本体）

- [ ] REST API 核心：task 数据模型、开发者 API Key 鉴权、计费与余额模型
- [ ] 花钱闸门：单次任务预算上限 + 日累计限额 + 超阈值强制人类确认（agent 出草稿 → 人批准付款）
- [ ] Web 控制台：发布任务、看进度、收报告
- [ ] AI 报告合成链路：多源反馈聚类去重，把技术报告与用户体验映射到同一问题框架，输出结构化报告
- [ ] 异步任务协议：发布即返回 `task_id`，`get_status` / `get_report` 轮询 + webhook 回调
- [ ] 任务发布审核：自动审核 + 人工抽审，防钓鱼 App / 垃圾任务滥用通道

### MCP 层（薄适配，REST 稳定后包装）

- [ ] MCP server 最小工具集：`publish_task` / `get_status` / `get_report`
- [ ] 打磨三个工具的 tool description（决定 agent 会不会正确使用，优先级高于平台前端 UI）
- [ ] "全球第一个 MCP-native 测试平台"宣传物料与社区发布

### 运营与风控

- [ ] 现金轨防作弊体系：录屏/操作轨迹证据、设备指纹、同一问题多人交叉验证、信誉分
- [ ] 测试者待命池调度：支撑小时级 SLA 的在线调度与储备
- [ ] 积分经济参数落地：6 个月有效期、月 earning cap、30% 提现锚定、高价值任务优先派积分轨（积分轨整体后置，现金单轨先跑通）

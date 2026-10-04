---
name: multi-agent-dev-flow
description: 多 AI 协作全栈开发流程编排。当用户要求从零开发一个项目/小程序/Web 应用/MVP、搭建前端+后端+数据库、写产品需求文档（PRD）、接口契约文档、测试用例，或需要用多个 AI agent 分工协作开发、节省 token、用本地脚本代替 AI 做重复性基础工作、防止 AI 幻觉时，使用本 skill。覆盖需求梳理 → 美术风格确认（HTML UI 先行）→ 前端构建 → 后端搭建 → 数据库搭建 → 测试验收 → MVP → 迭代的完整流水线。
---

# 多 Agent 协作开发流水线（Multi-Agent Dev Flow）

用多个 AI agent 分工完成全栈项目开发：文档是唯一事实源，本地脚本代替 AI 做重复劳动，每个 agent 只持有自己所需的上下文，通过契约文档与互审机制防止幻觉。

## 核心原则（先于一切流程）

1. **文档唯一事实源（Single Source of Truth）**：PRD、接口契约、数据库设计的最新版在 `docs/` 目录。agent 之间不口头传话，只传文档路径。发现文档矛盾时**停下对齐，禁止各自猜测**。
2. **脚本优先于 AI 劳动**：凡确定性、重复性的检查（契约 lint、探针、归档、对账），一律写成本地脚本（`scripts/`）由 Python/Bash 执行，不消耗 AI token，且结果可复现。
3. **小上下文隔离**：每个 agent 只读取自己负责的文档与代码。master  agent 只持有目录结构与契约指针，不读具体实现。详细知识放 `references/`，按需加载。
4. **互相校验防幻觉**：前端/后端对同一接口契约各自实现；测试 agent 独立按验收用例执行；关键变更必须双 agent 确认。任何 agent 不得凭记忆复述契约字段——一律回读文档原文。
5. **硬规则**：接口契约文档一旦变更，当次交付必须同步更新 CHANGELOG 并重打包文档包（见 `references/agent-collab.md` §契约变更硬规则）。

## 八阶段流水线

```
① 需求梳理 → ② 美术风格确认 → ③ 前端构建 → ④ 后端搭建 → ⑤ 数据库搭建 → ⑥ 测试验收 → ⑦ MVP 完成 → ⑧ 迭代（回到①）
```

| 阶段 | 负责 | 输入 | 交付物（gate，缺一不可） |
| --- | --- | --- | --- |
| ① 需求梳理 | 需求 agent + 用户拍板 | 用户口述/参考 | PRD（用 `assets/templates/prd-template.md`）；用户确认范围与优先级 🅿️0/🅿️1 |
| ② 美术风格确认 | 设计 agent | PRD、品牌资料 | 美术风格指导 + HTML 静态 UI 预览（先用纯 HTML 实现页面视觉，用户确认后再进入编码）+ 品牌文案规范 |
| ③ 前端构建 | 前端 agent | UI 预览、PRD | 页面代码；**同时产出自己消费接口所需的接口契约草稿**，交 master 汇总 |
| ④ 后端搭建 | 后端 agent | PRD、接口契约 | 云函数/服务代码 + 统一响应格式 + 错误码表 |
| ⑤ 数据库搭建 | 数据库 agent | PRD、后端文档 | 集合/表 DDL + 索引清单 + 枚举状态机登记 |
| ⑥ 测试验收 | 测试 agent（独立） | 全部文档 | 自动化测试脚本 + 按 `test-cases-template.md` 逐条执行，出具通过/失败清单 |
| ⑦ MVP 完成 | master + 用户 | 测试结果 | 全链路走通；用户按验收集亲自确认 |
| ⑧ 迭代 | 按需回到①-⑥ | CHANGELOG 归档 | 每轮变更走同一套流程，不跳阶段 |

> ③④⑤ 可由三个 agent 并行施工，但**契约文档由 master 合并去重后冻结**，冻结后任何字段变更走硬规则。
> 详细每阶段操作手册见 `references/workflow.md`。

## 各域范式（按需阅读）

- 前端工作范式（UI 先行、主题即配置、接口消费纪律）：`references/frontend-paradigm.md`
- 后端工作范式（函数即边界、写操作五步法、幂等、金额/时区红线）：`references/backend-paradigm.md`
- 数据库范式（命名、索引、枚举登记、软删除、生命周期）：`references/database-paradigm.md`
- 美术风格范式（风格指导文档、HTML 预览、审查整改报告、禁忌清单）：`references/art-style.md`
- 多 agent 协作与防幻觉（角色分工、互审、契约变更硬规则）：`references/agent-collab.md`
- Token 节省与本地资源（记忆归档、脚本清单、探针）：`references/token-saving.md`

## 文档模板（直接复制使用）

`assets/templates/` 下提供五套现成模板：

| 模板 | 用途 |
| --- | --- |
| `prd-template.md` | 产品需求文档（阶段①） |
| `art-style-guide-template.md` | 美术风格指导（阶段②） |
| `api-contract-template.md` | 接口契约文档（③④⑤共用，唯一事实源） |
| `test-cases-template.md` | 测试与验收用例（阶段⑥） |
| `dev-norms-template.md` | 开发计划与协作规范（项目启动时） |

## 本地脚本（代替 AI 做基础工作）

所有脚本位于 `scripts/`，零第三方依赖（Python 3 标准库），可直接运行：

| 脚本 | 用途 | 典型调用 |
| --- | --- | --- |
| `contract_lint.py` | 检查接口契约文档：每个接口必须有入参表/出参表/错误码，缺项即报 | `python scripts/contract_lint.py docs/api-contract.md` |
| `changelog_check.py` | 契约变更同步检查：契约文件修改时间晚于 CHANGELOG 最后一条即报警（硬规则守门员） | `python scripts/changelog_check.py docs/api-contract.md CHANGELOG.md` |
| `archive_memory.py` | 记忆归档：把进度/过程文档按日期归入 `存档-YYYY-MM/` 并生成清单 | `python scripts/archive_memory.py 进度/ --into 存档` |
| `probe_api.py` | 接口探针：发请求验证接口存活与返回码，代替 AI 手工 curl | `python scripts/probe_api.py -u <url> -a <action> -d '{"k":1}'` |

> 跑通流水线不靠 AI 记忆力，靠这些脚本与文档。新增重复性工作时，第一反应是"写成脚本"，第二反应才是让 AI 做。

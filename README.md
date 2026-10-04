# multi-agent-dev-flow

多 AI Agent 协作全栈开发流程 Skill：用「文档唯一事实源 + 本地脚本 + 多 agent 分工互审」的方式完成前端 + 后端 + 数据库的完整项目开发，**节省 token、缓解上下文长度危机、互相校验防止幻觉**。

## 它解决什么问题

- **上下文爆炸**：master agent 只持任务指针，每个 agent 只读自己负责的文档，细节按需加载。
- **AI 幻觉**：契约文档是唯一事实源，字段一律回读原文；前端 × 后端 × 测试三方交叉校验；能用脚本验证的事实绝不靠 AI 口述。
- **token 浪费**：契约 lint、接口探针、记忆归档、同步检查全部交给零依赖 Python 脚本，AI 只负责设计与判断。

## 开发流水线

```
① 需求梳理(PRD) → ② 美术风格确认(HTML UI 先行) → ③ 前端构建 → ④ 后端搭建
→ ⑤ 数据库搭建 → ⑥ 测试验收 → ⑦ MVP → ⑧ 迭代（回到①）
```

前端/后端/数据库三个 agent 可并行施工，接口契约由 master 合并冻结；每轮迭代走 CHANGELOG + 归档闭环。

## 目录结构

```
multi-agent-dev-flow/
├── SKILL.md                  # Skill 主文件（触发与核心流程）
├── references/               # 七份范式文档（按需加载）
│   ├── workflow.md           # 八阶段操作手册
│   ├── frontend-paradigm.md  # 前端范式（UI 先行、主题即配置、契约纪律）
│   ├── backend-paradigm.md   # 后端范式（写操作五步法、幂等、金额/时区红线）
│   ├── database-paradigm.md  # 数据库范式（枚举唯一登记、迁移脚本化）
│   ├── art-style.md          # 美术风格范式（风格指导→HTML 预览→审查整改）
│   ├── agent-collab.md       # 多 agent 协作与防幻觉机制
│   └── token-saving.md       # Token 节省与本地资源利用
├── assets/templates/         # 五套文档模板（PRD/风格/契约/用例/协作规范）
└── scripts/                  # 四个零依赖本地脚本（均已实测）
    ├── contract_lint.py      # 契约文档完整性检查
    ├── changelog_check.py    # 契约变更硬规则守门员
    ├── archive_memory.py     # 记忆文档按月归档
    └── probe_api.py          # 接口存活探针
```

## 安装使用

**作为 Kimi / Claude Code 等 Agent 的 Skill：**

```bash
# 用户级（推荐）
cp -r multi-agent-dev-flow ~/.config/agents/skills/

# 或项目级
cp -r multi-agent-dev-flow <你的项目>/.agents/skills/
```

之后对 AI 说「按 multi-agent-dev-flow 流程帮我开发一个 XX 项目」即可触发。

**脚本独立使用（不依赖任何 AI）：**

```bash
python scripts/contract_lint.py docs/api-contract.md
python scripts/changelog_check.py docs/api-contract.md CHANGELOG.md
python scripts/archive_memory.py 进度/ --into 存档
python scripts/probe_api.py -u <url> -a <action> -d '{"k":1}' -e 0,2002
```

## 设计来源

本 Skill 提炼自一个真实的小程序商城项目（PRD → UI 预览 → 云函数 → 数据库 → 积分体系，历经 60+ 轮迭代）中验证有效的工程实践：文档包硬规则、UI 细节审核报告、幂等设计、时区锁定事故、配置漂移事故、双 AI 交叉评审等，全部固化为可复用的流程与脚本。

## License

[MIT](LICENSE)

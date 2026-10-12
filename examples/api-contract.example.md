# 示例商城 · 接口契约文档（API 定义）

> 本文档是前端、后端、测试三方共享的唯一事实源。字段增删改必须同步 CHANGELOG（见文末变更管理）。任何 agent 引用字段一律回读本文档原文，禁止凭记忆。
>
> 本文件是 `assets/templates/api-contract-template.md` 的完整套用示例（demo 项目「示例商城」），配套用例见 `test-cases.example.md`，lint 证明见 `README.md`。

## 1. 通用约定

### 1.1 请求

- 网关入口：`https://api.example-mall.dev`，所有接口通过 `action` 字段分发。
- 鉴权头：`Authorization: Bearer <token>`；未登录接口除外。
- 统一请求体：`{ "action": "<名>", "data": { ... } }`

### 1.2 统一响应

```json
{ "code": 0, "msg": "ok", "data": { } }
```

| code | 含义 |
| --- | --- |
| 0 | 成功 |
| 1001 | 参数错误 |
| 1002 | 未登录 / token 失效 |
| 1003 | 无权限 |
| 2001 | 业务校验失败（msg 带具体原因） |
| 2002 | 重复提交（幂等拦截） |
| 3001 | 第三方异常 |
| 5000 | 系统异常 |

### 1.3 通用字段约定

- 金额：整数「分」；时间：ISO 8601 UTC 字符串；分页：`cursor + limit`（游标 = `createdAt_id`）。
- 幂等：写接口支持 `idempotencyKey`（重试带同值，命中返回原结果，code=0）。

## 2. user 域

### 2.1 用户注册

| 项 | 内容 |
| --- | --- |
| action | `user.register` |
| 鉴权 | 公开 |
| 说明 | 手机号 + 短信验证码注册，成功后直接登录态返回 |

**入参（data）**

| 字段 | 类型 | 必填 | 含义 | 示例 |
| --- | --- | --- | --- | --- |
| phone | string | 是 | 手机号（11 位大陆号段） | 13800138000 |
| smsCode | string | 是 | 短信验证码（6 位数字） | 483920 |
| idempotencyKey | string | 是 | 幂等键，客户端生成（重试带同值） | reg-20261009-a1 |

**出参（data）**

| 字段 | 类型 | 必有 | 含义 | 示例 |
| --- | --- | --- | --- | --- |
| userId | string | 是 | 用户 ID | u_9f3a2c |
| token | string | 是 | 登录态 token | eyJhbGciOi... |
| expiresAt | string | 是 | token 过期时间（ISO 8601 UTC） | 2026-10-16T09:00:00Z |

**错误码（本接口特有）**

| code | 触发条件 |
| --- | --- |
| 0 | 成功 |
| 1001 | 手机号格式非法 / 验证码错误 / 验证码过期 |
| 2001 | 该手机号已注册（msg 提示直接登录） |
| 2002 | 幂等拦截：同 idempotencyKey 重试命中，返回首次结果 |

---

### 2.2 用户登录

| 项 | 内容 |
| --- | --- |
| action | `user.login` |
| 鉴权 | 公开 |
| 说明 | 手机号 + 密码登录 |

**入参（data）**

| 字段 | 类型 | 必填 | 含义 | 示例 |
| --- | --- | --- | --- | --- |
| phone | string | 是 | 手机号 | 13800138000 |
| password | string | 是 | 密码（前端先做一次 SHA-256） | 5e884898... |

**出参（data）**

| 字段 | 类型 | 必有 | 含义 | 示例 |
| --- | --- | --- | --- | --- |
| userId | string | 是 | 用户 ID | u_9f3a2c |
| token | string | 是 | 登录态 token | eyJhbGciOi... |
| expiresAt | string | 是 | token 过期时间（ISO 8601 UTC） | 2026-10-16T09:00:00Z |

**错误码（本接口特有）**

| code | 触发条件 |
| --- | --- |
| 0 | 成功 |
| 1001 | 参数缺失或格式非法 |
| 2001 | 手机号未注册 / 密码错误（msg 区分提示，code 统一 2001 防枚举） |

---

## N. 变更管理

- 字段增删改 → 同步更新本文档 + CHANGELOG，标注版本与日期。
- 契约变更 = 当次交付必须重打包文档包（包内契约字节与磁盘一致，打包时间晚于契约最后修改时间）。
- 用 `scripts/changelog_check.py <本文档> <CHANGELOG>` 自动守门。

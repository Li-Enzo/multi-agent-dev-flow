# 数据库范式

> 适用：文档型数据库（CloudBase/Mongo）、关系库（MySQL/SQLite/Postgres）。原则：约定先行、枚举唯一登记、迁移脚本化管理。

## 1. 通用约定

| 项 | 约定 |
| --- | --- |
| 主键 | 文档型用 `_id`（ObjectId）；关系库用自增/BIGINT；业务单号另存 `xxxNo` 字段并建唯一索引 |
| 金额 | 一律整数「分」，字段名带 `Amount/Fee/Price` 后缀，禁止浮点 |
| 时间 | ISO 8601 UTC 字符串；字段名 `createdAt/updatedAt/paidAt` 等 |
| 布尔 | `true/false`，默认 false，禁用 0/1 |
| 枚举 | 字符串枚举，**全部登记在数据库文档"枚举与状态机汇总"章**，代码中禁止出现未登记魔法值 |
| 软删除 | `deleted: boolean` + `deletedAt`，默认查询过滤；流水类集合不删除 |
| 审计 | 每个集合统一含 `createdAt`、`updatedAt` |
| 用户引用 | `userId` 关联用户表主键，禁止用第三方 openid 做关联字段 |
| 快照 | 订单相关集合对商品名/规格/单价/图片做冗余快照，与商品表解耦 |
| 索引命名 | 普通 `idx_<字段>`，唯一 `uk_<字段>` |

## 2. 容量与性能基线（设计时先估）

- 预估用户量 / 日订单量 / 5 年总量，据此决定是否分表（如订单 + 订单明细分离）。
- 列表查询全部走索引；分页基于索引字段排序，**禁止 skip 深分页**，用 `createdAt + _id` 游标。
- 热点库存字段走条件更新（`stock >= N`），每日更新频次 < 1 万的集合无需额外优化。
- 大文件（图片/素材）存对象存储，库里只存 URL；单文档控制在 100KB 内。

## 3. 关系总览先行

动手建表前先画集合关系总览（文本树即可）：

```
themes ─┬─< categories ─< goods ─< goods_sku
users ─┬─< addresses
       ├─< orders ─┬─< order_items（快照）
       │           └─< payments ─< refunds
admins ─> roles；op_logs（操作日志）
counters（单号序列）/ job_logs（定时任务）
```

## 4. 迁移脚本化

- DDL 变更只走 `scripts/migrations/` 下的脚本，幂等（`CREATE TABLE IF NOT EXISTS`、`PRAGMA` 检测后 `ALTER` 补列），禁止手改生产库。
- 本地测试库可用 SQLite 驱动跑同一套迁移脚本，与生产 DDL 保持字段口径一致。
- 迁移脚本可重复执行；补列/建索引都要先检测存在性。

## 5. 枚举与状态机（唯一权威定义）

文档中设专章登记每个状态机的全部取值与扭转规则，例如：

```
订单 status：pending(待支付) → paid(已支付) → shipped(已发货) → received(已收货) → done(完成)
              ↘ closed(超时关闭)  ↘ refunding(退款中) → refunded(已退款)
扭转规则：仅允许上述有向边；扭转必须落 orders.timeline 流水。
```

任何代码、契约、测试用例中出现的枚举值，都要能在此章找到；找不到 = 文档欠账，先补登再施工。

## 6. 数据生命周期与归档

- 为每类数据定保留期：流水/日志类（如 job_logs、op_logs）保留 N 天后归档或清理。
- 归档走脚本，归档记录可审计。

## 7. 口径偏差声明

需求与约束冲突时（如"余额允许记负" vs `CHECK (balance>=0)`），不改约束，显式记录偏差声明：落地口径（如"扣到 0，差额记负债字段"）+ 承接方案 + 知会方。禁止静默违反。

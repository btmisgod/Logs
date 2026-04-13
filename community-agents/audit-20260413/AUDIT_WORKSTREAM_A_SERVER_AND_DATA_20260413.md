# 审计任务 A：社区工程 Server 与数据合同 2026-04-13

## 1. 任务定位

这个板块只负责：

- `myproject` 中社区 server 的基础建设审计与修正

重点是：

- 通用 server 行为
- onboarding / session 合同
- 消息 / Event / AgentSession / GroupSession 这些正式数据对象
- 消息字段的 server 消费方式
- 旧逻辑残留的 server 侧清理

当前不做：

- 群组 bootstrap 功能实现
- 新 workflow 功能开发
- 前端大改

## 2. 必读文档

1. `G:\community agnts\community agents\docs\control-plane\AUDIT_SPLIT_PLAN_20260413.md`
2. `G:\community agnts\community agents\docs\control-plane\AUDIT_HANDOFF_NEXT_THREAD_20260413.md`
3. `G:\community agnts\community agents\docs\control-plane\SYSTEM_AUDIT_TASKBOOK_20260412.md`
4. `G:\community agnts\community agents\docs\control-plane\SYSTEM_AUDIT_INITIAL_FINDINGS_20260412.md`
5. `G:\community agnts\community agents\myproject\docs\design-facts\Agent Community 架构设计文档.txt`
6. `G:\community agnts\community agents\myproject\docs\design-facts\Agent Community Server设计文档.txt`
7. `G:\community agnts\community agents\myproject\docs\design-facts\Agent Community 数据模型设计文档.txt`
8. `G:\community agnts\community agents\myproject\docs\design-facts\Agent Community Onboarding与Session合同设计文档.txt`
9. `G:\community agnts\community agents\myproject\docs\design-facts\Agent Community 历史遗留与降级说明.md`

## 3. 需要回答的问题

### 3.1 社区 server 的正式通用合同

必须查清：

- 当前 server 对 fresh agent 接入到底要求什么
- `/agents/me/session/sync` 是否属于当前正式合同
- 如果属于，当前实现是否完整
- 如果不属于，当前 skill 为什么在依赖它

### 3.2 统一消息基型的 server 消费方式

必须查清：

- `Message` 各字段被谁消费
- `status_block` 对 server 的通用消费是否足够
- `context_block`、`relations`、`routing`、`extensions` 的 server 消费点
- `author_kind` 双写当前为什么还存在

特别要求：

- `author_kind` 只能作为兼容残留审计项跟踪
- 现在不要贸然删
- 必须查：
  - schema ingestion
  - 存储读回
  - 前端渲染影响

### 3.3 通用数据对象

必须查清：

- `Event` 谁生产、谁消费
- `AgentSession` 谁生产、谁消费
- `GroupSession` 谁生产、谁消费
- 当前实现有没有偏离最新数据模型文档

### 3.4 协议装载和 server 执行边界

必须查清：

- server 当前到底消费哪些群组协议字段
- 哪些协议文件只是 shell / scaffold / draft
- 哪些文件真的进入 runtime inputs

## 4. 修正任务

查清以后，直接修：

1. server onboarding / session 合同和设计文档不一致的地方
2. 数据模型与 schema 中明显违背当前设计的地方
3. server 内部遗留的旧逻辑和假路径
4. 会污染 skill 对 server 正式理解的错误接口或错误字段

## 5. 产出要求

必须产出：

- A 板块问题清单
- 每条问题的根因、影响、修正
- 改动后的文件列表
- 每条修正对应的验证结果
- 仍未能修掉的问题和 blocker

## 6. 完成标准

这个板块算完成，至少要满足：

1. 当前 community server 的正式接入 / session 合同已被查清并修正
2. 数据模型与 schema 的基础矛盾已被清理
3. `author_kind` 已作为兼容残留被明确标记和影响分析
4. server 侧不再带明显历史残留去误导 skill
5. A 板块结果能给 B 板块提供稳定合同面

# 审计任务 B：Skill、Runtime 与消息封装 2026-04-13

## 1. 任务定位

这个板块只负责：

- `community-skill` 的基础建设审计与修正

重点是：

- onboarding
- runtime 最小责任判断
- 协议挂载
- agent 协议挂载
- skill 侧统一消息基型封装
- skill 出站行为
- skill 仓库 release 面污染清理

当前不做：

- 群组 bootstrap 功能实现
- 模板仓主逻辑开发
- 用模板仓逻辑去覆盖 skill 主体

## 2. 必读文档

1. `G:\community agnts\community agents\docs\control-plane\AUDIT_SPLIT_PLAN_20260413.md`
2. `G:\community agnts\community agents\docs\control-plane\AUDIT_HANDOFF_NEXT_THREAD_20260413.md`
3. `G:\community agnts\community agents\docs\control-plane\SYSTEM_AUDIT_TASKBOOK_20260412.md`
4. `G:\community agnts\community agents\docs\control-plane\SYSTEM_AUDIT_INITIAL_FINDINGS_20260412.md`
5. `G:\community agnts\community agents\myproject\docs\design-facts\Agent Community 架构设计文档.txt`
6. `G:\community agnts\community agents\myproject\docs\design-facts\Agent Community Runtime设计文档.txt`
7. `G:\community agnts\community agents\myproject\docs\design-facts\Agent Community Agent协议设计文档.txt`
8. `G:\community agnts\community agents\myproject\docs\design-facts\Agent Community Skill设计文档.txt`
9. `G:\community agnts\community agents\myproject\docs\design-facts\Agent Community 数据模型设计文档.txt`
10. `G:\community agnts\community agents\myproject\docs\design-facts\Agent Community Onboarding与Session合同设计文档.txt`

## 3. 需要回答的问题

### 3.1 onboarding 与 session 合同

必须查清：

- `community-skill` 当前依赖哪些 community server 接口
- 这些依赖是否符合最新设计文档
- skill 是否错误依赖了过时或未完成的 server 接口

### 3.2 runtime 当前到底做了什么

必须查清：

- runtime 是否真的只做最小责任判断与协议挂载
- runtime 有没有偷做不该做的事情
- runtime 有没有缺少当前设计要求的协议挂载

特别注意：

- runtime 应挂载 agent protocol
- runtime 应按 `group_id` 挂载群组协议
- runtime 不应被写成完整 manager 编排器

### 3.3 skill 侧消息基型封装

必须查清：

- 当前 skill 是否仍保留统一消息基型封装能力
- 封装路径是否与最新数据模型设计一致
- 是否还残留旧合同 / 旧模板 / 旧字段拼装逻辑

### 3.4 release 面污染

必须查清：

- skill 仓当前保留了哪些具体环境默认值
- 哪些允许保留
- 哪些必须清理

当前允许保留：

- 当前社区 server 地址
- 默认 public 入口群

其它特定配置、测试路径、实例残留都要清。

## 4. 修正任务

查清以后，直接修：

1. onboarding / session 路径与设计文档不一致的地方
2. runtime 与设计文档不一致的地方
3. agent 协议 / 群组协议挂载缺失的地方
4. skill 侧统一消息封装缺失或被污染的地方
5. skill 仓 release 面中的旧逻辑残留和具体环境污染

## 5. 产出要求

必须产出：

- B 板块问题清单
- 每条问题的根因、影响、修正
- skill 仓改动文件列表
- 出站封装 / onboarding / runtime 对齐的验证结果
- 尚未能修掉的问题和 blocker

## 6. 完成标准

这个板块算完成，至少要满足：

1. `community-skill` 的 onboarding 行为与最新设计文档对齐
2. runtime 的职责边界已对齐
3. protocol mounting 路径已对齐
4. skill 侧统一消息基型封装仍存在且已对齐
5. release 面污染已显著清理
6. `community-skill` 不再依赖模板仓作为真实逻辑来源

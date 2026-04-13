# 基础建设审计总计划 2026-04-13

## 1. 当前任务目标

当前任务不是继续做群组功能，也不是继续补单点 bug。

当前任务目标是：

- 先把 `myproject` 和 `community-skill` 的基础建设实现
- 对齐到当前最新设计文档
- 清理旧逻辑残留
- 让后续群组功能实现建立在干净的社区工程和 skill 工程之上

当前**不做**：

- 群组 bootstrap / 开机流的代码实现
- 新的群组 workflow 功能开发
- 为了通过测试而写临时硬编码逻辑

## 2. 三个并行审计板块

本轮拆成 3 个并行板块：

### A. 社区工程 Server / 数据合同 / 基础模型审计与修正

目标：

- 对齐 `myproject` 中社区 server、消息模型、session 合同、协议装载相关基础建设

### B. Skill / Runtime / Agent 协议挂载 / 消息封装审计与修正

目标：

- 对齐 `community-skill` 中 onboarding、runtime、协议挂载、消息封装、出站行为

### C. Live 部署面 / Fresh 安装面 / 模板分叉与残留审计与修正

目标：

- 用真实安装面和真实运行面验证 A / B 的修正是否成立
- 排查并清理部署漂移、模板分叉、历史残留对当前判断的污染

## 3. 三条共同硬规则

### 3.1 community server 是通用社区 server

- 这里说的 server 是社区层通用 server
- 不是为了某个群组测试临时定制的 server
- 单群超出 server 通用能力范围的差异，后续优先放到 group protocol 和消息扩展字段

### 3.2 `community-skill` 是唯一 skill 主体真相源

- `community-skill` 是 skill 主体
- `openclaw-for-community` 只是模板 / 工具 / 次级对照面
- 它不能继续作为主实现依据

### 3.3 runtime 当前只承担最小责任判断与协议挂载

- runtime 负责最小责任认定
- runtime 负责挂载 agent protocol
- runtime 负责按 `group_id` 挂载当前 group protocol
- runtime 把这些上下文交给 agent 自身行为与决策链

当前不要把 runtime 直接偷换成完整 manager 编排器。

## 4. 本轮所有线程共同的必读材料

### 4.1 审计与交接文档

1. `G:\community agnts\community agents\docs\control-plane\AUDIT_HANDOFF_NEXT_THREAD_20260413.md`
2. `G:\community agnts\community agents\docs\control-plane\SYSTEM_AUDIT_TASKBOOK_20260412.md`
3. `G:\community agnts\community agents\docs\control-plane\SYSTEM_AUDIT_INITIAL_FINDINGS_20260412.md`

### 4.2 当前设计事实源

4. `G:\community agnts\community agents\myproject\docs\design-facts\README.md`
5. `G:\community agnts\community agents\myproject\docs\design-facts\Agent Community 设计文档事实源索引.md`
6. `G:\community agnts\community agents\myproject\docs\design-facts\Agent Community 架构设计文档.txt`
7. `G:\community agnts\community agents\myproject\docs\design-facts\Agent Community Server设计文档.txt`
8. `G:\community agnts\community agents\myproject\docs\design-facts\Agent Community Runtime设计文档.txt`
9. `G:\community agnts\community agents\myproject\docs\design-facts\Agent Community Agent协议设计文档.txt`
10. `G:\community agnts\community agents\myproject\docs\design-facts\Agent Community Skill设计文档.txt`
11. `G:\community agnts\community agents\myproject\docs\design-facts\Agent Community 数据模型设计文档.txt`
12. `G:\community agnts\community agents\myproject\docs\design-facts\Agent Community 群组协议设计文档.txt`
13. `G:\community agnts\community agents\myproject\docs\design-facts\Agent Community Onboarding与Session合同设计文档.txt`
14. `G:\community agnts\community agents\myproject\docs\design-facts\Agent Community 历史遗留与降级说明.md`
15. `G:\community agnts\community agents\myproject\docs\design-facts\Agent Community 设计文档审计报告 20260412.md`

## 5. 本轮共通的禁止事项

- 不要直接做群组 bootstrap 功能实现
- 不要继续从旧 `designlog` 直接推出当前结论
- 不要把“以前成功过”当成当前体系已经按设计落地
- 不要把 `HTTP 200/202` 当成 canonical effect 成功
- 不要为了通过测试写新的硬编码 workflow
- 不要把兼容残留字段顺手删掉

## 6. 三个板块的最终合并要求

三个板块完成后，必须能汇合成一次最终综合审计。

汇合前提：

1. 社区 server / 数据合同 / session 合同已经对齐到设计文档
2. `community-skill` 的 onboarding / runtime / 消息封装 / 出站行为已经对齐到设计文档
3. live 部署面与 fresh 安装面已经验证：
   - 使用 fresh upstream OpenClaw
   - 使用 fresh GitHub `community-skill`
   - 不依赖旧实例污染
   - 不依赖模板仓分叉逻辑
4. 旧逻辑残留已清理或已正式降级，不再混成当前真相源

## 7. 每个线程都必须产出的结果

每个线程都要产出：

- 审计范围内的问题清单
- 每个问题的根因判断
- 每个问题的修正方案
- 已完成修正的文件与验证证据
- 尚未能修正的问题及其 blocker
- 与最新设计文档仍未对齐的点

## 8. 推荐执行顺序

三个线程可以并行，但推荐节奏是：

1. A 板块先把社区 server / 数据合同 / session 合同查清
2. B 板块据此收口 `community-skill`
3. C 板块持续用 fresh 安装 / live 运行面做验证

如果 C 发现真实环境结论推翻了 A / B 的假设，A / B 必须回退修正，而不是硬解释。

## 9. 对用户协作方式的要求

- 用中文
- 直接说结论
- 不要拍马屁
- 专业术语要讲大白话
- 不要一边出大问题一边继续讲空泛规划
- 这轮任务的重点是把基础建设收干净，不是讲故事

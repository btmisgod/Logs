# 审计任务 C：Live 部署面、Fresh 安装面与模板分叉 2026-04-13

## 1. 任务定位

这个板块负责：

- live 部署面
- 已安装实例面
- fresh upstream OpenClaw + fresh GitHub `community-skill` 安装面
- 模板仓的分叉、模板泄漏、历史残留排查

这是当前唯一允许主要依赖非本地环境的审计板块。

## 2. 必读文档

1. `G:\community agnts\community agents\docs\control-plane\AUDIT_SPLIT_PLAN_20260413.md`
2. `G:\community agnts\community agents\docs\control-plane\AUDIT_HANDOFF_NEXT_THREAD_20260413.md`
3. `G:\community agnts\community agents\docs\control-plane\SYSTEM_AUDIT_TASKBOOK_20260412.md`
4. `G:\community agnts\community agents\docs\control-plane\SYSTEM_AUDIT_INITIAL_FINDINGS_20260412.md`
5. `G:\community agnts\community agents\myproject\docs\design-facts\Agent Community 架构设计文档.txt`
6. `G:\community agnts\community agents\myproject\docs\design-facts\Agent Community Skill设计文档.txt`
7. `G:\community agnts\community agents\myproject\docs\design-facts\Agent Community 数据模型设计文档.txt`
8. `G:\community agnts\community agents\myproject\docs\design-facts\Agent Community Onboarding与Session合同设计文档.txt`
9. `G:\community agnts\community agents\myproject\docs\design-facts\Agent Community 历史遗留与降级说明.md`

## 3. 需要回答的问题

### 3.1 live 部署面是否真的和源仓一致

必须查清：

- source repo commit
- 已安装 runtime asset
- live process

这三者是否一致。

### 3.2 fresh install 是否真的成立

必须查清：

- 使用 fresh upstream OpenClaw
- 使用 fresh GitHub `community-skill`
- 使用当前 community server

时，是否真的能成功：

- 建立身份
- 完成 session/onboarding
- 建立 socket / send route
- 接收真实 inbound
- 产生 canonical effect

### 3.3 模板仓是否仍在污染当前实现判断

必须查清：

- `openclaw-for-community` 中有哪些行为分叉
- 哪些只是模板便利性
- 哪些是模板仓不应再保留的主实现逻辑
- 哪些 historical workflow success 属于 legacy 路径

## 4. 修正任务

查清以后，直接修：

1. live 安装面漂移
2. stale process
3. fresh install 与设计文档不一致的问题
4. 模板仓泄漏到 skill 主实现判断里的问题
5. 必要的模板仓降级 / 标注 / 清理

注意：

- 模板仓不是主实现
- 这个板块不能把模板仓改成新的 skill 真相源

## 5. 产出要求

必须产出：

- C 板块问题清单
- 每条问题的根因、影响、修正
- live / fresh install 证据
- 模板分叉与模板泄漏清单
- 尚未能修掉的问题和 blocker

## 6. 完成标准

这个板块算完成，至少要满足：

1. live 部署面与源仓的一致性已被验证
2. fresh upstream OpenClaw + fresh GitHub `community-skill` 可以在当前 community server 上完成真实接入
3. 真实 inbound 后不止是 `200/202`，还要有 canonical effect
4. `openclaw-for-community` 已被明确限制在模板 / 对照面角色
5. 历史残留成功路径已被重新分类，不再污染当前结论

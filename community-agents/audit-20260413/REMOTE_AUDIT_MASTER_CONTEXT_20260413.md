# 远端审计总上下文 2026-04-13

## 1. 当前任务阶段

当前不是正常开发阶段。

当前阶段是：

- 基础建设严格审计

当前不做：

- 群组 bootstrap 功能实现
- 新 workflow 功能开发
- 为了通过测试写新的硬编码流程

## 2. 当前三条硬边界

### 2.1 community server 是社区层通用 server

- 这里说的 server 是社区层通用 server
- 不是为某个群组测试定制的 server

### 2.2 `community-skill` 是唯一 skill 主体真相源

- `community-skill` 是 skill 主体
- `openclaw-for-community` 只是模板 / 工具 / 次级对照面

### 2.3 runtime 只做最小责任判断与协议挂载

- runtime 负责最小责任认定
- runtime 负责挂载 agent protocol
- runtime 负责按 `group_id` 挂载当前 group protocol
- runtime 把协议上下文交给 agent 自身行为与决策

## 3. 当前已知系统性问题

1. `community-skill` 和当前 community server 在 fresh onboarding/session 合同上不一致
2. `community-skill` 当前只证明了 intake/judgment/generic reply
3. `community-skill` release 面被具体环境默认值污染
4. `myproject` 的协议 / 文档面污染更严重
5. `openclaw-for-community` 只应作为次级对照面，不能继续被当作 skill 主实现依据
6. 历史硬编码 orchestration 残留会制造“以前成功过”的假证据
7. duplicated `author_kind` 是兼容残留，不能顺手删

## 4. 当前通用 bootstrap 共识

bootstrap 是群组中的一条通用初始化 workflow。

当前已经收口为：

- `step0`
- `step1`
- `step2`
- `formal_start`

说明：

- 旧的三步开机流已经废弃
- 旧 `task contract` 口径是历史残留
- `broadcast` 不再是 bootstrap 必经动作
- `broadcast` 现在只保留为公共信息写入群上下文的功能

## 5. 当前工作方式

- 先审计，再修正
- 不把 200/202 当成 canonical effect
- 不把旧成功当当前体系成立证据
- 不直接从旧 `designlog` 推当前结论
- 小问题不允许掩盖大问题

## 6. 当前审计目标

把社区工程和 skill 工程中的基础建设实现：

- 对齐到最新设计文档
- 去除旧逻辑残留

等这一步完成后，才进入群组功能实现与 workflow 落地。

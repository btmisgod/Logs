# Agent Community 产品修复续跑上下文 2026-04-13

## 1. 当前任务定位

这不是一条新的功能开发任务。
这是在上一轮产品级修复已经打通关键主链之后，继续把 `myproject` 和 `community-skill` 修到“合格产品基础建设”的续跑任务。

当前仍然 **不做**：
- 群组 bootstrap / 开机工作流产品实现
- step0 / step1 / step2 / formal_start 的正式施工
- 新 workflow 功能扩展
- 为了单群测试通过而写硬编码

## 2. 当前唯一真相

### 仓库边界

1. `myproject`
- 社区工程主仓
- 承载 community server、消息/事件事实、session/sync、GroupSession、通用 server 行为

2. `community-skill`
- 唯一 skill 主体真相源
- 承载 onboarding、接入准备、runtime 连接、agent 侧统一消息基型封装、agent 行为桥接

3. `openclaw-for-community`
- 模板/工具仓
- 只作次级对照面和安装工具面
- 不作为 skill 主实现真相源

### 当前正式链路

`community server -> group protocol -> runtime -> agent protocol -> agent 自身行为`

边界补充：
- community server 是通用社区 server，不为单群反向定制
- runtime 只做最小责任判断和协议挂载
- skill 必须保留 agent 侧统一消息封装
- agent 自身行为由 OpenClaw 本地 agent 执行桥承接

## 3. 上一轮已经完成的关键修复

上一轮产品级修复已经确认：

1. live `myproject` 已部署到 `8de4dc6`
2. live `POST /api/v1/agents/me/session/sync` 已可用
3. fresh upstream OpenClaw + fresh GitHub `community-skill` 已能完成：
   - onboarding
   - 身份准备
   - webhook 订阅
   - send route
   - 规范入库
4. `message.posted -> needs_agent_judgment -> local OpenClaw bridge -> canonical reply` 主链已修通
5. 已验证：
   - inbound message id: `86b47afc-acd7-405f-9d4e-a54d3ebcb8d8`
   - reply message id: `6bb4e217-27a3-46fd-b56c-71c70bb195b0`
   - reply text: `product-repair-effect-fixed-1776082236`
   - journal 有 `execution_bridge=openclaw_local_agent`
   - 数据库中存在 `parent_message_id=86b47afc-acd7-405f-9d4e-a54d3ebcb8d8` 的 reply 行

## 4. 这说明什么

当前已经排除：
- server 未投递
- onboarding 未闭环
- session/sync 缺失
- send route 不通
- runtime 只会判断不会真正走到 agent

当前新的续跑任务不是“再修这条主链”，而是：

> 以这条已经修通的主链为新基线，继续审计并去除 `myproject` 与 `community-skill` 中剩余的设计错位、兼容残留、发布面污染和历史逻辑残留。

## 5. 本轮续跑重点

### 优先级 1：继续找设计与实现不一致处

只查基础建设范围：
- onboarding/session/sync
- Message / Event / AgentSession / GroupSession
- server 对统一消息字段的消费
- runtime 的最小责任边界
- skill 的统一消息封装
- agent 行为桥接的稳定性

### 优先级 2：清理旧逻辑残留

包括但不限于：
- 旧兼容假设
- 错误默认值
- release 面污染
- 模板仓带来的分叉误导
- 与最新设计文档不一致但暂时没爆炸的代码路径

### 优先级 3：每修一批就重验

验证要求：
- 不能只看 `200/202`
- 不能只看 service active
- 不能只看 send route accepted
- 必须看真实 canonical effect

## 6. 当前明确暂缓的内容

以下内容本轮不做：
- 群组 bootstrap 的产品实现
- 通用开机流 step0/step1/step2/formal_start 的正式施工
- 群组工作流功能落地
- 新增 workflow 特性

这些内容要等基础建设合格后再做。

## 7. 当前必须记住的禁区

1. 不要把 `openclaw-for-community` 当 skill 主体真相源
2. 不要再引用“community-skill 已移除 session/sync 依赖”的旧说法
3. 不要把 runtime 扩写成完整 manager orchestrator
4. 不要删除 duplicated `author_kind`
5. 不要为了演示通过而补 generic fake reply
6. 不要把群组功能实现混进当前基础建设修复

## 8. 本轮任务目标

把 `myproject` 和 `community-skill` 继续修到下面这个标准：

1. 基础建设主链与最新设计事实源不再明显打架
2. fresh install + live community + canonical effect 验证持续成立
3. 关键旧逻辑残留被清掉或降级
4. 基础层可以被视为“合格产品底座”

## 9. 结果要求

续跑结束时，结果必须明确回答：

1. 这轮又发现了哪些剩余问题
2. 每个问题的根因是什么
3. 修了哪些文件
4. 验证跑了什么
5. 还有哪些设计不匹配尚未收口
6. 当前基础建设是否已经可以认定为“合格”

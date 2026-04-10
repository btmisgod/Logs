# 固定 Worker 登记

更新时间：2026-04-04 Asia/Shanghai

## 主控
- 主线程：你 + 我

## 固定 Worker
- 实现-后端-skill
  - agent_id: `019d58c5-8e87-7c20-86b4-a2cba958d7d9`
  - 默认推理：`medium`
  - 职责：`community-skill` 内 runtime/deliberation、community webhook、skill 行为与相关测试；必要时才碰直接相关的 `myproject` 后端代码
  - 类型：本地固定子 agent（当前会话内可复用）

- 实现-前端
  - agent_id: `019d58c5-8ee0-7351-8201-705d6a68b0f6`
  - 默认推理：`medium`
  - 职责：`myproject` 前端/UI/页面交互/前端测试；聚焦社区前端、登录页、agent 列表、群组页面、看板 UI；不发明后端契约
  - 类型：本地固定子 agent（当前会话内可复用）

- 服务器测试
  - agent_id: `019d58c5-8ecb-7230-b892-a96781ef2a01`
  - 默认推理：`medium`
  - 职责：通过控制器调用服务器上的 Codex executor，执行真实环境验证、多 agent 通讯测试、功能测试、blocker 收窄、少量环境修复；不承担主开发的大逻辑改动
  - 类型：本地固定协调子 agent（当前会话内可复用），不等于服务器上的执行 agent 本体

## 调度规则
- 默认复用以上固定 worker，不再随手新建一次性实现 agent。
- 只有在 worker 明确失效、不可恢复，或你明确要求额外并行 worker 时，才新建替代/附加 worker。
- 未经你明确要求，我不直接亲自做主要实现；优先分派给固定 worker。
- 如果某个任务需要临时提高推理档位，任务结束后必须恢复到 `medium`。
- 这些固定 worker 的“固定”含义是：在当前会话内持续复用同一批子 agent；如果会话被系统重置、压缩或失效，需要重新注册，但逻辑角色保持不变。

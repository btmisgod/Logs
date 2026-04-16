# Server Codex Capability Prompt

把下面这段 prompt 发给服务器上的 Codex。

```text
你现在的任务不是立即开始做项目，而是先学习并加载一套“从设计文档到项目交付”的多线程研发能力配置。

先读取以下 GitHub 资料，不要跳过顺序：

1. https://github.com/btmisgod/Logs/blob/main/research/codex-autonomous-build-kit/README.md
2. https://github.com/btmisgod/Logs/blob/main/research/codex-autonomous-build-kit/execution-playbook.md
3. https://github.com/btmisgod/Logs/blob/main/research/codex-autonomous-build-kit/papers.json
4. https://github.com/btmisgod/Logs/blob/main/research/codex-autonomous-build-kit/capability-config.json
5. https://github.com/btmisgod/Logs/blob/main/research/codex-autonomous-build-kit/codex-prompt.md

如果你的读取工具更适合 raw 链接，则改用：

1. https://raw.githubusercontent.com/btmisgod/Logs/main/research/codex-autonomous-build-kit/README.md
2. https://raw.githubusercontent.com/btmisgod/Logs/main/research/codex-autonomous-build-kit/execution-playbook.md
3. https://raw.githubusercontent.com/btmisgod/Logs/main/research/codex-autonomous-build-kit/papers.json
4. https://raw.githubusercontent.com/btmisgod/Logs/main/research/codex-autonomous-build-kit/capability-config.json
5. https://raw.githubusercontent.com/btmisgod/Logs/main/research/codex-autonomous-build-kit/codex-prompt.md

你的当前目标是“获得能力”，不是“立即执行项目”。

你必须遵守以下加载规则：

1. 先完整读取并理解 capability-config.json。
2. 把 capability-config.json 视为能力契约，而不是普通参考资料。
3. 当前状态必须保持为 capability_only / armed_not_running，不能私自切换到执行状态。
4. 在没有明确执行命令前，你只能做能力学习、研究总结、模板准备、角色设计、阶段闸门设计、任务拆解策略设计。
5. 在没有明确执行命令前，你不能改项目文件，不能启动项目实现，不能宣布项目已开工。
6. 你必须具备在未来执行时将长任务自动拆解为子任务、并按边界分配给子线程的能力，但当前只允许学习这项能力，不允许对真实项目触发它。
7. 如果未来收到执行命令，你必须先检查四个条件是否满足：
   - bootstrap_completed
   - design_document_available
   - runnable_environment_available
   - explicit_user_execution_request_received
8. 如果四个条件没有同时满足，你必须停留在能力准备阶段。

你需要从这些资料中吸收并保留以下能力：

- 从设计文档提炼 requirements、assumptions、acceptance criteria
- 将长任务拆成可解、完整、不重复的子任务
- 把子任务分派给有明确边界的子线程
- 把实现、审阅、测试、运行验证相互隔离
- 用阶段闸门控制执行，而不是一步写到底
- 区分单元测试、集成测试、端到端测试和真实运行验证
- 在环境失败时进入故障排查，而不是伪造完成状态

你要特别记住关于长任务拆解和子线程派发的规则：

- 只有任务过大、可以安全拆开、且每个子任务都有清晰交付物时，才能派发子线程。
- 子线程必须知道自己能改哪些文件，不能改哪些文件。
- 子线程不能互相覆盖同一片写入区域，除非有明确合并策略。
- 审阅线程和测试线程不能和实现线程是同一个责任体。
- 父线程要负责整合子线程产物，而不是把责任全丢出去。

完成学习后，你先不要执行项目。你只需要输出以下内容：

A. 你已成功加载的能力清单
B. 你理解的激活条件
C. 你理解的长任务拆解规则
D. 你理解的子线程分派边界规则
E. 你当前为什么不能直接开工
F. 你在未来收到设计文档和运行环境后会按什么顺序启动

不要开始实现任何真实项目，除非用户在后续消息中明确要求你执行。
```

## 用途

这份 prompt 适合服务器上的 Codex 先做能力装载。

它的目标不是让服务器立刻去改项目，而是先把这套多线程研发能力、阶段闸门和子线程拆解规则吃进去。
# Codex Prompt

把下面整段提示词发给新的 Codex 线程即可。

```text
你现在要先读取一份 GitHub 上的研究资料包，再基于它设计并执行一个“从设计文档到项目交付”的多线程 coding workflow。

第一步，不要急着写代码。先读取以下 GitHub 文件：

1. https://github.com/btmisgod/Logs/blob/main/research/codex-autonomous-build-kit/README.md
2. https://github.com/btmisgod/Logs/blob/main/research/codex-autonomous-build-kit/execution-playbook.md
3. https://github.com/btmisgod/Logs/blob/main/research/codex-autonomous-build-kit/papers.json

如果你的 GitHub 工具更适合读 raw 链接，也可以读取：

1. https://raw.githubusercontent.com/btmisgod/Logs/main/research/codex-autonomous-build-kit/README.md
2. https://raw.githubusercontent.com/btmisgod/Logs/main/research/codex-autonomous-build-kit/execution-playbook.md
3. https://raw.githubusercontent.com/btmisgod/Logs/main/research/codex-autonomous-build-kit/papers.json

第二步，读完后先做研究吸收，不要立刻实现。你需要输出一份“执行方案”，把论文里的思想落成工程规则，而不是空谈论文。

你的目标是：仅基于我提供的设计文档和运行环境，设计并执行一个尽量少人工介入的多线程研发工作流，覆盖：
- 需求归一化
- 任务拆解
- 项目管理与线程编排
- 代码实现
- 代码审阅
- 自动测试
- 真实运行验证
- 最终交付

你必须遵守这些规则：

1. 先读研究包，再开始规划。
2. 不允许把“写代码”当作第一步，必须先产出需求包和任务图。
3. 不允许所有线程都做同一种工作，至少分出：需求、规划、实现、审阅、测试、运行验证。
4. 不允许实现线程自己审自己、测自己然后直接宣布完成。
5. 不允许只给我泛泛建议，你要把执行流程落实成角色、状态机、闸门条件、交付物模板。
6. 不允许把测试通过等同于真实可用，必须明确区分单元测试、集成测试、端到端测试和真实运行验证。
7. 如果设计文档存在歧义，你要显式输出 assumptions，而不是偷偷脑补。
8. 如果环境跑不起来，你要进入故障排查和证据收集，而不是继续伪造“项目已完成”。
9. 你的方案必须吸收 papers.json 里列出的论文，但不能生搬硬套成学术复述。
10. 你的方案要明确说明当前自动化的边界，不要把系统能力吹成完全可靠的无人研发团队。

在真正开始实现前，先给出以下内容：

A. 一份 1 页以内的研究结论摘要
B. 一份线程角色设计
C. 一份状态机/阶段闸门设计
D. 一份交付物清单
E. 一份失败回退机制
F. 一份你准备如何把设计文档转成 requirement pack 的方法

然后再根据我给你的设计文档和环境，进入执行阶段。

如果你能使用子线程或并行 worker，就把它们限制在明确边界内，避免多个线程写同一片区域。

如果你发现研究包和真实项目条件冲突，优先服从真实项目约束，但要明确记录偏离点。
```

## 使用建议

- 最稳的方式是先把这份 prompt 发给新线程，再把设计文档和环境说明贴过去。
- 如果新线程有 GitHub 工具，优先让它直接读取 GitHub 文件。
- 如果新线程没有 GitHub 工具，就把 `execution-playbook.md` 和 `papers.json` 的内容再转发一份。
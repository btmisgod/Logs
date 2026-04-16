# Codex Autonomous Build Research Pack

这不是“论文堆料包”，而是给执行线程看的研究入口。

目标场景：给 Codex 一份设计文档和一个可运行环境，希望它尽量少依赖人工介入，完成从需求整理、任务拆解、项目推进、代码实现、审阅、测试到真实运行验证的一整条链路。

## 为什么这里不直接存整篇 PDF

1. 版权和长期维护更麻烦。
2. 真正对执行线程有用的不是整篇论文，而是可落实的工作流约束。
3. 这里优先放官方论文链接、机器可读元数据和提炼后的执行规则。

## 包内文件

- `README.md`: 总览、阅读顺序、覆盖范围
- `execution-playbook.md`: 从论文中提炼出的执行工作流
- `papers.json`: 机器可读论文清单，适合程序化读取
- `codex-prompt.md`: 给 Codex 直接使用的提示词模板

## 这套材料解决什么问题

| 阶段 | 关键论文 | 用途 |
| --- | --- | --- |
| 设计文档 -> 需求与测试 | ArchCode | 从文字需求中提炼功能/非功能要求，并把要求转成测试 |
| 多线程角色分工 | MetaGPT | 把软件开发流程拆成可执行的角色与 SOP |
| 任务拆解与分配 | Agent-Oriented Planning | 约束子任务必须可解、完整、不重复 |
| 多线程对齐 | RTADev | 在出现理解偏差时做对齐检查和临时会审 |
| 仓库级代码执行 | SWE-agent / SWE-Dev | 强调工具接口、仓库探索、补丁与测试闭环 |
| 测试驱动修复 | TDFlow | 强制分离“提补丁/调试/修补丁/测例生成” |
| 自动审阅 | CodeAgent | 把审阅线程从实现线程中独立出来 |
| 现实约束校正 | DevEval / OSWorld / GitGoodBench | 提醒当前系统在哪些地方还不可靠 |

## 建议阅读顺序

1. `ArchCode`
2. `MetaGPT`
3. `Agent-Oriented Planning in Multi-Agent Systems`
4. `RTADev`
5. `SWE-agent`
6. `SWE-Dev`
7. `TDFlow`
8. `CodeAgent`
9. `Prompting Large Language Models to Tackle the Full Software Development Lifecycle: A Case Study`
10. `OSWorld`
11. `GitGoodBench`

## 怎么喂给执行线程

建议不要让执行线程自己从零读所有论文，而是按这个顺序用：

1. 先读 `execution-playbook.md`
2. 再读 `papers.json`
3. 必要时再跳转到论文官方页
4. 最后用 `codex-prompt.md` 作为启动提示词

## 你应该对系统抱什么预期

这套材料能帮助构建“更像自动化开发组织”的 Codex 工作流，但它不能把今天的模型神化成完全可靠的无人研发团队。

尤其要记住：

- DevEval 这类研究说明，完整软件生命周期目前仍然很难完全自动打通。
- TDFlow 说明，真正的硬点往往不是补代码，而是写出靠谱的复现测试。
- OSWorld 说明，涉及真实电脑操作、多应用流程时，模型离稳定可用还有明显距离。

## 官方来源

官方来源都已经整理在 `papers.json` 中，优先使用会议官网、ACL Anthology、ICLR Proceedings、NeurIPS Proceedings、OpenReview 等原始页面。
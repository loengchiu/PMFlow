# Codex 记忆交接

本文件用于新会话中快速恢复本次讨论的关键判断。新会话开始后，先读本文件，再讨论 PMFlow。

## 1. 用户真实目标

用户要做的不是一个全自动 PRD 生成器，而是一套 PM 掌控型的 AI IDE skill workflow。

核心目标：

- AI 帮 PM 理清需求、方案、原型、PRD。
- PM 每个阶段都必须看过、理解、确认。
- 产物要能用于真实评审和研发沟通。
- AI 不能悄悄把整条链路跑完。

## 2. 当前阶段判断

旧 OMP 已经解决了很多基础问题：

- 安装方式。
- 命令入口。
- PowerShell 退场。
- 模板/skill/reference/contracts 分层。
- 人读/机读分离的方向。

但旧 OMP 的质量链路仍不足：

- reviewer 弱。
- 方法论没有真正驱动生成。
- solution 容易漏字段、流程、信息架构。
- prototype 容易靠 AI 经验布局。
- PRD 与字段/数据字典联动不足。
- 自然语言触发和阶段推进仍有风险。

因此决定新起 PMFlow，而不是继续在旧 OMP 上修补。

## 3. 必须坚持的设计方向

- 新项目，不继承旧 OMP 运行时。
- 学 testany-eng 的工程思想，不照搬它的完整范围。
- 保留 B 端中后台 PM 工作流焦点。
- 显式命令入口。
- `guide` 是默认入口。
- interviewer / writer / reviewer 分离。
- 每阶段结束必须停下。
- 人读产物干净，机读 metadata 放 sidecar。
- 方法论在生成前生效，不是生成后检查。

## 4. 不能再犯的旧坑

- 不要自然语言自动路由。
- 不要自动跨阶段。
- 不要让 AI 把背景材料当会后回答。
- 不要让模板代替 skill。
- 不要把 reference 样例当门禁规则。
- 不要把纠错案例堆进 skill。
- 不要把机读字段放进 `output/`。
- 不要让 reviewer 复述 writer。
- 不要一有小改动就整篇重写。
- 不要为了轻量牺牲质量。

## 5. 用户偏好的工作方式

- 先质疑，再设计。
- 不要一味顺着用户的临时想法走。
- 发现路线问题要直接指出。
- 文件要直接落盘，不要只聊天。
- 规则要分层，不能乱放。
- 输出要像人类 PM 写的，不要 AI 味。
- 中文为主，技术词保留英文。
- 需要给其他 AI 执行时，要写得像教实习生一样清楚。

## 6. 参考对象判断

### ShitPM

优点：

- PRD 文风稳定。
- 命令和状态比较稳。
- 产物更像人类 PM 写的。

不足：

- 后期改需求时上下游同步困难。
- 字段、页面、数据字典容易脱钩。
- AI 做完后 PM 掌握感不足。

### OMP

优点：

- 已有显式命令方向。
- 已积累真实项目问题。
- 已开始做 metadata/lint/methods。

不足：

- 历史残留多。
- 规则修补痕迹重。
- reviewer 不够独立。
- workflow core 不够工程化。

### testany-eng

优点：

- 工程思想强。
- `/guide` 清晰。
- interviewer/writer/reviewer 清晰。
- traceability metadata 成熟。
- Phase 0 上下文收集硬。

不照搬：

- API/HLD/LLD/Test 全链路。
- 过强自动化推进。
- 文档内嵌可见 metadata。

## 7. 新项目文件分工

PMFlow 当前交接包：

```text
AGENTS.md               给 DeepSeek 的执行纪律
prd.machine.yaml        机读产品定义
handoff.md              旧经验交接
anti-patterns.md        反模式清单
review-manual.md        给 Codex 的验收手册
codex-memory-handoff.md 给 Codex 的记忆交接
USER-GUIDE.md           给用户的操作手册
```

## 8. 讨论环境

后续不要继续在 `D:\work\ShitPM` 里讨论 PMFlow。

应切到：

```text
D:\work\PMFlow
```

新会话中，用户如果说“继续 PMFlow”，优先读取：

```text
D:\work\PMFlow\codex-memory-handoff.md
D:\work\PMFlow\prd.machine.yaml
D:\work\PMFlow\review-manual.md
```

## 9. 最重要的一句话

PMFlow 不是 AI 替 PM 做完，而是 AI 帮 PM 分阶段理解、确认、产出，并保证 PM 始终能掌控需求。

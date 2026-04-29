# PMFlow 执行纪律

本项目用于从零设计一套新的 PM workflow skills。执行者主要是 Claude Code CLI + DeepSeek V4 PRO。Codex 后续负责验收。

## 1. 工作目标

PMFlow 要解决的是 B 端中后台需求从模糊输入到可评审 PRD / 原型的工作流质量问题。

目标不是全自动生成完整链路，而是让 PM 在每个关键阶段都能看懂、确认、掌控产物。

## 2. 总原则

- 先审计，再设计，再实现。
- 不要继承旧 OMP 的运行时。
- 不要照搬 testany-eng 的全链路范围。
- 学习 testany-eng 的工程思想：明确入口、interviewer/writer/reviewer 分离、追溯元数据、阶段门禁。
- 保留 ShitPM 的优点：PRD 文风稳定、产物去 AI 化、模板不露馅。
- 每个阶段完成后必须停下，等待 PM 显式确认。
- AI 是 PM 的协作工具，不是自动驾驶系统。

## 3. 禁止事项

- 不得自然语言自动跨阶段。
- 不得因为“看起来可以继续”就直接进入下一阶段。
- 不得把项目文件自动当作需求输入。
- 不得把背景材料当作会后回答。
- 不得恢复 PowerShell 主流程。
- 不得把样例当规则。
- 不得把所有说明都塞进 `SKILL.md`。
- 不得把机读字段、调试字段、内部路径暴露到人读产物。
- 不得让 reviewer 复述 writer 的判断。
- 不得小改动就整篇重写产物。

## 4. 分层规则

| 层级 | 职责 |
|---|---|
| `commands/` | 显式命令入口，只负责触发哪个 skill |
| `skills/` | 当前动作 SOP：输入、步骤、产出、门禁、停止条件 |
| `contracts/` | 跨 skill 的硬约束 |
| `profiles/` | 阶段产物的机读契约 |
| `schemas/` | 结构化字段、枚举、必填项校验 |
| `references/` | 写法参考、方法论示例、好坏例子 |
| `templates/` | 人读产物骨架和最低格式 |
| `scripts/` | 只做确定性校验和聚合，不做主流程判断 |
| `.pmflow/` | 业务项目内部状态和 metadata |
| `.pmflow/reviews/` | reviewer 的内部审查结果、阻断原因和可追溯检查记录 |
| `output/` | PM、需求方、研发可读产物 |

放置规则：

- 当前动作不看就会跑偏：放 `skills/`
- 多个动作共用的硬约束：放 `contracts/`
- 写作风格和示例：放 `references/`
- 文件结构骨架：放 `templates/`
- 可脚本校验的结构：放 `profiles/` 和 `schemas/`

## 5. 阶段模型

`solution`、`prototype`、`prd` 三个核心产出阶段必须拆成：

```text
writer -> reviewer -> PM ownership gate
```

- `writer` 负责生成或修改当前阶段产物。
- `reviewer` 负责独立检查当前阶段是否满足进入下一阶段。
- `PM ownership gate` 负责停下，让 PM 读懂并确认。

阶段通过不代表自动进入下一阶段。只有 PM 显式执行下一命令，才能继续。

`brd-interviewer` 和 `uc-interviewer` 属于 interviewer 模式，不强制单独拆 reviewer；它们必须在阶段末尾完成推进判断，并进入 PM ownership gate。

## 6. 建议 skill 链路

第一版优先实现：

```text
pm-guide
brd-interviewer
uc-interviewer
solution-writer
solution-reviewer
prototype-designer
prototype-reviewer
prd-writer
prd-reviewer
```

建议命令映射：

| 命令 | 触发 skill | 说明 |
|---|---|---|
| `/pm-guide` | `pm-guide` | 判断项目状态和唯一下一步 |
| `/pm-brd` | `brd-interviewer` | 梳理业务需求和会面问题 |
| `/pm-uc` | `uc-interviewer` | 梳理用户路径和任务流 |
| `/pm-solution` | `solution-writer` | 生成或修改方案稿 |
| `/pm-solution-review` | `solution-reviewer` | 审查方案是否可进入原型或 PRD |
| `/pm-proto` | `prototype-designer` | 生成或修改原型 |
| `/pm-proto-review` | `prototype-reviewer` | 审查原型是否可进入 PRD |
| `/pm-prd` | `prd-writer` | 生成或修改 PRD |
| `/pm-prd-review` | `prd-reviewer` | 审查 PRD 是否可归档和评审 |

第二版再考虑：

```text
fix
change
review-pack
export
```

## 7. 质量优先级

按下面顺序取舍：

1. 不乱写。
2. 不跳步。
3. PM 看过并掌控。
4. 字段、流程、页面、规则不脱钩。
5. reviewer 能独立发现问题。
6. 产物像人类 PM 写的。
7. 自动化程度。

## 8. 回归案例

设计和实现时必须保留三组回归样本：

- `D:\work\交投软件中心\审计系统`
- `D:\work\交投软件中心\智慧服务区\公众服务管理`
- `D:\work\交投软件中心\智慧服务区\物业管理\资产管理`

这些案例用于验证建设类型、字段、流程、背景材料识别、PRD 文风和原型可读性。

## 9. 执行节奏

当前阶段只做当前阶段。

每完成一个阶段，必须输出：

```text
已完成：
- ...

修改文件：
- ...

未解决问题：
- ...

需要 PM 或 Codex 验收：
- ...

下一步建议：
- ...
```

如果需要决策，先问。不要替 PM 拍板。

## 10. 语言和文风

- 默认使用简体中文。
- 技术术语保留英文原文，必要时首次标注中文。
- 文档要直接、清楚、可执行。
- 不写“作为 AI”“我建议你”“根据规则要求”等暴露协作痕迹的表达。
- 对外产物避免模板感、填空感、解释性废话。

## 11. 验收意识

最终产物必须能经得起这些问题：

- 新项目第一次怎么启动？
- 当前阶段为什么不能自动进入下一阶段？
- PM 需要读懂什么才能继续？
- 人读产物和机读 metadata 分别在哪里？
- reviewer 如何独立检查 writer？
- 小改动如何避免整篇重写？
- 审计系统为什么是新建，不是混合？

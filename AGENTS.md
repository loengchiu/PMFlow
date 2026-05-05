# PMFlow 执行纪律

PMFlow 用于支撑 B 端中后台需求从模糊输入到可评审 PRD 和高保真原型的工作流。

核心目标不是全自动跑完整链路，而是让 PM 在每个关键阶段都能读懂、修改、复查并手动决定是否进入下一步。

## 1. 语言原则

- 默认使用简体中文。
- 技术术语保留英文原文，必要时首次标注中文。
- 文档直接、清楚、可执行。
- 对外产物不得出现 AI 痕迹、内部路径、metadata 字段或调试字段。

## 2. 主链路

```text
pm-guide
  -> pm-input
  -> pm-align
  -> pm-align-review
  -> pm-design
  -> pm-design-review
  -> pm-wireframe
  -> pm-wireframe-review
  -> pm-prd
  -> pm-prd-review
  -> pm-prototype
  -> pm-prototype-review
```

修改收口链路：

```text
pm-fix -> pm-fix-review
```

## 3. 阶段职责

| 阶段 | 主要职责 |
|---|---|
| input | 吸收 PM 提供的材料、识别建设类型、记录缺口和需求方认可材料 |
| align | 形成需求对齐稿，用于和需求方确认理解、目标、范围和方案方向 |
| design | 产出功能清单、页面清单、数据字典、系统流程和规则设计 |
| wireframe | 产出可选线框稿，用于快速发现页面组织、流程和信息呈现问题 |
| prd | 产出正式 PRD，用于研发评审、排期和归档 |
| prototype | 产出高保真 HTML 原型，用于产品评审和研发理解 |
| fix | 对已产出内容做局部或跨阶段修改，并登记复查债务 |

## 4. 推进纪律

- 每个 writer 完成后只提示对应 reviewer 或下一步唯一建议，然后停止。
- 每个 reviewer 只审查当前阶段，写入 review 结果，然后停止。
- reviewer 通过不代表自动进入下一阶段；PM 必须手动执行下一命令。
- 有 open 状态的 `fix_debts` 时，`pm-guide` 优先推荐 `pm-fix-review`。
- 不使用确认命令推进阶段；阶段推进由 writer 成功后更新 `current_stage`，reviewer 不推进阶段。

## 5. 分层规则

| 层级 | 职责 |
|---|---|
| `skills/` | 当前动作 SOP：输入、步骤、产出、门禁、停止条件 |
| `contracts/` | 跨 skill 的硬约束 |
| `profiles/` | 阶段产物的机读契约 |
| `schemas/` | 结构化字段、枚举、必填项校验 |
| `references/` | 写法参考、方法论示例、好坏例子 |
| `templates/` | 人读产物骨架和最低格式 |
| `scripts/` | 确定性校验、安装、聚合，不做主流程判断 |
| `.pmflow/` | 业务项目内部状态、metadata、review、snapshot |
| `output/` | PM、需求方、研发可读产物 |

放置规则：

- 当前动作不看就会跑偏：放 `skills/`
- 多个动作共用的硬约束：放 `contracts/`
- 写作风格和示例：放 `references/`
- 文件结构骨架：放 `templates/`
- 可脚本校验的结构：放 `profiles/` 和 `schemas/`

## 6. 禁止事项

- 不得自然语言自动跨阶段。
- 不得因为“看起来可以继续”就直接进入下一阶段。
- 不得把项目文件自动当作需求输入。
- 不得把背景材料当作会后回答。
- 不得恢复 PowerShell 主流程。
- 不得把样例当规则。
- 不得把所有说明都塞进 `SKILL.md`。
- 不得让 reviewer 复述 writer 的判断。
- 不得小改动就整篇重写产物。

## 7. 质量优先级

1. 不乱写。
2. 不跳步。
3. PM 看过并掌控。
4. 字段、流程、页面、规则不脱钩。
5. reviewer 能独立发现问题。
6. 产物像人类 PM 写的。
7. 自动化程度。

## 8. 输出节奏

每个 skill 完成后输出：

```text
已完成：
- ...

修改文件：
- ...

未解决问题：
- ...

需要 PM 或 Codex 验收：
- ...

下一步唯一建议：
- ...
```

如果需要 PM 决策，先问；不要替 PM 拍板。

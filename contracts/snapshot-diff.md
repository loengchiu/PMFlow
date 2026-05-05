# 快照 diff 契约

业务项目不强制使用 git。PMFlow 在无 git 的业务项目中通过快照 diff 支持 `/pm-fix` 自动识别人读物变更。

## 1. 快照位置

```text
.pmflow/snapshots/<stage>/<stage>.last-synced.*
```

示例：

```text
.pmflow/snapshots/align/align.last-synced.md
.pmflow/snapshots/design/design.last-synced.md
.pmflow/snapshots/wireframe/wireframe.last-synced.md
.pmflow/snapshots/prd/prd.last-synced.md
.pmflow/snapshots/prototype/prototype.last-synced.html
```

## 2. 快照更新时机

快照只在"同步干净"时更新：

- 阶段 writer 生成完成，并同步机读物后。
- `/pm-fix` 完成同步，并通过局部检查后。
- `/pm-fix-review` 确认本批变更已收口后。

**禁止**在 PM 刚手工修改人读物后立即更新快照，否则未同步变更会被吞掉。

**阶段 reviewer 不更新 snapshot**。/pm-fix-review 不属于阶段 reviewer，可按收口规则更新 snapshot。snapshot diff 是 `/pm-fix` 的确定性输入来源，不是主流程脚本驱动。

## 3. diff 机制

```text
PM 修改人读物
-> /pm-fix
-> 先用 .pmflow/snapshots/ 与当前人读物做 deterministic diff
-> 只把变更片段交给 AI
-> AI 匹配机读锚点、分析影响范围、同步机读物和下游产物
```

有 git 时可辅助读取 git diff。git 不存在、git diff 为空或 git diff 太乱时，仍退回 snapshot diff。

## 4. token 控制规则

- **禁止**把当前全文和快照全文同时交给模型比较。
- 必须先由确定性 diff 工具生成最小变更片段。
- AI 只读取 diff 片段、相关机读锚点分片和必要的人读上下文。

## 5. diff 分级处理

| diff 规模 | 处理 |
|---|---|
| 小 diff | 直接给 AI 分析 |
| 中 diff | 按章节或锚点分组，逐组处理 |
| 大 diff | 先生成变更摘要和候选锚点，询问 PM 是否分批处理 |
| 超大 diff | 拒绝一次性处理，要求拆分或按阶段处理 |

建议阈值：

| 指标 | 建议 |
|---|---|
| 单次 diff 上下文 | 不超过 200 行 |
| 单个变更组 | 不超过 50 行上下文 |
| 变更组数量 | 超过 10 个先汇总，不逐项展开 |
| 删除或新增超过全文 30% | 视为大改，不能当普通 fix |

## 6. 禁止行为

- 业务项目没有 git 时 `/pm-fix` 无法识别 PM 手改内容。
- 要求 PM 必须描述自己改了哪里。
- 把全文和快照全文都塞进模型上下文。
- 用户只改 5 行，却让 AI 重读 2000 行人读稿。
- PM 手改后立即覆盖快照，导致变更消失。
- 大 diff 不分组、不摘要、不询问，直接一次性处理。

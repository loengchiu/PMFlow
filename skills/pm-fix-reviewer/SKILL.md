---
name: pm-fix-reviewer
description: 修改收口。合并本批 /pm-fix 变更，检查人机同步和跨产物一致性。
triggers: ["/pm-fix-review"]
tags: [pmflow, fix, review, debt]
---

# pm-fix-reviewer 收口审查 SOP

按独立审查模式执行。不依赖 writer 会话结论，重新读取 status / artifact / metadata / profile 后再审查。

## 0. 执行方式

- Claude Code 环境下，如果 `pmflow-reviewer` subagent 可用，必须使用 `pmflow-reviewer` 执行审查，主会话不得直接做内容审查。
- 主会话负责把本 SOP、当前阶段、项目路径传给 subagent，并接收 `PMFLOW-REVIEW-RESULT`。
- 主会话根据 subagent 结果写入 review 文件，并追加 `.pmflow/status.yaml` 的 `review_results`。
- 如果 Claude Code 环境下 `pmflow-reviewer` 不可用，必须在输出中说明原因，再按独立审查模式执行。
- 非 Claude Code 环境按 `contracts/reviewer-independence.md` 的独立审查模式执行。

## 1. 前置读取

- `contracts/reviewer-independence.md`（独立审查契约）
- `contracts/gates.md`（门禁定义）
- `contracts/review-debt.md`（复查债务契约）
- `contracts/human-sync.md`（人机同步契约）
- `contracts/snapshot-diff.md`（快照 diff 契约）
- `contracts/lightweight-metadata.md`（轻量 metadata 契约）
- `schemas/status.schema.yaml`（状态 schema）

## 2. 执行顺序

### 步骤 1：读取所有 open fix_debts

读取 `.pmflow/status.yaml` 中所有 `status: open` 的 `fix_debts`。

如果没有 open 债务：停止，提示 PM 当前没有待收口的修改。

### 步骤 2：合并 affected_stages / affected_objects

合并所有 open 债务的 `affected_stages` 和 `affected_objects`，按阶段分组，识别重复影响的对象。

### 步骤 3：检查 changed_files 是否存在

对每条 open debt 的 `changed_files` 列表，检查文件是否存在于磁盘。不存在的标记为待处理项。

### 步骤 4：检查 metadata_files 是否存在

对每条 open debt 的 `metadata_files` 列表，检查文件是否存在于磁盘。不存在的标记为待处理项。

### 步骤 5：检查 snapshot_files 是否存在

对每条 open debt 的 `snapshot_files` 列表，检查文件是否存在于磁盘。不存在的标记为待处理项。

### 步骤 6：检查 sync_status 与同步证据

对每条 open debt 的 `sync_status`：

- `synced` → `changed_files`、`metadata_files`、`snapshot_files` 必须非空，且文件存在于磁盘。缺少文件证据必须 fail，不得 pass。
- `partial` → `changed_files` 至少非空；缺失的 metadata/snapshot 进入 warnings 或 pending_items。
- `pending` / `blocked` → 允许文件列表为空。

然后按 sync_status 判定：

- `blocked` → fail
- `pending` → warn 或 fail，取决于是否影响主链继续
- `partial` → warn
- `synced` → 可 pass（前提：文件证据完整）

### 步骤 6.5：检查同类关联点检测

检查 /pm-fix 是否做了同类关联点检测。如果 fix_debts 缺少 `affected_objects` 或 `affected_stages`，fail。如果明显存在同类关联点但 /pm-fix 未处理也未询问 PM，fail。如果同类关联点已列出但待 PM 确认，verdict 可以 warn，但不得关闭债务。

### 步骤 7：检查同类关联点

- 同字段在多个页面出现。
- 同操作在 PRD 和 prototype 都出现。
- 上游 design 修改但下游 prd/prototype 未同步。

### 步骤 8：合并 needs_stage_review

收集所有 open debt 的 `needs_stage_review`，去重合并。

### 步骤 9：输出审查文件

写入 `.pmflow/reviews/fix-review-{timestamp}.yaml`。

必须包含：

```yaml
stage: fix
check_type: reviewer_check
verdict: pass | warn | fail
reviewed_artifact_revision: ""
reviewed_metadata_revision: ""
debts_reviewed: []
merged_impact: {}
pending_items: []
closed_debts: []
needs_stage_review: []
checked_at: ""
```

### 步骤 10：verdict 为 pass/warn 时关闭债务并更新快照

- 关闭已收口 debt（`status: closed`）。
- 写 `closed_at`（ISO 时间）。
- 写 `close_reason`（收口原因摘要）。
- 更新相关 snapshot 和 `snapshot_records`（/pm-fix-review 是修改收口动作，不是阶段 reviewer，可在收口时更新快照）。

### 步骤 11：verdict 为 fail 时不关闭 debt

- 不关闭任何 debt。
- 不更新 snapshot 或 `snapshot_records`。
- 输出待处理项。

### 步骤 12：输出下一步

- fail：继续 `/pm-fix`。
- pass/warn 且 `needs_stage_review` 非空：提示手动执行对应阶段 review。
- pass/warn 且不需要阶段 review：提示回到正常主链，由 PM 手动执行下一命令或 `/pm-guide` 查看。

### 步骤 13：停止

输出收口结果后**必须停止**。不得自动执行阶段 review，不得自动执行 /pm-fix。

## 3. 判定标准

**fail**（任一满足）：

- sync_status 为 `blocked`
- 人机同步不一致且未处理
- 跨产物同步缺失且未提示风险
- 关键关联点遗漏
- 人读产物与 metadata 不一致

**warn**：

- sync_status 为 `partial` 或 `pending`
- 存在风险但不阻断
- 部分同步待完善

**pass**：

- 所有 debt sync_status 为 `synced`
- 人机同步一致
- 跨产物同步完整或已提示风险

## 4. 输出格式

```text
fix-review 完成。

审查结果：pass | warn | fail

本批变更：
- 共 N 条债务
- 已关闭 N 条
- 待处理 N 条

待收口项：
- [具体到对象、产物和问题]

需要阶段 review：
- /pm-design-review（原因：...）

下一步建议：
- [fail] 继续 /pm-fix 处理
- [pass/warn 且 needs_stage_review 非空] 手动执行 /pm-xxx-review
- [pass/warn 且不需要阶段 review] 回到正常主链，/pm-guide 查看
```

## 5. 禁止行为

- 只复述变更，不检查同类关联点
- 把正常修改循环强制绕到 /pm-guide
- 必须阶段 review 的债务没有落状态
- 自动执行阶段 review
- fail 时更新 snapshot（fail 时不得关闭 debt、不得更新快照）
- 阶段 reviewer 更新 snapshot（阶段 reviewer 只写 reviews/*.yaml 和 review_results；/pm-fix-review 是修改收口动作，不等同阶段 reviewer）

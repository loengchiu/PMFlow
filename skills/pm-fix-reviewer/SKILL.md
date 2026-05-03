---
name: pm-fix-reviewer
description: 修改收口。合并本批 /pm-fix 变更，检查人机同步和跨产物一致性。
triggers: ["/pm-fix-review"]
tags: [pmflow, fix, review, debt]
---

# pm-fix-reviewer 收口审查 SOP

## 1. 前置读取

- `contracts/gates.md`（门禁定义）
- `contracts/review-debt.md`（复查债务契约）
- `contracts/human-sync.md`（人机同步契约）
- `contracts/snapshot-diff.md`（快照 diff 契约）
- `schemas/status.schema.yaml`（状态 schema）
- `status.yaml` 中所有 `status: open` 的 `fix_debts`

## 2. 前置检查

读取 `.pmflow/status.yaml`，确认：

- `fix_debts` 中存在 `status: open` 的记录

如果没有 open 债务：停止，提示 PM 当前没有待收口的修改。

## 3. 收口流程

```text
读取未收口变更
-> 合并影响范围
-> 检查人机同步
-> 检查跨产物同步
-> 检查同类关联点
-> 输出待收口项
-> 关闭已收口变更
-> 给出下一步建议
```

### 3.1 合并影响范围

- 合并所有 open 债务的 `affected_stages` 和 `affected_objects`
- 按阶段分组，识别重复影响的对象
- 合并同阶段 review 债务

### 3.2 人机同步检查

对每个受影响阶段：

- 检查人读产物与机读 metadata 是否一致
- 检查快照是否已更新（`snapshot_records` 中对应 stage）
- 检查阅读编号是否与 metadata 对应

### 3.3 跨产物同步检查

- 上游基线变更后，下游产物是否已同步
- 未同步的产物是否存在风险

### 3.4 同类关联点检查

- 受影响对象是否存在同类关联
- 批量修改是否覆盖所有关联点

## 4. 判定输出

### 4.1 输出文件

写入 `.pmflow/reviews/fix-review-{timestamp}.yaml`。

必须包含：

```yaml
stage: fix
check_type: reviewer_check
verdict: pass | warn | fail
debts_reviewed: []  # 本次审查的 debt_id 列表
merged_impact: {}
  # 按阶段列出受影响对象
pending_items: []   # 待收口项
closed_debts: []    # 已关闭的 debt_id
needs_stage_review: []  # 需要执行的阶段 review
checked_at: ""
```

### 4.2 判定标准

**fail**（任一满足）：

- 人机同步不一致且未处理
- 跨产物同步缺失且未提示风险
- 关键关联点遗漏

**warn**：

- 存在风险但不阻断
- 部分同步待完善

**pass**：

- 本批变更已收口
- 人机同步一致
- 跨产物同步完整或已提示风险

### 4.3 关闭债务

verdict 为 pass 或时，将已收口的 debt 状态更新为 `closed`，记录 `closed_at`。

## 5. 输出格式

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
- /pm-prd-review（原因：...）

下一步建议：
- [如果有待收口项] 继续 /pm-fix 处理
- [如果需要阶段 review] 手动执行 /pm-xxx-review
- [如果全部收口] 回到正常主链
```

## 6. 停止条件

- 输出收口结果后**必须停止**
- 不得自动执行阶段 review
- 不得自动执行 /pm-fix

## 7. 禁止行为

- 只复述变更，不检查同类关联点
- 把正常修改循环强制绕到 /pm-guide
- 必须阶段 review 的债务没有落状态
- 自动执行阶段 review

## 8. 使用示例

```text
用户：/pm-fix-review

AI：fix-review 完成。
审查结果：pass
本批变更：共 2 条债务，已关闭 2 条
需要阶段 review：/pm-design-review（原因：L3 变更涉及页面清单）
下一步建议：手动执行 /pm-design-review
```

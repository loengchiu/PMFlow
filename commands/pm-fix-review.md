---
description: 修改收口。合并本批 /pm-fix 变更，检查人机同步和跨产物一致性，关闭复查债务。
argument-hint: 无参数
---

# pm-fix-review

触发 skill：`pm-fix-reviewer`

## 输入

- `status.yaml` 中 `status: open` 的 `fix_debts`
- 相关阶段的最新产物和 metadata
- `.pmflow/snapshots/` 中的快照（用于人机同步检查）

## 输出

- `.pmflow/reviews/fix-review-{timestamp}.yaml`（收口审查结果）
- 更新 `status.yaml` 中 `fix_debts` 状态（open -> closed）

## 不做什么

- 不直接修改产物文件
- 不把正常修改循环强制绕到 /pm-guide
- 收口后只给出下一步建议（可能需要阶段 review，也可能不需要）

---
description: 方案审查。独立审查 solution note，逐项检查 6 个维度。不进入 prototype。
argument-hint: 无参数，直接运行 /pm-solution-review
---

# pm-solution-review

触发 skill：`solution-reviewer`

## 输入

- `output/solution/solution-note-*.md`（人读方案）
- `.pmflow/metadata/solution/solution-*.yaml`（机读 metadata）
- `profiles/solution-review.profile.yaml`（审查标准）
- `profiles/solution.profile.yaml`（方案契约，对照检查）
- `.pmflow/status.yaml`（读取当前状态）

## 输出

- `output/review/solution-review-*.md`（人读审查报告）
- `.pmflow/reviews/solution-review-*.yaml`（机读审查记录）

## 不做什么

- 不修改 solution note
- 不在 fail 时提示 /pm-confirm 或 /pm-proto
- 不在 pass/warn 时提示 /pm-proto（只提示 /pm-confirm）
- 不代 PM 确认

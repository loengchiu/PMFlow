---
description: 原型审查。独立审查 prototype note，逐项检查 6 个维度。不进入 PRD。
argument-hint: 无参数，直接运行 /pm-proto-review
---

# pm-proto-review

触发 skill：`prototype-reviewer`

## 输入

- `output/prototype/prototype-note-*.md`（人读原型）
- `.pmflow/metadata/prototype/prototype-*.yaml`（机读 metadata）
- `profiles/prototype-review.profile.yaml`（审查标准）
- `profiles/prototype.profile.yaml`（原型契约，对照检查）
- `.pmflow/status.yaml`（读取当前状态）

## 输出

- `output/review/prototype-review-*.md`（人读审查报告）
- `.pmflow/reviews/prototype-review-*.yaml`（机读审查记录）

## 不做什么

- 不修改 prototype note
- 不在 fail 时提示 /pm-confirm 或 /pm-prd
- 不在 pass/warn 时提示 /pm-prd（只提示 /pm-confirm）
- 不代 PM 确认

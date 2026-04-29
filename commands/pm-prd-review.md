---
description: PRD 审查。独立审查 PRD 文档，逐项检查 7 个维度。
argument-hint: 无参数，直接运行 /pm-prd-review
---

# pm-prd-review

触发 skill：`prd-reviewer`

## 输入

- `output/prd/prd-*.md`（人读 PRD）
- `.pmflow/metadata/prd/prd-*.yaml`（机读 PRD metadata）
- 已确认的 prototype note + metadata
- 已确认的 solution note + metadata（对照字段和流程一致性）
- 已确认的 UC note + metadata（对照用户任务覆盖）
- 已确认的 BRD note + metadata（对照业务目标覆盖）
- `profiles/prd-review.profile.yaml`（审查标准）
- `profiles/prd.profile.yaml`（PRD 契约，对照检查）
- `.pmflow/status.yaml`（读取前置基线）

## 输出

- `output/review/prd-review-*.md`（人读审查报告）
- `.pmflow/reviews/prd-review-*.yaml`（机读审查记录）

## 不做什么

- 不修改 PRD 文档
- 不在 fail 时提示 /pm-confirm 或任何后续命令
- 不在 pass/warn 时提示任何后续阶段命令（只提示 /pm-confirm）
- 不代 PM 确认

---
description: "[legacy] 方案写作。基于已确认的 BRD 和 UC，产出 solution note。不进入 prototype。"
argument-hint: 可附带补充材料或澄清说明
---

# pm-solution [legacy]

> **legacy**: 此命令属于旧主链，新项目请使用 `/pm-design` 替代。

触发 skill：`solution-writer`

## 输入

- 已确认的 BRD note（`output/brd/` 和 `.pmflow/metadata/brd/`）
- 已确认的 UC note（`output/uc/` 和 `.pmflow/metadata/uc/`）
- PM 补充材料（如有）
- `.pmflow/status.yaml`（读取当前状态）

## 输出

- `output/solution/solution-note-*.md`（人读方案 note）
- `.pmflow/metadata/solution/solution-*.yaml`（机读 metadata）

## 不做什么

- 不进入 prototype / prd
- 不自行扩大 BRD 范围之外的模块或页面
- 完成后只提示 /pm-solution-review，不提示 /pm-proto 或 /pm-confirm
- 不生成原型或 PRD

---
description: "[legacy] 用户路径与任务流访谈。梳理用户角色、场景、任务流，产出 UC note。不进入 solution。"
argument-hint: 可附带用户角色补充、场景材料或澄清说明
---

# pm-uc [legacy]

> **legacy**: 此命令属于旧主链，新项目请使用 `/pm-align` 替代。

触发 skill：`uc-interviewer`

## 输入

- 已确认的 BRD note（`output/brd/` 和 `.pmflow/metadata/brd/`）
- PM 补充的用户角色、场景材料（如有）
- `.pmflow/status.yaml`（读取当前状态）

## 输出

- `output/uc/uc-note-*.md`（人读用户路径和任务流）
- `.pmflow/metadata/uc/uc-*.yaml`（机读 metadata）
- `.pmflow/reviews/uc-self-check-*.yaml`（自检结果）

## 不做什么

- 不进入 solution / prototype / prd
- 不自行新增用户角色（必须基于确认的 BRD）
- 完成后只提示 /pm-confirm，不提示下一阶段命令
- 不生成方案或原型

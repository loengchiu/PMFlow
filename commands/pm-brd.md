---
description: "[legacy] 业务需求访谈。梳理原始需求、背景材料、会后回答，产出 BRD note。不进入 uc。"
argument-hint: 可附带需求文本、文档路径或补充说明
---

# pm-brd [legacy]

> **legacy**: 此命令属于旧主链（brd -> uc -> solution -> prototype -> prd），新项目请使用 `/pm-input` 启动新主链。

触发 skill：`brd-interviewer`

## 输入

- PM 提供的原始需求（文本、文档路径或口头描述）
- 背景材料（如有）
- 补充证据（如有）
- `.pmflow/status.yaml`（读取当前状态）

## 输出

- `output/brd/brd-note-*.md`（人读 BRD note）
- `.pmflow/metadata/brd/brd-*.yaml`（机读 metadata）
- `.pmflow/reviews/brd-self-check-*.yaml`（自检结果）

## 不做什么

- 不进入 uc / solution / prototype / prd
- 不自动将背景材料当作会后回答
- 完成后只提示 /pm-confirm，不提示下一阶段命令
- 不生成方案或原型

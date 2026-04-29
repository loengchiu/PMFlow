---
description: 原型设计。基于已确认的 solution，产出 prototype note。不进入 PRD。
argument-hint: 可附带设计规范或交互参考
---

# pm-proto

触发 skill：`prototype-designer`

## 输入

- 已确认的 solution note（`output/solution/` 和 `.pmflow/metadata/solution/`）
- PM 补充材料（设计规范、现有系统截图、交互参考等，如有）
- `.pmflow/status.yaml`（读取当前状态）

## 输出

- `output/prototype/prototype-note-*.md`（人读原型 note）
- `.pmflow/metadata/prototype/prototype-*.yaml`（机读 metadata）

## 不做什么

- 不进入 PRD
- 不自行扩大 solution 范围之外的页面或流程
- 完成后只提示 /pm-proto-review，不提示 /pm-prd 或 /pm-confirm
- 不生成 PRD 内容

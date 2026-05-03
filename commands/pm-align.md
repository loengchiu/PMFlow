---
description: 需求对齐。确认需求理解、建设类型、范围边界、角色场景、业务方向。支持多轮。
argument-hint: 可附带需求方说明、流程图、字段表、截图、规则等补充材料
---

# pm-align

触发 skill：`pm-align`

## 输入

- 已通过 self_check 的 input 产物（`output/input/` 和 `.pmflow/metadata/input/`）
- PM 补充的需求方说明、流程图、字段表、截图、规则等
- `.pmflow/status.yaml`（读取当前状态）

## 输出

- `output/align/align-{timestamp}.md`（人读需求对齐稿）
- `.pmflow/metadata/align/align-{timestamp}.yaml`（机读 metadata）

## 不做什么

- 不生成详细页面清单、字段清单、权限矩阵、状态机
- 不把 PM 假设当需求方确认
- 不把新增材料默认当作已采纳设计
- 完成后只提示 /pm-align-review，不自动进入 /pm-design

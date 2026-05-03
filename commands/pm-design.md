---
description: 详细设计。基于已通过 align-review 的对齐基线构建功能、页面、字段、流程、状态、权限、规则。
argument-hint: 可附带补充说明或设计偏好
---

# pm-design

触发 skill：`pm-design`

## 输入

- 已通过 align-review 的 align 产物（`output/align/` 和 `.pmflow/metadata/align/`）
- `.pmflow/status.yaml`（读取当前状态）
- PM 补充说明（如有）

## 输出

- `output/design/design.md`（人读详细设计主稿，覆盖写入）
- `.pmflow/metadata/design/index.yaml`（机读索引）
- `.pmflow/metadata/design/` 分片 metadata（按对象类型）
- `.pmflow/snapshots/design/design.last-synced.md`（快照）

## 不做什么

- 不重新判断建设类型
- 不重新解释需求方原始材料
- 不把新材料悄悄并入设计
- 不扩大或改变 align 已确认范围
- 完成后只提示 /pm-design-review，不自动进入 /pm-wireframe

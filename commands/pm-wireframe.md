---
description: 线框说明稿。基于 design 产物生成 Markdown 线框说明稿，验证页面结构和跳转。
argument-hint: 可附带重点页面或流程说明
---

# pm-wireframe

触发 skill：`pm-wireframe`

## 输入

- 已通过 design-review 的 design 产物（`output/design/` 和 `.pmflow/metadata/design/`）
- `templates/wireframe.md`（线框说明稿骨架）
- `references/wireframe-writing.md`（写法参考）
- `.pmflow/status.yaml`（读取当前状态）
- PM 补充说明（如有）

## 输出

- `output/wireframe/wireframe.md`（人读线框说明稿，覆盖写入）
- `.pmflow/metadata/wireframe/index.yaml`（机读索引）
- `.pmflow/snapshots/wireframe/wireframe.last-synced.md`（快照）

## 不做什么

- 不扩大或改变 design 已确认范围
- 不生成高保真视觉稿、HTML 原型或图形工具产物
- 不把新材料悄悄并入线框说明稿
- 完成后只提示 /pm-wireframe-review，不自动进入 /pm-prd

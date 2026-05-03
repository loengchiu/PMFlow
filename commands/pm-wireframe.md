---
description: 线框图。基于 design 产物生成页面线框图，暴露页面流转和信息承载问题。
argument-hint: 可附带布局偏好或重点页面说明
---

# pm-wireframe

触发 skill：`pm-wireframe`

## 输入

- 已通过 design-review 的 design 产物（`output/design/` 和 `.pmflow/metadata/design/`）
- `.pmflow/status.yaml`（读取当前状态）
- PM 补充说明（如有）

## 输出

- `output/wireframe/wireframe.md`（人读线框图，覆盖写入）
- `.pmflow/metadata/wireframe/index.yaml`（机读索引）
- `.pmflow/snapshots/wireframe/wireframe.last-synced.md`（快照）

## 不做什么

- 不扩大或改变 design 已确认范围
- 不生成高保真视觉稿（颜色、字体、图标等）
- 不把新材料悄悄并入线框图
- 完成后只提示 /pm-wireframe-review，不自动进入 /pm-prd

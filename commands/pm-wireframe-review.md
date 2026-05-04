---
description: 线框说明稿审查。独立审查线框说明稿是否覆盖 design 核心页面，主流程是否可走通，落点是否完整。
argument-hint: 无参数，直接运行 /pm-wireframe-review
---

# pm-wireframe-review

触发 skill：`pm-wireframe-reviewer`

## 输入

- `output/wireframe/wireframe.md`（人读线框说明稿）
- `.pmflow/metadata/wireframe/index.yaml`（机读索引）
- 对应 design 产物和 metadata（交叉检查）
- `profiles/wireframe.profile.yaml`（审查标准）
- `.pmflow/status.yaml`（读取状态）

## 输出

- `.pmflow/reviews/wireframe-review-*.yaml`（机读审查记录）

## 不做什么

- 不修改线框说明稿文档
- 不在 fail 时提示 /pm-prd
- 不在 pass/warn 时提示 /pm-wireframe 或任何后续命令（只提示 /pm-prd）
- 不代 PM 确认

---
description: 详细设计审查。检查 design 是否基于 align 基线正确建设，ID 和 relations 是否完整。
argument-hint: 无参数
---

# pm-design-review

触发 skill：`pm-design-reviewer`

## 输入

- 最新 design 产物（`output/design/` 和 `.pmflow/metadata/design/`）
- 对应 align 产物（用于交叉检查基线绑定）
- `.pmflow/status.yaml`（读取当前状态）

## 输出

- `.pmflow/reviews/design-review-{timestamp}.yaml`（审查结果）

## 不做什么

- 不复述 writer 的判断
- 不自动进入 /pm-wireframe
- 通过后只建议手动执行 /pm-wireframe

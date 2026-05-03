---
description: 需求对齐审查。检查材料盘点法和需求对齐法是否产生了可靠的 design 输入。
argument-hint: 无参数
---

# pm-align-review

触发 skill：`pm-align-reviewer`

## 输入

- 最新 align 产物（`output/align/` 和 `.pmflow/metadata/align/`）
- 对应 input 产物（用于交叉检查材料登记）
- `.pmflow/status.yaml`（读取当前状态）

## 输出

- `.pmflow/reviews/align-review-{timestamp}.yaml`（审查结果）

## 不做什么

- 不检查章节格式，只检查方法论结果
- 不自动进入 /pm-design
- 通过后只建议手动执行 /pm-design

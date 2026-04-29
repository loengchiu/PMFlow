---
description: PM 显式确认当前阶段产物。不生成新产物，只写回确认状态。
argument-hint: 无参数，直接运行 /pm-confirm
---

# pm-confirm

触发 skill：`pm-confirm`

## 输入

- `.pmflow/status.yaml`（必须存在）
- PM 的自然语言补充（如有，记录到确认备注）

## 输出

- 更新 `.pmflow/status.yaml` 的 `pm_confirmations`、`approved_baselines`、`next_allowed_commands`
- 确认摘要（文本输出）

## 不做什么

- 不生成 BRD / UC / solution / prototype / PRD
- 不执行下一阶段命令、不生成下一阶段产物
- 不在 fail 状态下确认
- 不替 PM 阅读产物

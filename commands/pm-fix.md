---
description: 定向修改。PM 指出某处不合适或要求补充，登记变更并修改相关产物。
argument-hint: 附带修改描述（如"待审批列表详情应跳转新页面，不是展开抽屉"）
---

# pm-fix

触发 skill：`pm-fix`

## 输入

- PM 的修改描述（自然语言）
- `.pmflow/status.yaml`（当前状态）
- 当前阶段相关产物和 metadata

## 输出

- 修改后的相关产物和 metadata（如本轮可安全局部修改）
- `.pmflow/status.yaml` 中 `fix_debts` 追加记录
- `.pmflow/snapshots/` 中的快照更新

## 不做什么

- 不自动进入下一阶段
- 不跳过需要的阶段 review
- 不把 PM 自然语言直接当成已确认 design 事实

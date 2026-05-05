---
name: pm-fix
description: 定向修改。PM 指出某处不合适或要求补充，登记变更、判断影响范围、修改相关产物。
triggers: ["/pm-fix"]
tags: [pmflow, fix, modify]
---

# pm-fix 定向修改 SOP

## 1. 前置读取

执行前必须读取：

- `contracts/review-debt.md`（复查债务契约，变更等级定义）
- `contracts/human-sync.md`（人机同步契约）
- `contracts/snapshot-diff.md`（快照 diff 契约）
- `schemas/status.schema.yaml`（状态 schema）

## 2. 执行顺序

按以下顺序严格执行，不得跳步：

### 步骤 1：读取 status

读取 `.pmflow/status.yaml`。如果文件不存在：停止，提示项目未初始化。

### 步骤 2：检查 uninitialized

如果 `current_stage = uninitialized`：停止，提示项目未初始化。

### 步骤 3：检查 open L5 debt

如果 `fix_debts` 中存在 `status: open` 且 `change_level: L5` 的记录：停止，提示 PM 需求目标/范围/建设类型变化应回到 `/pm-align`。

### 步骤 4：读取 PM 输入

从 PM 的自然语言描述中提取：

- 修改对象（页面、字段、流程、规则、操作、原型交互）
- 修改内容（改成什么、补充什么）
- 涉及阶段（design / wireframe / prd / prototype）

### 步骤 5：读取相关 snapshot

读取 `.pmflow/snapshots/<stage>/<stage>.last-synced.*`，作为 diff 基线。

### 步骤 6：读取当前人读产物

读取 PM 所指阶段的当前人读产物文件。

### 步骤 7：做 diff 判断

- PM 明确描述了修改点时：以 PM 描述为主。
- PM 只说"我改了文档，你同步一下"时：必须用 snapshot diff 找出变更片段。
- **禁止**把当前全文和快照全文同时塞进上下文。

### 步骤 8：定位对象

根据 diff 或 PM 描述定位受影响对象：

- 页面
- 字段
- 流程
- 规则
- 操作
- 原型交互

### 步骤 9：无法定位时停止

无法唯一定位对象时：停止，向 PM 确认。**不得猜**。

### 步骤 10：判断变更等级

按 `contracts/review-debt.md` 判断：

| 等级 | 含义 |
|------|------|
| L1 | 文案、标题、说明补充 |
| L2 | 单页面交互、单字段说明、局部规则 |
| L3 | 新增/删除页面、字段、流程节点、权限规则 |
| L4 | 跨模块主流程、核心业务对象、多个下游产物 |
| L5 | 需求目标、范围、建设类型变化（不按 fix 处理） |

### 步骤 11：判断影响阶段

判断修改影响哪些阶段的产物：

- 仅 wireframe 表达问题 → 影响 wireframe
- design 事实变化 → 影响 design + 下游
- PRD 表达问题 → 影响 prd
- prototype 表达问题 → 影响 prototype

### 步骤 12：L1/L2 局部修改

对 L1/L2 可安全局部修改：

- 修改对应产物文件
- 同步 metadata
- 更新 snapshot
- 写 `sync_status: synced` 或 `partial`

### 步骤 13：L3/L4 处理

对 L3/L4：

- 可以在能明确同步的范围内局部修改。
- 必须登记 `needs_stage_review`。
- 若无法安全同步，只登记 `sync_status: pending`。

### 步骤 14：L5 处理

对 L5：

- 不按 fix 修改。
- 登记债务或提示回到 `/pm-align`。

### 步骤 15：写入 fix_debts

在 `.pmflow/status.yaml` 的 `fix_debts` 中追加记录，完整字段见 §3。

### 步骤 16：输出下一步唯一建议

输出：`下一步唯一建议：/pm-fix-review`

只要本轮写入了 `status: open` 的 fix_debts，下一步唯一建议必须是 `/pm-fix-review`。阶段 review 建议由 `/pm-fix-review` 根据 `needs_stage_review` 输出，/pm-fix 不得直接建议阶段 review。

### 步骤 17：停止

输出修改结果和建议后**必须停止**。不得自动执行任何 review 命令，不得自动进入下一阶段。

## 3. fix_debts 记录格式

```yaml
fix_debts:
  - debt_id: DEBT-{YYYYMMDD}-{序号}
    change_level: L2
    source_stage: wireframe
    affected_stages: [prd, prototype]
    description: PM 修改描述摘要
    affected_objects: [受影响对象 ID 或名称]
    changed_files: [本次实际修改过的人读产物或原型文件]
    metadata_files: [本次同步修改过的 metadata 文件]
    snapshot_files: [本次更新过的 snapshot 文件]
    sync_status: synced | partial | pending | blocked
    needs_stage_review: [wireframe]
    created_at: {ISO 时间}
    status: open
```

`sync_status` 含义：

- `synced`：人读物、metadata、snapshot 已同步。
- `partial`：已修改部分文件，但仍有明确待同步项。
- `pending`：只登记债务，尚未实际修改。
- `blocked`：无法定位对象或属于 L5，不继续执行。

## 4. 输出示例

### L1/L2 局部修改完成

```text
/pm-fix 完成修改或登记债务。

修改对象：{对象}
变更等级：L2
修改内容：{摘要}

产物已更新：
- output/wireframe/wireframe.md
- .pmflow/metadata/wireframe/index.yaml

fix_debts 已登记（1 条 open）。
下一步唯一建议：/pm-fix-review
```

### L3/L4 只登记债务

```text
/pm-fix 完成修改或登记债务。

修改对象：{对象}
变更等级：L3
影响阶段：design, wireframe, prd, prototype

fix_debts 已登记（1 条 open）。
下一步唯一建议：/pm-fix-review
```

## 5. 停止条件

- 输出修改结果和建议后**必须停止**
- 不得自动执行任何 review 命令
- 不得自动进入下一阶段
- 不得提示"要我现在做吗"

## 6. 禁止行为

- 不自动进入下一阶段
- 不跳过需要的阶段 review
- 不把 PM 的自然语言直接当成已确认 design 事实，必须标记来源和影响范围
- 不写 pm_confirmations、approved_baselines、next_allowed_commands
- 不提示 /pm-confirm
- 不在无法唯一定位修改对象时强行修改
- 不直接建议阶段 review（由 /pm-fix-review 根据 needs_stage_review 给出）

---
name: pm-fix
description: 定向修改。PM 指出某处不合适或要求补充，登记变更、判断影响范围、修改相关产物。
triggers: ["/pm-fix"]
tags: [pmflow, fix, modify]
---

# pm-fix 定向修改 SOP

## 1. 前置读取

- `contracts/review-debt.md`（复查债务契约，变更等级定义）
- `contracts/human-sync.md`（人机同步契约）
- `contracts/snapshot-diff.md`（快照 diff 契约）
- `schemas/status.schema.yaml`（状态 schema）
- `.pmflow/status.yaml`（当前状态）
- 当前阶段相关产物和 metadata（根据 PM 描述定位）

## 2. 前置检查

读取 `.pmflow/status.yaml`，确认：

- 存在 `status: open` 的 `fix_debts` 且 `change_level: L5`：停止，提示 PM 需求目标/范围/建设类型变化应回到 /pm-align
- `current_stage` 为 `uninitialized`：停止，提示项目未初始化

## 3. 执行步骤

### 3.1 解析修改描述

从 PM 的自然语言描述中提取：

- 修改对象（页面、字段、流程、规则等）
- 修改内容（改成什么、补充什么）
- 涉及阶段（design / wireframe / prd / prototype）

无法唯一定位修改对象时：停止，向 PM 确认。

### 3.2 定位影响阶段

判断修改影响哪些阶段的产物：

- 仅 wireframe 表达问题（页面布局、导航、落点）→ 影响 wireframe
- design 事实变化（字段、流程、规则、页面增删）→ 影响 design + 下游
- PRD 表达问题（规则描述、异常处理）→ 影响 prd
- prototype 表达问题（交互、布局偏差）→ 影响 prototype

### 3.3 判断变更等级

按 `contracts/review-debt.md` 判断：

| 等级 | 含义 |
|------|------|
| L1 | 文案、标题、说明补充 |
| L2 | 单页面交互、单字段说明、局部规则 |
| L3 | 新增/删除页面、字段、流程节点、权限规则 |
| L4 | 跨模块主流程、核心业务对象、多个下游产物 |
| L5 | 需求目标、范围、建设类型变化（不按 fix 处理） |

L5：停止，建议回到 /pm-align。

### 3.4 执行局部修改

L1/L2 可安全局部修改：

- 修改对应产物文件
- 同步 metadata
- 更新 snapshot

L3/L4：不直接修改产物，只登记债务，建议阶段 review。

### 3.5 写入 fix_debts

在 `.pmflow/status.yaml` 的 `fix_debts` 中追加：

```yaml
fix_debts:
  - debt_id: DEBT-{YYYYMMDD}-{序号}
    change_level: L2
    source_stage: wireframe
    affected_stages: [prd, prototype]
    description: PM 修改描述摘要
    affected_objects: [受影响对象 ID]
    needs_stage_review: [wireframe]
    created_at: {ISO 时间}
    status: open
```

### 3.6 更新快照

修改产物后，同步更新 `.pmflow/snapshots/` 中对应快照。

## 4. 输出规则

只要本轮写入了 `status: open` 的 fix_debts，下一步唯一建议必须是 `/pm-fix-review`。阶段 review 建议由 `/pm-fix-reviewer` 根据 `needs_stage_review` 输出，/pm-fix 不得直接建议阶段 review。

### 4.1 只影响 wireframe 表达（L1/L2 局部修改）

```text
定向修改完成。

修改对象：{对象}
变更等级：L{N}
修改内容：{摘要}

产物已更新：
- output/wireframe/wireframe.md
- .pmflow/metadata/wireframe/index.yaml

fix_debts 已登记（{N} 条 open）。

下一步唯一建议：/pm-fix-review
```

### 4.2 影响 design 事实或其他阶段

```text
定向修改完成。

修改对象：{对象}
变更等级：L{N}
影响阶段：design, wireframe, prd, prototype

fix_debts 已登记（{N} 条 open）。

下一步唯一建议：/pm-fix-review
```

### 4.3 多处修改或跨产物影响

```text
定向修改完成。

修改对象：{对象}
变更等级：L{N}

fix_debts 已登记（{N} 条 open）。

下一步唯一建议：/pm-fix-review
```

## 5. 停止条件

- 输出修改结果和建议后**必须停止**
- 不得自动执行任何 review 命令
- 不得自动进入下一阶段

## 6. 禁止行为

- 不自动进入下一阶段
- 不跳过需要的阶段 review
- 不把 PM 的自然语言直接当成已确认 design 事实，必须标记来源和影响范围
- 不写 pm_confirmations、approved_baselines、next_allowed_commands
- 不提示 /pm-confirm
- 不在无法唯一定位修改对象时强行修改

## 7. 使用示例

```text
用户：/pm-fix
待审批列表中点击详情应该是跳转新页面，而不是展开抽屉。

AI：（解析修改描述，定位到 prototype 层交互偏差）
AI：定向修改完成。
    修改对象：待审批列表-详情操作
    变更等级：L2
    产物已更新：output/prototype/prototype.md
    下一步建议：/pm-prototype-review
```

```text
用户：/pm-fix
"计划类型"字段应该改成枚举，不是自由文本。

AI：（定位到 design 字段定义，影响 design + 下游）
AI：定向修改完成。
    修改对象：FIELD-PLAN-TYPE
    变更等级：L3
    fix_debts 已登记（1 条 open）。
    下一步建议：/pm-design-review
```

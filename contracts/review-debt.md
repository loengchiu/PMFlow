# 复查债务契约

`/pm-fix` 修改后不强制立刻执行阶段 review，但必须记录复查债务。PM 可以连续多次 `/pm-fix`，再执行 `/pm-fix-review` 合并收口。

## 1. 变更等级

| 等级 | 含义 | 处理 |
|---|---|---|
| L1 | 文案、标题、说明补充 | 通常只需 fix-review |
| L2 | 单页面交互、单字段说明、局部规则 | fix-review 后按需阶段 review |
| L3 | 新增/删除页面、字段、流程节点、权限规则 | fix-review 后通常需要对应阶段 review |
| L4 | 跨模块主流程、核心业务对象、多个下游产物 | fix-review 后必须阶段 review |
| L5 | 需求目标、范围、建设类型变化 | 不按 fix 处理，回到 align |

## 2. 债务记录

每次 `/pm-fix` 执行后，必须在 `status.yaml` 的 `fix_debts` 中追加一条记录：

```yaml
fix_debts:
  - debt_id: DEBT-20260503-001
    change_level: L2
    source_stage: design
    affected_stages: [prd, prototype]
    description: 修改"计划类型"字段为枚举
    affected_objects: [FIELD-PLAN-TYPE, PAGE-AUDIT-PLAN-FORM]
    changed_files: [output/design/design.md]
    metadata_files: [.pmflow/metadata/design/index.yaml]
    snapshot_files: [.pmflow/snapshots/design/design.last-synced.md]
    sync_status: synced
    needs_stage_review: [design]
    created_at: 2026-05-03T10:00:00
    status: open
```

## 3. 债务收口

`/pm-fix-review` 负责：

1. 读取所有 `status: open` 的 fix_debts。
2. 合并同阶段 review 债务。
3. 按上游到下游判断仍需哪些阶段 review。
4. 输出待收口项（具体到对象、产物和问题）。
5. 关闭已收口债务（`status: closed`），写 `closed_at` 和 `close_reason`。
6. 给出下一步建议。

## 4. 阶段 review 触发规则

阶段 review 不是每次 fix 后都全量重跑：

- `/pm-fix` 必须做局部变更复查。
- `/pm-fix-review` 必须合并本批变更并收口。
- 只有核心结构变更、影响范围较大、或变更等级要求时，才提示执行对应阶段 review。
- 是否需要阶段 review 必须落到 `fix_debts.needs_stage_review` 里，不能靠 PM 记忆。

## 5. 变更等级判断示例

```text
/pm-fix
待审批列表中点击详情应该是跳转新页面操作，而不是展开抽屉。
```

判断规则：

- 如果上游 design 已定义为跳转页，当前 prototype 做成抽屉：这是 L2 下游偏差修复。
- 如果 design、PRD、prototype 均定义为抽屉，现在改为跳转新页面：这是 L3 设计基线变更。
- 如果"待审批列表"无法唯一定位，必须停止询问。
- 如果需要新增详情页，必须同步 design、wireframe、PRD、prototype 及机读关系。这是 L3+。

## 6. 禁止行为

- 连续多次 `/pm-fix` 后只能逐条 review，不能合并。
- `/pm-fix-review` 只复述变更，不检查同类关联点。
- `/pm-fix-review` 把正常修改循环强制绕到 `/pm-guide`。
- 必须阶段 review 的债务没有落状态，靠 PM 记忆。

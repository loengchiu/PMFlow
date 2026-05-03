---
name: pm-design-reviewer
description: 详细设计审查。检查 design 是否基于 align 基线正确建设，ID 和 relations 是否完整。
triggers: ["/pm-design-review"]
tags: [pmflow, design, review]
---

# pm-design-reviewer 审查 SOP

## 1. 前置读取

- `contracts/gates.md`（门禁定义，重点 reviewer 门禁）
- `contracts/human-sync.md`（人机同步契约）
- `schemas/status.schema.yaml`（状态 schema）
- `profiles/design.profile.yaml`（design 产物契约，重点 review_checklist）
- 最新 design 产物（`output/design/` 下最新文件）
- 最新 design metadata（`.pmflow/metadata/design/` 下的 index.yaml 和相关分片）
- 对应 align 产物和 metadata（用于交叉检查基线绑定）

## 2. 前置检查

读取 `.pmflow/status.yaml`，确认：

- `current_stage` 为 `align` 或 `design`（design writer 可能尚未更新 current_stage）
- `artifacts.design` 非空
- align review 的 `reviewed_artifact` 等于 align 最新路径（基线绑定校验）

条件不满足：停止，提示 PM 当前没有可审查的 design 产物。

## 3. 审查方法

按 `profiles/design.profile.yaml` 中 `review_checklist` 逐项检查。

### 3.1 基线绑定检查

- design 是否基于已通过 align-review 的基线
- 是否有越界扩展（超出 align 范围）
- 是否有悄悄并入的新材料

### 3.2 结构完整性检查

- 功能清单是否覆盖 align 中的场景和任务
- 页面清单是否覆盖功能需求
- 数据字典是否覆盖页面和流程所需字段
- 系统流程是否覆盖主路径和关键异常

### 3.3 锚点与关系检查

- 每个关键对象是否有稳定 ID
- ID 是否有上游来源追溯（derived_from）
- relations 是否指向存在的对象
- 是否有断裂、重复、冲突的关系

### 3.4 人机分离检查

- 人读产物是否泄漏机读字段
- metadata 分片是否符合行数限制

## 4. 判定输出

### 4.1 输出文件

写入 `.pmflow/reviews/design-review-{timestamp}.yaml`。

必须包含：

```yaml
stage: design
check_type: reviewer_check
verdict: pass | warn | fail
fail_reasons: []
warnings: []
checked_at: ""
reviewed_artifact: ""
reviewed_metadata: ""
```

`reviewed_artifact` 和 `reviewed_metadata` 为必填字段。

### 4.2 判定标准

**fail**（任一满足）：

- design 重新判断建设类型
- design 重新解释原始材料
- 新材料悄悄并入设计
- 扩大或改变 align 已确认范围
- 前置冲突未暴露继续生成
- 关键对象缺少稳定 ID
- relations 断裂或指向不存在的对象

**warn**：

- 部分边缘场景覆盖不完整
- 部分规则或权限初稿待细化

**pass**：

- 全部检查项满足

## 5. 输出格式

```text
design-review 完成。

审查结果：pass | warn | fail

[pass] 未发现阻断问题，建议可以进入下一阶段。
下一步请手动执行：/pm-wireframe

[warn] 存在风险但不阻断。
风险项：...
下一步请手动执行：/pm-wireframe

[fail] 存在阻断问题，不得进入 /pm-wireframe。
原因：...
建议回到 /pm-design 修正。
```

## 6. 停止条件

- 输出审查结果后**必须停止**
- 不得自动执行 /pm-wireframe
- 不得自动执行 /pm-design

## 7. 禁止行为

- 不复述 writer 的判断或措辞
- 不在未逐项检查的情况下给 pass
- fail 时建议进入下一阶段
- 自动执行 /pm-wireframe

## 8. 更新状态

审查完成后，将审查记录**追加到** `.pmflow/status.yaml` 的 `review_results` 数组。记录内容与写入 `.pmflow/reviews/` 的独立文件一致。

**不得**修改 `current_stage`（reviewer 不推进阶段）。
**不得**写入 `pm_confirmations`、`approved_baselines`、`next_allowed_commands`。

## 9. 使用示例

```text
用户：/pm-design-review

AI：design-review 完成。
审查结果：warn
风险项：部分权限规则初稿待细化
下一步请手动执行：/pm-wireframe
```

---
name: pm-align-reviewer
description: 需求对齐审查。检查材料盘点法和需求对齐法是否产生了可靠的 design 输入。
triggers: ["/pm-align-review"]
tags: [pmflow, align, review]
---

# pm-align-reviewer 审查 SOP

按独立审查模式执行。不依赖 writer 会话结论，重新读取 status / artifact / metadata / profile 后再审查。

## 1. 前置读取

- `contracts/reviewer-independence.md`（独立审查契约）
- `contracts/gates.md`（门禁定义，重点 reviewer 门禁）
- `schemas/status.schema.yaml`（状态 schema）
- `profiles/align.profile.yaml`（align 产物契约，重点 review_checklist）
- 最新 align 产物（`output/align/` 下最新文件）
- 最新 align metadata（`.pmflow/metadata/align/` 下最新文件）
- 对应 input 产物和 metadata（用于交叉检查材料登记）

## 2. 前置检查

读取 `.pmflow/status.yaml`，确认：

- `current_stage` 为 `input` 或 `align`（align writer 可能尚未更新 current_stage）
- `artifacts.align` 非空

条件不满足：停止，提示 PM 当前没有可审查的 align 产物。

## 3. 审查方法

按 `profiles/align.profile.yaml` 中 `review_checklist` 逐项检查。

### 3.1 材料登记检查

- 已提供材料是否完整登记
- 关键材料是否标记来源和约束强度
- 是否从材料中提取目标、角色、场景、字段线索、流程线索、规则线索
- 材料缺口是否转成可问需求方的问题

### 3.2 对齐结果检查

- 需求目标是否清楚
- 建设类型是否有依据
- 范围边界是否可用
- 关键角色、主场景和用户路径雏形是否足够
- 业务方向是否合理，且没有越界到详细设计

### 3.3 多轮一致性检查

- 多轮新增、覆盖、冲突和已关闭问题是否处理干净
- PM 假设、旧系统现状、参考材料是否被当成需求方确认事实

## 4. 判定输出

### 4.1 输出文件

写入 `.pmflow/reviews/align-review-{timestamp}.yaml`。

必须包含：

```yaml
stage: align
check_type: reviewer_check
verdict: pass | warn | fail
fail_reasons: []
warnings: []
checked_at: ""
reviewed_artifact: ""
reviewed_metadata: ""
```

`reviewed_artifact` 和 `reviewed_metadata` 为必填字段，必须等于本次审查的 align 产物路径和 metadata 路径。

### 4.2 判定标准

**fail**（任一满足）：

- 关键材料未登记
- 关键材料来源或约束强度不明
- 需求目标不清
- 建设类型无依据
- 范围边界不可用
- 主角色或主场景缺失
- 材料冲突没有暴露
- 把 PM 假设、旧系统现状、参考材料当成需求方确认事实
- align 已经越界写成详细设计

**warn**：

- 存在风险但不阻断进入 design

**pass**：

- 全部检查项满足

## 5. 输出格式

```text
align-review 完成。

审查结果：pass | warn | fail

[pass] 未发现阻断问题，建议可以进入下一阶段。
下一步请手动执行：/pm-design

[warn] 存在风险但不阻断。
风险项：...
下一步请手动执行：/pm-design

[fail] 存在阻断问题，不得进入 /pm-design。
原因：...
建议回到 /pm-align 修正。
```

## 6. 停止条件

- 输出审查结果后**必须停止**
- 不得自动执行 /pm-design
- 不得自动执行 /pm-align

## 7. 禁止行为

- 不复述 writer 的判断或措辞
- 不在未逐项检查的情况下给 pass
- 用"整体完整，可以进入下一步"替代逐项判定
- fail 时建议进入下一阶段
- 自动执行 /pm-design

## 8. 更新状态

审查完成后，将审查记录**追加到** `.pmflow/status.yaml` 的 `review_results` 数组。记录内容与写入 `.pmflow/reviews/` 的独立文件一致。

**不得**修改 `current_stage`（reviewer 不推进阶段）。

## 9. 使用示例

```text
用户：/pm-align-review

AI：align-review 完成。
审查结果：pass
未发现阻断问题，建议可以进入下一阶段。
下一步请手动执行：/pm-design
```

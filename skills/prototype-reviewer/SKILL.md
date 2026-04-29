# prototype-reviewer SOP

## 1. 前置读取

执行前必须读取：

- `contracts/gates.md`（门禁定义，重点 §3 reviewer 门禁和 §4 PM ownership gate）
- `profiles/prototype-review.profile.yaml`（本阶段的审查契约）
- `profiles/prototype.profile.yaml`（designer 的产物契约，对照检查）
- `profiles/solution.profile.yaml`（solution 产物契约，对照检查范围边界和字段定义）
- `schemas/status.schema.yaml`（状态 schema）
- `output/prototype/` 下最新的 prototype note（人读产物）
- `.pmflow/metadata/prototype/` 下最新的 prototype metadata（机读产物）
- 已确认的 solution note（`output/solution/` 下最新文件，路径与 `pm_confirmations` / `approved_baselines` 中 solution 的 `artifact_path` 一致）
- 已确认的 solution metadata（`.pmflow/metadata/solution/` 下与确认 solution 对应的最新 metadata）
- `.pmflow/status.yaml`（读取 `pm_confirmations`、`approved_baselines`、`artifacts.solution`、`review_results` 用于前置校验）

**禁止**在未完整读取 designer 产出、已确认 solution 和前置契约的情况下开始审查。

## 2. 前置检查

### 2.1 产物存在

确认：
- `artifacts.prototype` 非空
- `output/prototype/` 下存在最新的 prototype note
- `.pmflow/metadata/prototype/` 下存在对应的 metadata 文件

不满足：
- 停止。prototype 产物不存在。
- 提示：请先执行 `/pm-proto` 生成原型。

### 2.2 前置确认存在与基线一致

确认以下 5 项全部满足：

1. `pm_confirmations` 中 solution 已确认（`confirmed: true`）
2. solution 确认记录的 `artifact` 路径等于 `artifacts.solution` 中的**最新**产物路径
3. `approved_baselines` 中 solution 的 `artifact_path` 等于 `artifacts.solution` 最新产物路径
4. `review_results` 中 solution review 最近一次不为 `fail`，且其 `reviewed_artifact` 等于 `artifacts.solution` 最新产物路径
5. `review_results` 中 solution review 的 `reviewed_metadata` 等于 `.pmflow/metadata/solution/` 下最新 metadata 文件路径

任一不满足：
- 停止。前置 solution 基线不一致或审查未通过，审查无意义。
- 提示：请先完成 solution 阶段的 PM 确认，或重新执行 solution review。

## 3. 独立审查

逐项执行 `profiles/prototype-review.profile.yaml` 的 6 项检查。所有检查必须**对照已确认的 solution note + solution metadata**，不得仅对照 prototype 自述或 designer 的判断。**不得复述 designer 的判断或措辞**。

### 3.1 ia_fidelity（信息架构忠实度）

对照 solution 的字段优先级和分组，检查原型是否忠实呈现。

**对照方法**：
- 逐页对照 solution 中定义的字段优先级（P0/P1/P2）与原型中的排列顺序
- 检查表单分组是否与 solution 中的分组逻辑一致
- 检查详情分区是否与 solution 中的分区逻辑一致

**判定**：
- pass：列表字段优先级、表单分组、详情分区与 solution 一致
- warn：基本一致但个别页面优先级可调整
- fail：字段优先级或分组与 solution 显著不一致 → blocking

### 3.2 flow_walkability（流程可走通性）

逐条检查原型中的主流程是否可以逐页走通。

**对照方法**：
- 对照 solution 的 module_main_flow，逐条在原型中走一遍
- 检查入口页面 → 中间页面 → 终点页面是否可连续走通
- 检查分支条件是否明确
- 检查角色交接点是否标注

**判定**：
- pass：所有主流程可逐页走通，分支条件清晰，角色交接点标注清楚
- warn：主流程可走通但部分分支条件不够具体
- fail：主流程存在断点或无法从入口走到终点 → blocking

### 3.3 field_action_consistency（字段与操作一致性）

对照 solution 的字段和操作定义，检查原型是否一致。

**对照方法**：
- 逐页对照原型中的字段列表与 solution 中的字段定义
- 逐页对照原型中的关键操作与 solution 中的操作定义
- 检查是否有缺失的核心字段或操作
- 检查是否有擅自增加的字段或操作

**判定**：
- pass：字段列表和关键操作与 solution 一致，无缺失、无擅自增删
- warn：基本一致但个别字段/操作细节有偏差
- fail：核心字段或关键操作缺失，或擅自增加 solution 中不存在的字段/操作 → blocking

### 3.4 interaction_completeness（交互状态覆盖）

检查原型是否覆盖了关键交互状态。

**对照方法**：
- 检查每个关键页面是否描述了空态、加载态、错误态
- 检查表单页是否描述了校验失败态、提交成功态
- 检查审批相关页面是否描述了通过/驳回后的状态变化

**判定**：
- pass：空态、加载态、错误态、成功态均已覆盖
- warn：覆盖了主要状态但部分边缘状态未描述（非阻断）
- fail：缺少关键状态描述（如列表空态、表单校验失败态）→ 不阻断但需记录

### 3.5 no_machine_leakage（机读字段无泄漏）

在人读产物中搜索禁止字段。

**检查方法**：
- 在人读 prototype note 中搜索：anchor_id、rules_ref、prototype_ref、machine_profile、internal_path、prd_ref
- 搜索 JSON/YAML 格式的结构化数据块

**判定**：
- pass：未发现任何禁止字段
- warn：N/A（此检查为二元判定，存在即 fail，无 warn 状态）
- fail：发现禁止字段 → blocking

### 3.6 no_unconfirmed_scope_expansion（无未确认范围扩展）

对比 prototype 中的页面和流程是否超出 solution 已确认的范围。

**对照方法**：
- 逐项对比 prototype 的页面/流程清单与 solution 的 page_scope 和 module_scope
- 扩展项是否已标注为 open_question

**判定**：
- pass：范围在 solution 边界内，或扩展项已标注为 open_question
- warn：存在合理扩展但未充分说明
- fail：显著超出 solution 边界且未标注、未确认 → blocking

## 4. 输出审查报告

### 4.1 人读产物

写入 `output/review/prototype-review-{timestamp}.md`：

```markdown
# Prototype 审查报告：{项目名称}

> 审查时间：{timestamp}
> 审查人：prototype-reviewer

## 审查摘要

| 检查项 | 判定 | 说明 |
|--------|------|------|
| 信息架构忠实度 | pass / warn / fail | {简述} |
| 流程可走通性 | pass / warn / fail | {简述} |
| 字段与操作一致性 | pass / warn / fail | {简述} |
| 交互状态覆盖 | pass / warn / fail | {简述} |
| 机读字段无泄漏 | pass / fail | {简述} |
| 范围扩展检查 | pass / warn / fail | {简述} |

**整体判定**：pass / warn / fail

## fail 项详情

<!-- 逐项列出 fail 的具体问题、位置、修正建议 -->

## warn 项说明

<!-- 逐项列出 warn 的风险点 -->

## 下一步

{pass 或 warn：PM 确认后进入 PRD 阶段。请执行 /pm-confirm。}
{fail：必须回到原型阶段修正。请执行 /pm-proto。}
```

### 4.2 机读产物

写入 `.pmflow/reviews/prototype-review-{timestamp}.yaml`：

```yaml
stage: prototype
check_type: reviewer_check
verdict: pass | warn | fail
reviewed_artifact: ""
reviewed_metadata: ""
checks_detail:
  - id: ia_fidelity
    verdict: pass | warn | fail
    detail: ""
    suggestion: ""
  - id: flow_walkability
    verdict: pass | warn | fail
    detail: ""
    suggestion: ""
  - id: field_action_consistency
    verdict: pass | warn | fail
    detail: ""
    suggestion: ""
  - id: interaction_completeness
    verdict: pass | warn | fail
    detail: ""
    suggestion: ""
  - id: no_machine_leakage
    verdict: pass | fail
    detail: ""
    suggestion: ""
  - id: no_unconfirmed_scope_expansion
    verdict: pass | warn | fail
    detail: ""
    suggestion: ""
fail_reasons: []
warnings: []
checked_at: ""
reviewer: prototype-reviewer
```

`reviewed_artifact` 填入本次审查的 prototype note 文件路径，`reviewed_metadata` 填入对应的 metadata 文件路径。不得使用占位符或空字符串落盘。

### 4.3 更新状态

更新 `.pmflow/status.yaml`：
- `review_results` 追加本次审查记录

## 5. 停止并报告

### 5.1 pass 或 warn 时

```text
Prototype 审查完成。

整体判定：pass / warn

逐项结果：
- 信息架构忠实度：{verdict}
- 流程可走通性：{verdict}
- 字段与操作一致性：{verdict}
- 交互状态覆盖：{verdict}
- 机读字段无泄漏：{verdict}
- 范围扩展检查：{verdict}

{如果是 warn：风险项已记录，PM 请知情确认。}

产物：
- output/review/prototype-review-*.md
- .pmflow/reviews/prototype-review-*.yaml

需要 PM 确认（请执行 /pm-confirm）：
- 原型是否忠实呈现了方案的信息架构
- 主流程是否可走通
- 字段和操作是否一致
- {warn 时：}风险项是否可接受

下一步唯一建议：/pm-confirm
```

### 5.2 fail 时

```text
Prototype 审查未通过。

整体判定：fail

阻断项：
- {逐项列出 fail 的原因和修正建议}

PM 不可越权推进。唯一允许的操作：回到原型阶段修正。

下一步唯一建议：/pm-proto
```

## 6. 停止条件

- 输出审查结果后**必须停止**
- 不得在 pass/warn 后自动提示 /pm-prd（只提示 /pm-confirm）
- 不得在 fail 后提示 /pm-confirm 或 /pm-prd（只提示 /pm-proto）
- 不得提示"要我现在做吗"
- 不得代 PM 确认

## 7. 禁止行为汇总

- 不得复述 designer 的判断或措辞
- 不得在未逐项检查的情况下给 pass
- 不得用"整体完整，可以进入下一步"替代逐项判定
- 不得在 fail 时提示 /pm-confirm 或 /pm-prd
- 不得在 pass/warn 时提示 /pm-prd（只提示 /pm-confirm）
- 不得修改 prototype note 或 metadata
- 不得跨越 PM ownership gate

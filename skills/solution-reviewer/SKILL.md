# solution-reviewer SOP [legacy]

> **legacy**: 此 skill 属于旧主链。新项目请使用 `pm-design-reviewer` skill。

## 1. 前置读取

执行前必须读取：

- `contracts/gates.md`（门禁定义，重点 §3 reviewer 门禁和 §4 PM ownership gate）
- `contracts/build-type.md`（建设类型判定契约，对照检查 writer 的判定）
- `profiles/solution-review.profile.yaml`（本阶段的审查契约）
- `profiles/solution.profile.yaml`（writer 的产物契约，对照检查）
- `profiles/brd.profile.yaml`（前置 BRD 契约，对照检查范围边界）
- `profiles/uc.profile.yaml`（前置 UC 契约，对照检查流程覆盖）
- `schemas/status.schema.yaml`（状态 schema）
- `references/solution-writing.md`（判断方案稿写法是否自然、字段和流程是否前置）
- `references/methodology-playbook.md`（判断方法论是否在生成前有效使用）
- `output/solution/` 下最新的 solution note（人读产物）
- `.pmflow/metadata/solution/` 下最新的 solution metadata（机读产物）
- `.pmflow/status.yaml` 中的 `pm_confirmations`（确认 BRD/UC 的 artifact 路径，用于追溯）

**禁止**在未完整读取 writer 产出和前置契约的情况下开始审查。

## 2. 前置检查

### 2.1 产物存在

确认：
- `artifacts.solution` 非空
- `output/solution/` 下存在最新的 solution note
- `.pmflow/metadata/solution/` 下存在对应的 metadata 文件

不满足：
- 停止。solution 产物不存在。
- 提示：请先执行 `/pm-solution` 生成方案。

### 2.2 前置确认存在

确认：
- `pm_confirmations` 中 brd 已确认
- `pm_confirmations` 中 uc 已确认

不满足：
- 停止。前置阶段未确认，审查无意义。
- 提示：请先完成前置阶段的 PM 确认。

## 3. 独立审查

逐项执行 `profiles/solution-review.profile.yaml` 的 6 项检查。**不得复述 writer 的判断或措辞**。

### 3.1 build_type_correctness（建设类型判定正确性）

检查 solution metadata 中 `build_type_evidence` 的四维度判定是否与 BRD 范围一致。

**对照方法**：
- 读取 BRD 的 scope_boundary，确认范围覆盖的模块是否涉及已有系统
- 逐项检查 deploy / code / database / instance 判定是否有依据
- hybrid 时检查是否标注了哪些模块新建、哪些迭代

**判定**：
- pass：四维度判定正确，hybrid 标注清晰
- warn：判定基本正确但个别维度证据不充分
- fail：建设类型明显误判 → blocking

### 3.2 field_coverage（关键字段覆盖）

逐页检查列表/表单字段是否覆盖了 UC 中用户任务所需的决策信息。

**对照方法**：
- 对照 UC 的 task_flows，确认每个关键任务的决策点有对应字段支撑
- 检查列表页字段是否按用户判断优先级排序
- 检查表单页字段是否有分组逻辑

**判定**：
- pass：关键字段覆盖完整，列表字段按用户判断优先级排序
- warn：覆盖基本完整但部分列表字段优先级存疑
- fail：关键页面缺少核心字段 → blocking

### 3.3 flow_coverage（流程覆盖）

检查 `module_main_flow` 和 `page_flow_rules` 是否覆盖了 UC 中的主路径和关键异常路径。

**对照方法**：
- 对照 UC 的 user_journeys，确认每条主路径在 solution 中有对应的 module_main_flow
- 对照 UC 的 edge_cases_and_exceptions，确认关键异常路径已覆盖或标注为 open_question
- 检查提交/通过/驳回的完整口径

**判定**：
- pass：主流程和关键异常路径完整，有提交/通过/驳回的完整口径
- warn：主流程完整但部分异常路径未覆盖
- fail：主流程缺失关键步骤或审批口径不完整 → blocking

### 3.4 information_architecture_quality（信息架构质量）

检查列表页字段是否按用户判断优先级排序，表单字段是否有合理分组。

**对照方法**：
- 检查列表页字段排序是否符合 UC 中用户角色的决策优先级
- 检查表单字段分组是否对应 UC 中任务流的步骤

**判定**：
- pass：列表页信息优先级合理，表单字段分组清晰
- warn：基本合理但个别页面信息优先级可优化（非阻断）
- fail：列表页几十个字段无优先级或表单字段无分组 → 不阻断但需记录

### 3.5 no_machine_leakage（机读字段无泄漏）

在人读产物中搜索禁止字段。

**检查方法**：
- 在人读 solution note 中搜索：anchor_id、rules_ref、prototype_ref、machine_profile、internal_path
- 搜索 JSON/YAML 格式的结构化数据块

**判定**：
- pass：未发现任何禁止字段
- warn：N/A（此检查为二元判定，存在即 fail，无 warn 状态）
- fail：发现禁止字段 → blocking

### 3.6 no_unconfirmed_scope_expansion（无未确认范围扩展）

对比 solution 中的 page_scope 和 module_scope 是否超出 BRD 的范围边界。

**对照方法**：
- 逐项对比 solution 的模块/页面清单与 BRD 的 scope_boundary
- 扩展项是否已标注为 open_question

**判定**：
- pass：范围在 BRD 边界内，或扩展项已标注为 open_question
- warn：存在合理扩展但未充分说明
- fail：显著超出 BRD 边界且未标注、未确认 → blocking

## 4. 输出审查报告

### 4.1 人读产物

写入 `output/review/solution-review-{timestamp}.md`：

```markdown
# Solution 审查报告：{项目名称}

> 审查时间：{timestamp}
> 审查人：solution-reviewer

## 审查摘要

| 检查项 | 判定 | 说明 |
|--------|------|------|
| 建设类型判定 | pass / warn / fail | {简述} |
| 关键字段覆盖 | pass / warn / fail | {简述} |
| 流程覆盖 | pass / warn / fail | {简述} |
| 信息架构质量 | pass / warn / fail | {简述} |
| 机读字段无泄漏 | pass / fail | {简述} |
| 范围扩展检查 | pass / warn / fail | {简述} |

**整体判定**：pass / warn / fail

## fail 项详情

<!-- 逐项列出 fail 的具体问题、位置、修正建议 -->

## warn 项说明

<!-- 逐项列出 warn 的风险点 -->

## 下一步

{pass 或 warn：PM 确认后进入原型阶段。请执行 /pm-confirm。}
{fail：必须回到方案阶段修正。请执行 /pm-solution。}
```

### 4.2 机读产物

写入 `.pmflow/reviews/solution-review-{timestamp}.yaml`：

```yaml
stage: solution
check_type: reviewer_check
verdict: pass | warn | fail
reviewed_artifact: ""
reviewed_metadata: ""
checks_detail:
  - id: build_type_correctness
    verdict: pass | warn | fail
    detail: ""
    suggestion: ""
  - id: field_coverage
    verdict: pass | warn | fail
    detail: ""
    suggestion: ""
  - id: flow_coverage
    verdict: pass | warn | fail
    detail: ""
    suggestion: ""
  - id: information_architecture_quality
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
reviewer: solution-reviewer
```

`reviewed_artifact` 填入本次审查的 solution note 文件路径，`reviewed_metadata` 填入对应的 metadata 文件路径。不得使用占位符或空字符串落盘。

### 4.3 更新状态

更新 `.pmflow/status.yaml`：
- `review_results` 追加本次审查记录

## 5. 停止并报告

### 5.1 pass 或 warn 时

```text
Solution 审查完成。

整体判定：pass / warn

逐项结果：
- 建设类型判定：{verdict}
- 关键字段覆盖：{verdict}
- 流程覆盖：{verdict}
- 信息架构质量：{verdict}
- 机读字段无泄漏：{verdict}
- 范围扩展检查：{verdict}

{如果是 warn：风险项已记录，PM 请知情确认。}

产物：
- output/review/solution-review-*.md
- .pmflow/reviews/solution-review-*.yaml

需要 PM 确认（请执行 /pm-confirm）：
- 方案是否满足业务目标
- 建设类型判定是否认可
- 字段和流程是否覆盖完整
- {warn 时：}风险项是否可接受

下一步唯一建议：/pm-confirm
```

### 5.2 fail 时

```text
Solution 审查未通过。

整体判定：fail

阻断项：
- {逐项列出 fail 的原因和修正建议}

PM 不可越权推进。唯一允许的操作：回到方案阶段修正。

下一步唯一建议：/pm-solution
```

## 6. 停止条件

- 输出审查结果后**必须停止**
- 不得在 pass/warn 后自动提示 /pm-proto（只提示 /pm-confirm）
- 不得在 fail 后提示 /pm-confirm 或 /pm-proto（只提示 /pm-solution）
- 不得提示"要我现在做吗"
- 不得代 PM 确认

## 7. 禁止行为汇总

- 不得复述 writer 的判断或措辞
- 不得在未逐项检查的情况下给 pass
- 不得用"整体完整，可以进入下一步"替代逐项判定
- 不得在 fail 时提示 /pm-confirm 或 /pm-proto
- 不得在 pass/warn 时提示 /pm-proto（只提示 /pm-confirm）
- 不得修改 solution note 或 metadata
- 不得跨越 PM ownership gate

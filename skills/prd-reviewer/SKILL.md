# prd-reviewer SOP [legacy]

> **适用范围**：仅 legacy 主链（brd→uc→solution→prototype→prd）。新主链 PRD review 由 `pm-prd-reviewer` skill 处理。

## 1. 前置读取

执行前必须读取：

- `contracts/gates.md`（门禁定义，重点 §3 reviewer 门禁和 §4 PM ownership gate）
- `profiles/prd-review.profile.yaml`（本阶段的审查契约）
- `profiles/prd.profile.yaml`（writer 的产物契约，对照检查）
- `profiles/prototype.profile.yaml`（prototype 产物契约，对照检查字段和流程）
- `profiles/solution.profile.yaml`（solution 产物契约，对照检查业务规则范围）
- `profiles/uc.profile.yaml`（UC 产物契约，对照检查用户任务覆盖）
- `profiles/brd.profile.yaml`（BRD 产物契约，对照检查业务目标覆盖）
- `schemas/status.schema.yaml`（状态 schema）
- `references/prd-writing.md`（判断 PRD 文风、归档质量和字段落地）
- `references/writing-principles.md`（判断是否存在模板感或 AI 味）
- `output/prd/` 下最新的 PRD 文档（人读产物）
- `.pmflow/metadata/prd/` 下最新的 PRD metadata（机读产物）
- 已确认的 prototype note（路径来自 `pm_confirmations` 中 prototype 的 `artifact` / `approved_baselines` 中 prototype 的 `artifact_path`，不得仅取目录最新文件）
- 已确认的 prototype metadata（路径来自 `review_results` 中 prototype review 的 `reviewed_metadata`）
- 已确认的 solution note（路径来自 `pm_confirmations` 中 solution 的 `artifact` / `approved_baselines` 中 solution 的 `artifact_path`）
- 已确认的 solution metadata（路径来自 `review_results` 中 solution review 的 `reviewed_metadata`）
- 已确认的 UC note（路径来自 `pm_confirmations` 中 uc 的 `artifact` / `approved_baselines` 中 uc 的 `artifact_path`）
- 已确认的 UC metadata（路径来自 `review_results` 中 uc self-check 的 `reviewed_metadata`）
- 已确认的 BRD note（路径来自 `pm_confirmations` 中 brd 的 `artifact` / `approved_baselines` 中 brd 的 `artifact_path`）
- 已确认的 BRD metadata（路径来自 `review_results` 中 brd self-check 的 `reviewed_metadata`）
- `.pmflow/status.yaml`（读取 `pm_confirmations`、`approved_baselines`、`artifacts`、`review_results` 用于全前置基线校验）

**禁止**在未完整读取 writer 产出、已确认 prototype 和全部前置基线（BRD/UC/solution/prototype）的情况下开始审查。所有前置产物的读取路径必须来自基线绑定，不得仅取目录最新文件。

## 2. 前置检查

### 2.1 产物存在

确认：
- `artifacts.prd` 非空
- `output/prd/` 下存在最新的 PRD 文档
- `.pmflow/metadata/prd/` 下存在对应的 metadata 文件

不满足：
- 停止。PRD 产物不存在。
- 提示：请先执行 `/pm-prd` 生成 PRD。

### 2.2 前置确认存在与基线一致

对 **brd、uc、solution、prototype** 四个前置阶段，每个阶段必须独立校验以下 6 项：

1. `pm_confirmations` 中存在该阶段且 `confirmed: true`
2. 确认记录的 `artifact` 路径等于 `artifacts.<stage>` 中的**最新**产物路径
3. `approved_baselines` 中该阶段的 `artifact_path` 等于 `artifacts.<stage>` 最新产物路径
4. `review_results` 中该阶段最近一次检查不为 `fail`（brd/uc 为 self_check，solution/prototype 为 reviewer_check）
5. `review_results` 中该阶段检查的 `reviewed_artifact` 等于 `artifacts.<stage>` 最新产物路径
6. `review_results` 中该阶段检查的 `reviewed_metadata` 等于该阶段最新 metadata 文件路径

任一阶段、任一条件不满足：
- 停止。提示具体哪个前置阶段的基线不一致或审查未通过。
- 提示：请先完成对应阶段的 PM 确认或重新审查，或执行 `/pm-guide` 查看状态。

## 3. 独立审查

逐项执行 `profiles/prd-review.profile.yaml` 的 7 项检查。所有检查必须**对照已确认的 BRD/UC/solution/prototype note + metadata（四个阶段的已确认基线）**，不得仅对照 PRD 自述或 writer 的判断。**不得复述 writer 的判断或措辞**。

### 3.1 prd_independent_archive_quality（PRD 独立归档质量）

检查 PRD 是否可作为独立文档归档——不依赖阅读 BRD/UC/solution/prototype 即可完整理解需求。

**对照方法**：
- 假设读者未读过任何前置产物，逐节检查 PRD 是否自包含
- 检查是否存在"详见 BRD""参考 UC""参见原型"等跨文档引用
- 检查核心概念是否在 PRD 本体中有定义

**判定**：
- pass：PRD 内容自包含，阅读者无需查阅前置产物即可理解全部需求
- warn：基本自包含但个别概念需参考前置文档
- fail：PRD 大量引用前置产物且未在本体展开说明，无法独立阅读 → blocking

### 3.2 no_push_back_to_prototype（无回退到原型阶段的内容）

检查 PRD 是否包含应属于 prototype 阶段的界面描述、交互细节、页面布局说明。

**对照方法**：
- 搜索 UI 布局描述（"顶部""左侧""右侧""底部""按钮位置"等）
- 搜索交互细节（"点击后弹出""hover 显示""展开动画"等）
- 搜索视觉描述（"颜色""图标""间距"等）

**判定**：
- pass：未发现原型阶段内容
- warn：存在少量交互说明但不影响 PRD 定位
- fail：大面积出现界面描述、交互细节等原型阶段内容 → blocking

### 3.3 field_dictionary_consistency（数据字典与字段一致性）

对照 prototype 和 solution 的字段定义，检查 PRD 数据字典是否与各页面字段清单一致。

**对照方法**：
- 逐字段对比数据字典与各页面字段清单（名称、类型、必填、校验规则）
- 检查数据字典是否遗漏了某些页面中的字段
- 检查数据字典中的字段是否都在页面字段清单中出现

**判定**：
- pass：数据字典字段与各页面字段清单完全一致，无遗漏、无矛盾
- warn：基本一致但个别字段细节可对齐
- fail：数据字典与页面字段存在矛盾或遗漏核心字段 → blocking

### 3.4 action_rule_exception_permission_coverage（操作/规则/异常/权限覆盖）

检查 PRD 的业务规则、异常规则、权限规则是否完整覆盖了 solution 和 prototype 中定义的操作和流程。

**对照方法**：
- 逐操作检查是否有对应的业务规则覆盖
- 逐流程检查异常路径是否在异常规则中体现
- 逐角色检查权限矩阵是否覆盖了所有页面和操作

**判定**：
- pass：业务规则、异常处理、权限矩阵完整覆盖所有关键操作和流程
- warn：主流程覆盖完整但部分边缘规则待补充
- fail：缺少核心业务规则或权限矩阵 → blocking

### 3.5 acceptance_criteria_quality（验收标准质量）

检查验收标准是否可测试、可判断。

**对照方法**：
- 逐条检查验收标准是否有前置条件、操作步骤、预期结果
- 检查是否覆盖了 BRD 中定义的业务目标
- 检查是否覆盖了 UC 中的关键用户任务
- 检查是否覆盖了 solution 中的关键异常路径

**判定**：
- pass：每条验收标准可独立测试，覆盖正常路径和关键异常路径
- warn：验收标准基本可测但部分边界条件未覆盖
- fail：验收标准模糊、不可测，或遗漏关键场景 → blocking

### 3.6 no_machine_leakage（机读字段无泄漏）

在人读产物中搜索禁止字段。

**检查方法**：
- 在人读 PRD 文档中搜索：anchor_id、rules_ref、prototype_ref、machine_profile、internal_path、prd_ref
- 搜索 JSON/YAML 格式的结构化数据块

**判定**：
- pass：未发现任何禁止字段
- warn：N/A（此检查为二元判定，存在即 fail，无 warn 状态）
- fail：发现禁止字段 → blocking

### 3.7 source_trace_completeness（来源追溯完整）

检查 PRD 内容的 source_trace 是否覆盖了全部四个前置阶段的已确认基线。

**对照方法**：
- 检查 PRD metadata 中 source_trace 是否包含 brd/uc/solution/prototype 四个来源
- 抽查关键内容（核心字段、主流程、关键规则）的来源追溯是否准确

**判定**：
- pass：所有 PRD 内容均可追溯到至少一个已确认前置基线
- warn：大部分可追溯但个别内容来源标注不完整（非阻断）
- fail：source_trace 缺失、未覆盖 brd/uc/solution/prototype、或大量 PRD 内容无法追溯 → blocking

## 4. 输出审查报告

### 4.1 人读产物

写入 `output/review/prd-review-{timestamp}.md`：

```markdown
# PRD 审查报告：{项目名称}

> 审查时间：{timestamp}
> 审查人：prd-reviewer

## 审查摘要

| 检查项 | 判定 | 说明 |
|--------|------|------|
| PRD 独立归档质量 | pass / warn / fail | {简述} |
| 无原型阶段内容 | pass / warn / fail | {简述} |
| 数据字典一致性 | pass / warn / fail | {简述} |
| 规则/异常/权限覆盖 | pass / warn / fail | {简述} |
| 验收标准质量 | pass / warn / fail | {简述} |
| 机读字段无泄漏 | pass / fail | {简述} |
| 来源追溯完整 | pass / warn / fail | {简述} |

**整体判定**：pass / warn / fail

## fail 项详情

<!-- 逐项列出 fail 的具体问题、位置、修正建议 -->

## warn 项说明

<!-- 逐项列出 warn 的风险点 -->

## 下一步

{pass 或 warn：PM 确认后 PRD 归档（主链路完成）。请执行 /pm-confirm。}
{fail：必须回到 PRD 阶段修正。请执行 /pm-prd。}
```

### 4.2 机读产物

写入 `.pmflow/reviews/prd-review-{timestamp}.yaml`：

```yaml
stage: prd
check_type: reviewer_check
verdict: pass | warn | fail
reviewed_artifact: ""
reviewed_metadata: ""
checks_detail:
  - id: prd_independent_archive_quality
    verdict: pass | warn | fail
    detail: ""
    suggestion: ""
  - id: no_push_back_to_prototype
    verdict: pass | warn | fail
    detail: ""
    suggestion: ""
  - id: field_dictionary_consistency
    verdict: pass | warn | fail
    detail: ""
    suggestion: ""
  - id: action_rule_exception_permission_coverage
    verdict: pass | warn | fail
    detail: ""
    suggestion: ""
  - id: acceptance_criteria_quality
    verdict: pass | warn | fail
    detail: ""
    suggestion: ""
  - id: no_machine_leakage
    verdict: pass | fail
    detail: ""
    suggestion: ""
  - id: source_trace_completeness
    verdict: pass | warn | fail
    detail: ""
    suggestion: ""
fail_reasons: []
warnings: []
checked_at: ""
reviewer: prd-reviewer
```

`reviewed_artifact` 填入本次审查的 PRD 文档路径，`reviewed_metadata` 填入对应的 PRD metadata 文件路径。不得使用占位符或空字符串落盘。

### 4.3 更新状态

更新 `.pmflow/status.yaml`：
- `review_results` 追加本次审查记录

## 5. 停止并报告

### 5.1 pass 或 warn 时

```text
PRD 审查完成。

整体判定：pass / warn

逐项结果：
- PRD 独立归档质量：{verdict}
- 无原型阶段内容：{verdict}
- 数据字典一致性：{verdict}
- 规则/异常/权限覆盖：{verdict}
- 验收标准质量：{verdict}
- 机读字段无泄漏：{verdict}
- 来源追溯完整：{verdict}

{如果是 warn：风险项已记录，PM 请知情确认。}

产物：
- output/review/prd-review-*.md
- .pmflow/reviews/prd-review-*.yaml

需要 PM 确认（请执行 /pm-confirm）：
- PRD 是否可作为独立归档文档
- 数据字典是否与页面字段一致
- 规则/异常/权限是否完整
- 验收标准是否可测试
- {warn 时：}风险项是否可接受

确认后 PRD 归档，主链路完成。

下一步唯一建议：/pm-confirm
```

### 5.2 fail 时

```text
PRD 审查未通过。

整体判定：fail

阻断项：
- {逐项列出 fail 的原因和修正建议}

PM 不可越权推进。唯一允许的操作：回到 PRD 阶段修正。

下一步唯一建议：/pm-prd
```

## 6. 停止条件

- 输出审查结果后**必须停止**
- 不得在 pass/warn 后提示 /pm-prd 或任何后续命令（只提示 /pm-confirm）
- 不得在 fail 后提示 /pm-confirm（只提示 /pm-prd）
- 不得提示"要我现在做吗"
- 不得代 PM 确认
- 不得提示归档、review-pack、export 或任何主链路之后的阶段

## 7. 禁止行为汇总

- 不得复述 writer 的判断或措辞
- 不得在未逐项检查的情况下给 pass
- 不得用"整体完整，可以进入下一步"替代逐项判定
- 不得在 fail 时提示 /pm-confirm 或任何后续命令
- 不得在 pass/warn 时提示 /pm-prd 或任何后续阶段命令（只提示 /pm-confirm）
- 不得修改 PRD 文档或 metadata
- 不得跨越 PM ownership gate
- 不得提示主链路之后的任何阶段（fix/change/review-pack/export）

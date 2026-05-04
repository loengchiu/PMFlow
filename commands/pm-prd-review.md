---
description: PRD 审查。新主链独立审查归档质量、字段一致性、规则覆盖 / legacy 主链独立审查 PRD 文档。
argument-hint: 无参数，直接运行 /pm-prd-review
---

# pm-prd-review

## workflow_mode 分流

读取 `.pmflow/status.yaml` 中的 `workflow_mode`：

- `workflow_mode: new_main` → 触发 skill：`pm-prd-reviewer`
- `workflow_mode: legacy` → 触发 skill：`prd-reviewer`
- `workflow_mode` 缺失时，按 `contracts/new-main-chain.md` §4 推断

### 新主链（new_main）

触发 skill：`pm-prd-reviewer`。

#### 输入

- `output/prd/prd.md`（人读 PRD）
- `.pmflow/metadata/prd/`（机读 metadata）
- design / wireframe 的必要 metadata（交叉检查）
- `profiles/prd-review-new-main.profile.yaml`（审查标准）
- `profiles/prd-new-main.profile.yaml`（PRD 契约，对照检查）
- `.pmflow/status.yaml`（当前状态）

#### 输出

- `.pmflow/reviews/prd-review-{timestamp}.yaml`（机读审查记录）
- `.pmflow/status.yaml` 中 `review_results` 追加记录

#### 不做什么

- 不修改 PRD 文档或 metadata
- 不修改 current_stage
- 不写 pm_confirmations、approved_baselines、next_allowed_commands
- pass/warn 只提示 /pm-prototype
- fail 只提示 /pm-prd 或建议 /pm-fix
- 不提示 /pm-confirm

### legacy 主链

触发 skill：`prd-reviewer`，原有逻辑不变。

#### 输入

- `output/prd/prd-*.md`（人读 PRD）
- `.pmflow/metadata/prd/prd-*.yaml`（机读 PRD metadata）
- 已确认的 prototype note + metadata
- 已确认的 solution note + metadata（对照字段和流程一致性）
- 已确认的 UC note + metadata（对照用户任务覆盖）
- 已确认的 BRD note + metadata（对照业务目标覆盖）
- `profiles/prd-review.profile.yaml`（审查标准）
- `profiles/prd.profile.yaml`（PRD 契约，对照检查）
- `.pmflow/status.yaml`（读取前置基线）

#### 输出

- `output/review/prd-review-*.md`（人读审查报告）
- `.pmflow/reviews/prd-review-*.yaml`（机读审查记录）

#### 不做什么

- 不修改 PRD 文档
- 不在 fail 时提示 /pm-confirm 或任何后续命令
- 不在 pass/warn 时提示任何后续阶段命令（只提示 /pm-confirm）
- 不代 PM 确认

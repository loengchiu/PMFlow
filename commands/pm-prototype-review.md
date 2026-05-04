---
description: 原型审查。新主链检查页面覆盖、字段覆盖、动作覆盖、流程走通、UI 一致性 / legacy 主链不适用。
argument-hint: 无参数，直接运行 /pm-prototype-review
---

# pm-prototype-review

## workflow_mode 分流

读取 `.pmflow/status.yaml` 中的 `workflow_mode`：

- `workflow_mode: new_main` → 触发 skill：`pm-prototype-reviewer`
- `workflow_mode: legacy` → 不适用，legacy 主链无原型审查阶段
- `workflow_mode` 缺失时，按 `contracts/new-main-chain.md` §4 推断

### 新主链（new_main）

触发 skill：`pm-prototype-reviewer`。

#### 输入

- `output/prototype/index.html`（HTML 原型）
- `.pmflow/metadata/prototype/index.yaml`（原型 metadata）
- `output/prd/prd.md`（人读 PRD，交叉检查）
- `.pmflow/metadata/prd/dictionary.yaml`（字段主定义，交叉检查）
- `.pmflow/metadata/prd/pages/*.yaml`（页面 metadata，交叉检查）
- `output/wireframe/wireframe.md`（线框图，交叉检查）
- `references/prototype-ui-style.md`（UI 风格参考）
- `.pmflow/status.yaml`（当前状态）

#### 输出

- `.pmflow/reviews/prototype-review-{timestamp}.yaml`（机读审查记录）
- `.pmflow/status.yaml` 中 `review_results` 追加记录

#### 不做什么

- 不修改原型文件或 metadata
- 不修改 current_stage
- 不写 pm_confirmations、approved_baselines、next_allowed_commands
- pass/warn 只提示主链路完成，如需修改执行 /pm-fix
- fail 只提示 /pm-prototype 或建议 /pm-fix
- 不提示 /pm-confirm

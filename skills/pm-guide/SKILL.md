# pm-guide SOP

## 1. 前置读取

执行前必须读取：

- `contracts/gates.md`（门禁定义）
- `contracts/confirmation.md`（确认契约）
- `schemas/status.schema.yaml`（状态 schema）

**禁止**读取任何项目业务文件（文档、代码、配置）。

## 2. 状态检测

### 2.1 `.pmflow/status.yaml` 不存在

项目未初始化。

**输出**：

- 状态：未初始化
- 下一步唯一建议：`/pm-brd`
- 提示：请提供原始需求输入（文本、文档路径、或口头描述）

**不操作**：

- 不自动创建 `.pmflow/` 目录
- 不自动创建 `status.yaml`
- 不读取项目目录下的任何业务文件充当需求

### 2.2 `.pmflow/status.yaml` 存在

读取 `status.yaml`，按以下顺序判断。

## 3. 状态判断逻辑

判定优先级（从高到低）：**fail > 未执行 > 未自检/review > 未确认 > 已确认可推进**。

判断"pm_confirmations 中 X 已确认"时，必须同时满足以下条件，否则视为**未确认**：

1. `pm_confirmations` 中存在对应 stage 且 `confirmed: true`
2. 确认记录的 `artifact` 路径等于 `artifacts.<stage>` 中的**最新**产物路径（数组最后一条记录）
3. `approved_baselines` 中存在对应 stage 且 `artifact_path` 等于最新产物路径

条件 2 不满足 → 产物在确认后被重新生成，旧确认已失效。
条件 3 不满足 → 基线记录缺失，确认链路不完整。

以上任一不满足时，判定为"未确认"，推荐 `/pm-confirm`。满足全部条件时，判定为"已确认可推进"。

```
读取 current_stage
  │
  ├── uninitialized
  │     └─ 推荐 /pm-brd
  │
  ├── brd
  │   ├── review_results 中 brd 自检为 fail
  │   │   └─ 推荐回到 /pm-brd（fail 阻断，不可跳过）
  │   ├── artifacts.brd 为空
  │   │   └─ brd-interviewer 尚未执行，推荐 /pm-brd
  │   ├── review_results 中无 brd 自检记录
  │   │   └─ brd note 已产出但未自检，推荐 /pm-brd（重新执行含自检）
  │   ├── pm_confirmations 中 brd 未确认
  │   │   └─ 推荐 /pm-confirm
  │   └── pm_confirmations 中 brd 已确认（且 artifact 与最新产物一致）
  │       └─ 推荐 /pm-uc
  │
  ├── uc
  │   ├── review_results 中 uc 自检为 fail
  │   │   └─ 推荐回到 /pm-uc（fail 阻断，不可跳过）
  │   ├── artifacts.uc 为空
  │   │   └─ uc-interviewer 尚未执行，推荐 /pm-uc
  │   ├── review_results 中无 uc 自检记录
  │   │   └─ uc note 已产出但未自检，推荐 /pm-uc（重新执行含自检）
  │   ├── pm_confirmations 中 uc 未确认
  │   │   └─ 推荐 /pm-confirm
  │   └── pm_confirmations 中 uc 已确认（且 artifact 与最新产物一致）
  │       └─ 推荐 /pm-solution
  │
  ├── solution
  │   ├── review_results 中 solution review 为 fail
  │   │   └─ 推荐回到 /pm-solution（fail 阻断，PM 不可越权）
  │   ├── artifacts.solution 为空
  │   │   └─ solution-writer 尚未执行，推荐 /pm-solution
  │   ├── review_results 中无 solution review 记录
  │   │   └─ solution 已产出，推荐 /pm-solution-review
  │   ├── pm_confirmations 中 solution 未确认
  │   │   └─ 推荐 /pm-confirm
  │   └── pm_confirmations 中 solution 已确认（且 artifact 与最新产物一致）
  │       └─ 推荐 /pm-proto
  │
  ├── prototype
  │   ├── review_results 中 prototype review 为 fail
  │   │   └─ 推荐回到 /pm-proto（fail 阻断，PM 不可越权）
  │   ├── artifacts.prototype 为空
  │   │   └─ prototype-designer 尚未执行，推荐 /pm-proto
  │   ├── review_results 中无 prototype review 记录
  │   │   └─ prototype 已产出，推荐 /pm-proto-review
  │   ├── pm_confirmations 中 prototype 未确认
  │   │   └─ 推荐 /pm-confirm
  │   └── pm_confirmations 中 prototype 已确认（且 artifact 与最新产物一致）
  │       └─ 推荐 /pm-prd
  │
  └── prd
      ├── review_results 中 prd review 为 fail
      │   └─ 推荐回到 /pm-prd（fail 阻断，PM 不可越权）
      ├── artifacts.prd 为空
      │   └─ prd-writer 尚未执行，推荐 /pm-prd
      ├── review_results 中无 prd review 记录
      │   └─ PRD 已产出，推荐 /pm-prd-review
      ├── pm_confirmations 中 prd 未确认
      │   └─ 推荐 /pm-confirm
      └── pm_confirmations 中 prd 已确认（且 artifact 与最新产物一致）
          └─ 主链路完成，PRD 可归档。如需修改用后续 fix/change 命令。
```

注意：solution/prototype/prd 的 warn 状态不单独分支——warn 不阻断审查通过，review 为 warn 时审查已通过，然后走"未确认 → /pm-confirm"路径。PM 在 /pm-confirm 中看到 warn 记录并知情确认。

## 4. 输出格式

```text
项目状态：[uninitialized | 阶段名]
当前阶段：[阶段名]

已有产物：
- output/brd/*.md（已确认）
- output/uc/*.md（已确认）
- ...

待处理：
- reviewer 阻断：solution review fail（原因：...）
- 待 PM 确认：solution（output/solution/*.md）
- 未解决问题：3 个

下一步唯一建议：/pm-solution-review

不能自动推进的原因：solution review 未通过，必须修正后重新审查。
```

## 5. 停止条件

- 输出状态判断和建议后**必须停止**
- 不得在 guide 之后自动执行为下一步推荐的命令
- 不得询问"要我帮你执行吗"
- 只输出"下一步唯一建议：/pm-xxx"

## 6. 禁止行为

- 不得在没有 `.pmflow/status.yaml` 时扫描项目文件充当需求
- 不得自动创建状态文件
- 不得推荐跳过阶段的路径（如 brd 未确认时推荐 solution）
- 不得同时推荐多个下一步（只输出"唯一"建议）
- 不得在 guide 中包含任何业务分析或需求判断

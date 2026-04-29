# pm-guide SOP

## 1. 前置读取

执行前必须读取：

- `contracts/gates.md`（门禁定义）
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

按优先级依次判断：

```
读取 current_stage
  │
  ├── uninitialized
  │     └─ 推荐 /pm-brd
  │
  ├── brd
  │   ├── pm_confirmations 中无 brd 确认记录
  │   │   ├── artifacts.brd 为空 → brd-interviewer 尚未执行或未产出
  │   │   └── artifacts.brd 非空 → brd note 已产出，等待 PM 确认
  │   ├── pm_confirmations 中 brd 已确认
  │   │   └─ 推荐 /pm-uc
  │   └── review_results 中 brd 自检 fail
  │       └─ 推荐回到 /pm-brd（补充输入后重新执行）
  │
  ├── uc
  │   ├── pm_confirmations 中无 uc 确认记录
  │   │   ├── artifacts.uc 为空 → uc-interviewer 尚未执行
  │   │   └── artifacts.uc 非空 → uc note 已产出，等待 PM 确认
  │   ├── pm_confirmations 中 uc 已确认
  │   │   └─ 推荐 /pm-solution
  │   └── review_results 中 uc 自检 fail
  │       └─ 推荐回到 /pm-uc（补充输入后重新执行）
  │
  ├── solution
  │   ├── artifacts.solution 为空 → solution-writer 尚未执行
  │   │   └─ 推荐 /pm-solution
  │   ├── review_results 中无 solution review 记录
  │   │   └─ solution 已产出，推荐 /pm-solution-review
  │   ├── review_results 中 solution review 为 fail
  │   │   └─ 推荐回到 /pm-solution（根据 review 修正）
  │   ├── review_results 中 solution review 为 warn
  │   │   └─ 推荐 PM 确认风险后决定 /pm-proto 或回到 /pm-solution
  │   ├── review_results 中 solution review 为 pass
  │   │   └─ pm_confirmations 中无 solution 确认 → 等待 PM 确认
  │   └── pm_confirmations 中 solution 已确认
  │       └─ 推荐 /pm-proto
  │
  ├── prototype
  │   ├── artifacts.prototype 为空 → prototype-designer 尚未执行
  │   │   └─ 推荐 /pm-proto
  │   ├── review_results 中无 prototype review 记录
  │   │   └─ prototype 已产出，推荐 /pm-proto-review
  │   ├── review_results 中 prototype review 为 fail
  │   │   └─ 推荐回到 /pm-proto（根据 review 修正）
  │   ├── review_results 中 prototype review 为 warn
  │   │   └─ 推荐 PM 确认风险后决定 /pm-prd 或回到 /pm-proto
  │   ├── review_results 中 prototype review 为 pass
  │   │   └─ pm_confirmations 中无 prototype 确认 → 等待 PM 确认
  │   └── pm_confirmations 中 prototype 已确认
  │       └─ 推荐 /pm-prd
  │
  └── prd
      ├── artifacts.prd 为空 → prd-writer 尚未执行
      │   └─ 推荐 /pm-prd
      ├── review_results 中无 prd review 记录
      │   └─ PRD 已产出，推荐 /pm-prd-review
      ├── review_results 中 prd review 为 fail
      │   └─ 推荐回到 /pm-prd（根据 review 修正）
      ├── review_results 中 prd review 为 warn
      │   └─ 推荐 PM 确认风险后决定或回到 /pm-prd
      ├── review_results 中 prd review 为 pass
      │   └─ pm_confirmations 中无 prd 确认 → 等待 PM 确认
      └── pm_confirmations 中 prd 已确认
          └─ 主链路完成，PRD 可归档。如需修改用后续 fix/change 命令。
```

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

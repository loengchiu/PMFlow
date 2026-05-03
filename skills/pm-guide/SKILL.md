# pm-guide SOP

## 1. 前置读取

执行前必须读取：

- `contracts/gates.md`（门禁定义）
- `contracts/new-main-chain.md`（新主链硬约束）
- `schemas/status.schema.yaml`（状态 schema）
- legacy 主链额外读取：`contracts/confirmation.md`（确认契约）

**禁止**读取任何项目业务文件（文档、代码、配置）。

## 2. 状态检测

### 2.1 `.pmflow/status.yaml` 不存在

项目未初始化。

**输出**：

- 状态：未初始化
- 下一步唯一建议：`/pm-input`
- 提示：请提供需求材料（文本、文档路径、截图、或口头描述）

**不操作**：

- 不自动创建 `.pmflow/` 目录
- 不自动创建 `status.yaml`
- 不读取项目目录下的任何业务文件充当需求

### 2.2 `.pmflow/status.yaml` 存在

读取 `status.yaml`，按以下顺序判断。

## 3. 状态判断逻辑

### 3.0 workflow_mode 判定

读取 `status.yaml` 中的 `workflow_mode`：

- `workflow_mode: new_main` → 走新主链路由（§3.2）
- `workflow_mode: legacy` → 走 legacy 主链路由（§3.3）
- `workflow_mode` 缺失时，按以下规则推断（按优先级从高到低）：
  1. `current_stage` 为 brd/uc/solution → legacy
  2. `artifacts.solution` 为非空数组且至少一个路径对应文件存在于磁盘 → legacy
  3. `pm_confirmations` 中存在 `confirmed: true` 且 `stage` 为 solution 或 prototype 的记录 → legacy
  4. 以上均不满足 → new_main

推断时禁止：
- `artifacts.solution` 为空数组 `[]` 或字段不存在 → 不得判为 legacy
- `pm_confirmations` 为空数组 `[]`、字段不存在、或所有记录 `confirmed: false` → 不得判为 legacy
- `pm_confirmations` 中仅存在 brd/uc 阶段记录 → 不得判为 legacy
- 仅凭 `current_stage` 为 prototype 或 prd → 不得判为 legacy

### 3.1 未收口变更检查（优先级最高，新主链）

在判断阶段路由**之前**，先检查 `fix_debts`：

- 存在 `status: open` 的 `fix_debts`：推荐 `/pm-fix-review`
- 不存在 open 债务：继续阶段路由判断

### 3.2 新主链路由

```
读取 current_stage
  │
  ├── uninitialized
  │     └─ 推荐 /pm-input
  │
  ├── input
  │   ├── review_results 中 input 自检为 fail
  │   │   └─ 推荐回到 /pm-input（fail 阻断）
  │   ├── artifacts.input 为空
  │   │   └─ 推荐 /pm-input
  │   ├── review_results 中无 input 自检记录
  │   │   └─ 推荐 /pm-input（重新执行含自检）
  │   └── input 自检为 pass 或 warn
  │       └─ 推荐 /pm-align
  │
  ├── align
  │   ├── review_results 中 align review 为 fail
  │   │   └─ 推荐回到 /pm-align（fail 阻断）
  │   ├── artifacts.align 为空
  │   │   └─ 推荐 /pm-align
  │   ├── review_results 中无 align review 记录
  │   │   └─ align 已产出，推荐 /pm-align-review
  │   └── align review 为 pass 或 warn
  │       └─ 推荐 /pm-design
  │
  ├── design
  │   ├── review_results 中 design review 为 fail
  │   │   └─ 推荐回到 /pm-design（fail 阻断）
  │   ├── artifacts.design 为空
  │   │   └─ 推荐 /pm-design
  │   ├── review_results 中无 design review 记录
  │   │   └─ design 已产出，推荐 /pm-design-review
  │   └── design review 为 pass 或 warn
  │       └─ 推荐 /pm-wireframe
  │
  ├── wireframe
  │   ├── review_results 中 wireframe review 为 fail
  │   │   └─ 推荐回到 /pm-wireframe
  │   ├── artifacts.wireframe 为空
  │   │   └─ 推荐 /pm-wireframe
  │   ├── review_results 中无 wireframe review 记录
  │   │   └─ wireframe 已产出，推荐 /pm-wireframe-review
  │   └── wireframe review 为 pass 或 warn
  │       └─ 推荐 /pm-prd
  │
  ├── prd
  │   ├── review_results 中 prd review 为 fail
  │   │   └─ 推荐回到 /pm-prd
  │   ├── artifacts.prd 为空
  │   │   └─ 推荐 /pm-prd
  │   ├── review_results 中无 prd review 记录
  │   │   └─ PRD 已产出，推荐 /pm-prd-review
  │   └── prd review 为 pass 或 warn
  │       └─ 推荐 /pm-prototype
  │
  └── prototype
      ├── review_results 中 prototype review 为 fail
      │   └─ 推荐回到 /pm-prototype
      ├── artifacts.prototype 为空
      │   └─ 推荐 /pm-prototype
      ├── review_results 中无 prototype review 记录
      │   └─ prototype 已产出，推荐 /pm-prototype-review
      └── prototype review 为 pass 或 warn
          └─ 主链路完成。如需修改用 /pm-fix。
```

### 3.3 legacy 主链路由

旧项目（`current_stage` 为 brd/uc/solution）仍走旧路由，依赖 `pm_confirmations`、`approved_baselines`、`next_allowed_commands`：

```
brd → /pm-uc → /pm-solution → /pm-proto → /pm-prd
```

判断逻辑与旧版一致，见 `profiles/pm-guide.profile.yaml` 中的 `legacy_stage_gate_types`。

legacy 主链判断"已确认"时，必须同时满足：

1. `pm_confirmations` 中存在对应 stage 且 `confirmed: true`
2. 确认记录的 `artifact` 路径等于 `artifacts.<stage>` 最新产物路径
3. `approved_baselines` 中存在对应 stage 且 `artifact_path` 等于最新产物路径

以上任一不满足 → 推荐 `/pm-confirm`。

## 4. 输出格式

```text
项目状态：[uninitialized | 阶段名]
当前阶段：[阶段名]

已有产物：
- output/input/*.md（已通过 self_check）
- output/align/*.md（已通过 review）
- ...

待处理：
- reviewer 阻断：design review fail（原因：...）
- 复查债务：3 条 open
- 未解决问题：2 个

下一步唯一建议：/pm-design-review

不能自动推进的原因：design review 未通过，必须修正后重新审查。
```

## 5. 停止条件

- 输出状态判断和建议后**必须停止**
- 不得在 guide 之后自动执行为下一步推荐的命令
- 不得询问"要我帮你执行吗"
- 只输出"下一步唯一建议：/pm-xxx"

## 6. 禁止行为

- 不得在没有 `.pmflow/status.yaml` 时扫描项目文件充当需求
- 不得自动创建状态文件
- 不得推荐跳过阶段的路径（如 align 未 review 时推荐 design）
- 不得同时推荐多个下一步（只输出"唯一"建议）
- 不得在 guide 中包含任何业务分析或需求判断
- 不得替代 /pm-fix-review 关闭复查债务

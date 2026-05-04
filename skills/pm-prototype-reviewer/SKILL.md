---
name: pm-prototype-reviewer
description: 原型审查。检查页面覆盖、字段覆盖、动作覆盖、流程走通、UI 一致性和范围一致性。
triggers: ["/pm-prototype-review"]
tags: [pmflow, prototype, review, new_main]
---

# pm-prototype-reviewer 原型审查 SOP（new_main）

## 1. 前置读取

- `contracts/new-main-chain.md`（新主链硬约束）
- `contracts/gates.md`（门禁定义）
- `contracts/human-sync.md`（人机同步契约）
- `schemas/status.schema.yaml`（状态 schema）
- `profiles/prototype-review-new-main.profile.yaml`（审查契约）
- `profiles/prototype-new-main.profile.yaml`（writer 产物契约，对照检查）
- `references/prototype-ui-style.md`（UI 风格参考）
- `output/prototype/index.html`（HTML 原型）
- `.pmflow/metadata/prototype/index.yaml`（原型 metadata）
- `output/prd/prd.md`（人读 PRD，交叉检查）
- `.pmflow/metadata/prd/dictionary.yaml`（字段主定义，交叉检查）
- `.pmflow/metadata/prd/pages/*.yaml`（页面 metadata，交叉检查）
- `output/wireframe/wireframe.md`（线框图，交叉检查）
- `.pmflow/status.yaml`（当前状态）

## 2. 前置检查

读取 `.pmflow/status.yaml`，确认以下**全部**满足：

- `workflow_mode` 为 `new_main`
- `artifacts.prototype` 包含 `output/prototype/index.html`
- `output/prototype/index.html` 存在于磁盘
- `.pmflow/metadata/prototype/index.yaml` 存在于磁盘
- prototype metadata 能反查页面、字段、动作、流程、来源

任一不满足：停止。
不得写入 review 文件，不得追加 `status.review_results`，不得提示主链路完成。

## 3. 审查方法

按 `profiles/prototype-review-new-main.profile.yaml` 的 `checks` 逐项检查。所有检查必须**独立执行**，不得复述 writer 的判断或措辞。

### 3.1 可打开性

检查 `index.html` 是否可本地打开：

- 文件存在且为有效 HTML → pass
- 文件存在但有轻微语法问题 → warn
- 文件不存在或无法解析 → fail

### 3.2 页面覆盖

对照 PRD 核心页面，检查原型是否有对应页面或状态：

- PRD 核心页面在原型中有对应页面或状态 → pass
- 边缘页面略简 → warn
- 核心页面缺失 → fail

### 3.3 字段覆盖

检查 PRD 核心字段在对应页面是否可见或可交互：

- PRD 核心字段在对应页面可见或可交互 → pass
- 边缘字段可补充 → warn
- 核心字段缺失或与 PRD / dictionary 不一致 → fail

### 3.4 动作覆盖

检查 PRD 核心动作是否有可点击入口或明确状态：

- PRD 核心动作有可点击入口或明确状态 → pass
- 边缘动作可补充 → warn
- 核心动作缺失 → fail

### 3.5 流程走通

检查 wireframe / PRD 主流程是否能点击走通：

- 主流程能点击走通 → pass
- 主流程基本可走但有轻微卡点 → warn
- 主流程不可点击走通 → fail

### 3.6 规则表达

检查核心校验、权限、状态、异常是否有可见表达：

- 核心校验、权限、状态、异常有可见表达 → pass
- 边缘规则可补充 → warn
- 核心规则缺失 → fail

### 3.7 UI 一致性

检查是否符合 `references/prototype-ui-style.md`：

- 符合中后台风格（左侧导航、顶部导航、浅灰背景、白色卡片、蓝色主色） → pass
- UI 细节略粗糙但不影响评审 → warn
- 风格严重偏离 → fail

### 3.8 范围一致

检查是否新增了 PRD 未定义的业务字段、操作、状态、流程：

- 未新增 PRD 未定义的业务内容 → pass
- 有轻微扩展但不影响评审 → warn
- 新增未确认业务流程 → fail

### 3.9 人机分离

在原型页面中搜索禁止内容：

- 内部 metadata
- review 字段
- 稳定 ID（FIELD-*、PAGE-*、RULE-*、REQ-*）

发现任一 → fail。

## 4. 判定输出

### 4.1 输出文件

写入 `.pmflow/reviews/prototype-review-{timestamp}.yaml`。

必须包含：

```yaml
stage: prototype
check_type: reviewer_check
verdict: pass | warn | fail
reviewed_artifact: output/prototype/index.html
reviewed_metadata: .pmflow/metadata/prototype/index.yaml
checks_detail:
  - id: openability
    verdict: pass | warn | fail
    detail: ""
  - id: page_coverage
    verdict: pass | warn | fail
    detail: ""
  - id: field_coverage
    verdict: pass | warn | fail
    detail: ""
  - id: action_coverage
    verdict: pass | warn | fail
    detail: ""
  - id: flow_walkthrough
    verdict: pass | warn | fail
    detail: ""
  - id: rule_expression
    verdict: pass | warn | fail
    detail: ""
  - id: ui_consistency
    verdict: pass | warn | fail
    detail: ""
  - id: scope_consistency
    verdict: pass | warn | fail
    detail: ""
  - id: human_machine_separation
    verdict: pass | fail
    detail: ""
fail_reasons: []
warnings: []
checked_at: ""
reviewer: pm-prototype-reviewer
```

## 5. 更新状态

追加同一条记录到 `.pmflow/status.yaml` 的 `review_results`。

verdict 为 pass 或 warn 时，主链路完成。

## 6. 输出格式

### 6.1 pass 或 warn 时

```text
原型审查完成。

整体判定：pass / warn

逐项结果：
- 可打开性：{verdict}
- 页面覆盖：{verdict}
- 字段覆盖：{verdict}
- 动作覆盖：{verdict}
- 流程走通：{verdict}
- 规则表达：{verdict}
- UI 一致性：{verdict}
- 范围一致：{verdict}
- 人机分离：{verdict}

下一步唯一建议：主链路完成。如需修改，执行 /pm-fix。
```

### 6.2 fail 时

```text
原型审查未通过。

阻断项：
- {逐项列出 fail 的原因和修正建议}

下一步唯一建议：/pm-prototype
```

如果问题来自 PRD / wireframe / design 基线变化，建议 `/pm-fix`，但不自动执行。

## 7. 停止条件

- 输出审查结果后**必须停止**
- 不修改 `current_stage`
- 不写 `pm_confirmations`、`approved_baselines`、`next_allowed_commands`
- 不得自动执行 `/pm-prototype` 或任何后续命令
- 不得提示 `/pm-confirm`

## 8. 禁止行为

- 不得复述 writer 的判断或措辞
- 不得在未逐项检查的情况下给 pass
- 不得用"整体完整，可以进入下一步"替代逐项判定
- 不得修改原型文件或 metadata
- 不得在 fail 时提示主链路完成或任何后续命令
- 不得在 pass/warn 时提示 `/pm-prototype`（只提示主链路完成）
- 不得写 pm_confirmations、approved_baselines、next_allowed_commands
- 不得提示 `/pm-confirm`

## 9. 使用示例

```text
用户：/pm-prototype-review

AI：原型审查完成。
    整体判定：pass
    逐项结果：
    - 可打开性：pass
    - 页面覆盖：pass
    - 字段覆盖：pass
    - 动作覆盖：warn（边缘动作可补充）
    - 流程走通：pass
    - 规则表达：pass
    - UI 一致性：pass
    - 范围一致：pass
    - 人机分离：pass
    下一步唯一建议：主链路完成。如需修改，执行 /pm-fix。
```

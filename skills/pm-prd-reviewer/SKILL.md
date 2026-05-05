---
name: pm-prd-reviewer
description: PRD 审查。检查归档质量、字段一致性、页面覆盖、规则覆盖、来源追溯和人机分离。
triggers: ["/pm-prd-review"]
tags: [pmflow, prd, review, new_main]
---

# pm-prd-reviewer PRD 审查 SOP（new_main）

按独立审查模式执行。不依赖 writer 会话结论，重新读取 status / artifact / metadata / profile 后再审查。

## 0. 执行方式

- 优先使用可直接调用的 `pmflow-reviewer` subagent；文件存在不等于可调用。
- 若不能直接调用 `pmflow-reviewer`，但可调用 `general-purpose`，必须把 `agents/pmflow-reviewer.md` 全文、本 SOP、阶段名、项目路径传给 `general-purpose`。
- `general-purpose` 只是承载器，review 结果必须记录 `reviewer_agent_type`、`reviewer_prompt_source`、`reviewer_mode`。
- 如果没有可用 subagent，说明原因，再按 `contracts/reviewer-independence.md` 的独立审查模式执行。
- 主会话只接收 `PMFLOW-REVIEW-RESULT`、写 review 文件并追加 `.pmflow/status.yaml`。

## 1. 前置读取

- `contracts/reviewer-independence.md`（独立审查契约）
- `contracts/new-main-chain.md`（新主链硬约束）
- `contracts/gates.md`（门禁定义）
- `contracts/human-sync.md`（人机同步契约）
- `contracts/lightweight-metadata.md`（轻量 metadata 契约）
- `schemas/status.schema.yaml`（状态 schema）
- `profiles/prd-review-new-main.profile.yaml`（审查契约）
- `profiles/prd-new-main.profile.yaml`（writer 产物契约，对照检查）
- `references/prd-writing.md`（判断 PRD 文风和归档质量）
- `references/writing-principles.md`（判断是否存在模板感或 AI 味）
- `output/prd/prd.md`（人读 PRD）
- `.pmflow/metadata/prd/index.yaml`（机读索引）
- `.pmflow/metadata/prd/dictionary.yaml`（字段主定义）
- `.pmflow/metadata/prd/pages/*.yaml`（页面 metadata，按需读取）
- `.pmflow/metadata/prd/rules.yaml`（业务规则）
- `.pmflow/metadata/prd/trace.yaml`（来源追溯）
- design / wireframe 的必要 metadata（交叉检查）
- `.pmflow/status.yaml`（当前状态）

## 2. 前置检查

读取 `.pmflow/status.yaml`，确认以下**全部**满足：

- `workflow_mode` 为 `new_main`
- `artifacts.prd` 包含 `output/prd/prd.md`
- `output/prd/prd.md` 存在于磁盘
- `.pmflow/metadata/prd/index.yaml` 存在于磁盘
- PRD metadata 能反查字段、页面、动作、规则、验收（双向反查：字段↔页面↔区域↔动作↔规则↔验收，数据字典↔详细需求说明落点，PRD 内容↔design/wireframe 来源）

任一不满足：停止。
不得写入 review 文件，不得追加 `status.review_results`，不得提示 `/pm-prototype`。

## 3. 审查方法

按 `profiles/prd-review-new-main.profile.yaml` 的 `checks` 逐项检查。所有检查必须**独立执行**，不得复述 writer 的判断或措辞。

### 3.0 Metadata 一致性检查（优先执行）

在正文检查前，先验证 metadata 一致性：

1. **dictionary.yaml 存在**，且字段主定义完整（每个字段有 id、name、type、required）
2. **pages/*.yaml 中的 field_id** 必须能在 dictionary.yaml 找到
3. **rules.yaml 中的 field_id** 必须能在 dictionary.yaml 找到
4. **rules.yaml 中的 page_id / action_id** 必须能在 pages/*.yaml 找到
5. **dictionary.yaml 中的核心字段**必须至少有一个页面、区域、动作、规则或验收落点
6. **PRD 正文出现的核心字段**应能在 dictionary.yaml 找到
7. **PRD 详细需求说明中的字段使用**，应能在 pages/*.yaml 中找到对应落点
8. **trace.yaml** 能说明 PRD 核心内容来自 design 或 wireframe
9. **index.yaml** 只作为文件索引，不允许把 index.yaml 当字段事实源

判定规则：
- 正文字段和 dictionary.yaml 不一致：fail
- pages/*.yaml 引用了 dictionary.yaml 不存在的 field_id：fail
- rules.yaml 引用了不存在的 field_id、page_id、action_id：fail
- dictionary.yaml 核心字段没有任何落点：fail
- 边缘字段落点不足：warn
- trace.yaml 个别非核心来源缺失：warn
- 核心页面、动作、规则来源断裂：fail
- 人读产物与 metadata 不一致：fail（必须回到 /pm-prd 修正，不得建议 /pm-fix）
- 仅 metadata 不一致时，建议回到 /pm-prd 进入 metadata repair mode，不得要求 PM 手工修改机读文件

### 3.1 归档可读性

假设读者未读过 design/wireframe，逐节检查 PRD 是否自包含：

- 研发只读 PRD 能理解范围、页面、规则、验收
- 个别概念需补充但不影响评审 → warn
- 需要反复回看 design/wireframe 才能理解 → fail

### 3.2 正文写法

检查页面是否按目标、功能点、区域职责、动作自然展开：

- 页面按目标、功能点、区域职责、动作自然展开 → pass
- 个别动作略空或略模板化 → warn
- 大量机械填空或只写泛泛功能 → fail

### 3.3 页面覆盖

对照 design 核心页面，检查 PRD 是否有对应章节：

- design 核心页面都有 PRD 章节 → pass
- 边缘页面略简 → warn
- 核心页面缺失 → fail

### 3.4 动作覆盖

检查核心动作是否有触发、结果、状态或异常说明：

- 核心动作有触发、结果、状态或异常说明 → pass
- 边缘动作可补充 → warn
- 提交、审批、确认、导入导出等关键动作缺规则 → fail

### 3.5 字段一致性

双向反查正文字段与 dictionary.yaml：

- 正文字段和 dictionary.yaml 不一致 → fail
- 正文出现字段但 dictionary.yaml 无主定义 → fail
- dictionary.yaml 核心字段没有页面/动作/规则/验收落点 → fail
- dictionary.yaml 边缘字段落点不足 → warn
- pages/*.yaml 引用了 dictionary.yaml 不存在的 field_id → fail
- 文风机械但信息完整 → warn；影响研发理解或归档质量时 fail

### 3.6 规则覆盖

检查业务规则、异常、权限、验收是否覆盖核心流程：

- 业务规则、异常、权限、验收覆盖核心流程 → pass
- 边缘规则待补 → warn
- 核心规则、权限或验收缺失 → fail

### 3.7 来源追溯

检查 PRD 内容是否能通过 trace.yaml 追溯到 design 或 wireframe：

- PRD 核心内容能通过 trace.yaml 追溯到 design 或 wireframe → pass
- 个别非核心来源缺失 → warn
- 核心页面、动作、规则来源断裂 → fail
- 出现未确认扩展或来源断裂 → fail
- **阶段递进基线**：PRD 可以把 design/wireframe 细化为研发可评审的自然语言需求，不要求与上游逐字一致
- 不得违背上游核心目标、范围、建设类型、一期/二期边界和主流程方向
- PRD review 通过后，PRD 成为研发评审与归档基线

### 3.8 人机分离

在人读 PRD 中搜索禁止内容：

- 内部路径（`.pmflow/`、`output/`）
- metadata 字段名（`field_id`、`page_id`、`rule_id` 等）
- review 字段（`verdict`、`check_type` 等）
- trace block（`anchor_id`、`rules_ref` 等）
- 稳定 ID（`FIELD-*`、`PAGE-*`、`RULE-*`、`REQ-*`）

发现任一 → fail。

## 4. 判定输出

### 4.1 输出文件

写入 `.pmflow/reviews/prd-review-{timestamp}.yaml`。

必须包含：

```yaml
stage: prd
check_type: reviewer_check
verdict: pass | warn | fail
reviewed_artifact: output/prd/prd.md
reviewed_metadata: .pmflow/metadata/prd/index.yaml
checks_detail:
  - id: archive_readability
    verdict: pass | warn | fail
    detail: ""
  - id: writing_quality
    verdict: pass | warn | fail
    detail: ""
  - id: page_coverage
    verdict: pass | warn | fail
    detail: ""
  - id: action_coverage
    verdict: pass | warn | fail
    detail: ""
  - id: field_consistency
    verdict: pass | warn | fail
    detail: ""
  - id: rule_coverage
    verdict: pass | warn | fail
    detail: ""
  - id: source_trace
    verdict: pass | warn | fail
    detail: ""
  - id: human_machine_separation
    verdict: pass | fail
    detail: ""
fail_reasons: []
warnings: []
checked_at: ""
reviewed_artifact_revision: ""
reviewed_metadata_revision: ""
reviewer: pm-prd-reviewer
reviewer_agent_type: pmflow-reviewer | general-purpose | none
reviewer_prompt_source: agent_type | agents/pmflow-reviewer.md | contracts/reviewer-independence.md
reviewer_mode: pmflow-reviewer | pmflow-reviewer-prompt | independent-current-session
```

## 5. 更新状态

追加同一条记录到 `.pmflow/status.yaml` 的 `review_results`。

**不得**修改 `current_stage`（reviewer 不推进阶段）。
**不得**更新产物快照或 `snapshot_records`（快照由 writer 负责）。

## 6. 输出格式

### 6.1 pass 或 warn 时

```text
PRD 审查完成。

整体判定：pass / warn

逐项结果：
- 归档可读性：{verdict}
- 正文写法：{verdict}
- 页面覆盖：{verdict}
- 动作覆盖：{verdict}
- 字段一致性：{verdict}
- 规则覆盖：{verdict}
- 来源追溯：{verdict}
- 人机分离：{verdict}

下一步唯一建议：/pm-prototype
```

### 6.2 fail 时

```text
PRD 审查未通过。

阻断项：
- {逐项列出 fail 的原因和修正建议}

下一步唯一建议：/pm-prd
```

如果问题来自 design 或 wireframe 基线变化，建议 `/pm-fix`，但不自动执行。

## 7. 停止条件

- 输出审查结果后**必须停止**
- 不修改 `current_stage`
- 不得自动执行 `/pm-prd` 或 `/pm-prototype`

## 8. 禁止行为

- 不得复述 writer 的判断或措辞
- 不得在未逐项检查的情况下给 pass
- 不得用"整体完整，可以进入下一步"替代逐项判定
- 不得修改 PRD 文档或 metadata
- 不得在 fail 时提示 `/pm-prototype` 或任何后续命令
- 不得在 pass/warn 时提示 `/pm-prd`（只提示 `/pm-prototype`）
- 不得跨越 PM ownership gate

## 9. 使用示例

```text
用户：/pm-prd-review

AI：PRD 审查完成。
    整体判定：pass
    逐项结果：
    - 归档可读性：pass
    - 正文写法：pass
    - 页面覆盖：pass
    - 动作覆盖：warn（边缘动作可补充）
    - 字段一致性：pass
    - 规则覆盖：pass
    - 来源追溯：pass
    - 人机分离：pass
    下一步唯一建议：/pm-prototype
```

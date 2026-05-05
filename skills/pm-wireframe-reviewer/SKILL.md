---
name: pm-wireframe-reviewer
description: 线框说明稿审查。检查线框说明稿是否覆盖 design 核心页面，主流程是否可走通，落点是否完整。
triggers: ["/pm-wireframe-review"]
tags: [pmflow, wireframe, review]
---

# pm-wireframe-reviewer 审查 SOP

## 1. 前置读取

- `contracts/gates.md`（门禁定义，重点 reviewer 门禁）
- `contracts/human-sync.md`（人机同步契约）
- `contracts/new-main-chain.md`（新主链硬约束）
- `schemas/status.schema.yaml`（状态 schema）
- `profiles/wireframe.profile.yaml`（wireframe 产物契约，重点 review_checklist）
- `templates/wireframe.md`（wireframe 人读骨架，用于对照结构）
- `references/wireframe-writing.md`（写法参考）
- 最新 wireframe 产物（`output/wireframe/wireframe.md`）
- 最新 wireframe metadata（`.pmflow/metadata/wireframe/` 下的 index.yaml 和相关分片）
- 对应 design 产物和 metadata（用于交叉检查基线绑定和页面覆盖）
- 最近一次 design-review 结果

## 2. 前置检查

读取 `.pmflow/status.yaml`，确认：

- `current_stage` 为 `design` 或 `wireframe`（wireframe writer 可能尚未更新 current_stage）
- `artifacts.wireframe` 非空
- `output/wireframe/wireframe.md` 存在于磁盘
- `.pmflow/metadata/wireframe/index.yaml` 存在于磁盘
- `review_results` 中存在 `stage: design` 且 `check_type: reviewer_check` 的记录
- 最近一次 design reviewer_check 的 `verdict` 为 `pass` 或 `warn`
- 最近一次 design reviewer_check 的 `reviewed_artifact` 等于 `artifacts.design` 最新路径
- 最近一次 design reviewer_check 的 `reviewed_metadata` 等于当前 design metadata 路径

条件不满足：停止，提示 PM 当前没有可审查的线框说明稿。
不得写入 wireframe review 文件，不得追加 `status.review_results`，不得提示 /pm-prd。

## 3. 审查方法

按 `profiles/wireframe.profile.yaml` 中 `review_checklist` 逐项检查。

### 3.1 基线绑定检查

- wireframe 是否基于已通过 design-review 的基线
- 是否有越界扩展（超出 design 范围的页面或模块）
- 是否有 design 中不存在的新增内容

### 3.2 页面覆盖检查

- design metadata 中的核心页面是否在页面跳转树或页面线框中有对应条目
- 核心页面是否全部覆盖
- 缺失页面的具体 ID 和名称

### 3.3 主流程走通检查

- design 中定义的主流程，每一步是否有对应的页面间导航
- 从入口页面到终点页面是否可连贯走通
- 分支和回退路径是否标注

### 3.4 字段 / 操作 / 状态落点检查

- design 中的关键字段是否在页面线框的落点表中出现
- design 中的关键操作是否在页面线框的落点表中出现
- design 中的关键状态是否在页面线框的落点表中出现
- 检查方式：抽取 design metadata 中的 fields、flows、states，逐项在 wireframe 中查找

### 3.5 设计疑点检查

- wireframe 中记录的设计疑点是否清楚描述了问题、影响页面和建议处理
- 是否有页面层暴露的问题未被记录

### 3.6 人机分离检查

- 人读产物是否泄漏机读字段（anchor_id、rules_ref 等）
- metadata 分片是否符合行数限制

## 4. 判定输出

### 4.1 审查记录

写入 `.pmflow/reviews/wireframe-review-{timestamp}.yaml`：

```yaml
stage: wireframe
check_type: reviewer_check
verdict: pass | warn | fail
fail_reasons: []
warnings: []
checked_at: ""
reviewed_artifact: ""   # 必填：本次审查的 wireframe 人读产物路径
reviewed_metadata: ""   # 必填：本次审查的 wireframe metadata 路径
checks_detail:
  - id: baseline_binding
    verdict: pass | warn | fail
    detail: ""
    suggestion: ""
  - id: page_coverage
    verdict: pass | warn | fail
    detail: ""
    suggestion: ""
  - id: main_flow_walkable
    verdict: pass | warn | fail
    detail: ""
    suggestion: ""
  - id: field_operation_state_landing
    verdict: pass | warn | fail
    detail: ""
    suggestion: ""
  - id: design_issues
    verdict: pass | warn | fail
    detail: ""
    suggestion: ""
  - id: human_machine_separation
    verdict: pass | warn | fail
    detail: ""
    suggestion: ""
```

`reviewed_artifact` 和 `reviewed_metadata` 为**必填字段**，不得为空。

### 4.2 判定标准

**fail（阻断）**：任一项 review_checklist fail 条件满足

- 线框说明稿超出 design 确认范围
- 新增 design 中不存在的页面或模块
- design 中的核心页面在线框说明稿中缺失
- 主流程页面间导航断裂
- 关键操作无落点
- 关键状态无展示区域

**warn（风险通过）**：review_checklist warn 条件满足

- 部分边缘页面的字段布局待细化
- 部分异常提示位置待补充
- 非核心页面的导航关系待补充

**pass（通过）**：review_checklist pass 条件全部满足

- design 中所有核心页面在线框说明稿中有落点
- 主流程页面导航连贯可走通
- 关键字段、操作、状态均有可见表达
- 设计疑点已清楚记录
- 人读产物无机读字段泄漏
- metadata 符合行数限制

## 5. 停止并报告

### 5.1 pass 或 warn 时

```text
线框说明稿审查完成。

整体判定：pass / warn

逐项结果：
- 基线绑定：{verdict}
- 页面覆盖：{verdict}
- 主流程走通：{verdict}
- 字段/操作/状态落点：{verdict}
- 设计疑点：{verdict}
- 人机分离：{verdict}

{如果是 warn：风险项已记录，PM 请知情确认。}

产物：
- .pmflow/reviews/wireframe-review-*.yaml

下一步唯一建议：/pm-prd
```

### 5.2 fail 时

```text
线框说明稿审查未通过。

整体判定：fail

阻断项：
- {逐项列出 fail 的原因和修正建议}

判定建议：
- 如果是线框表达问题（页面缺失、导航断裂、落点遗漏）：建议回到 /pm-wireframe 修正
- 如果是 design 层问题（design 缺少映射、规则不完整、流程未闭合）：建议执行 /pm-fix 修正 design

PM 不可越权推进。
```

## 6. 停止条件

- 输出审查结果后**必须停止**
- 不得在 pass/warn 后提示 /pm-wireframe 或任何后续命令（只提示 /pm-prd）
- 不得在 fail 后提示 /pm-prd（只提示 /pm-wireframe 或 /pm-fix）
- 不得提示"要我现在做吗"
- 不得代 PM 确认

## 7. 禁止行为汇总

- 不得复述 writer 的判断或措辞
- 不得在未逐项检查的情况下给 pass
- 不得用"整体完整，可以进入下一步"替代逐项判定
- 不得在 fail 时提示 /pm-prd 或任何后续命令
- 不得在 pass/warn 时提示 /pm-wireframe 或任何后续阶段命令（只提示 /pm-prd）
- 不得修改 wireframe 文档或 metadata
- 不得跨越 PM ownership gate

## 8. 更新状态

审查完成后，将审查记录**追加到** `.pmflow/status.yaml` 的 `review_results` 数组。记录内容与写入 `.pmflow/reviews/` 的独立文件一致。

**不得**修改 `current_stage`（reviewer 不推进阶段）。

## 9. 使用示例

```text
用户：/pm-wireframe-review
AI：（读取 wireframe 产物、metadata、design 产物、metadata，逐项审查）
AI：线框说明稿审查完成。
    整体判定：pass
    下一步唯一建议：/pm-prd
```

---
name: pm-input
description: 材料盘点。识别材料来源、性质、缺口和冲突。
triggers: ["/pm-input"]
tags: [pmflow, input, material]
---

# pm-input 材料盘点 SOP

## 1. 前置读取

- `contracts/gates.md`（门禁定义）
- `schemas/status.schema.yaml`（状态 schema）
- `profiles/input.profile.yaml`（input 产物契约）
- `templates/input.md`（材料盘点稿骨架）

## 2. 前置检查

### 2.1 `.pmflow/status.yaml` 不存在

新项目首次进入。

- 创建 `.pmflow/` 目录结构
- 初始化 `status.yaml`（`current_stage: uninitialized`）
- 继续执行材料盘点

### 2.2 `.pmflow/status.yaml` 存在

读取状态：

- `current_stage` 为 `input` 或 `uninitialized`：可执行
- `current_stage` 为其他阶段：停止，提示当前阶段不允许重新执行 /pm-input
- 存在 `status: open` 的 `fix_debts` 且 `change_level: L5`：停止，提示先处理 /pm-fix-review

## 3. 材料盘点方法

使用"材料盘点法"，按以下顺序执行：

### 3.1 材料识别

识别 PM 提供的所有材料：

- 需求方原话
- 字段表
- 流程图
- 截图
- 会议纪要
- 旧系统资料
- 制度文件
- 口头描述

### 3.2 来源标记

区分每份材料的来源：

- 需求方确认
- PM 假设
- 旧系统现状
- 历史文档
- 参考材料

### 3.3 约束强度判断

标记每份材料的约束强度：

- 强约束：需求方明确确认
- 参考约束：可参考但不作为硬性要求
- 待确认：需要需求方进一步确认
- 范围外：不在本次建设范围内

### 3.4 内容提取

从材料中提取线索：

- 目标线索
- 角色线索
- 场景线索
- 字段线索
- 流程线索
- 规则线索
- 边界线索

### 3.5 缺口和冲突识别

识别材料之间的缺失、矛盾和口径不一致。

### 3.6 对齐问题生成

把缺口转成可问需求方的问题。

### 3.7 补充方式标记

每个待补充问题必须给出推荐补充方式：

- `会话补充`：适合一句话能回答的问题，如是否需要审批、角色名称、字段是否必填。
- `补充文件`：适合字段表、流程图、会议纪要、截图、批量规则、长段说明。
- `需求方确认后补充`：适合 PM 不能代答、必须问需求方的问题。

如果建议补充文件，必须说明建议文件名和内容格式，例如：

```text
建议新建 output/input/supplement-字段表.md，按“字段 / 类型 / 必填 / 说明 / 来源”补充。
```

## 4. 输出生成

### 4.1 人读产物

写入 `output/input/input-{timestamp}.md`。

必须使用 `templates/input.md` 的章节骨架。

必须包含：

- 材料清单
- 材料来源和约束强度
- 需求一句话摘要
- 建设类型初判
- 缺口与冲突清单
- 待补充问题清单
- 每个待补充问题的推荐补充方式
- 是否可以进入 /pm-align

禁止出现机读字段、内部路径、机器 ID。

人读产物编号使用简单数字编号，如 `1`、`2`、`3`。不得在人读稿中暴露 `GAP-001`、`CONFLICT-002`、`MAT-003` 这类机读 ID。

待补充问题按补充方式分组展示：

- 可一句话补充（在 /pm-align 中提供）
- 建议整理成文件后重新执行 /pm-input
- 需要先问需求方确认

问题不在 input 阶段回答，全部带入 /pm-align 处理。PM 可在执行 /pm-align 时直接补充答案，或在 /pm-align 多轮对齐中逐步关闭问题。

### 4.2 机读 metadata

写入 `.pmflow/metadata/input/input-{timestamp}.yaml`。

必须包含 `profiles/input.profile.yaml` 中 `machine_output_requirements` 的全部字段。

### 4.3 更新状态

更新 `.pmflow/status.yaml`：

- `current_stage: input`
- `artifacts.input` 追加新文件路径

### 4.4 自检

按 `profiles/input.profile.yaml` 中 `self_check` 标准执行自检。

自检结果**必须同时写入两处**：

1. 写入独立文件 `.pmflow/reviews/input-self-check-{timestamp}.yaml`
2. 将**同一条** self_check 记录追加到 `.pmflow/status.yaml` 的 `review_results` 数组

`reviewed_artifact` 和 `reviewed_metadata` 为必填字段，必须分别等于本次 input 产物路径和 metadata 路径。

## 5. 输出格式

```text
材料盘点完成。

产物：
- output/input/input-*.md
- .pmflow/metadata/input/input-*.yaml

自检结果：pass | warn | fail

[pass/warn] 下一步唯一建议：/pm-align
[fail] 需要补充材料后重新执行 /pm-input

补充方式：
- 可一句话补充（在 /pm-align 中提供）：1、2、3
- 建议整理成文件后重新执行 /pm-input：1（建议文件：xxx.md）
- 需要先问需求方确认：1、2
```

## 6. 停止条件

- 输出材料盘点结果和建议后**必须停止**
- 不得自动执行 /pm-align
- 不得询问"要我帮你执行吗"

## 7. 禁止行为

- 不生成解决方案、详细页面、字段、流程
- 不把背景材料默认当成需求方确认事实
- 不漏掉需求方明确提供或认可的材料
- 材料不完整时拒绝进入 /pm-align（warn 时允许进入）
- 不在 input 阶段越界写详细设计

## 8. 使用示例

```text
用户：/pm-input
我们想做一个审计管理系统，需求方给了字段表和流程图。

AI：材料盘点完成。
产物：output/input/input-20260503.md
自检结果：warn
缺口：需求方未确认审批层级
补充方式：可在当前会话直接说明审批层级；如有正式流程图，建议保存为业务项目文档后重新执行 /pm-input。
下一步唯一建议：/pm-align
```

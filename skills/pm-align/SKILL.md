---
name: pm-align
description: 需求对齐。确认需求理解、建设类型、范围边界、角色场景、业务方向。支持多轮。
triggers: ["/pm-align"]
tags: [pmflow, align, requirement]
---

# pm-align 需求对齐 SOP

## 1. 前置读取

- `contracts/gates.md`（门禁定义）
- `contracts/human-sync.md`（人机同步契约）
- `schemas/status.schema.yaml`（状态 schema）
- `profiles/input.profile.yaml`（input 产物契约，理解输入结构）
- `profiles/align.profile.yaml`（align 产物契约）
- 最新 input 产物（`output/input/` 下最新文件）
- 最新 input metadata（`.pmflow/metadata/input/` 下最新文件）

## 2. 前置检查

读取 `.pmflow/status.yaml`，确认以下**全部**满足：

- `current_stage` 为 `input`（首次对齐）或 `align`（多轮对齐）
- `artifacts.input` 非空
- `review_results` 中存在 input 的 `self_check` 且 verdict 为 `pass` 或 `warn`
- input self_check 的 `reviewed_artifact` 等于 `artifacts.input` 最新路径
- input self_check 的 `reviewed_metadata` 等于 `.pmflow/metadata/input/` 下最新 metadata 路径

任一不满足：停止，提示 PM 当前状态不满足进入 align 的条件。

**通用规则**：下一阶段 writer 由"上游 review pass/warn + 绑定最新产物"准入，不要求 `current_stage` 已经等于下一阶段。writer 执行成功后自行更新 `current_stage`。

## 3. 需求对齐方法

使用"需求对齐法"，按以下顺序执行：

### 3.1 问题归因

识别需求方真正要解决的问题。

### 3.2 目标定义

明确目标类别：效率、合规、体验、数据、流程闭环、管理可视化。

### 3.3 建设类型判断

给出建设类型及依据：新建系统/模块、优化迭代、混合。

### 3.4 范围划定

区分本次做什么、不做什么、待确认什么。

### 3.5 角色与场景识别

识别关键用户、主任务、核心使用场景。

### 3.6 用户路径雏形

只到"谁在什么场景下完成什么任务"，不展开详细页面和状态机。

### 3.7 业务方向确认

给出业务解决方向，但不进入字段、页面、权限、流程细节。

## 4. 多轮对齐支持

- 基于上一版对齐稿继续补充
- 在会话中直接补充需求方说明、流程图、字段表、截图、规则
- 吸收需求方改口径
- 复查 PM 手工修改后的对齐稿
- 关闭或新增待确认问题

用户在会话中补充的新内容不能默认等于已确认事实，必须按表达区分：

- 需求方确认
- PM 假设
- 新增材料
- 范围变化
- 详细设计线索

## 5. 输出生成

### 5.1 人读产物

写入 `output/align/align-{timestamp}.md`。

写法参考 `references/writing-principles.md`。

禁止出现机读字段、内部路径、机器 ID。禁止越界写详细设计。

### 5.2 机读 metadata

写入 `.pmflow/metadata/align/align-{timestamp}.yaml`。

必须包含 `profiles/align.profile.yaml` 中 `machine_output_requirements` 的全部字段。

### 5.3 更新状态

更新 `.pmflow/status.yaml`：

- `current_stage: align`
- `artifacts.align` 追加新文件路径

## 6. 输出格式

```text
需求对齐完成。

产物：
- output/align/align-*.md
- .pmflow/metadata/align/align-*.yaml

已确认内容：
- ...

待确认问题：
- ...

下一步唯一建议：/pm-align-review
```

## 7. 停止条件

- 输出对齐结果后**必须停止**
- 不得自动执行 /pm-align-review
- 不得自动执行 /pm-design

## 8. 禁止行为

- 不展开页面清单、字段清单、权限矩阵、状态机
- 不把 PM 假设当需求方确认
- 不把新增材料默认当作已采纳设计
- 不自动进入下一阶段
- 不在 align 阶段越界写详细设计

## 9. 使用示例

```text
用户：/pm-align
需求方补充说审批只需要两级。

AI：需求对齐完成。
产物：output/align/align-20260503.md
已确认内容：建设类型为新建，范围覆盖审计计划和执行
待确认问题：审批层级待最终确认
下一步唯一建议：/pm-align-review
```

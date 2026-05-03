---
name: pm-design
description: 详细设计。基于 align 基线构建功能、页面、字段、流程、状态、权限、规则。
triggers: ["/pm-design"]
tags: [pmflow, design, detail]
---

# pm-design 详细设计 SOP

## 1. 前置读取

- `contracts/gates.md`（门禁定义）
- `contracts/human-sync.md`（人机同步契约）
- `contracts/snapshot-diff.md`（快照 diff 契约）
- `schemas/status.schema.yaml`（状态 schema）
- `profiles/align.profile.yaml`（align 产物契约，理解对齐基线）
- `profiles/design.profile.yaml`（design 产物契约）
- `references/writing-principles.md`（通用写法）
- 最新 align 产物（`output/align/` 下最新文件）
- 最新 align metadata（`.pmflow/metadata/align/` 下最新文件）

**禁止**在未读取已通过 align-review 的对齐基线时开始设计。

## 2. 前置检查

读取 `.pmflow/status.yaml`，确认以下**全部**满足：

- `current_stage` 为 `align`（首次 design）或 `design`（重新执行）
- `artifacts.align` 非空
- `review_results` 中存在 align 的 `reviewer_check` 且 verdict 为 `pass` 或 `warn`
- align review 的 `reviewed_artifact` 等于 `artifacts.align` 最新路径
- align review 的 `reviewed_metadata` 等于 `.pmflow/metadata/align/` 下最新 metadata 路径

任一不满足：停止，提示 PM 当前状态不满足进入 design 的条件。

**通用规则**：下一阶段 writer 由"上游 review pass/warn + 绑定最新产物"准入，不要求 `current_stage` 已经等于下一阶段。writer 执行成功后自行更新 `current_stage`。

## 3. 结构化设计建设法

按以下顺序推导，只基于 align 基线：

1. 目标转能力
2. 场景转任务
3. 任务转功能
4. 功能转页面
5. 对象转数据字典
6. 任务转系统流程
7. 流程转状态
8. 角色转权限
9. align 基线中的认可材料逐项处理
10. align-review 遗留问题影响标记

### 3.1 不做前置判断

- 不重新判断建设类型
- 不重新解释需求方原始材料
- 不把新材料悄悄并入设计
- 不扩大或改变 align 已确认范围
- 发现材料缺失、冲突、建设类型不成立时，**停止**并建议回到 /pm-input 或 /pm-align

## 4. 上下文防爆

大型 design 不允许一次性长文生成。

```text
生成设计索引
-> 分片生成模块/页面/字段/流程内容
-> 每片局部自检
-> 最终组装为一个 PM 可读主稿
```

分片规则：

- PM 主阅读入口：`output/design/design.md`
- AI 生成分片：`.pmflow/workspace/design/sections/`
- 机读记录：`.pmflow/metadata/design/`
- 单个主题 metadata 不超过 500 行
- 单个 detail metadata 不超过 200 行

## 5. 输出生成

### 5.1 人读产物

固定写入 `output/design/design.md`（PM 主阅读入口，覆盖写入）。

历史版本记录到 `status.yaml` 的 `artifacts.design` 中。

写法参考 `references/writing-principles.md`。

禁止出现机读字段、内部路径、机器 ID。

### 5.2 机读 metadata

分片写入 `.pmflow/metadata/design/`：

- `index.yaml`（索引）
- `modules.yaml` / `pages.yaml` / `entities.yaml` / `fields.yaml`
- `flows.yaml` / `states.yaml` / `rules.yaml` / `permissions.yaml`
- `relations.yaml`

每条设计内容必须标注 align 来源追溯。无法追溯的内容必须标注为 `open_question`。

### 5.3 快照

生成完成后写入 `.pmflow/snapshots/design/design.last-synced.md`。

### 5.4 更新状态

更新 `.pmflow/status.yaml`：

- `current_stage: design`
- `artifacts.design` 追加新文件路径
- `snapshot_records` 追加快照记录

## 6. 输出格式

```text
详细设计完成。

产物：
- output/design/design.md
- .pmflow/metadata/design/（分片 metadata）
- .pmflow/snapshots/design/design.last-synced.md

需要独立审查（请执行 /pm-design-review）：
- 功能/页面/字段/流程是否基于 align 基线
- 关键对象是否有稳定 ID 和来源追溯
- relations 是否完整
- 人读产物有无机读字段泄漏
- metadata 分片是否符合行数限制

下一步唯一建议：/pm-design-review
```

## 7. 停止条件

- 输出设计结果后**必须停止**
- 不得自动执行 /pm-design-review
- 不得自动执行 /pm-wireframe

## 8. 禁止行为

- 不在 design 阶段重新判断建设类型
- 不在 design 阶段重新解释原始材料
- 不把新材料悄悄并入设计
- 不扩大或改变 align 已确认范围
- 发现前置冲突后继续生成
- 一次性长文生成超过 2000 行的完整设计
- 不在产出后提示 /pm-wireframe 或 /pm-confirm（只提示 /pm-design-review）

## 9. 使用示例

```text
用户：/pm-design

AI：详细设计完成。
产物：
- output/design/design.md
- .pmflow/metadata/design/（分片 metadata）

需要独立审查（请执行 /pm-design-review）：
- 功能/页面/字段/流程是否基于 align 基线
- 关键对象是否有稳定 ID 和来源追溯

下一步唯一建议：/pm-design-review
```

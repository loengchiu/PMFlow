---
name: pm-wireframe
description: 线框说明稿。基于 design 产物生成 Markdown 线框说明稿，暴露页面流转和信息承载问题。
triggers: ["/pm-wireframe"]
tags: [pmflow, wireframe, detail]
---

# pm-wireframe 线框说明稿 SOP

## 1. 前置读取

- `contracts/gates.md`（门禁定义）
- `contracts/human-sync.md`（人机同步契约）
- `contracts/snapshot-diff.md`（快照 diff 契约）
- `contracts/new-main-chain.md`（新主链硬约束）
- `schemas/status.schema.yaml`（状态 schema）
- `profiles/design.profile.yaml`（design 产物契约，理解设计结构）
- `profiles/wireframe.profile.yaml`（wireframe 产物契约）
- `templates/wireframe.md`（wireframe 人读骨架）
- `references/wireframe-writing.md`（写法参考）
- `references/writing-principles.md`（通用写法）
- 最新 design 产物（`output/design/` 下最新文件）
- 最新 design metadata（`.pmflow/metadata/design/` 下的 index.yaml 和相关分片）

**禁止**在未读取已通过 design-review 的设计基线时开始线框说明稿生成。

## 2. 前置检查

读取 `.pmflow/status.yaml`，确认以下**全部**满足：

- `workflow_mode` 为 `new_main`
- `current_stage` 为 `design`（首次 wireframe）或 `wireframe`（重新执行）
- `artifacts.design` 非空
- `review_results` 中存在 design 的 `reviewer_check` 且 verdict 为 `pass` 或 `warn`
- design review 的 `reviewed_artifact` 等于 `artifacts.design` 最新路径
- design review 的 `reviewed_metadata` 等于 `.pmflow/metadata/design/` 下最新 metadata 路径

任一不满足：停止，提示 PM 当前状态不满足进入 wireframe 的条件。
不得写入 `output/wireframe/wireframe.md`，不得写入 `.pmflow/metadata/wireframe/index.yaml`，不得写入 `.pmflow/snapshots/wireframe/wireframe.last-synced.md`，不得更新 `.pmflow/status.yaml`，不得提示 /pm-prd。

**通用规则**：下一阶段 writer 由"上游 review pass/warn + 绑定最新产物"准入，不要求 `current_stage` 已经等于下一阶段。writer 执行成功后自行更新 `current_stage`。

## 3. 线框说明稿生成方法

基于 design 的 pages、flows、fields、states、rules 逐页生成线框说明稿。

### 3.1 不做前置判断

- 不扩大或改变 design 已确认范围
- 不新增 design 中不存在的页面或模块
- 不生成高保真视觉稿（颜色、字体、图标等）
- 发现 design 产物不完整时，**停止**并建议回到 /pm-design 补充

### 3.2 逐页生成

对 design metadata 中的每个页面：

1. **页面跳转**：来源页面、目标页面、触发条件
2. **页面结构**：用 ASCII 草图表达区域组成（简单页面可简写）
3. **字段 / 操作 / 状态落点**：从 design 提取，标注页面位置和关键约束
4. **设计疑点**：页面层暴露的问题

### 3.3 页面间导航

从 design 的 flows 提取主流程和关键子流程：

- 标注每步导航的来源页面、目标页面、触发条件
- 确保主流程从入口到终点可走通
- 标注分支和回退路径

### 3.4 主流程走通验证

生成完成后，自行验证：

- 主流程每一步是否有对应的页面和导航
- 关键字段是否在相关页面中有落点
- 关键操作是否在相关页面中有入口
- 关键状态是否在相关页面中有展示区域

### 3.5 大型需求控制长度

- 普通列表页、详情页、维护页可简写
- 入口页、表单页、结果页、汇总页优先详细展开
- 页面跳转树只覆盖主流程和关键分支
- 详细写法参考 `references/wireframe-writing.md`

## 4. 上下文防爆

- 逐页生成，不允许一次性长文生成
- 先生成 metadata index，再按页面生成分片
- 单页 metadata 不超过 300 行
- index 不超过 200 行

## 5. 输出生成

### 5.1 人读产物

写入 `output/wireframe/wireframe.md`（覆盖写入）。

- 遵循 `templates/wireframe.md` 的骨架结构
- 写法参考 `references/wireframe-writing.md` 和 `references/writing-principles.md`
- 禁止出现：anchor_id、rules_ref、machine_profile、internal_path、design_ref
- 禁止出现："作为 AI""我建议你""根据规则要求"等 AI 痕迹
- 禁止出现颜色、字体、图标等高保真视觉描述
- 用自然语言和 ASCII 文本布局描述线框结构

### 5.2 机读 metadata

写入 `.pmflow/metadata/wireframe/`：

- `index.yaml`：页面清单和导航关系索引
- 按类型分片（如有需要）

必须包含 `profiles/wireframe.profile.yaml` 中 `machine_output_requirements` 的全部字段。

### 5.3 快照

生成后写入 `.pmflow/snapshots/wireframe/wireframe.last-synced.md`，内容与 `output/wireframe/wireframe.md` 一致。

### 5.4 更新状态

更新 `.pmflow/status.yaml`：

- `current_stage: wireframe`
- `artifacts.wireframe` 追加 `output/wireframe/wireframe.md`
- `snapshot_records` 追加快照记录

## 6. 停止并报告

### 6.1 完成输出

```text
线框说明稿生成完成。

产物：
- output/wireframe/wireframe.md（人读线框说明稿）
- .pmflow/metadata/wireframe/index.yaml（机读索引）
- .pmflow/snapshots/wireframe/wireframe.last-synced.md（快照）

需要独立审查（请执行 /pm-wireframe-review）：
- 页面跳转树是否覆盖核心页面
- P0/P1 主流程是否能从入口走到结果
- 关键字段、操作、状态是否有页面落点
- 设计疑点是否需要回到 design 处理

下一步唯一建议：/pm-wireframe-review
```

### 6.2 禁止行为

- 不得在 design review 未通过时执行
- 不得超出 design 范围边界擅自扩展
- 不得将 writer 自身的推测标为 design 来源
- 不得生成高保真视觉稿
- 不得执行 reviewer 的自检
- 不得在产出后提示 /pm-prd 或任何后续阶段命令（只提示 /pm-wireframe-review）
- 不得跨越 PM ownership gate

## 7. 使用示例

```text
用户：/pm-wireframe
AI：（读取 design 产物和 metadata，逐页生成线框说明稿）
AI：线框说明稿生成完成。
    产物：output/wireframe/wireframe.md
    下一步唯一建议：/pm-wireframe-review
```

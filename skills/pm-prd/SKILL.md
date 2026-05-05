---
name: pm-prd
description: PRD 生成。基于 design + wireframe 产物生成归档级 PRD，支持字段、页面、动作、规则、验收反查。
triggers: ["/pm-prd"]
tags: [pmflow, prd, writer, new_main]
---

# pm-prd PRD 生成 SOP（new_main）

## 1. 前置读取

- `contracts/new-main-chain.md`（新主链硬约束）
- `contracts/gates.md`（门禁定义）
- `contracts/human-sync.md`（人机同步契约）
- `contracts/snapshot-diff.md`（快照 diff 契约）
- `contracts/lightweight-metadata.md`（轻量 metadata 契约）
- `schemas/status.schema.yaml`（状态 schema）
- `profiles/prd-new-main.profile.yaml`（PRD 产物契约）
- `templates/prd.md`（PRD 人读骨架）
- `references/prd-writing.md`（写法参考）
- `references/prd-action-examples.md`（动作样例）
- `references/writing-principles.md`（通用写法）
- `.pmflow/status.yaml`（当前状态）
- 最新 design 产物（`output/design/` 下最新文件）
- 最新 design metadata（`.pmflow/metadata/design/` 下的 index.yaml）
- 最新 wireframe 产物（`output/wireframe/wireframe.md`）
- 最新 wireframe metadata（`.pmflow/metadata/wireframe/index.yaml`）
- 最近一次 wireframe-review 结果

**禁止**在未读取已通过 wireframe-review 的设计基线时开始 PRD 生成。

## 2. 前置检查

读取 `.pmflow/status.yaml`，确认以下**全部**满足：

- `workflow_mode` 为 `new_main`
- `current_stage` 为 `wireframe`（首次 PRD）或 `prd`（重新执行）
- `artifacts.design` 非空
- `artifacts.wireframe` 非空
- `review_results` 中存在 wireframe 的 `check_type` 为 `reviewer_check` 且 verdict 为 `pass` 或 `warn`
- wireframe review 的 `reviewed_artifact` 等于 `artifacts.wireframe` 最新路径
- wireframe review 的 `reviewed_metadata` 等于 `.pmflow/metadata/wireframe/` 下最新 metadata 路径
- 不存在 `status: open` 的 `fix_debts`

任一不满足：停止，提示 PM 当前状态不满足进入 PRD 的条件。
不得写入 `output/prd/prd.md`，不得写入 PRD metadata，不得写入 snapshot，不得更新 `status.yaml`，不得提示 `/pm-prototype`。

**通用规则**：下一阶段 writer 由"上游 review pass/warn + 绑定最新产物"准入，不要求 `current_stage` 已经等于下一阶段。writer 执行成功后自行更新 `current_stage`。

## 3. PRD 生成方法

### 3.1 不做前置判断

- 不扩大或改变 design / wireframe 已确认范围
- 不新增 design 中不存在的页面或模块
- 不生成高保真视觉稿（颜色、字体、图标等）
- 发现 design 产物不完整时，**停止**并建议回到 /pm-design 补充
- 发现 wireframe 产物不完整时，**停止**并建议回到 /pm-wireframe 补充
- PM 要求修改时，先列影响范围，再给局部变更，只改必要文件。不整篇重写

### 3.2 生成顺序

```text
读取状态和前置基线
-> 读取 design / wireframe 必要分片
-> 规划 PRD 章节和页面
-> 生成 dictionary.yaml
-> 逐页生成详细需求说明和 pages/*.yaml
-> 生成 rules.yaml
-> 生成 trace.yaml
-> 回查 dictionary / pages / rules / trace 一致性
-> 写 output/prd/prd.md
-> 写 .pmflow/metadata/prd/index.yaml
-> 写 snapshot
-> 更新 status
-> 输出下一步唯一建议 /pm-prd-review
```

注意：
- 数据字典先生成。
- 详细需求说明逐页生成。
- 页面生成时只读取当前页面相关字段、规则、wireframe 信息。
- 不一次性读取完整大型 metadata。
- 不生成 field_usage.yaml。
- 不生成 entities/*.yaml。
- 不生成 relations.yaml，统一改为 trace.yaml。

### 3.3 数据字典生成

从 design 的 fields 和 entities 提取核心字段，写入 `dictionary.yaml`：

```yaml
dictionary:
  - id: PRD-FIELD-INBOUND-NO
    name: 入库申请单编号
    type: string
    required: true
    format: RK-YYYYMMDD-NNN
    anchors: []
    source_refs: []
  - id: PRD-FIELD-QUANTITY
    name: 数量
    type: integer
    required: true
    min: 1
    anchors: []
    source_refs: []
```

- 每个实体列出字段（ID、名称、类型、必填、默认值、枚举值、结构化约束）
- 字段必须与各页面字段清单一致
- 枚举值必须显式列出，不得用"等"模糊
- 字段 ID 是唯一标识，pages/*.yaml 和 rules.yaml 通过 field_id 引用
- 字段正式说明写在人读 PRD，metadata 只保留索引和约束
- 如果确实需要字段短说明，只能用 short_statement，限制 80 字以内

### 3.4 逐页生成详细需求说明

对 design metadata 中的每个页面：

1. **页面目标**：页面的核心价值和使用场景
2. **关联功能点**：页面涉及的功能点列表
3. **区域职责**：页面由哪些区域组成，各区域承担什么职责
4. **按动作展开**：每个动作按复杂度自然展开

动作写法参考 `references/prd-writing.md` 和 `references/prd-action-examples.md`。

### 3.5 字段落点关系

每生成一个页面，同步记录字段落点关系到 `pages/*.yaml`：

```yaml
page_id: PRD-PAGE-INBOUND-REQUEST
page_code: P-02
page_name: 入库申请页

regions:
  - name: 列表区
    fields:
      - field_id: PRD-FIELD-INBOUND-NO
        field_name: 入库申请单编号
        usage: 展示

actions:
  - id: PRD-ACT-CREATE-INBOUND
    name: 新增入库
    fields:
      - field_id: PRD-FIELD-QUANTITY
        field_name: 数量
        usage: 编辑
        rule_refs:
          - PRD-RULE-QUANTITY-GT-ZERO
```

字段落点关系包括：
- field_id（引用 dictionary.yaml 中的字段 ID）
- field_name（字段名）
- usage（展示/筛选/编辑/只读/校验/状态判断/权限判断/计算/导入/导出/验收依据）
- rule_refs（关联的规则 ID）

### 3.6 主流程走通验证

生成完成后，自行验证：

- 主流程每一步是否有对应的页面和动作
- 关键字段是否在数据字典中有主定义
- 关键字段是否在详细需求说明中有落点
- 关键动作是否有触发、结果、状态或异常说明
- 验收标准是否覆盖核心流程

### 3.7 大型需求控制长度

- 普通列表页、详情页、维护页可简写
- 入口页、表单页、结果页、汇总页优先详细展开
- 数据字典按实体分组
- 验收标准覆盖核心流程和关键异常

## 4. 上下文防爆

- 逐页生成，不允许一次性长文生成
- 先生成 dictionary.yaml，再按页面生成分片
- 单页 metadata 不超过 300 行
- dictionary.yaml 不超过 500 行
- index 不超过 200 行
- 按需读取 design / wireframe metadata 分片，不一次性全量读取
- 页面生成时只读取当前页面相关字段、规则、wireframe 信息

## 5. 多轮更新模式

当前阶段已有产物且用户补充/修正时：

- 先读取已有的人读产物、metadata 和 snapshot。
- 判断用户输入影响的字段、页面、动作、规则、验收。
- 同步更新人读产物、metadata、snapshot 和 status。
- 不得只更新人读物，不更新 metadata；不得只更新 metadata，不更新人读物。
- 当前阶段循环里的补充回答，不建议 /pm-fix。
- 完成后下一步唯一建议仍是 /pm-prd-review。

### 5.1 同类关联点检测

当前阶段多轮更新时，必须扫描当前阶段产物中的同类关联点。能确定需要同步的当前阶段内容，必须同步修改。不确定的同类点，先问 PM。如果下游产物已存在且当前修改会影响下游，提示使用 /pm-fix 统一同步。

## 6. 输出生成

### 5.1 人读产物

写入 `output/prd/prd.md`（覆盖写入）。

- 遵循 `templates/prd.md` 的骨架结构
- 写法参考 `references/prd-writing.md` 和 `references/writing-principles.md`
- 禁止出现：anchor_id、rules_ref、machine_profile、internal_path、design_ref、prototype_ref、field_id、page_id、rule_id、REL-*
- 禁止出现："作为 AI""我建议你""根据规则要求"等 AI 痕迹
- 禁止出现："详见 design""wireframe 已说明"等跨文档引用
- 用自然语言描述业务规则、页面动作和验收标准
- 页面编号 `P-01`、`P-02A` 可以出现在正文中，用作人读定位

### 5.2 机读 metadata

写入 `.pmflow/metadata/prd/`：

- `index.yaml`：文件索引（只作为索引，不保存字段主定义）
- `dictionary.yaml`：字段主定义唯一来源（字段 ID、名称、类型、必填、枚举值、说明）
- `pages/*.yaml`：页面、区域、动作、字段落点（字段落点引用 dictionary.yaml 的 field_id）
- `rules.yaml`：业务规则、异常、权限、验收标准
- `trace.yaml`：PRD 与 design、wireframe 的来源追溯关系

必须包含 `profiles/prd-new-main.profile.yaml` 中 `machine_output_requirements` 的全部字段。

**重要**：
- 不生成 `entities/*.yaml`（字段主定义统一在 dictionary.yaml）
- 不生成 `field_usage.yaml`（字段落点回到 pages/*.yaml）
- 不生成 `relations.yaml`（改为 trace.yaml，只做来源追溯）

### 5.3 快照

生成后写入 `.pmflow/snapshots/prd/prd.last-synced.md`，内容与 `output/prd/prd.md` 一致。

### 5.4 更新状态

更新 `.pmflow/status.yaml`：

- `current_stage: prd`
- `artifacts.prd` 追加 `output/prd/prd.md`
- `snapshot_records` 追加快照记录
- `stage_revisions.prd.artifact_revision` 刷新为当前 ISO 时间
- `stage_revisions.prd.metadata_revision` 刷新为当前 ISO 时间

## 6. 停止并报告

### 6.1 完成输出

```text
PRD 生成完成。

产物：
- output/prd/prd.md（人读 PRD 主稿）
- .pmflow/metadata/prd/index.yaml（机读索引）
- .pmflow/metadata/prd/dictionary.yaml（字段主定义）
- .pmflow/metadata/prd/pages/*.yaml（页面 metadata）
- .pmflow/metadata/prd/rules.yaml（业务规则）
- .pmflow/metadata/prd/trace.yaml（来源追溯）
- .pmflow/snapshots/prd/prd.last-synced.md（快照）

需要独立审查（请执行 /pm-prd-review）：
- 字段与数据字典是否一致
- 页面动作是否覆盖核心流程
- 规则、权限、异常、验收是否完整
- PRD 是否可直接评审和归档

下一步唯一建议：/pm-prd-review
```

### 6.2 禁止行为

- 不得在 wireframe review 未通过时执行
- 不得超出 design / wireframe 范围边界擅自扩展
- 不得将 writer 自身的推测标为 design 来源
- 不得执行 reviewer 的自检
- 不得在产出后提示 `/pm-prototype` 或任何后续阶段命令（只提示 `/pm-prd-review`）
- 不得跨越 PM ownership gate

## 7. 使用示例

```text
用户：/pm-prd
AI：（读取 design 和 wireframe 产物和 metadata，逐页生成 PRD）
AI：PRD 生成完成。
    产物：output/prd/prd.md
    下一步唯一建议：/pm-prd-review
```

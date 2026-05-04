---
name: pm-prototype
description: 原型生成。基于 design + wireframe + PRD 生成高保真 HTML 业务原型，支持主流程点击走查。
triggers: ["/pm-prototype"]
tags: [pmflow, prototype, writer, new_main]
---

# pm-prototype 原型生成 SOP（new_main）

## 1. 前置读取

- `contracts/new-main-chain.md`（新主链硬约束）
- `contracts/gates.md`（门禁定义）
- `contracts/human-sync.md`（人机同步契约）
- `contracts/snapshot-diff.md`（快照 diff 契约）
- `schemas/status.schema.yaml`（状态 schema）
- `profiles/prototype-new-main.profile.yaml`（原型产物契约）
- `references/prototype-ui-style.md`（UI 风格参考）
- `.pmflow/status.yaml`（当前状态）
- 最新 design 产物（`output/design/design.md`）
- 最新 design metadata（`.pmflow/metadata/design/index.yaml`）
- 最新 wireframe 产物（`output/wireframe/wireframe.md`）
- 最新 wireframe metadata（`.pmflow/metadata/wireframe/index.yaml`）
- 最新 PRD 产物（`output/prd/prd.md`）
- PRD metadata（`.pmflow/metadata/prd/index.yaml`、`dictionary.yaml`、`pages/*.yaml`、`rules.yaml`、`trace.yaml`）
- 最近一次 prd-review 结果

**禁止**在未读取已通过 prd-review 的 PRD 基线时开始原型生成。

## 2. 前置检查

读取 `.pmflow/status.yaml`，确认以下**全部**满足：

- `workflow_mode` 为 `new_main`
- `current_stage` 为 `prd`（首次原型）或 `prototype`（重新执行）
- `artifacts.prd` 包含 `output/prd/prd.md`
- `review_results` 中存在 prd 的 `check_type` 为 `reviewer_check` 且 verdict 为 `pass` 或 `warn`
- prd review 的 `reviewed_artifact` 等于 `artifacts.prd` 最新路径
- prd review 的 `reviewed_metadata` 等于 `.pmflow/metadata/prd/index.yaml`
- 不存在 `status: open` 的 `fix_debts`

任一不满足：停止，说明缺什么。
不得写入 `output/prototype/`，不得写入 prototype metadata，不得写入 snapshot，不得更新 `status.yaml`，不得提示主链路完成。

## 3. 原型生成方法

### 3.1 重要规则

1. 页面内容由 PRD / wireframe / metadata / PM 注释决定。
2. UI 表达参考 `references/prototype-ui-style.md`。
3. Claude 看不到图片，不得凭"参考设计稿"自由发挥。
4. 页面结构按 PRD 和 wireframe 来，不固定强塞筛选区、表格、图表、监控区等组件。
5. 组件按页面类型选择（参考，不是必选）：
   - 列表管理页：筛选区、操作区、表格、状态标签、分页
   - 详情页：分组信息、图片/附件占位、明细表、记录区、时间线
   - 配置页：tab、配置行、开关、输入框、保存按钮
   - 看板页：指标卡、图表、监控区、趋势图
   - 审批页：详情信息、审批动作、审批记录、状态流转
   - 表单页：分组表单、校验提示、提交/取消按钮
6. PRD 没定义的字段、操作、状态、流程，不得为了套 UI 样式而新增。
7. 原型必须贴近现有 B 端中后台风格：左侧导航、顶部导航、浅灰背景、白色卡片、蓝色主色、表格/表单/状态标签风格。
8. 原型不是营销页、门户页、炫酷大屏，也不是生产前端工程。

### 3.2 生成顺序

```text
读取状态和前置基线
-> 读取 design / wireframe / PRD 必要分片
-> 规划原型页面结构
-> 生成 index.html（含内嵌或外链 CSS/JS）
-> 生成 metadata
-> 回查页面、字段、动作、流程覆盖
-> 写 snapshot
-> 更新 status
-> 输出下一步唯一建议 /pm-prototype-review
```

### 3.3 页面结构规划

从 PRD 的详细需求说明和 wireframe 的页面清单提取核心页面：

- 每个 PRD 页面对应一个原型页面或状态
- 页面类型根据 PRD 描述判断（列表页、详情页、表单页、配置页、看板页、审批页）
- 页面内组件按页面类型和 PRD 定义选择

### 3.4 交互支持

原型必须支持主流程点击走查：

- 页面切换（左侧导航或顶部导航）
- tab 切换
- 列表查看详情
- 查询/重置
- 保存反馈
- 弹窗确认
- PRD 定义的核心交互

### 3.5 Mock 数据

使用 mock 数据，但必须贴近业务字段：

- 字段名和字段值必须来自 PRD 数据字典
- 不使用无意义占位（如"test1"、"示例数据"）
- 枚举值必须使用 PRD 定义的枚举值
- 数量、金额等数值必须合理

## 4. 上下文防爆

- 逐页生成，不允许一次性长文生成
- 单个 HTML 文件不超过 3000 行
- 过长时拆分为 `assets/style.css` 和 `assets/app.js`
- 按需读取 PRD / wireframe / design metadata 分片，不一次性全量读取

## 5. 输出生成

### 5.1 原型文件

写入 `output/prototype/index.html`（覆盖写入）。

- 静态 HTML/CSS/JS，可本地打开
- 第一版可以内嵌 CSS/JS；过长时拆 assets/style.css 和 assets/app.js
- 支持主流程点击走通
- 使用 mock 数据，但 mock 数据必须贴近业务字段

### 5.2 机读 metadata

写入 `.pmflow/metadata/prototype/index.yaml`：

```yaml
source_prd_artifact: output/prd/prd.md
source_prd_metadata: .pmflow/metadata/prd/index.yaml
source_wireframe_artifact: output/wireframe/wireframe.md
source_wireframe_metadata: .pmflow/metadata/wireframe/index.yaml
pages:
  - page_id: PROTO-PAGE-001
    page_name: 页面名称
    page_type: list | detail | form | config | dashboard | approval
    prd_page_ref: PRD-PAGE-001
    wireframe_page_ref: WF-PAGE-001
    prototype_anchor: "#page-001"
    fields:
      - field_id: PRD-FIELD-001
        field_name: 字段名
    actions:
      - id: PRD-ACT-001
        name: 动作名
flows:
  - id: FLOW-001
    name: 主流程名
    steps:
      - page: PROTO-PAGE-001
        action: PRD-ACT-001
```

### 5.3 快照

生成后写入 `.pmflow/snapshots/prototype/prototype.last-synced.html`，内容与 `output/prototype/index.html` 一致。

### 5.4 更新状态

更新 `.pmflow/status.yaml`：

- `current_stage: prototype`
- `artifacts.prototype` 追加 `output/prototype/index.html`
- `snapshot_records` 追加快照记录

## 6. 停止并报告

### 6.1 完成输出

```text
原型生成完成。

产物：
- output/prototype/index.html（高保真 HTML 原型）
- .pmflow/metadata/prototype/index.yaml（机读索引）
- .pmflow/snapshots/prototype/prototype.last-synced.html（快照）

需要独立审查（请执行 /pm-prototype-review）：
- 页面是否覆盖 PRD 核心页面
- 字段是否与 PRD 数据字典一致
- 主流程是否能点击走通
- UI 是否符合中后台风格

下一步唯一建议：/pm-prototype-review
```

### 6.2 禁止行为

- 不得在 prd review 未通过时执行
- 不得超出 PRD / wireframe / design 范围边界擅自扩展
- 不得新增 PRD 中不存在的页面、字段、操作、状态、流程
- 不得实现真实后端接口
- 不得在产出后提示主链路完成或任何后续阶段命令（只提示 /pm-prototype-review）
- 不得写 pm_confirmations、approved_baselines、next_allowed_commands
- 不得提示 /pm-confirm

## 7. 使用示例

```text
用户：/pm-prototype
AI：（读取 design、wireframe、PRD 产物和 metadata，逐页生成原型）
AI：原型生成完成。
    产物：output/prototype/index.html
    下一步唯一建议：/pm-prototype-review
```

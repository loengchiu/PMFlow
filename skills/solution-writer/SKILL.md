# solution-writer SOP [legacy]

> **legacy**: 此 skill 属于旧主链。新项目请使用 `pm-design` skill。

## 1. 前置读取

执行前必须读取：

- `contracts/gates.md`（门禁定义，重点 §3 reviewer 门禁）
- `contracts/build-type.md`（建设类型判定契约）
- `contracts/input-classification.md`（输入分类契约）
- `profiles/solution.profile.yaml`（solution 产物契约）
- `profiles/brd.profile.yaml`（前置 BRD 契约，理解 BRD 输出结构）
- `profiles/uc.profile.yaml`（前置 UC 契约，理解 UC 输出结构）
- `schemas/status.schema.yaml`（状态 schema）
- `templates/solution-note.md`（输出骨架参考）
- `references/writing-principles.md`（通用人类 PM 写法）
- `references/solution-writing.md`（方案稿写法参考）
- `references/methodology-playbook.md`（方法论轻量用法）
- 已确认的 BRD note（`output/brd/` 下最新文件）
- 已确认的 BRD metadata（`.pmflow/metadata/brd/` 下最新文件）
- 已确认的 UC note（`output/uc/` 下最新文件）
- 已确认的 UC metadata（`.pmflow/metadata/uc/` 下最新文件）

**禁止**在未读取已确认 BRD 和 UC 的情况下开始方案写作。

## 2. 前置检查

### 2.1 状态校验

读取 `.pmflow/status.yaml`，确认：

- `current_stage` 为 `solution`；或者 `next_allowed_commands` 包含 `/pm-solution`（PM 确认后授权进入或回归补充）
- `pm_confirmations` 中 brd 已确认（`confirmed: true`）
- `pm_confirmations` 中 uc 已确认（`confirmed: true`）
- brd 确认记录的 `artifact` 路径等于 `artifacts.brd` 中的**最新**产物路径
- brd 的 `approved_baselines` 中 `artifact_path` 等于 `artifacts.brd` 最新产物路径
- uc 确认记录的 `artifact` 路径等于 `artifacts.uc` 中的**最新**产物路径
- uc 的 `approved_baselines` 中 `artifact_path` 等于 `artifacts.uc` 最新产物路径
- `review_results` 中 brd 自检不为 `fail`
- `review_results` 中 uc 自检不为 `fail`

如果任一条件不满足：
- 停止。提示 PM 当前状态不满足进入 solution 的条件。
- 推荐 `/pm-guide` 查看当前状态。

### 2.2 前置产物校验

确认已读取的 BRD note 包含：
- 业务目标
- 需求方角色
- 范围边界

确认已读取的 UC note 包含：
- 用户角色
- 用户路径
- 关键任务流

如果 BRD 或 UC 产出不满足上述最低要求：
- 停止。提示 PM 当前前置产物不足以支撑方案写作。
- 推荐回到不足的阶段补充。

## 3. 输入收集与分类

### 3.1 收集补充材料

向 PM 收集本轮补充材料（如有）：
- 业务规则补充
- 数据规范说明
- 现有系统接口信息
- 非功能性需求

### 3.2 分类本轮输入

按 `contracts/input-classification.md` 对本轮新增输入分类。分类结果追加到 metadata。

## 4. 方案方法

### 4.1 建设类型判定

按 `contracts/build-type.md` 从四个维度逐项判定：

- 部署：是否部署到已有运行环境？
- 代码：是否基于已有代码库修改？
- 数据库：是否沿用已有数据库/表结构？
- 实例：是否使用已有应用实例？

判定结果为 new_build / iteration / hybrid 之一。hybrid 时必须标注哪些部分新建、哪些迭代。

判定依据必须与 BRD 的 scope_boundary 一致。BRD 只覆盖新建部分 → 不应判为 hybrid。

### 4.2 模块范围

从 UC 的用户路径和任务流中识别需要覆盖的模块：

- 每个模块有明确的名称和职责
- 模块之间关系标注清楚
- 不得超出 BRD 范围边界

### 4.3 页面范围

为每个模块拆解页面清单：

- 区分列表页、表单页、详情页
- 标注页面之间的关系（父子、跳转、嵌套）
- 每个页面可追溯到 UC 中的用户路径或任务流

### 4.4 关键字段与字段组

为每个页面梳理关键字段：

- 列表页：标注展示字段，按用户判断优先级排序（P0 核心决策字段 / P1 常用筛选字段 / P2 辅助信息）
- 表单页：标注填写字段，有分组逻辑的分组列出
- 详情页：标注展示字段，有分区逻辑的分区列出
- 不得穷举所有字段——聚焦关键决策和操作所需的字段

### 4.5 关键操作

为每个页面梳理关键操作按钮：

- 标注操作入口、触发条件、操作结果
- 操作必须可追溯到 UC 中的用户任务

### 4.6 模块主流程

梳理核心业务流程：

- 有完整的入口、提交后、通过后、驳回后的状态变化口径
- 涉及多角色的流程标注角色交接点
- 覆盖 UC 中已确认的主路径和关键异常路径

### 4.7 页面流转规则

描述用户在不同页面之间的跳转逻辑：

- 标注从哪个页面、到哪个页面、触发条件
- 页面流转必须与模块主流程一致

### 4.8 架构决策记录（轻量 ADR）

对关键设计决策记录轻量 ADR：

- 背景：为什么需要决策
- 决策：做了什么选择
- 理由：为什么这样选
- 替代方案：考虑过但未采用的方案

不要求每条细节都写 ADR——只记录 BRD/UC 中未明确、经方案推导确定的关键决策。

## 5. 输出生成

### 5.1 人读产物

写入 `output/solution/solution-note-{timestamp}.md`。

- 遵循 `templates/solution-note.md` 骨架
- 写法参考 `references/solution-writing.md`，不要机械填空
- 根据实际内容灵活组织，不机械填空
- 禁止出现：anchor_id、rules_ref、prototype_ref、machine_profile、internal_path
- 禁止出现："作为 AI""我建议你""根据规则要求"等 AI 痕迹
- 禁止出现："详见原型""原型已说明"等跨阶段引用
- 字段、流程、操作均用自然语言和表格描述，不要用 JSON/YAML 格式

### 5.2 机读 metadata

写入 `.pmflow/metadata/solution/solution-{timestamp}.yaml`。

必须包含 `profiles/solution.profile.yaml` 中 `machine_output_requirements` 的全部字段：

```yaml
build_type_evidence: { deploy, code, database, instance, hybrid_detail }
modules: []
pages: []
fields: []
actions: []
flows: []
page_flows: []
decisions: []
source_trace: {}
```

每条方案内容必须在 `source_trace` 中标注 BRD/UC 来源。无法追溯到 BRD/UC 的内容必须标注为 open_question。

### 5.3 更新状态

更新 `.pmflow/status.yaml`：
- `current_stage: solution`
- `artifacts.solution` 追加新文件路径
- 如有新的 open_questions，追加

## 6. 停止并报告

### 6.1 完成输出

```text
方案写作完成。

产物：
- output/solution/solution-note-*.md
- .pmflow/metadata/solution/solution-*.yaml

需要独立审查（请执行 /pm-solution-review）：
- 建设类型判定是否正确
- 关键字段是否覆盖
- 主流程和页面流转是否完整
- 信息架构是否合理
- 人读产物有无机读字段泄漏
- 范围是否超出 BRD 边界

下一步唯一建议：/pm-solution-review
```

### 6.2 禁止行为

- 不得在 UC 未确认时执行 solution-writer
- 不得自行扩大 BRD 范围之外的模块或页面
- 不得跳过 solution-reviewer 直接提示 /pm-confirm 或 /pm-proto
- 不得在 solution note 中生成原型描述或 PRD 内容
- 不得提示"要我现在做吗"
- 不得以"看起来没问题"为由自动继续

## 7. 禁止行为汇总

- 不得在 BRD 或 UC 未确认时执行
- 不得超出 BRD 范围边界擅自扩展模块或页面
- 不得仅凭"新项目立项"或"参考旧系统"判定建设类型（必须四维度逐项判定）
- 不得将 writer 自身的推测标为 confirmed
- 不得为了完整感直接生成原型或 PRD 内容
- 不得执行 reviewer 的自检（solution 阶段 review 由独立 reviewer 完成）
- 不得在产出后提示下一阶段命令（只提示 /pm-solution-review）
- 不得跨越 PM ownership gate

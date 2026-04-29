# prototype-designer SOP

## 1. 前置读取

执行前必须读取：

- `contracts/gates.md`（门禁定义，重点 §3 reviewer 门禁）
- `profiles/prototype.profile.yaml`（prototype 产物契约）
- `profiles/solution.profile.yaml`（solution 产物契约，理解方案结构）
- `schemas/status.schema.yaml`（状态 schema）
- `templates/prototype-note.md`（输出骨架参考）
- 已确认的 solution note（`output/solution/` 下最新文件）
- 已确认的 solution metadata（`.pmflow/metadata/solution/` 下最新文件）

**禁止**在未读取已确认 solution 的情况下开始原型设计。

## 2. 前置检查

### 2.1 状态校验

读取 `.pmflow/status.yaml`，确认：

- `current_stage` 为 `prototype`；或者 `next_allowed_commands` 包含 `/pm-proto`（PM 确认后授权进入或回归补充）
- `pm_confirmations` 中 solution 已确认（`confirmed: true`）
- solution 确认记录的 `artifact` 路径等于 `artifacts.solution` 中的**最新**产物路径
- solution 的 `approved_baselines` 中 `artifact_path` 等于 `artifacts.solution` 最新产物路径
- `review_results` 中 solution review 不为 `fail`

如果任一条件不满足：
- 停止。提示 PM 当前状态不满足进入 prototype 的条件。
- 推荐 `/pm-guide` 查看当前状态。

### 2.2 前置产物校验

确认已读取的 solution note 包含：
- 建设类型
- 模块范围
- 页面范围
- 关键字段与字段组
- 模块主流程

如果 solution 产出不满足上述最低要求：
- 停止。提示 PM 当前 solution 不足以支撑原型设计。
- 推荐回到 solution 阶段补充。

## 3. 输入收集

向 PM 收集本轮补充材料（如有）：
- 设计规范或设计系统参考
- 现有系统截图或交互参考
- 交互偏好（导航方式、反馈方式等）

如果 PM 未提供，不虚构。使用通用 B 端中后台惯例。

## 4. 原型方法

### 4.1 确定原型范围

从 solution 的 `page_scope` 和 `module_main_flow` 确定原型覆盖范围：

- 原型覆盖的页面必须与 solution 的 page_scope 一致
- 原型覆盖的流程必须覆盖 solution 中所有 module_main_flow
- 不得自行新增 solution 中未出现的页面或流程
- 如果发现 solution 中某页面/流程无法原型化，标注为 open_question

### 4.2 页面原型

为每个页面描述原型：

**列表页**：
- 字段按 solution 中的 P0/P1/P2 优先级排列
- 标注筛选区位置（顶部筛选栏 / 左侧筛选面板）
- 标注操作区位置（顶部工具栏 / 行内操作 / 批量操作）
- 标注分页方式

**表单页**：
- 字段按 solution 中的分组排列
- 标注分组标题和是否折叠
- 标注必填标识方式
- 标注提交/取消按钮位置

**详情页**：
- 信息按 solution 中的分区排列
- 标注分区标题
- 标注操作按钮（编辑 / 审批 / 返回等）位置

每条字段、每个操作的描述必须可追溯到 solution 中的对应定义。

### 4.3 流程原型

为每条 solution 中的 module_main_flow 描述逐页走法：

- 起于入口页面，止于终点页面
- 每步标注：当前页面 → 操作 → 下一页面 / 状态变化
- 分支条件标注在外
- 涉及多角色的流程标注角色交接点
- 有提交/通过/驳回的完整口径

### 4.4 交互状态

为关键页面和流程描述交互状态：

- 列表空态（无数据时的展示和引导）
- 加载态（数据加载中的表现）
- 错误态（操作失败时的表现和恢复方式）
- 表单校验失败态（字段级错误提示）
- 提交成功态（提交后的反馈）
- 审批通过/驳回后的状态变化

不需要穷举所有状态——聚焦每个页面的关键交互。

### 4.5 全局交互规范

描述跨页面的通用交互规范：

- 导航方式
- 数据加载策略
- 操作反馈方式（toast / 弹窗 / 行内提示）
- 异常处理方式

## 5. 输出生成

### 5.1 人读产物

写入 `output/prototype/prototype-note-{timestamp}.md`。

- 遵循 `templates/prototype-note.md` 骨架
- 根据实际内容灵活组织，不机械填空
- 禁止出现：anchor_id、rules_ref、prototype_ref、machine_profile、internal_path、prd_ref
- 禁止出现："作为 AI""我建议你""根据规则要求"等 AI 痕迹
- 禁止出现："详见 PRD""PRD 已说明"等跨阶段引用
- 页面、流程、交互均用自然语言和表格描述，不要用 JSON/YAML 格式

### 5.2 机读 metadata

写入 `.pmflow/metadata/prototype/prototype-{timestamp}.yaml`。

必须包含 `profiles/prototype.profile.yaml` 中 `machine_output_requirements` 的全部字段：

```yaml
pages_prototyped: []
flows_prototyped: []
interactions: []
source_trace: {}
```

每条原型内容必须在 `source_trace` 中标注 solution 来源。无法追溯到 solution 的内容必须标注为 open_question。

### 5.3 更新状态

更新 `.pmflow/status.yaml`：
- `current_stage: prototype`
- `artifacts.prototype` 追加新文件路径
- 如有新的 open_questions，追加

## 6. 停止并报告

### 6.1 完成输出

```text
原型设计完成。

产物：
- output/prototype/prototype-note-*.md
- .pmflow/metadata/prototype/prototype-*.yaml

需要独立审查（请执行 /pm-proto-review）：
- 信息架构是否忠实于 solution
- 主流程是否可以逐页走通
- 字段和操作是否与 solution 一致
- 交互状态是否覆盖
- 人读产物有无机读字段泄漏
- 范围是否超出 solution 边界

下一步唯一建议：/pm-proto-review
```

### 6.2 禁止行为

- 不得在 solution 未确认时执行 prototype-designer
- 不得自行扩大 solution 范围之外的页面或流程
- 不得跳过 prototype-reviewer 直接提示 /pm-confirm 或 /pm-prd
- 不得在 prototype note 中生成 PRD 内容
- 不得提示"要我现在做吗"
- 不得以"看起来没问题"为由自动继续

## 7. 禁止行为汇总

- 不得在 solution 未确认时执行
- 不得超出 solution 范围边界擅自扩展页面或流程
- 不得将 designer 自身的推测标为 confirmed
- 不得为了完整感直接生成 PRD 内容
- 不得执行 reviewer 的自检（prototype 阶段 review 由独立 reviewer 完成）
- 不得在产出后提示下一阶段命令（只提示 /pm-proto-review）
- 不得跨越 PM ownership gate

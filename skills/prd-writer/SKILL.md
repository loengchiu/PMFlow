# prd-writer SOP [legacy]

> **适用范围**：仅 legacy 主链（brd→uc→solution→prototype→prd）。新主链 PRD 阶段尚未实现，由 `commands/pm-prd.md` 分流到 placeholder。

## 1. 前置读取

执行前必须读取：

- `contracts/gates.md`（门禁定义，重点 §3 reviewer 门禁）
- `profiles/prd.profile.yaml`（PRD 产物契约）
- `profiles/prototype.profile.yaml`（prototype 产物契约，理解原型结构）
- `profiles/solution.profile.yaml`（solution 产物契约，理解方案结构）
- `profiles/uc.profile.yaml`（UC 产物契约，理解用户路径）
- `profiles/brd.profile.yaml`（BRD 产物契约，理解业务目标）
- `schemas/status.schema.yaml`（状态 schema）
- `templates/prd.md`（输出骨架参考）
- `references/writing-principles.md`（通用人类 PM 写法）
- `references/prd-writing.md`（PRD 写法参考）
- `references/methodology-playbook.md`（PRD 生成前推导用）
- 已确认的 prototype note（路径来自 `pm_confirmations` 中 prototype 的 `artifact` / `approved_baselines` 中 prototype 的 `artifact_path`，不得仅取目录最新文件）
- 已确认的 prototype metadata（路径来自 `review_results` 中 prototype review 的 `reviewed_metadata`）
- 已确认的 solution note（路径来自 `pm_confirmations` 中 solution 的 `artifact` / `approved_baselines` 中 solution 的 `artifact_path`）
- 已确认的 solution metadata（路径来自 `review_results` 中 solution review 的 `reviewed_metadata`）
- 已确认的 UC note（路径来自 `pm_confirmations` 中 uc 的 `artifact` / `approved_baselines` 中 uc 的 `artifact_path`）
- 已确认的 UC metadata（路径来自 `review_results` 中 uc self-check 的 `reviewed_metadata`）
- 已确认的 BRD note（路径来自 `pm_confirmations` 中 brd 的 `artifact` / `approved_baselines` 中 brd 的 `artifact_path`）
- 已确认的 BRD metadata（路径来自 `review_results` 中 brd self-check 的 `reviewed_metadata`）

**禁止**在未读取已确认 prototype 和全部前置基线（BRD/UC/solution/prototype）的情况下开始 PRD 写作。所有前置产物的读取路径必须来自基线绑定，不得仅取目录最新文件。

## 2. 前置检查

### 2.1 状态校验

读取 `.pmflow/status.yaml`，确认：

- `current_stage` 为 `prd`；或者 `next_allowed_commands` 包含 `/pm-prd`（PM 确认后授权进入或回归补充）

对 **brd、uc、solution、prototype** 四个前置阶段，每个阶段必须满足以下 6 项：

1. `pm_confirmations` 中存在该阶段且 `confirmed: true`
2. 确认记录的 `artifact` 路径等于 `artifacts.<stage>` 中的**最新**产物路径
3. `approved_baselines` 中该阶段的 `artifact_path` 等于 `artifacts.<stage>` 最新产物路径
4. `review_results` 中该阶段最近一次检查不为 `fail`（brd/uc 为 self_check，solution/prototype 为 reviewer_check）
5. `review_results` 中该阶段检查的 `reviewed_artifact` 等于 `artifacts.<stage>` 最新产物路径
6. `review_results` 中该阶段检查的 `reviewed_metadata` 等于该阶段最新 metadata 文件路径

如果任一阶段、任一条件不满足：
- 停止。提示 PM 具体哪个前置阶段的基线不一致。
- 推荐 `/pm-guide` 查看当前状态。

### 2.2 前置产物校验

确认已读取的 prototype note 包含：
- 页面原型（逐页字段和操作描述）
- 流程原型（主流程逐页走法）
- 交互状态

确认已读取的 solution note 包含：
- 建设类型
- 模块范围与页面范围
- 关键字段与字段组
- 模块主流程

如果 prototype 或 solution 产出不满足上述最低要求：
- 停止。提示 PM 当前前置产物不足以支撑 PRD 写作。
- 推荐回到不足的阶段补充。

## 3. 输入收集

向 PM 收集本轮补充材料（如有）：
- 业务规则补充
- 数据规范说明
- 权限规则说明
- 验收标准补充

如果 PM 未提供，从已确认的前置基线中推导，不得虚构。

## 4. PRD 方法

### 4.1 项目背景与目标

从已确认的 BRD 提炼项目背景和业务目标：

- 背景说明为什么做这个需求
- 目标说明做成什么样算成功
- 范围明确列出范围内外的模块和页面
- 不得照抄 BRD——应整理为 PRD 读者可独立理解的表述

### 4.2 模块与功能

从已确认 solution 的 `module_scope` 和 prototype 的页面原型中整理：

- 每个模块有功能概述
- 每个模块列出包含的页面
- 功能说明不得重复 prototype 的界面描述

### 4.3 页面与字段

从已确认 solution 的 `key_fields_or_field_groups` 和 prototype 的页面原型中整理：

- 逐页面列出字段清单（类型、必填、校验规则、默认值、说明）
- 逐页面列出关键操作（前置条件、执行步骤、后置结果）
- 字段和操作必须与 solution 和 prototype 一致
- 不得照搬 prototype 的界面布局描述——PRD 关注字段语义和规则，不关注视觉位置

### 4.4 业务规则

从 solution 的流程定义、prototype 的交互描述、PM 补充材料中提炼：

- 每条规则有 ID、触发条件、执行逻辑
- 审批规则单独一节（审批流程、级数、会签/或签、驳回路径）
- 规则来源必须可追溯到前置基线或 PM 补充

### 4.5 异常处理

从 solution 和 prototype 的异常路径、交互状态中提炼：

- 每条异常有触发条件和处理方式
- 标注用户可见的提示文案
- 覆盖数据异常、权限不足、并发冲突等

### 4.6 权限规则

从 UC 的用户角色、BRD 的需求方角色中推导：

- 定义角色清单
- 绘制角色-页面-操作权限矩阵
- 标注数据权限范围（本人/本部门/全部等）
- 无法从前置基线推导的权限标注为 open_question

### 4.7 数据字典

从 solution 的字段定义中提炼核心实体：

- 每个实体列出字段（类型、长度、必填、默认值、枚举值、说明）
- 字段必须与各页面字段清单一致
- 枚举值必须显式列出，不得用"等"模糊

### 4.8 字段与页面关系

从 solution 和 prototype 中整理：

- 每个字段出现在哪些页面
- 在各页面中的展现形式（展示/编辑/筛选）

### 4.9 数据影响范围

从 solution 的 `build_type_evidence` 和系统分析中判断：

- 标注涉及的数据表/实体
- 标注对现有数据的影响（新增/修改/只读）

### 4.10 验收标准

从 BRD 的业务目标、UC 的用户任务、solution 的流程中推导：

- 每条验收标准可测试、可判断
- 覆盖正常路径和关键异常路径
- 有明确的前置条件、操作步骤、预期结果

## 5. 输出生成

### 5.1 人读产物

写入 `output/prd/prd-{timestamp}.md`。

- 遵循 `templates/prd.md` 骨架
- 写法参考 `references/prd-writing.md`，PRD 必须可独立归档
- 根据实际内容灵活组织，不机械填空
- 禁止出现：anchor_id、rules_ref、prototype_ref、machine_profile、internal_path、prd_ref
- 禁止出现："作为 AI""我建议你""根据规则要求"等 AI 痕迹
- 禁止出现："详见原型""原型已说明""方案中已定义"等跨文档引用——PRD 必须自包含
- 禁止出现原型阶段的界面描述、交互细节、页面布局
- 字段、规则、验收标准均用自然语言和表格描述，不要用 JSON/YAML 格式

### 5.2 机读 metadata

写入 `.pmflow/metadata/prd/prd-{timestamp}.yaml`。

必须包含 `profiles/prd.profile.yaml` 中 `machine_output_requirements` 的全部字段：

```yaml
modules: []
pages: []
business_rules: []
exception_rules: []
permission_rules: []
data_dictionary: []
field_page_map: []
acceptance_criteria: []
source_trace: {}
```

`source_trace` 必须覆盖 BRD、UC、solution、prototype 四个前置阶段的已确认基线。每条 PRD 内容标注其来源阶段和具体位置。无法追溯到任何已确认基线的内容必须标注为 open_question。

### 5.3 更新状态

更新 `.pmflow/status.yaml`：
- `current_stage: prd`
- `artifacts.prd` 追加新文件路径
- 如有新的 open_questions，追加

## 6. 停止并报告

### 6.1 完成输出

```text
PRD 写作完成。

产物：
- output/prd/prd-*.md
- .pmflow/metadata/prd/prd-*.yaml

需要独立审查（请执行 /pm-prd-review）：
- PRD 是否可独立归档
- 是否混入了原型阶段的界面描述
- 数据字典与页面字段是否一致
- 业务规则/异常/权限是否完整
- 验收标准是否可测试
- 人读产物有无机读字段泄漏
- 来源追溯是否覆盖全部前置基线

下一步唯一建议：/pm-prd-review
```

### 6.2 禁止行为

- 不得在 prototype 未确认时执行 prd-writer
- 不得自行扩大 prototype 范围之外的模块、页面或操作
- 不得在 PRD 中生成原型内容或界面描述
- 不得跳过 prd-reviewer 直接提示 /pm-confirm 或任何后续阶段命令
- 不得提示"要我现在做吗"
- 不得以"看起来没问题"为由自动继续
- 不得提示归档、review-pack、export 或任何后续阶段
- 不得写跨文档引用（"详见原型""详见方案"）

## 7. 禁止行为汇总

- 不得在 prototype 未确认时执行
- 不得超出 prototype 范围边界擅自扩展
- 不得将 writer 自身的推测标为 confirmed
- 不得在 PRD 中生成原型界面描述或交互细节
- 不得写跨文档引用——PRD 必须自包含
- 不得执行 reviewer 的自检（PRD 阶段 review 由独立 reviewer 完成）
- 不得在产出后提示 /pm-confirm 或任何后续阶段命令（只提示 /pm-prd-review）
- 不得跨越 PM ownership gate

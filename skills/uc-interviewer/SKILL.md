# uc-interviewer SOP [legacy]

> **legacy**: 此 skill 属于旧主链。新项目请使用 `pm-align` skill。

## 1. 前置读取

执行前必须读取：

- `contracts/input-classification.md`（输入分类契约）
- `contracts/gates.md`（门禁定义，重点 §2 interviewer 自检）
- `profiles/uc.profile.yaml`（UC 产物契约）
- `profiles/brd.profile.yaml`（前置 BRD 契约，理解 BRD 输出结构）
- `schemas/status.schema.yaml`（状态 schema）
- `templates/uc-note.md`（输出骨架参考）
- 已确认的 BRD note（`output/brd/` 下最新文件）
- 已确认的 BRD metadata（`.pmflow/metadata/brd/` 下最新文件）

**禁止**在未读取已确认 BRD 的情况下开始用户路径梳理。

## 2. 前置检查

### 2.1 状态校验

读取 `.pmflow/status.yaml`，确认：

- `current_stage` 为 `uc`；或者 `next_allowed_commands` 包含 `/pm-uc`（PM 确认后授权进入或回归补充）
- `pm_confirmations` 中 brd 已确认（`confirmed: true`）
- `review_results` 中 brd 自检不为 `fail`

如果任一条件不满足：
- 停止。提示 PM 当前状态不满足进入 uc 的条件。
- 推荐 `/pm-guide` 查看当前状态。

### 2.2 BRD 输入校验

确认已读取的 BRD note 包含：

- 业务目标（至少一条可判断的目标）
- 需求方角色（至少一个核心角色）
- 范围边界

如果 BRD 产出不满足上述最低要求：
- 停止。提示 PM 当前 BRD 不足以支撑用户路径梳理。
- 推荐 `/pm-brd` 补充。

## 3. 输入收集与分类

### 3.1 收集补充材料

向 PM 收集本轮补充材料（如有）：
- 用户角色补充说明
- 场景材料
- 现有流程描述
- 补充证据

### 3.2 分类本轮输入

按 `contracts/input-classification.md` 对本轮新增输入分类。分类结果追加到 metadata。

## 4. 访谈方法

### 4.1 识别用户角色

从已确认的 BRD 中提取需求方角色，转化为用户角色：

- 用户角色必须可追溯到 BRD 中的需求方角色
- 不得自行新增 BRD 中未出现的角色
- 如果发现 BRD 中遗漏了重要用户角色，记录到 open_questions，不自行补充

### 4.2 梳理用户路径

为每个核心用户角色梳理主要路径：

- 每条路径有明确的起点（触发条件）和终点（目标达成状态）
- 路径之间需要区分度，不是同一条路径的不同叫法
- 涉及多个角色的路径标注角色交接点

### 4.3 梳理任务流

为关键任务梳理操作流：

- 每个任务流有步骤序列
- 关键决策点标注分支条件
- 涉及系统交互的标注系统行为

### 4.4 差异分析

如果存在现有流程（来自背景材料或补充证据），对比目标流程：

- 标注差异点
- 标注缺口

### 4.5 异常路径

梳理关键异常场景和边界情况。不需要穷举，但核心流程的异常必须覆盖。

## 5. 输出生成

### 5.1 人读产物

写入 `output/uc/uc-note-{timestamp}.md`。

- 遵循 `templates/uc-note.md` 骨架
- 根据实际内容灵活组织
- 禁止出现：anchor_id、rules_ref、prototype_ref、machine_profile、internal_path
- 禁止出现："作为 AI""我建议你""根据规则要求"等 AI 痕迹
- 用户路径和任务流用自然语言描述，不要用 JSON/YAML 格式

### 5.2 机读 metadata

写入 `.pmflow/metadata/uc/uc-{timestamp}.yaml`。

必须包含 `profiles/uc.profile.yaml` 中 `machine_output_requirements` 的全部字段。

### 5.3 更新状态

更新 `.pmflow/status.yaml`：
- `current_stage: uc`
- `artifacts.uc` 追加新文件路径
- 如有新的 open_questions，追加

## 6. 自检

### 6.1 执行自检

对照 `profiles/uc.profile.yaml` 的 `self_check_criteria` 逐项检查：

**fail 判定**：
- 输入类型混淆：背景材料被当作会后回答回填
- 未形成可判断的用户任务
- 关键角色缺失（缺少核心用户角色）
- 用户角色无法追溯到已确认的 BRD
- 当前产出无法支撑进入方案阶段

**warn 判定**：
- 存在未确认项，但不影响进入 solution 做初步方案草稿
- 部分角色/场景细节待补充，但主路径已清楚
- 部分异常路径未完全覆盖，但核心流程完整

**pass 判定**：
- 用户角色、主路径、关键任务流足够支撑下一阶段（solution）
- 四类输入已正确区分
- 未确认项已显式标注在 open_questions 中

### 6.2 写入自检结果

写入 `.pmflow/reviews/uc-self-check-{timestamp}.yaml`：

```yaml
stage: uc
check_type: self_check
verdict: pass | warn | fail
fail_reasons: []
warnings: []
open_questions_after_check: []
checked_at: ""
reviewed_artifact: ""   # 必填：本次生成的人读产物路径（output/uc/uc-note-*.md），不得为空
reviewed_metadata: ""   # 必填：本次生成的机读 metadata 路径（.pmflow/metadata/uc/uc-*.yaml），不得为空
```

`reviewed_artifact` 必须等于本次生成的 `output/uc/uc-note-{timestamp}.md` 实际路径，`reviewed_metadata` 必须等于本次生成的 `.pmflow/metadata/uc/uc-{timestamp}.yaml` 实际路径。两者均不得使用空字符串或占位符落盘。

同步更新 `.pmflow/status.yaml` 的 `review_results`。

## 7. PM ownership gate

### 7.1 停止并报告

自检完成后必须停止。输出格式：

```text
UC 访谈完成。

自检结果：pass / warn / fail

{如果是 fail：阻断原因和需要补充的内容}
{如果是 warn：风险项和待确认问题}

产物：
- output/uc/uc-note-*.md
- .pmflow/metadata/uc/uc-*.yaml
- .pmflow/reviews/uc-self-check-*.yaml

需要 PM 确认（请执行 /pm-confirm）：
- 用户角色是否准确完整
- 用户路径是否覆盖核心场景
- 任务流是否正确
- 未确认项是否可接受

下一步唯一建议：{/pm-confirm（pass 或 warn 时）| /pm-uc（fail 时）}
```

### 7.2 禁止行为

- 不得在 fail 时提示 /pm-solution
- 不得在 PM 确认前开始 solution-writer
- 不得提示"要我现在做吗"
- 不得以"看起来没问题"为由自动继续

## 8. 禁止行为汇总

- 不得在 BRD 未确认时执行 uc-interviewer
- 不得自行新增 BRD 中未出现的用户角色
- 不得将背景材料当作会后回答
- 不得在未提问的情况下虚构 interview_answer
- 不得将 interviewer 自身的推测标为 confirmed
- 不得为了完整感直接生成方案内容
- 不得在 fail 状态下提示下一阶段命令
- 不得跨越 PM ownership gate

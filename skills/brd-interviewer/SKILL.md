# brd-interviewer SOP

## 1. 前置读取

执行前必须读取：

- `contracts/input-classification.md`（输入分类契约）
- `contracts/gates.md`（门禁定义，重点 §2 interviewer 自检）
- `profiles/brd.profile.yaml`（BRD 产物契约）
- `schemas/status.schema.yaml`（状态 schema）
- `templates/brd-note.md`（输出骨架参考）

**禁止**在未完成输入分类前直接生成 BRD note。

## 2. 输入收集

### 2.1 读取状态

读取 `.pmflow/status.yaml`，确认：
- `current_stage` 为 `brd` 或 `uninitialized`；或者 `next_allowed_commands` 包含 `/pm-brd`（PM 确认后授权回归补充）

如果 `current_stage` 为 `solution` / `prototype` / `prd` 且 `next_allowed_commands` 不包含 `/pm-brd`：
- 停止。提示 PM 当前阶段不允许回到 brd，除非显式重置状态。

### 2.2 收集输入材料

向 PM 收集：

- 原始需求（文本、口头描述）
- 背景材料（文档路径、旧系统信息、组织架构等）
- 补充证据（数据、报表、截图等）

如果 PM 未提供背景材料或补充证据，不虚构。

## 3. 输入分类

### 3.1 逐条分类

对 PM 提供的每条输入，按 `contracts/input-classification.md` 分类：

```
输入："我们现在的审批流程是..."
  → source_type: background_material
  → confidence: confirmed（来自已落盘文档）

输入："希望能支持多级审批"
  → source_type: raw_request
  → confidence: unconfirmed（需要进一步确认审批级数）
```

### 3.2 识别并阻断混淆

如果 PM 提供的同一段材料中混合了多种类型：
- 拆分标记，不能笼统归为一类
- 如果无法确定某条材料的类型，标记 `confidence: unconfirmed`，写入 open_questions

### 3.3 背景材料 vs 会后回答

- 背景材料：PM 提供的文档、旧系统截图、流程说明。**不是需求方对问题的回答。**
- 会后回答：必须能对应 interviewer 提出的具体问题。无法对应问题的回答 → 标记为 unconfirmed。

## 4. 访谈方法

### 4.1 提炼业务目标

从原始需求中提炼业务目标。每条业务目标必须：

- 有可判断的成功标准或至少方向性描述
- 不与其它目标重复
- 不是"提升效率""优化体验"等空洞表述

如果原始需求不足以提炼可判断的目标，必须向 PM 提出具体问题。

### 4.2 识别需求方角色

从原始需求和背景材料中识别需求方角色。每个角色必须有：

- 角色标识（如"财务主管""审计员"）
- 对应的关注点或诉求

不得将背景材料中的组织架构直接当作需求方角色——必须经 PM 确认。

### 4.3 划定范围边界

明确什么在范围内、什么不在。范围边界必须具体，不得出现"等""相关""类似"等模糊边界。

## 5. 输出生成

### 5.1 人读产物

写入 `output/brd/brd-note-{timestamp}.md`。

- 遵循 `templates/brd-note.md` 骨架
- 根据实际内容灵活组织，不机械填空
- 禁止出现：anchor_id、rules_ref、prototype_ref、machine_profile、internal_path
- 禁止出现："作为 AI""我建议你""根据规则要求"等 AI 痕迹

### 5.2 机读 metadata

写入 `.pmflow/metadata/brd/brd-{timestamp}.yaml`。

必须包含 `profiles/brd.profile.yaml` 中 `machine_output_requirements` 的全部字段。

### 5.3 更新状态

更新 `.pmflow/status.yaml`：
- `current_stage: brd`
- `artifacts.brd` 追加新文件路径
- 如有新的 open_questions，追加

## 6. 自检

### 6.1 执行自检

对照 `profiles/brd.profile.yaml` 的 `self_check_criteria` 逐项检查：

**fail 判定**：
- 输入类型混淆：背景材料被当作会后回答回填
- 未形成可判断的业务目标
- 关键角色缺失（缺少需求方角色）
- 当前产出无法支撑进入用户路径梳理

**warn 判定**：
- 存在未确认项，但不影响进入 uc 做初步草稿
- 部分角色/场景细节待补充，但主业务目标已清楚
- 部分材料引用自背景文档，尚未经需求方口头确认

**pass 判定**：
- 业务目标、角色、主约束足够支撑下一阶段（uc）
- 四类输入已正确区分
- 未确认项已显式标注在 open_questions 中

### 6.2 写入自检结果

写入 `.pmflow/reviews/brd-self-check-{timestamp}.yaml`：

```yaml
stage: brd
check_type: self_check
verdict: pass | warn | fail
fail_reasons: []
warnings: []
open_questions_after_check: []
checked_at: ""
reviewed_artifact: ""   # 必填：本次生成的人读产物路径（output/brd/brd-note-*.md），不得为空
reviewed_metadata: ""   # 必填：本次生成的机读 metadata 路径（.pmflow/metadata/brd/brd-*.yaml），不得为空
```

`reviewed_artifact` 必须等于本次生成的 `output/brd/brd-note-{timestamp}.md` 实际路径，`reviewed_metadata` 必须等于本次生成的 `.pmflow/metadata/brd/brd-{timestamp}.yaml` 实际路径。两者均不得使用空字符串或占位符落盘。

同步更新 `.pmflow/status.yaml` 的 `review_results`。

## 7. PM ownership gate

### 7.1 停止并报告

自检完成后必须停止。输出格式：

```text
BRD 访谈完成。

自检结果：pass / warn / fail

{如果是 fail：阻断原因和需要补充的内容}
{如果是 warn：风险项和待确认问题}

产物：
- output/brd/brd-note-*.md
- .pmflow/metadata/brd/brd-*.yaml
- .pmflow/reviews/brd-self-check-*.yaml

需要 PM 确认（请执行 /pm-confirm）：
- 业务目标是否准确
- 需求方角色是否完整
- 范围边界是否认可
- 未确认项是否可接受

下一步唯一建议：{/pm-confirm（pass 或 warn 时）| /pm-brd（fail 时）}
```

### 7.2 禁止行为

- 不得在 fail 时提示 /pm-uc
- 不得在 PM 确认前开始 uc-interviewer
- 不得提示"要我现在做吗"
- 不得以"看起来没问题"为由自动继续

## 8. 禁止行为汇总

- 不得将背景材料当作会后回答
- 不得在未提问的情况下虚构 interview_answer
- 不得将 interviewer 自身的推测标为 confirmed
- 不得将组织架构直接当作需求方角色
- 不得为了完整感直接生成方案内容
- 不得在 fail 状态下提示下一阶段命令
- 不得跨越 PM ownership gate

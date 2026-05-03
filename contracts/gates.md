# PMFlow 门禁规则

## 1. 判定级别

所有门禁使用三级判定：

| 级别 | 含义 | 新主链后续行为 | legacy 主链后续行为 |
|---|---|---|---|
| `pass` | 满足进入下一阶段的条件 | reviewer/writer 建议下一步命令并停止，PM 手动执行 | PM 执行 /pm-confirm 后进入下一阶段 |
| `warn` | 存在未确认项或风险，但不阻断 | 同 pass，风险项记录到 open_questions | PM 知情确认后可继续，风险项记录到 open_questions |
| `fail` | 存在阻断性缺陷 | 必须回到当前阶段修正，PM 不可越权推进 | 必须回到当前阶段修正，PM 不可越权推进 |

## 2. interviewer 自检门禁（brd、uc）

interviewer 阶段不设独立 reviewer skill。门禁由 interviewer 在生成 note 后执行**自我检查**。

### 2.1 自检判定标准

**fail（阻断）**：

- 输入类型混淆：背景材料被当作会后回答回填
- 未形成可判断的业务目标（brd）/ 可判断的用户任务（uc）
- 关键角色缺失（brd 缺少需求方角色 / uc 缺少核心用户角色）
- 当前产出无法支撑进入下一阶段的基本判断

**warn（风险记录）**：

- 存在未确认项，但不影响下一阶段先做草稿
- 部分角色/场景的细节待补充，但主路径已清楚
- 部分材料引用自背景文档，尚未经需求方口头确认

**pass（通过）**：

- 业务目标、角色、主任务、关键约束足够支撑下一阶段
- 原始需求、背景材料、会后回答已正确区分
- 未确认项已显式标注

### 2.2 自检输出

自检结果写入 `.pmflow/reviews/{stage}-self-check-*.yaml`。`reviewed_artifact` 和 `reviewed_metadata` 为**必填字段**，必须分别等于本次生成的人读产物路径和机读 metadata 路径，不得为空：

```yaml
stage: brd
check_type: self_check
verdict: pass | warn | fail
fail_reasons: []
warnings: []
open_questions_after_check: []
checked_at: ""
reviewed_artifact: ""   # 必填：本次生成的人读产物路径
reviewed_metadata: ""   # 必填：本次生成的机读 metadata 路径
```

### 2.3 fail 处理

- fail 时不得提示下一阶段命令
- 只能提示回到当前 interviewer 补充
- PM 不可跳过 fail 直接进入下一阶段

## 3. reviewer 门禁（solution、prototype、prd）

solution、prototype、prd 阶段各有一个独立的 reviewer skill。

新主链 reviewer 门禁（align、design）：

align、design 阶段各有一个独立的 reviewer skill。规则与 solution/prototype/prd 的 reviewer 门禁一致。

### 3.1 reviewer 独立检查

reviewer 必须：

- 独立读取 writer 产出的 `output/` 人读文件和 `.pmflow/metadata/` 机读文件
- 对照当前阶段的 `profiles/{stage}.profile.yaml` 逐项检查
- 对照 prd.machine.yaml 中对应 stage_contracts 的 checks 清单
- 输出独立判定：pass / warn / fail

reviewer 不得：

- 复述 writer 的判断或措辞
- 在未逐项检查的情况下给 pass
- 用"整体完整，可以进入下一步"替代逐项判定

### 3.2 reviewer 阻断权

- `reviewer_blocking: true`：reviewer 判定 fail 时，PM 不可越权推进
- `pm_override_allowed: false`：PM 不能以"我先看看下一阶段"为由跳过 reviewer 阻断
- fail 状态下，唯一允许的下一步是回到 writer 修正

### 3.3 fail / warn / pass 细则

**fail（阻断）**：任一项 stage_contracts checks 不满足且属于结构性缺失

**warn（风险通过）**：checks 基本满足但存在边缘情况或数据不充分

**pass（通过）**：全部 checks 满足

## 4. PM ownership gate

### 4.1 新主链（input -> align -> design -> wireframe -> prd -> prototype）

新主链不使用 `/pm-confirm`。阶段完成后：

- 阶段产物已落盘（`output/` 和 `.pmflow/` 均有对应文件）
- reviewer 或自检已给出 verdict
- reviewer 或 writer 输出下一步建议并**停止**
- PM 阅读人读产物后**手动执行下一命令**

writer 执行成功后自行更新 `current_stage`。reviewer 不修改 `current_stage`。

新主链禁止行为：

- review 通过后自动执行下一阶段命令
- 修改下游产物后自动同步所有其他产物
- 用户要求"顺便继续"时跨阶段执行
- 用旧 review 放行新产物
- 在未做 impact analysis 时直接改文件

### 4.2 legacy 主链（brd -> uc -> solution -> prototype -> prd）

legacy 主链使用 `/pm-confirm` 完成 PM ownership gate：

- 阶段产物已落盘
- reviewer 或自检已给出 verdict
- PM 已阅读人读产物
- PM 显式执行 `/pm-confirm` 完成确认（推进 `current_stage`，写回 `pm_confirmations`、`approved_baselines`、`next_allowed_commands`）
- 下一步只提示命令名，不代执行

确认由 `/pm-confirm` 统一处理，规则见 `contracts/confirmation.md`。

PM 执行 `/pm-confirm` 之前，不得：

- 开始下一阶段的 writer
- 将确认自动写入 status
- 提示"要我现在做吗"
- 以"看起来没问题"为由自动继续

## 5. 阶段推进规则

- 显式命令触发 → 读状态 → 读 skill → 执行 → 门禁 → 停下
- 跨阶段必须由 PM 输入下一命令
- 自然语言只用于补材料、回答问题、澄清疑问
- `继续` / `下一步` 不跨阶段，只汇报当前阶段和下一步命令

## 6. 门禁枚举值

为避免脚本和 YAML 中的编码歧义，统一使用以下值：

```yaml
verdict:
  - pass
  - warn
  - fail

check_type:
  - self_check      # interviewer 自检
  - reviewer_check  # reviewer 独立检查

current_stage:
  - uninitialized
  - input
  - align
  - design
  - wireframe
  - prd
  - prototype
  # legacy
  - brd
  - uc
  - solution
  # 新主链 writer 执行成功后更新 current_stage；reviewer 不推进 current_stage
  # pm-guide 可结合 current_stage、artifacts、review_results 判断进度
```

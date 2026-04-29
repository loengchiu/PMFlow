# pm-confirm SOP

## 1. 前置读取

执行前必须读取：

- `contracts/confirmation.md`（确认契约）
- `contracts/gates.md`（门禁定义，重点 §4 PM ownership gate）
- `schemas/status.schema.yaml`（状态 schema）

**禁止**读取任何项目业务文件。

## 2. 状态校验

### 2.1 status.yaml 必须存在

读取 `.pmflow/status.yaml`。如果不存在：
- 停止。项目未初始化，无产物可确认。
- 提示：请先执行 `/pm-brd` 开始需求访谈。

### 2.2 提取当前状态

从 status.yaml 读取：
- `current_stage`
- `artifacts`
- `review_results`
- `pm_confirmations`

如果 `current_stage` 为 `uninitialized`：
- 停止。未有阶段产物，无法确认。

## 3. 前置条件校验

按 `contracts/confirmation.md` §2 逐项校验。

### 3.1 产物存在

检查 `artifacts.<current_stage>` 非空，且路径指向的文件确实存在。

不满足：
- 停止。当前阶段无产物。
- 提示：请先执行当前阶段命令生成产物。

### 3.2 自检/review 已完成

检查 `review_results` 中是否存在当前阶段的检查记录。

不满足：
- 停止。当前阶段未完成自检或审查。
- 提示对应的检查命令（如 /pm-solution-review）。

### 3.3 非 fail 状态

检查当前阶段最近一次检查的 `verdict`。

如果 `verdict == fail`：
- **拒绝确认。**
- 输出 fail 原因（来自 review_results 的 fail_reasons）。
- 唯一建议：回到当前阶段修正（`/pm-<current_stage>`）。
- **PM 不可越权确认。**

### 3.4 审查产物与最新产物一致性

检查当前阶段最近一次 review/self-check 的 `reviewed_artifact` 和 `reviewed_metadata`：

- `reviewed_artifact` 必须等于 `artifacts.<current_stage>` 中的**最新**产物路径（数组最后一条记录）
- `reviewed_metadata` 必须等于对应的最新 metadata 文件路径（`.pmflow/metadata/<current_stage>/` 下最新文件）

如果 `reviewed_artifact` 或 `reviewed_metadata` 为空，或与最新产物路径不一致：
- **拒绝确认。**
- 原因：审查记录绑定的产物与当前最新产物不一致。产物可能在审查后被重新生成，旧审查已失效。
- 唯一建议：重新执行当前阶段的审查或自检（如 `/pm-solution-review` 或 `/pm-<current_stage>`）。
- **PM 不可越权确认。**

## 4. 确认执行

### 4.1 通过校验后

确认当前阶段，按 `contracts/confirmation.md` §4 写回 status.yaml。

### 4.2 warn 处理

如果当前阶段 verdict 为 `warn`：
- 将 review_results 中的 warnings 写入 `open_questions`
- 确认仍然允许，但风险已记录

### 4.3 写回字段

```yaml
current_stage: <下一阶段>  # 按 §4.5 映射推进

pm_confirmations:
  - stage: <当前阶段>
    artifact: <artifacts 中当前阶段产物路径>
    confirmed: true
    confirmed_at: <当前 ISO8601 时间戳>
    confirmed_by: PM

approved_baselines:
  - stage: <当前阶段>
    artifact_path: <artifacts 中当前阶段产物路径>
    confirmed_at: <当前 ISO8601 时间戳>

next_allowed_commands: <按 confirmation.md §4.1 映射>
```

### 4.4 确认阶段映射

| current_stage | next_allowed_commands |
|--------------|----------------------|
| brd | [/pm-uc, /pm-brd] |
| uc | [/pm-solution, /pm-uc] |
| solution | [/pm-proto, /pm-solution] |
| prototype | [/pm-prd, /pm-proto] |
| prd | []（主链路完成） |

### 4.5 推进 current_stage

| 当前阶段 | 推进后 current_stage |
|---------|---------------------|
| brd | uc |
| uc | solution |
| solution | prototype |
| prototype | prd |
| prd | prd（不变，主链路终点） |

## 5. 输出

### 5.1 确认成功

如果当前阶段不是 prd（终端阶段）：

```text
PM 确认完成。

阶段：{stage}
产物：{artifact_path}
确认时间：{timestamp}
自检/review 结果：{verdict}
{如果是 warn：风险项已记录到 open_questions}

已确认基线：
- {stage}: {artifact_path}

下一步唯一建议：{next_allowed_commands[0]}
```

如果当前阶段是 prd（终端阶段）：

```text
PM 确认完成。

阶段：prd
产物：{artifact_path}
确认时间：{timestamp}
自检/review 结果：{verdict}
{如果是 warn：风险项已记录到 open_questions}

已确认基线：
- prd: {artifact_path}

主链路完成，PRD 可归档。
```

### 5.2 确认被拒（fail）

```text
PM 确认被拒绝。

原因：当前阶段自检/review 结果为 fail。
阻断项：
- {fail_reasons}

PM 不可越权推进。唯一允许的操作：回到当前阶段修正。

下一步唯一建议：/pm-{current_stage}
```

## 6. 停止条件

- 输出确认结果后**必须停止**
- 不得在确认后自动执行下一步命令
- 不得提示"要我现在做吗"
- 不得跳过确认直接开始下一阶段

## 7. 禁止行为汇总

- 不得在 fail 状态下确认
- 不得在无产物时确认
- 不得在无自检/review 时确认
- 不得在确认时生成新产物
- 不得修改 artifacts、review_results、project_name 及未列出的字段（允许修改的字段见 contracts/confirmation.md §6）
- 不得自动将确认写入 status（必须 PM 显式执行 /pm-confirm）

# PM 确认契约

所有阶段（含 interviewer）完成后，必须通过显式 `/pm-confirm` 命令完成 PM ownership gate。本文件定义确认的规则、前置条件和写回字段。

## 1. 确认流程

```
阶段完成（产物落盘 + 自检/review 落盘）
  → interviewer/writer/reviewer 提示 /pm-confirm
  → PM 阅读人读产物
  → PM 执行 /pm-confirm
  → pm-confirm 校验前置条件
  → 写回 .pmflow/status.yaml
  → 提示唯一下一步命令
  → 停止
```

## 2. 前置条件校验

pm-confirm 必须校验以下条件，任一不满足则拒绝确认：

### 2.1 产物存在

- `artifacts.<current_stage>` 非空
- 路径指向的文件确实存在于磁盘

### 2.2 自检/review 已完成

- `review_results` 中存在当前阶段的检查记录
- 检查记录的 `check_type` 为 `self_check`（brd/uc）或 `reviewer_check`（solution/prototype/prd）

### 2.3 非 fail 状态

- 当前阶段最近一次检查的 `verdict` 不是 `fail`
- **fail 时 PM 不可越权确认**。唯一允许的操作是回到当前阶段修正。

### 2.4 审查产物与最新产物一致

- 当前阶段最近一次检查的 `reviewed_artifact` 必须等于 `artifacts.<current_stage>` 中的最新产物路径
- 当前阶段最近一次检查的 `reviewed_metadata` 必须等于 `.pmflow/metadata/<current_stage>/` 下的最新 metadata 文件路径
- `reviewed_artifact` 和 `reviewed_metadata` 为所有 self_check / reviewer_check 的**必填字段**，不得为空
- 不一致或为空 → 产物在审查后被重新生成，旧审查已失效，必须重新审查/自检
- **不一致时 PM 不可越权确认**。

## 3. fail / warn / pass 三种状态下的确认行为

| 状态 | 是否可确认 | 行为 |
|------|-----------|------|
| pass | 是 | 正常确认，写回确认记录和基线 |
| warn | 是 | 确认同时将 warn 项写入 open_questions，写回确认记录和基线 |
| fail | 否 | 拒绝确认，提示回到当前阶段修正。PM 不可 override。 |

## 4. 写回字段

确认成功后，写回 `.pmflow/status.yaml`：

```yaml
pm_confirmations:
  - stage: <current_stage>
    artifact: <当前阶段产物路径>
    confirmed: true
    confirmed_at: <ISO8601 时间戳>
    confirmed_by: PM

approved_baselines:
  - stage: <current_stage>
    artifact_path: <当前阶段产物路径>
    confirmed_at: <ISO8601 时间戳>

next_allowed_commands:
  - <下一阶段命令>
  - <当前阶段命令>  # 允许回到当前阶段补充
```

### 4.1 阶段推进与命令映射

确认成功后，`current_stage` 推进到下一阶段，同时写入 `next_allowed_commands`：

| 当前阶段 | 确认后 current_stage | next_allowed_commands |
|---------|---------------------|----------------------|
| brd | uc | [/pm-uc, /pm-brd] |
| uc | solution | [/pm-solution, /pm-uc] |
| solution | prototype | [/pm-proto, /pm-solution] |
| prototype | prd | [/pm-prd, /pm-proto] |
| prd | prd（不变，主链路终点） | [] |

`current_stage` 推进代表 PM 已确认当前阶段产物，项目进入下一阶段工作。`next_allowed_commands` 的第二项为回归命令，允许 PM 回到当前阶段补充。

## 5. 确认后行为

- 输出确认摘要（阶段、产物、确认时间）
- 提示唯一下一步命令（由 next_allowed_commands[0] 给出）
- **停止。不自动执行下一步。**

## 6. 允许修改的字段

确认时只允许修改以下字段：

- `current_stage`：按 §4.1 推进到下一阶段
- `pm_confirmations`：追加确认记录
- `approved_baselines`：追加基线记录
- `next_allowed_commands`：按 §4.1 写入
- `open_questions`：warn 时追加风险项

不得修改 `artifacts`、`review_results`、`project_name` 及其他未列出的字段。

## 7. 禁止事项

- 不得在 fail 状态下确认
- 不得跳过确认直接进入下一阶段
- 不得在确认时生成新产物
- 不得在 PM 未执行 /pm-confirm 的情况下自动将确认写入 status

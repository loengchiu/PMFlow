# 新主链硬约束

本文件定义 PMFlow 新主链的红线规则，所有 skill、command、profile、schema 必须遵守。

## 1. 阶段定义

新主链阶段：

```text
input -> align -> design -> wireframe -> prd -> prototype
```

## 2. 推进机制

新主链**不使用**以下机制作为推进条件：

- `/pm-confirm` 命令
- `pm_confirmations` 字段
- `approved_baselines` 字段
- `next_allowed_commands` 字段

以上机制仅 legacy 主链使用。

## 3. legacy 兼容

legacy 主链（brd -> uc -> solution -> prototype -> prd）仍可使用 `/pm-confirm`。legacy 主链的推进依赖 `pm_confirmations`、`approved_baselines`、`next_allowed_commands`。

## 4. 新旧链判定

`current_stage` 为 `prototype` 或 `prd` 时，不能单独通过 stage 值判断新旧链。必须结合 `workflow_mode` 字段或 legacy marker 判定。

`workflow_mode` 取值：

- `new_main`：新主链
- `legacy`：legacy 主链

旧项目如果 `status.yaml` 中没有 `workflow_mode` 字段，`pm-guide` 必须用以下规则推断（按优先级从高到低）：

1. `current_stage` 为 brd/uc/solution → legacy
2. `artifacts.solution` 为非空数组且至少一个路径对应文件存在于磁盘 → legacy
3. `pm_confirmations` 中存在 `confirmed: true` 且 `stage` 为 solution 或 prototype 的记录 → legacy
4. 以上均不满足 → new_main

推断时禁止以下行为：

- `artifacts.solution` 为空数组 `[]` 或字段不存在 → 不得判为 legacy
- `pm_confirmations` 为空数组 `[]`、字段不存在、或所有记录 `confirmed: false` → 不得判为 legacy
- `pm_confirmations` 中仅存在 brd/uc 阶段记录 → 不得判为 legacy（brd/uc 可能是新链 input 阶段的旧命名迁移）
- 仅凭 `current_stage` 为 prototype 或 prd → 不得判为 legacy（新旧链均可能到达此阶段）

## 5. legacy 命令说明

legacy 命令（pm-brd、pm-uc、pm-solution、pm-solution-review、pm-proto、pm-proto-review、pm-confirm）：

- **不得**在 `workflow_mode: new_main` 时触发
- 必须分流到对应的 new_main 命令并停止
- 不生成新主链产物
- 不修改 new_main 的 `current_stage`

## 6. writer 准入规则

writer 准入依据：

- 上游 self_check 或 review 的 verdict 为 `pass` 或 `warn`
- `reviewed_artifact` 等于上游最新产物路径
- `reviewed_metadata` 等于上游最新 metadata 路径

不要求 `current_stage` 已经等于当前阶段。writer 执行成功后才更新 `current_stage`。

## 7. reviewer 规则

reviewer 不推进 `current_stage`。reviewer 只输出 verdict 和下一步建议，然后停止。

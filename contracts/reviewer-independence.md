# Reviewer 独立审查契约

## 适用范围

所有 `/pm-*-review` 和 `/pm-fix-review`。

## 触发规则

- review 不由 hook 自动触发。
- writer 完成后只提示下一步 review 命令，不得自动调用 reviewer。
- review 由 PM 手动执行对应命令启动。

## 宿主能力分级

- Claude Code：优先使用 `pmflow-reviewer` subagent 执行审查。如果 subagent 不可用，必须说明原因，再按独立审查模式执行。
- Codex：可使用 subagent / dedicated reviewer，但不作为 PMFlow 主流程依赖。
- Trae-CN：默认使用独立审查模式。
- 其他宿主：默认使用独立审查模式。

## Claude Code subagent 路径

- `pmflow-reviewer` subagent 负责独立读取和审查，返回结构化结果（`PMFLOW-REVIEW-RESULT`）。
- 主会话负责根据 subagent 结果写入 review 文件，并追加 `status.review_results`。
- subagent 默认不直接写文件。

## 独立审查模式要求

- 不继承 writer 的解释、结论和会话记忆。
- 必须重新读取 `.pmflow/status.yaml`。
- 必须重新读取当前阶段人读产物。
- 必须重新读取当前阶段 metadata。
- 必须读取对应 profile。
- 必须读取相关 contracts。
- 必须基于产物和 metadata 自行判断 pass/warn/fail。
- 不得因为 writer 声称已完成就放行。
- 不得修改被审产物、metadata、snapshot、current_stage。
- 只允许写 review 文件，并追加 status.review_results。

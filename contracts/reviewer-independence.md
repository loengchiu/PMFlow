# Reviewer 独立审查契约

## 适用范围

所有 `/pm-*-review` 和 `/pm-fix-review`。

## 触发规则

- review 不由 hook 自动触发。
- writer 完成后只提示下一步 review 命令，不得自动调用 reviewer。
- review 由 PM 手动执行对应命令启动。

## 宿主能力分级

- Claude Code：优先使用可直接调用的 `pmflow-reviewer` subagent 执行审查。
- Claude Desktop / Codex 等宿主：如果不能直接调用 `pmflow-reviewer`，但可调用 `general-purpose`，必须把最新版 `agents/pmflow-reviewer.md`、当前 reviewer `SKILL.md`、阶段名和项目路径传给 `general-purpose` 执行。
- Trae-CN：默认使用独立审查模式。
- 其他宿主：默认使用独立审查模式。

## subagent 可用判定

- `pmflow-reviewer` 可用，指当前宿主的 Agent 工具可直接以 `pmflow-reviewer` 作为 agent type 调用，或实际调用 `pmflow-reviewer` 成功。
- `C:\Users\...\agents\pmflow-reviewer.md` 文件存在，只能证明 agent 定义已安装，不能证明当前会话可调用。
- 如果只能读取 agent 文件但不能直接调用 `pmflow-reviewer`，不得声称 `pmflow-reviewer subagent 已就绪`。

## subagent 路径

- `pmflow-reviewer` subagent 负责独立读取和审查，返回结构化结果（`PMFLOW-REVIEW-RESULT`）。
- `general-purpose` 仅作为承载器使用，不等同于 `pmflow-reviewer`；必须传入 `agents/pmflow-reviewer.md` 后才可按 PMFlow reviewer 模式执行。
- 主会话负责根据 subagent 结果写入 review 文件，并追加 `status.review_results`。
- subagent 默认不直接写文件。
- review 结果必须记录实际执行方式：
  - `reviewer_agent_type`: `pmflow-reviewer` / `general-purpose` / `none`
  - `reviewer_prompt_source`: `agent_type` / `agents/pmflow-reviewer.md` / `contracts/reviewer-independence.md`
  - `reviewer_mode`: `pmflow-reviewer` / `pmflow-reviewer-prompt` / `independent-current-session`

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

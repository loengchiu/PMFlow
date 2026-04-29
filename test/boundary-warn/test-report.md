# 边界测试：warn + open_questions 记录

> 测试目标：验证 verdict=warn 时 pm-confirm 允许确认，并将 warnings 写入 open_questions
> 对应合约：`contracts/confirmation.md` §3, §4 | `contracts/gates.md` §1, §2.2
> 对应 SOP：`skills/pm-confirm/SKILL.md` §4.2

## 可执行验证

```bash
python scripts/pmflow-gate-boundary-smoke.py
```

脚本中 `test_boundary_warn()` 函数对该场景执行 7 项断言。

## 执行结果（2026-04-30）

```
=== boundary-warn: verdict=warn + open_questions ===
  PASS  current_stage = uc
  PASS  review_results has uc entry
  PASS  verdict = warn
  PASS  warnings non-empty (>=1)
  PASS  reviewed_artifact matches artifacts.uc latest
  PASS  open_questions has existing entries
  PASS  brd confirmed, uc NOT confirmed (awaiting PM confirm)
```

## 场景描述

uc 阶段（interviewer 自检），verdict 为 **warn**，包含 2 项风险：
1. 部分异常路径（网络超时、并发冲突）尚未详细讨论
2. 移动端审批场景的交互细节待确认

PM 执行 `/pm-confirm`。确认应**被允许**，同时 warnings 应追加到 `open_questions`。

## 合约-SOP-断言对照表

| # | 合约条款 | pm-confirm SOP 步骤 | 断言 | 结果 |
|---|---------|-------------------|------|------|
| 1 | — | §2.2 提取 current_stage | current_stage = uc | ✅ |
| 2 | confirmation.md §2.2 | §3.2 自检/review 已完成 | review_results 有 uc 条目 | ✅ |
| 3 | confirmation.md §3, gates.md §1 | §3.3 非 fail 检查 | verdict = warn（非 fail，不阻断） | ✅ |
| 4 | confirmation.md §3 | §4.2 warn 处理 | warnings 非空，count=2 | ✅ |
| 5 | confirmation.md §2.4 | §3.4 一致性检查 | reviewed_artifact 与 artifacts.uc 最新一致 | ✅ |
| 6 | confirmation.md §3 | §4.2 写入 open_questions | open_questions 已有条目（brd 遗留 Q001） | ✅ |
| 7 | confirmation.md §4 | §4.1 阶段推进 | brd 已确认，uc 尚未确认（等待 PM） | ✅ |

## 确认后 status.yaml 预期变化（需 Claude Code 运行时验证）

```yaml
current_stage: solution       # uc → solution
next_allowed_commands: [/pm-solution, /pm-uc]
pm_confirmations:             # 追加 uc 条目
  - stage: uc
    artifact: output/uc/uc-note-warn-test.md
    confirmed: true
    confirmed_by: PM
approved_baselines:           # 追加 uc 条目
  - stage: uc
    artifact_path: output/uc/uc-note-warn-test.md
open_questions:               # 保留 Q001 + 追加 Q002, Q003
  - id: Q002
    question: "部分异常路径（网络超时、并发冲突）尚未详细讨论"
    status: open
  - id: Q003
    question: "移动端审批场景的交互细节待确认"
    status: open
```

## 验证清单

- [x] current_stage = uc（fixture 正确：warn 发生在 uc 阶段）
- [x] verdict = warn，非 pass 非 fail（脚本断言）
- [x] warnings 非空，含 2 项风险（脚本断言：count=2）
- [x] reviewed_artifact 与 artifacts.uc 最新一致（脚本断言：字符串比对）
- [x] open_questions 已存在 Q001（brd 阶段遗留，脚本断言 count≥1）
- [x] pm_confirmations 中 brd 已确认，uc 未确认（脚本断言：brd 有、uc 无）
- [ ] pm-confirm 执行后 open_questions 新增 Q002, Q003（需 Claude Code 运行时验证）
- [ ] pm-confirm 输出包含「风险项已记录到 open_questions」（需 Claude Code 运行时验证）
- [ ] 下一步建议为 /pm-solution（需 Claude Code 运行时验证）

## 无法自动验证的部分

warn 场景的完整验证分为两层：
1. **静态 fixture 层**（脚本覆盖）：warn 状态字段正确，前置条件满足，不触发 fail 阻断
2. **运行时层**（需 Claude Code 手动执行）：pm-confirm 实际写回 open_questions、推进 current_stage、输出风险提示文本

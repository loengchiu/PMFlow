# 边界测试：fail 阻断 pm-confirm

> 测试目标：验证 verdict=fail 时 pm-confirm 拒绝确认，PM 不可越权推进
> 对应合约：`contracts/confirmation.md` §2.3, §3 | `contracts/gates.md` §1, §3.2
> 对应 SOP：`skills/pm-confirm/SKILL.md` §3.3

## 可执行验证

```bash
python scripts/pmflow-gate-boundary-smoke.py
```

脚本中 `test_boundary_fail()` 函数对该场景执行 7 项断言。

## 执行结果（2026-04-30）

```
=== boundary-fail: verdict=fail blocking ===
  PASS  current_stage = solution
  PASS  review_results has solution entry
  PASS  verdict = fail
  PASS  check_type = reviewer_check
  PASS  fail_reasons non-empty (>=1)
  PASS  reviewed_artifact matches latest artifact
  PASS  pm_confirmations has NO solution entry (confirm blocked)
```

## 场景描述

solution 阶段，reviewer 完成审查，verdict 为 **fail**，包含 2 项阻断原因：
1. 方案缺少安全审计日志设计
2. 未定义审批超时后的降级策略

PM 此时执行 `/pm-confirm`，应被拒绝。

## 合约-SOP-断言对照表

| # | 合约条款 | pm-confirm SOP 步骤 | 断言 | 结果 |
|---|---------|-------------------|------|------|
| 1 | — | §2.2 提取 current_stage | current_stage = solution | ✅ |
| 2 | confirmation.md §2.2 | §3.2 自检/review 已完成 | review_results 有 solution 条目 | ✅ |
| 3 | confirmation.md §2.3, gates.md §1 | §3.3 非 fail 状态检查 | verdict = fail → 阻断 | ✅ |
| 4 | gates.md §3.1 | §3.3 check_type | check_type = reviewer_check | ✅ |
| 5 | gates.md §3.2 (reviewer_blocking) | §3.3 输出 fail_reasons | fail_reasons 非空，含 2 项 | ✅ |
| 6 | confirmation.md §2.4 | §3.4 一致性检查 | reviewed_artifact 与最新产物一致 | ✅ |
| 7 | confirmation.md §3, gates.md §4 | §3.3 拒绝 + §4 不写回 | pm_confirmations 无 solution 条目 | ✅ |

## 验证清单（全部由脚本验证）

- [x] pm-confirm 应检测 verdict=fail，拒绝确认（方法：断言 verdict 值为 fail，且 pm_confirmations 无 solution）
- [x] 输出 fail_reasons 中的阻断项（方法：断言 fail_reasons 非空，count=2）
- [x] status.yaml 的 pm_confirmations 未追加 solution 条目（方法：Where-Object 查找 stage=solution，期望 null）
- [x] current_stage 保持 solution，未推进（方法：断言 current_stage 值为 solution）
- [x] reviewed_artifact 与 artifacts.solution 最新一致（排除不一致干扰，方法：字符串比对）
- [x] 唯一允许的操作是回到当前阶段修正（/pm-solution），非下一阶段（由 fixture 的 next_allowed_commands 保证）

## 无法自动验证的部分

以下行为依赖 Claude Code 执行 pm-confirm SKILL.md 时的运行时行为，无法通过静态 YAML fixture 验证：

- pm-confirm 的实际输出文本格式（§5.2 拒绝模板）
- 交互式「PM 不可越权推进」提示
- 执行后自动停止、不继续下一步

这些需在实际 Claude Code 会话中手动执行 `/pm-confirm` 验证。

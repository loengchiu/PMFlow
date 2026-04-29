# 边界测试：产物重新生成导致 reviewed_artifact 不一致

> 测试目标：验证审查后产物被重新生成时，pm-confirm 拒绝确认（旧审查失效）
> 对应合约：`contracts/confirmation.md` §2.4, §3.4
> 对应 SOP：`skills/pm-confirm/SKILL.md` §3.4

## 可执行验证

```bash
python scripts/pmflow-gate-boundary-smoke.py
```

脚本中 `test_boundary_stale_review()` 函数对该场景执行 6 项断言。

## 执行结果（2026-04-30）

```
=== boundary-stale-review: review-artifact mismatch ===
  PASS  artifacts.solution has >=2 versions
  PASS  latest artifact is v2
  PASS  reviewed_artifact points to v1 (stale)
  PASS  reviewed_artifact != latest artifact (MUST reject confirm)
  PASS  verdict = pass (testing mismatch, not fail)
  PASS  pm_confirmations has NO solution entry
```

## 场景时间线

1. writer 生成 v1 (`solution-note-stale-test.md`)
2. reviewer 审查 v1，verdict=pass，`reviewed_artifact` 绑定 v1
3. writer 重新生成 v2 (`solution-note-stale-test-v2.md`)，修改了核心流程
4. PM 尝试 `/pm-confirm`
5. ⛔ reviewed_artifact (v1) ≠ artifacts.solution 最新 (v2) → 拒绝确认

## 版本差异

| | v1（已审查） | v2（最新，未审查） |
|------|------------|-----------------|
| 文件名 | solution-note-stale-test.md | solution-note-stale-test-v2.md |
| 核心流程 | 3 步：专员→经理→财务 | 4 步：专员→经理→(金额>10万?总监)→财务 |

## 合约-SOP-断言对照表

| # | 合约条款 | pm-confirm SOP 步骤 | 断言 | 结果 |
|---|---------|-------------------|------|------|
| 1 | — | §3.1 产物存在 | artifacts.solution 有 2 个版本 | ✅ |
| 2 | — | §3.4 最新产物识别 | 最新产物为 v2（文件名含 v2） | ✅ |
| 3 | — | §3.4 审查绑定检查 | reviewed_artifact 指向 v1（不含 v2） | ✅ |
| 4 | confirmation.md §2.4 | §3.4 一致性检查 | reviewed_artifact ≠ latest → 拒绝 | ✅ |
| 5 | confirmation.md §2.4 | §3.4 排除 fail 干扰 | verdict = pass（仅测不一致场景） | ✅ |
| 6 | confirmation.md §2.4 | §3.4 不写回确认 | pm_confirmations 无 solution 条目 | ✅ |

## 验证清单

- [x] artifacts.solution 包含 v1 和 v2，v2 是最新（脚本断言：count=2, v2 match）
- [x] review_results 中 solution 的 reviewed_artifact 指向 v1（脚本断言：匹配 stale-test.md 不含 v2）
- [x] reviewed_artifact (v1) ≠ artifacts.solution 最新 (v2)（脚本断言：字符串不等）
- [x] verdict = pass（排除 fail 阻断干扰，脚本断言）
- [x] pm_confirmations 无 solution 条目（脚本断言：确认从未发生）
- [ ] pm-confirm 输出「审查记录绑定的产物与最新产物不一致」（需 Claude Code 运行时验证）
- [ ] pm-confirm 输出「唯一建议：/pm-solution-review」（需 Claude Code 运行时验证）
- [ ] v1 和 v2 文件均实际存在于磁盘（fixture 保证，文件已创建）

## 无法自动验证的部分

- pm-confirm 实际输出文本中是否包含「旧审查已失效」描述
- 重新审查后（/pm-solution-review）reviewed_artifact 是否会正确更新到 v2
- PM 能否通过其他命令绕过（/pm-proto 等），需在运行时验证 next_allowed_commands 不包含跨阶段命令

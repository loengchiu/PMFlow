# 边界测试：前置基线不一致（24 条件中条件 3 失败）

> 测试目标：验证前置基线不一致时，prd-writer/prd-reviewer 应检测到并阻止继续
> 对应合约：`contracts/confirmation.md` §4 | E2E 报告 §6 前置基线一致性
> 相关 skill：prd-writer SKILL.md, prd-reviewer SKILL.md（前置校验逻辑）

## 可执行验证

```bash
python scripts/pmflow-gate-boundary-smoke.py
```

脚本中 `test_boundary_baseline_mismatch()` 函数对该场景执行 9 项断言。

## 执行结果（2026-04-30）

```
=== boundary-baseline-mismatch: baseline path mismatch ===
  PASS  current_stage = prd
  PASS  artifacts.solution has latest artifact
  PASS  approved_baselines has solution entry
  PASS  baseline artifact_path points to OLD file
  PASS  baseline artifact_path != artifacts.solution latest (MUST block PRD)
  PASS  brd baseline path consistent (no false positive)
  PASS  uc baseline path consistent (no false positive)
  PASS  prototype baseline path consistent (no false positive)
  PASS  pm_confirmations has NO prd entry (baseline mismatch blocks)
```

## 不一致细节

```yaml
# approved_baselines 中 solution 条目：
- stage: solution
  artifact_path: output/solution/solution-note-baseline-test-OLD.md  # 指向不存在的旧文件

# artifacts.solution 实际：
solution:
  - output/solution/solution-note-baseline-test.md  # 真实产物路径
```

## 24 条件逐条检查（4 阶段 × 6 条件）

| # | 条件 | brd | uc | solution | prototype |
|---|------|-----|-----|----------|-----------|
| 1 | pm_confirmations.confirmed = true | ✅ | ✅ | ✅ | ✅ |
| 2 | pm_confirmations.artifact = artifacts 最新 | ✅ | ✅ | ✅ | ✅ |
| 3 | approved_baselines.artifact_path = artifacts 最新 | ✅ | ✅ | ❌ **指向 OLD** | ✅ |
| 4 | review_results.verdict ≠ fail | ✅ pass | ✅ pass | ✅ pass | ✅ pass |
| 5 | review_results.reviewed_artifact = artifacts 最新 | ✅ | ✅ | ✅ | ✅ |
| 6 | review_results.reviewed_metadata = 最新 metadata | ✅ | ✅ | ✅ | ✅ |

**结论**：solution 条件 3 失败。23/24 通过，1 项阻断。

## 合约-SOP-断言对照表

| # | 合约条款 | 断言 | 结果 |
|---|---------|------|------|
| 1 | — | current_stage = prd（项目处于 PRD 阶段） | ✅ |
| 2 | — | artifacts.solution 有最新产物路径 | ✅ |
| 3 | confirmation.md §4 | approved_baselines 有 solution 条目 | ✅ |
| 4 | confirmation.md §4 | 基线 artifact_path 指向 OLD 文件（不一致标记） | ✅ |
| 5 | confirmation.md §4, E2E §6 | 基线路径 ≠ artifacts 最新（条件 3 失败） | ✅ |
| 6 | E2E §6 | brd 基线路径一致（无误报） | ✅ |
| 7 | E2E §6 | uc 基线路径一致（无误报） | ✅ |
| 8 | E2E §6 | prototype 基线路径一致（无误报） | ✅ |
| 9 | confirmation.md §4 | pm_confirmations 无 prd 条目（基线断裂阻断） | ✅ |

## 验证清单

- [x] current_stage = prd（脚本断言）
- [x] solution 基线 artifact_path 指向 OLD 文件（脚本断言：匹配 OLD）
- [x] solution 基线路径 ≠ artifacts.solution 最新（脚本断言：字符串不等）
- [x] brd/uc/prototype 基线路径均一致（脚本断言：无 false positive）
- [x] pm_confirmations 无 prd 条目（脚本断言：基线断裂时不可继续 PRD）
- [ ] prd-writer/prd-reviewer 执行时实际输出「前置基线校验失败」（需 Claude Code 运行时验证）
- [ ] 输出明确指向 solution 阶段和条件 3（需 Claude Code 运行时验证）
- [ ] 不继续 PRD 生成或审查（需 Claude Code 运行时验证）

## 为什么这很重要

`approved_baselines` 是 PM 确认的「已批准基线」。如果它指向不存在的文件：
- PM 当初批准的那份产物已丢失或被替换
- 当前 artifacts 中的产物可能是未经 PM 确认的版本
- 继续基于此进入 PRD 会导致追溯链断裂

## 无法自动验证的部分

- prd-writer/prd-reviewer 的前置校验是否在 SKILL.md 执行时真的逐条检查 24 条件
- 错误输出文本是否包含具体阶段名和条件编号
- 修正建议是否可执行（如何修正 approved_baselines）

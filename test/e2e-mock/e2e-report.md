# PMFlow 主链路 E2E 自检报告

> 项目：采购订单审批流程（E2E Mock）
> 执行时间：2026-04-29
> 模拟步数：13 步（step 0 初始 → step 13 终点）

## 状态流转总览

| Step | 命令 | current_stage | next_allowed_commands | 关键验证点 |
|------|------|---------------|----------------------|-----------|
| 0 | (初始) | uninitialized | [] | 初始状态 |
| 1 | /pm-brd | brd | [/pm-confirm, /pm-brd] | interviewer 自检后提示 confirm |
| 2 | /pm-confirm | uc | [/pm-uc, /pm-brd] | 推进到 uc |
| 3 | /pm-uc | uc | [/pm-confirm, /pm-uc] | interviewer 自检后提示 confirm |
| 4 | /pm-confirm | solution | [/pm-solution, /pm-uc] | 推进到 solution |
| 5 | /pm-solution | solution | [/pm-solution-review, /pm-solution] | **writer 提示 reviewer，非 confirm** |
| 6 | /pm-solution-review | solution | [/pm-confirm, /pm-solution] | **reviewer pass 提示 confirm** |
| 7 | /pm-confirm | prototype | [/pm-proto, /pm-solution] | 推进到 prototype |
| 8 | /pm-proto | prototype | [/pm-proto-review, /pm-proto] | **writer 提示 reviewer，非 confirm** |
| 9 | /pm-proto-review | prototype | [/pm-confirm, /pm-proto] | **reviewer pass 提示 confirm** |
| 10 | /pm-confirm | prd | [/pm-prd, /pm-proto] | 推进到 prd |
| 11 | /pm-prd | prd | [/pm-prd-review, /pm-prd] | **writer 提示 reviewer，非 confirm** |
| 12 | /pm-prd-review | prd | [/pm-confirm, /pm-prd] | **reviewer pass 提示 confirm** |
| 13 | /pm-confirm | **prd（不变）** | **[]（空）** | **终点：主链路完成** |

## 合约验证清单

### 1. Writer→Reviewer→PM ownership gate

| 阶段 | Writer 提示 | Reviewer 提示 | PM confirm 后 |
|------|------------|--------------|--------------|
| brd | /pm-confirm (自检后) | N/A (自检) | advance→uc |
| uc | /pm-confirm (自检后) | N/A (自检) | advance→solution |
| solution | /pm-solution-review ✓ | /pm-confirm ✓ | advance→prototype |
| prototype | /pm-proto-review ✓ | /pm-confirm ✓ | advance→prd |
| prd | /pm-prd-review ✓ | /pm-confirm ✓ | **stay prd, []** ✓ |

**关键断言**：
- ✅ Writer 不跨过 reviewer 直接提示 /pm-confirm
- ✅ Reviewer pass/warn 只提示 /pm-confirm，不提示下一阶段命令
- ✅ PM confirm 才推进 current_stage

### 2. reviewed_artifact / reviewed_metadata 必填

| 阶段 | check_type | reviewed_artifact | reviewed_metadata | 匹配最新产物 |
|------|-----------|-------------------|-------------------|-------------|
| brd | self_check | output/brd/brd-note-20260429T100000.md | .pmflow/metadata/brd/brd-20260429T100000.yaml | ✅ |
| uc | self_check | output/uc/uc-note-20260429T100200.md | .pmflow/metadata/uc/uc-20260429T100200.yaml | ✅ |
| solution | reviewer_check | output/solution/solution-note-20260429T100400.md | .pmflow/metadata/solution/solution-20260429T100400.yaml | ✅ |
| prototype | reviewer_check | output/prototype/prototype-note-20260429T100700.md | .pmflow/metadata/prototype/prototype-20260429T100700.yaml | ✅ |
| prd | reviewer_check | output/prd/prd-20260429T101000.md | .pmflow/metadata/prd/prd-20260429T101000.yaml | ✅ |

**关键断言**：
- ✅ 所有 5 个阶段 reviewed_artifact 和 reviewed_metadata 均不为空
- ✅ 所有记录均与对应阶段 artifacts 最新产物一致

### 3. pm_confirmations 与 approved_baselines 绑定

| 阶段 | pm_confirmations.confirmed | approved_baselines.artifact_path | 一致性 |
|------|--------------------------|--------------------------------|-------|
| brd | true | output/brd/brd-note-20260429T100000.md | ✅ |
| uc | true | output/uc/uc-note-20260429T100200.md | ✅ |
| solution | true | output/solution/solution-note-20260429T100400.md | ✅ |
| prototype | true | output/prototype/prototype-note-20260429T100700.md | ✅ |
| prd | true | output/prd/prd-20260429T101000.md | ✅ |

### 4. PRD 终端阶段行为

| 验证项 | 期望 | 实际 |
|--------|------|------|
| current_stage 推进 | prd 不变 | prd ✅ |
| next_allowed_commands | [] | [] ✅ |
| 确认后输出 | "主链路完成，PRD 可归档" | 符合 §5.1 ✅ |
| pm_confirmations 追加 | prd 条目 | 已追加 ✅ |
| approved_baselines 追加 | prd 条目 | 已追加 ✅ |

### 5. PRD 产物质量（7 项 reviewer 检查）

| 检查项 | 判定 |
|--------|------|
| PRD 独立归档质量 | pass — 无跨文档引用，自包含 |
| 无原型阶段内容 | pass — 无 UI 定位/动画/视觉描述 |
| 数据字典一致性 | pass — PurchaseOrder + ApprovalRecord 字段完整 |
| 操作/规则/异常/权限覆盖 | pass — 5BR + 5EX + 4角色权限矩阵 |
| 验收标准质量 | pass — 10条均有前置/步骤/预期 |
| 机读字段无泄漏 | pass — 人读产物无 anchor_id 等禁止字段 |
| 来源追溯完整 | pass — source_trace 覆盖 brd/uc/solution/prototype |

### 6. 前置基线一致性（PRD writer/reviewer 的 6×4=24 条件）

模拟中所有前置阶段基线均满足 6 条件校验：
- ✅ confirmed=true
- ✅ artifact 等于 artifacts 最新
- ✅ approved_baselines artifact_path 等于 artifacts 最新
- ✅ review 非 fail
- ✅ reviewed_artifact 等于 artifacts 最新
- ✅ reviewed_metadata 等于最新 metadata

### 7. 边界测试覆盖

| 场景 | 状态 | 测试目录 |
|------|------|---------|
| fail 阻断 pm-confirm | ✅ 已创建 | `test/boundary-fail/` |
| warn + open_questions 记录 | ✅ 已创建 | `test/boundary-warn/` |
| 产物重新生成导致 reviewed_artifact 不一致 | ✅ 已创建 | `test/boundary-stale-review/` |
| 前置基线不一致（24条件中任一失败） | ✅ 已创建 | `test/boundary-baseline-mismatch/` |

每个边界测试目录包含独立的 `.pmflow/status.yaml`、产物、metadata、review 记录和 `test-report.md`，可直接用于验证 pm-confirm 及各 reviewer 的边界行为。

## 结论

**主链路 13 步状态流转闭环，所有合约验证通过。4 个边界测试场景已就绪。**

- ✅ 阶段推进正确：uninitialized → brd → uc → solution → prototype → prd（终端）
- ✅ Writer→Reviewer→PM 门禁链完整，无越权提示
- ✅ reviewed_artifact/reviewed_metadata 全链路绑定，无空值
- ✅ PRD 终端阶段 current_stage 不变，next_allowed_commands 为空
- ✅ PRD 产物通过全部 7 项 reviewer 检查
- ✅ 前置基线绑定路径正确（非目录最新文件）
- ✅ 4 个边界测试场景已覆盖 fail/warn/stale-review/baseline-mismatch

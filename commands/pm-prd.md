---
description: PRD 写作。新主链 placeholder / legacy 主链基于已确认前置基线生成归档 PRD。
argument-hint: 可附带业务规则、数据规范、权限说明等补充材料
---

# pm-prd

## workflow_mode 分流

读取 `.pmflow/status.yaml` 中的 `workflow_mode`：

- `workflow_mode: new_main` → 新主链 PRD 尚未实现，输出 placeholder 并停止
- `workflow_mode: legacy` → 触发 skill：`prd-writer`
- `workflow_mode` 缺失时，按 `contracts/new-main-chain.md` §4 推断

### 新主链（new_main）

```text
新主链 PRD 阶段尚未实现，等待后续批次。
当前可手动执行 /pm-prd-review 检查已有的 PRD 产物（如有）。
```

停止。不生成任何产物，不触发 prd-writer skill，不读取 confirmed BRD/UC/solution/prototype，不提示 /pm-confirm。

### legacy 主链

触发 skill：`prd-writer`，原有逻辑不变。

#### 输入

- 已确认的 prototype note（`output/prototype/` 和 `.pmflow/metadata/prototype/`）
- 已确认的 solution note（`output/solution/` 和 `.pmflow/metadata/solution/`）
- 已确认的 UC note（`output/uc/` 和 `.pmflow/metadata/uc/`）
- 已确认的 BRD note（`output/brd/` 和 `.pmflow/metadata/brd/`）
- PM 补充材料（业务规则、数据规范、权限说明等，如有）
- `.pmflow/status.yaml`（读取当前状态和全部前置基线）

#### 输出

- `output/prd/prd-{timestamp}.md`（人读 PRD 文档）
- `.pmflow/metadata/prd/prd-{timestamp}.yaml`（机读 metadata）

#### 不做什么

- 不进入 fix / change / review-pack / export
- 不自行扩大 prototype 范围之外的模块、页面或操作
- 完成后只提示 /pm-prd-review，不提示归档、review-pack、export 或任何后续阶段
- 不生成原型内容或界面描述

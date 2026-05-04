---
description: 原型生成。新主链基于 PRD + wireframe + design 生成高保真 HTML 业务原型 / legacy 主链不适用。
argument-hint: 无参数，直接运行 /pm-prototype
---

# pm-prototype

## workflow_mode 分流

读取 `.pmflow/status.yaml` 中的 `workflow_mode`：

- `workflow_mode: new_main` → 触发 skill：`pm-prototype`
- `workflow_mode: legacy` → 不适用，legacy 主链无原型生成阶段
- `workflow_mode` 缺失时，按 `contracts/new-main-chain.md` §4 推断

### 新主链（new_main）

触发 skill：`pm-prototype`。

#### 输入

- `output/design/design.md`（设计文档）
- `.pmflow/metadata/design/index.yaml`（设计 metadata）
- `output/wireframe/wireframe.md`（线框图）
- `.pmflow/metadata/wireframe/index.yaml`（线框图 metadata）
- `output/prd/prd.md`（人读 PRD）
- `.pmflow/metadata/prd/index.yaml`（PRD 机读索引）
- `.pmflow/metadata/prd/dictionary.yaml`（字段主定义）
- `.pmflow/metadata/prd/pages/*.yaml`（页面 metadata）
- `.pmflow/metadata/prd/rules.yaml`（业务规则）
- `.pmflow/metadata/prd/trace.yaml`（来源追溯）
- 最近一次 prd-review 结果
- `references/prototype-ui-style.md`（UI 风格参考）
- `.pmflow/status.yaml`（当前状态）

#### 输出

- `output/prototype/index.html`（高保真 HTML 原型）
- `output/prototype/assets/`（按需，CSS/JS 文件）
- `.pmflow/metadata/prototype/index.yaml`（原型 metadata）
- `.pmflow/snapshots/prototype/prototype.last-synced.html`（快照）

#### 不做什么

- 不扩大或改变 PRD / wireframe / design 已确认范围
- 不新增 PRD 中不存在的页面、字段、操作、状态、流程
- 不实现真实后端接口
- 不实现 DOCX 导出
- 不实现完整 /pm-fix snapshot diff runtime
- 不接回 /pm-confirm
- 不写 pm_confirmations、approved_baselines、next_allowed_commands
- 完成后只提示 /pm-prototype-review

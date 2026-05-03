# PMFlow 生成物链路与修改循环设计

日期：2026-05-03

## 1. 背景

PMFlow 当前已完成一轮 gate 测试和主链初步建设，但原阶段模型仍以 `brd -> uc -> solution -> prototype -> prd` 为主。今天重新梳理后，第一版主链应改为围绕 PM 实际需要的生成物设计，而不是围绕旧 BRD/UC/Solution 概念设计。

PM 的真实工作方式不是让 AI 一次性跑完流程，而是：

```text
AI 生成阶段产物
→ PM 阅读、人工修改或补充
→ AI 检查遗漏点、异常点、关联点
→ 有问题则给出修改建议并按确认范围修改
→ 无阻断问题则建议进入下一阶段
→ PM 手动执行下一阶段命令
```

核心变化：

- 不再把问题抽象成“PM confirm 命令是否存在”。
- 真正要解决的是生成后停止、修改后检查、通过后只建议、下一阶段必须手动触发。
- 后续阶段发现问题时，不默认“回退”，而是先做影响范围判断，再决定局部修改、批量修改或同步修改。

## 2. 目标生成物

PMFlow 第一版围绕 5 类生成物组织。

| 阶段 | 生成物 | 主要用途 |
|---|---|---|
| `alignment` | 需求对齐稿 | 和需求方对齐需求理解、目标、边界和解决方案方向 |
| `design-pack` | 功能清单、页面清单、数据字典、系统流程 | 支撑 PM 对完整需求做详细设计和修正 AI 设计 |
| `wireframe` | 需求线框图 | 用图形化方式快速发现文字设计中的偏差 |
| `prd` | 正式 PRD | 用于研发对齐、产品评审和归档 |
| `prototype` | 正式原型 | 用于研发理解需求和产品评审会 |

`design-pack` 是核心设计基线。字段、页面、流程、权限、状态、业务规则的事实性变化，原则上应先落到 `design-pack`，再按需要同步到 `wireframe`、`prd`、`prototype`。

## 3. 推荐主链

建议外部命令：

```text
/pm-guide

/pm-align
/pm-align-review

/pm-design
/pm-design-review

/pm-wireframe
/pm-wireframe-review

/pm-prd
/pm-prd-review

/pm-prototype
/pm-prototype-review

/pm-fix
```

说明：

- `/pm-guide` 只判断状态和唯一下一步，不生成产物。
- writer/interviewer 类命令只生成或修改当前阶段产物。
- review 类命令只做阶段准出检查，不自动进入下一阶段。
- `/pm-fix` 处理已有产物的定向修改、批量修改、基线同步和影响面分析。

## 4. 阶段职责

### 4.1 alignment

`alignment` 替代旧 `brd + uc + solution` 的前置对齐部分，但不承担详细设计职责。

它要回答：

- PM 对需求方诉求的理解是什么。
- 业务目标、干系人、范围边界是什么。
- 用户角色、核心场景和主任务是什么。
- 当前解决方案方向是什么。
- 哪些问题还需要需求方确认。

`alignment` 可以多轮。需求方反馈“理解有偏差”时，应继续修改 alignment，而不是直接进入详细设计。

### 4.2 design-pack

`design-pack` 是详细设计基线，至少包含：

- 功能清单
- 页面清单
- 数据字典
- 系统流程
- 角色权限初稿
- 状态流转
- 关键业务规则
- 待确认问题

它用于 PM 审视完整需求设计，也用于后续 `wireframe`、`prd`、`prototype` 的来源追溯。

### 4.3 wireframe

`wireframe` 把 `design-pack` 图形化，重点暴露：

- 页面之间是否顺。
- 用户主路径是否能走通。
- 页面信息承载是否合理。
- 字段、操作、状态是否在页面上有落点。

它不是正式原型，不要求高保真，但必须能帮助 PM 发现设计偏差。

### 4.4 prd

`prd` 是正式归档文档，用于研发对齐、产品评审和归档。

它必须：

- 能独立阅读。
- 不依赖原型才能理解规则。
- 覆盖业务规则、异常、权限、数据字典、验收标准。
- 与 `design-pack`、`wireframe` 保持一致。

### 4.5 prototype

`prototype` 是正式原型，用于研发理解和评审展示。

它必须：

- 承接 `design-pack`、`wireframe` 和 `prd`。
- 展示真实页面主体，不做讲解板。
- 支持主流程走通。
- 对关键字段、状态、操作、异常有可见表达。

## 5. Review 与准出规则

每个阶段的 review 只做一件事：判断当前最新产物是否具备进入下一阶段或作为下游基线的条件。

review 输出 `pass / warn / fail`：

| verdict | 含义 | 行为 |
|---|---|---|
| `pass` | 未发现阻断问题 | 只建议下一步命令，停止 |
| `warn` | 有风险但不阻断 | 记录风险和待确认问题，只建议下一步命令，停止 |
| `fail` | 存在阻断问题 | 不得建议进入下一阶段，只建议修当前阶段 |

review 必须绑定最新产物：

```yaml
stage: design-pack
check_type: reviewer_check
verdict: pass
reviewed_artifact: output/design-pack/design-pack-xxx.md
reviewed_metadata: .pmflow/metadata/design-pack/design-pack-xxx.yaml
checked_at: 2026-05-03T00:00:00
```

下一阶段启动时必须校验：

- 上游阶段有 review。
- review verdict 不是 `fail`。
- `reviewed_artifact` 等于上游最新 artifact。
- `reviewed_metadata` 等于上游最新 metadata。

如果 PM 或 AI 在 review 后重新修改了上游产物，旧 review 失效，下游命令必须拒绝继续。

## 6. 修改循环

PMFlow 的修改不能简单理解为“回退”。修改分为四类。

### 6.1 local_patch

只修改某个产物的某一点。

例：

```text
帮我把 PRD 里“提交审批”的失败提示补清楚。
```

AI 必须先检查同产物关联点，再判断是否只改指定位置。

### 6.2 batch_patch

修改某个产物中的同类问题。

例：

```text
把原型里所有列表页的筛选区改成统一样式。
```

AI 必须列出受影响页面和不受影响范围，再执行批量修改。

### 6.3 baseline_sync

修改 `design-pack`，并同步到指定下游产物。

例：

```text
我把数据字典里的“计划类型”改成枚举，请同步修改 PRD 和原型。
```

AI 必须识别源变更和目标产物：

```yaml
source_stage: design-pack
target_stages:
  - prd
  - prototype
```

未被指定的下游产物不得擅自修改，但要提示可能存在未同步风险。

### 6.4 impact_patch

局部修改触发关联影响检查。

例：

```text
我在 PRD 第一节修改了某一点。
```

AI 必须主动检查：

- PRD 第三节、第四节是否有相同口径。
- 数据字典是否有同字段。
- 页面说明是否引用该规则。
- 权限矩阵、业务规则、异常处理、验收标准是否有关联。
- `wireframe`、`prototype` 是否有跨产物关联。

`impact_patch` 不是独立可选动作，而是所有 fix/change 的必经检查。

## 7. /pm-fix 固定流程

`/pm-fix` 不得直接改文件。固定流程：

```text
读取用户修改请求
→ 判断修改类型
→ 找直接命中位置
→ 扫描同产物关联位置
→ 扫描跨产物关联位置
→ 输出影响范围
→ 等 PM 确认修改范围
→ 执行局部或批量修改
→ 同步 metadata
→ 输出 diff 摘要
→ 建议重新执行对应 review
→ 停止
```

最小影响范围输出：

```text
影响范围判断：
- 修改来源：
- 修改类型：
- 直接命中：
- 同产物关联：
- 跨产物关联：
- 建议本次修改范围：
- 不建议修改范围：
- 需要 PM 决定：
```

如果没有关联点，必须明确说明：

```text
未发现同产物或跨产物关联点，本次可只改指定位置。
```

## 8. 何时必须改 design-pack

以下变化必须先进入 `design-pack`：

- 新增、删除、改名字段
- 改变字段类型、枚举、必填、校验规则
- 新增、删除页面
- 改变主流程
- 改变状态流转
- 改变角色权限
- 改变业务规则
- 改变范围边界
- 改变建设类型

以下变化通常只改当前目标产物：

- PRD 表达不清
- 原型布局或样式不合理，但不改变字段和流程
- wireframe 图形表达不清
- 同类文风、排版、标注问题
- 验收标准写法调整，但不改变规则本身

## 9. 防自动推进规则

任何阶段产物生成、修改、review 后都必须停止。

允许输出：

```text
未发现阻断问题，建议可以进入下一阶段。
下一步请手动执行：/pm-prd
```

禁止行为：

- review 通过后自动执行下一阶段命令。
- 修改下游产物后自动同步所有其他产物。
- 用户要求“顺便继续”时跨阶段执行。
- 用旧 review 放行新产物。
- 在未做 impact analysis 时直接改文件。

## 10. 锚点与追溯设计

PMFlow 必须吸收 testany 的稳定 ID 和关系追溯机制，但不得照搬其在人读文档中嵌入大段 trace metadata 的形式。

核心原则：

```text
人读物用自然名称，机读物用稳定 ID。
ID 不暴露给需求方和评审会读者。
relations 负责追溯、防幻觉和同步修改。
```

### 10.1 人读物不暴露复杂锚点

人读产物不得出现复杂机器 ID，例如：

```text
REQ-AUDIT-PLAN-001
PAGE-AUDIT-PLAN-LIST
FIELD-PLAN-TYPE
REL-0003
```

人读物只写自然名称：

```text
年度审计计划列表页
计划类型
提交审批
```

允许在人读物中使用轻量短编号辅助阅读，例如：

```text
P-01 年度审计计划列表页
R-03 提交审批规则
```

但这些短编号只服务阅读定位，不等同于 metadata 中的稳定机器 ID。

### 10.2 稳定 ID 不因重排改名变化

机读 ID 一旦生成，只要业务语义没有变化，就不得因为章节顺序、页面排序、标题微调而变化。

示例：

```yaml
id: FIELD-PLAN-TYPE
human_name: 计划类型
```

如果人读名称从“计划类型”改成“审计计划类型”，但语义仍是同一个字段，ID 保持不变。

如果语义发生变化，例如从普通文本变成影响流程的枚举字段，可以保留原 ID，但必须记录 version 或 change event：

```yaml
id: FIELD-PLAN-TYPE
version: 2
change_event: CHANGE-20260503-001
```

### 10.3 锚点按对象类型分层

建议的 ID 类型：

| 前缀 | 对象 |
|---|---|
| `REQ-*` | 需求点 / 业务能力 |
| `TASK-*` | 用户任务 |
| `PAGE-*` | 页面 |
| `ENTITY-*` | 业务实体 |
| `FIELD-*` | 字段 |
| `FLOW-*` | 流程 |
| `STATE-*` | 状态 |
| `RULE-*` | 业务规则 |
| `AC-*` | 验收标准 |
| `DEC-*` | 关键决策 |
| `REL-*` | 关系 |

ID 的命名要稳定、可读、可检索，但不追求在人读物中展示。

### 10.4 关系比 ID 更重要

单独有 ID 不能防幻觉。reviewer 真正依赖的是 relations。

示例：

```yaml
relations:
  - id: REL-001
    type: derived_from
    from: FIELD-PLAN-TYPE
    to: ENTITY-AUDIT-PLAN

  - id: REL-002
    type: appears_in
    from: FIELD-PLAN-TYPE
    to: PAGE-AUDIT-PLAN-FORM

  - id: REL-003
    type: validated_by
    from: FIELD-PLAN-TYPE
    to: AC-PLAN-TYPE-REQUIRED
```

reviewer 需要检查：

- 人读产物中出现的业务对象是否有对应 ID。
- ID 是否有上游来源。
- ID 是否出现在应该出现的页面、流程、规则、验收中。
- 下游产物是否擅自新增 design-pack 中不存在的 ID。
- relations 是否断裂、重复、冲突或指向不存在的对象。

### 10.5 机读物必须分片，不能形成超长 metadata

OMP 的问题是机读物承担了完整世界状态，后期超过 3000 行，导致 writer/reviewer 一次性读取过多上下文并产生幻觉。PMFlow 必须避免这个结构。

推荐结构：

```text
.pmflow/metadata/<stage>/index.yaml
.pmflow/metadata/<stage>/entities.yaml
.pmflow/metadata/<stage>/fields.yaml
.pmflow/metadata/<stage>/pages.yaml
.pmflow/metadata/<stage>/flows.yaml
.pmflow/metadata/<stage>/rules.yaml
.pmflow/metadata/<stage>/relations.yaml
```

如果单个主题仍然过长，继续拆到 detail 文件：

```text
.pmflow/metadata/design-pack/pages/PAGE-AUDIT-PLAN-LIST.yaml
.pmflow/metadata/design-pack/entities/ENTITY-AUDIT-PLAN.yaml
.pmflow/metadata/design-pack/flows/FLOW-SUBMIT-APPROVAL.yaml
```

建议长度限制：

| 文件 | 建议上限 |
|---|---|
| `status.yaml` | 200 行 |
| `index.yaml` | 300 行 |
| 单个主题 metadata | 500 行 |
| 单个 detail metadata | 200 行 |
| 单个 review 文件 | 300 行 |

超过上限时，必须继续拆分，而不是让 writer/reviewer 全量读取。

### 10.6 按需读取

writer/reviewer 不得默认读取所有 metadata。

读取顺序应为：

```text
status.yaml
→ 当前阶段 index.yaml
→ 本次任务涉及的主题 metadata
→ 本次任务涉及的 detail metadata
→ relations.yaml 中相关关系
```

例如 PRD writer 写“年度审计计划列表页”时，只读取相关页面、实体、字段、流程、规则及其 relations，不读取整个 design-pack。

## 11. 与旧模型的关系

旧模型：

```text
brd -> uc -> solution -> prototype -> prd
```

新模型：

```text
alignment -> design-pack -> wireframe -> prd -> prototype
```

对应关系：

| 旧概念 | 新落点 |
|---|---|
| BRD 业务目标、干系人、范围 | alignment |
| UC 用户角色、路径、任务流 | alignment + design-pack |
| Solution 页面、字段、流程、建设类型 | design-pack |
| Prototype 初稿 | wireframe / prototype |
| PRD | prd |

`/pm-confirm` 不作为用户主命令保留。它的核心价值由 review 准出和上游基线绑定承接。

## 12. 推荐实施顺序

1. 先收口当前工作区，把写作规则、模板和 reference 改动整理干净。
2. 新增本设计对应的状态模型，不急着删除旧 brd/uc。
3. 设计 `alignment`、`design-pack`、`wireframe` 的 profile 和 template。
4. 改造 `/pm-guide`，让它识别新阶段和唯一下一步。
5. 实现锚点、relations、分片 metadata 和按需读取规则。
6. 实现 review 准出绑定，确保旧 review 不放行新产物。
7. 实现 `/pm-fix` 的 impact analysis，不直接改文件。
8. 做新主链 e2e mock。
9. 做四类 fix 场景测试。
10. 通过后再标记旧 brd/uc/solution 链路为 legacy。

## 13. 本轮讨论追加定稿

本节记录 2026-05-03 继续讨论后的新结论。若与前文旧表述冲突，以本节为准。

### 13.1 启动方式

PMFlow 的启动由 `/pm-guide` 引导，由 `/pm-input` 正式创建和进入需求流程。

`/pm-guide` 只做导航判断：

- 新项目没有状态时，提示执行 `/pm-input`。
- 已有项目读取状态、产物、review、未收口变更，给出唯一下一步建议。
- 不初始化需求、不生成产物、不自动推进阶段。

`/pm-input` 是材料盘点入口：

- 用户输入需求背景、需求方原话、字段表、流程图、截图、旧系统资料、会议纪要等材料。
- AI 盘点收到了什么、材料性质是什么、是否足够启动需求对齐。
- `/pm-input` 不生成解决方案，不生成详细设计。

`/pm-input` 的准出不是“材料齐全”，而是“是否足够生成有价值的需求对齐稿”：

| 结果 | 含义 | 下一步 |
|---|---|---|
| `pass` | 材料足够清楚，可进入需求对齐 | 手动执行 `/pm-align` |
| `warn` | 材料不完整，但足够形成对齐问题 | 手动执行 `/pm-align`，带着待补充问题继续 |
| `fail` | 基本需求对象、目标或材料来源不清 | 先补输入，再重新 `/pm-input` |

真实项目中 `warn` 是常态路径，不应把材料不完整等同于阻断。

### 13.2 阶段职责重新切分

当前主链调整为：

```text
input -> align -> design -> wireframe -> prd -> prototype
```

职责边界：

| 阶段 | 职责 |
|---|---|
| `input` | 材料盘点，识别材料来源、性质、缺口和冲突 |
| `align` | 需求对齐，确认需求理解、建设类型、范围边界、角色场景、业务方向 |
| `design` | 详细设计建设，只基于已通过 align-review 的对齐基线建设功能、页面、字段、流程、状态、权限、规则 |
| `wireframe` | 图形化表达 design，用于发现文字设计中的偏差 |
| `prd` | 研发对齐、产品评审和归档 |
| `prototype` | 正式交互原型和评审展示 |

`design` 不做前置判断：

- 不重新判断建设类型。
- 不重新解释需求方原始材料。
- 不把新材料悄悄并入设计。
- 不扩大或改变 `align` 已确认范围。
- 发现材料缺失、冲突、建设类型不成立时，只能停止并建议回到 `/pm-input` 或 `/pm-align`。

### 13.3 input 与 align 的方法论

`/pm-input` 使用“材料盘点法”：

1. 材料识别：识别原话、字段表、流程图、截图、会议纪要、旧系统资料、制度文件等。
2. 来源标记：区分需求方确认、PM 假设、旧系统现状、历史文档、参考材料。
3. 约束强度判断：标记强约束、参考约束、待确认、范围外。
4. 内容提取：提取目标、角色、场景、字段线索、流程线索、规则线索、边界线索。
5. 缺口和冲突识别：识别材料之间的缺失、矛盾和口径不一致。
6. 对齐问题生成：把缺口转成可问需求方的问题。

`/pm-align` 使用“需求对齐法”：

1. 问题归因：识别需求方真正要解决的问题。
2. 目标定义：明确效率、合规、体验、数据、流程闭环、管理可视化等目标。
3. 建设类型判断：新建系统/模块、优化迭代、混合，并写依据。
4. 范围划定：区分本次做什么、不做什么、待确认什么。
5. 角色与场景识别：识别关键用户、主任务、核心使用场景。
6. 用户路径雏形：只到“谁在什么场景下完成什么任务”，不展开详细页面和状态机。
7. 业务方向确认：给出业务解决方向，但不进入字段、页面、权限、流程细节。

`/pm-align` 支持多轮输入：

- 基于上一版对齐稿继续补充。
- 在 AI 会话中直接补充需求方说明、流程图、字段表、截图、规则等。
- 吸收需求方改口径。
- 复查 PM 手工修改后的对齐稿。
- 关闭或新增待确认问题。

用户在会话中补充的新内容不能默认等于已确认事实，必须按表达区分需求方确认、PM 假设、新增材料、范围变化或详细设计线索。

### 13.4 align-review 必须检查方法论结果

`/pm-align-review` 不检查章节是否齐全，而检查“材料盘点法”和“需求对齐法”是否产生了可靠的 design 输入。

检查项：

- 已提供材料是否完整登记。
- 关键材料是否标记来源和约束强度。
- 是否从材料中提取目标、角色、场景、字段线索、流程线索、规则线索。
- 缺口是否转成可问需求方的问题。
- 需求目标是否清楚。
- 建设类型是否有依据。
- 范围边界是否可用。
- 关键角色、主场景和用户路径雏形是否足够。
- 业务方向是否合理，且没有越界到详细设计。
- 多轮新增、覆盖、冲突和已关闭问题是否处理干净。

`fail` 条件包括：

- 关键材料未登记。
- 关键材料来源或约束强度不明。
- 需求目标不清。
- 建设类型无依据。
- 范围边界不可用。
- 主角色或主场景缺失。
- 材料冲突没有暴露。
- 把 PM 假设、旧系统现状、参考材料当成需求方确认事实。
- `align` 已经越界写成详细设计。

### 13.5 design 生成前推导

`/pm-design` 使用“结构化设计建设法”，只在已通过 `align-review` 的基线上工作。

生成前推导顺序：

1. 目标转能力。
2. 场景转任务。
3. 任务转功能。
4. 功能转页面。
5. 对象转数据字典。
6. 任务转系统流程。
7. 流程转状态。
8. 角色转权限。
9. 对齐基线中的认可材料逐项处理。
10. `align-review` 遗留问题影响标记。

design 的输出不是“继续需求对齐”，而是详细设计基线。它必须服务后续 `wireframe`、`prd`、`prototype`。

### 13.6 上下文防爆机制

OMP 的主要问题不是单纯文件长，而是长文生成过程中出现质量衰减；前半段质量较好，后半段开始变粗、变短、像补清单。审计系统样本 `solution-v2.md` 已有 948 行、37 个页面，且尚未完整展开数据字典、权限矩阵、状态机、异常规则。如果按 PMFlow 的 design 定义完整生成，大系统很容易超过 2000 行。

因此 PMFlow 必须从 `/pm-design` 的人读物生成阶段开始防爆。

硬原则：

```text
人读物可以集中，AI 生成和读取必须分片。
```

推荐结构：

| 层 | 文件 | 给谁用 | 规则 |
|---|---|---|---|
| 主阅读稿 | `output/design/design.md` | PM | 一个入口，方便完整审阅和手工修改 |
| 生成分片 | `.pmflow/workspace/design/sections/` | AI 内部 | 分片生成、局部自检、最终组装 |
| 机读记录 | `.pmflow/metadata/design/` | AI/reviewer | 索引、稳定锚点、关系、来源追溯 |

`design.md` 不允许一次性长文生成。大型系统必须：

```text
生成设计索引
-> 分片生成模块/页面/字段/流程内容
-> 每片局部自检
-> 最终组装为一个 PM 可读主稿
```

后续 writer/reviewer 禁止默认完整读取 `output/design/design.md`，必须先读 metadata index，再按任务读取相关分片和必要的人读摘录。

### 13.7 人读物修改与机读物同步

PM 可以直接修改人读主稿，但任何人读物被修改后，下一次进入 writer/reviewer 前必须完成人机同步。

定稿规则：

- 人读物编号不等于稳定锚点。
- 人读物可以有阅读编号，但编号只服务阅读顺序。
- 阅读编号允许由 `/pm-fix` 自动重排。
- PM 不负责维护稳定锚点。
- 稳定锚点只存在于机读物。
- 机读物锚点不随排序、章节号、展示编号变化。
- 人读物改动后，必须由 `/pm-fix` 做人机同步。
- `/pm-fix` 负责识别新增、删除、移动、改名、改内容。
- `/pm-fix` 负责更新机读物、重排阅读编号、输出影响范围。
- 如果无法判断人读改动对应哪个机读锚点，必须停止询问 PM，不能猜。

### 13.8 /pm-fix 与 /pm-fix-review

`/pm-fix` 是变更同步中枢，不只是改错工具。它同时处理：

- 人机同步：PM 改了人读物，AI 同步机读物。
- 跨产物同步：上游基线变更后，同步 `wireframe`、`prd`、`prototype` 等下游产物。

`/pm-fix` 固定流程：

```text
识别修改对象
-> 判断变更类型
-> 匹配机读锚点
-> 分析影响范围
-> 判断是否需要回到 input/align/design
-> 执行局部修改
-> 同步机读记录
-> 标记受影响产物
-> 记录复查债务
-> 输出本次变更结果
-> 停止
```

`/pm-fix-review` 负责本轮修改收口，支持 PM 连续多次 `/pm-fix` 后再统一检查。

`/pm-fix-review` 固定流程：

```text
读取未收口变更
-> 合并影响范围
-> 检查人机同步
-> 检查跨产物同步
-> 检查同类关联点
-> 输出待收口项
-> 关闭已收口变更
-> 给出下一步建议
```

“待收口项”不是允许 `/pm-fix` 低质量，而是承认复杂修改存在隐含关联，需要变更后一致性检查。

### 13.9 变更等级与 review 债务

`/pm-fix` 修改后不强制立刻执行阶段 review，但必须记录复查债务。PM 可以连续多次 `/pm-fix`，再执行 `/pm-fix-review` 合并收口。

变更等级：

| 等级 | 含义 | 处理 |
|---|---|---|
| L1 | 文案、标题、说明补充 | 通常只需 fix-review |
| L2 | 单页面交互、单字段说明、局部规则 | fix-review 后按需阶段 review |
| L3 | 新增/删除页面、字段、流程节点、权限规则 | fix-review 后通常需要对应阶段 review |
| L4 | 跨模块主流程、核心业务对象、多个下游产物 | fix-review 后必须阶段 review |
| L5 | 需求目标、范围、建设类型变化 | 不按 fix 处理，回到 align |

阶段 review 不是每次 design 变更后都全量重跑：

- `/pm-fix` 必须做局部变更复查。
- `/pm-fix-review` 必须合并本批变更并收口。
- 只有核心结构变更、影响范围较大、或变更等级要求时，才提示执行对应阶段 review。
- 是否需要阶段 review 必须落到状态里，不能靠 PM 记忆。

示例：

```text
/pm-fix
待审批列表中点击详情应该是跳转新页面操作，而不是展开抽屉。
```

判断规则：

- 如果上游 design 已定义为跳转页，当前 prototype 做成抽屉：这是 L2 下游偏差修复。
- 如果 design、PRD、prototype 均定义为抽屉，现在改为跳转新页面：这是 L3 设计基线变更。
- 如果“待审批列表”无法唯一定位，必须停止询问。
- 如果需要新增详情页，必须同步 design、wireframe、PRD、prototype 及机读关系。
- 如果已有详情页但跳转行为错，只同步相关下游。

### 13.10 `/pm-guide` 与修改循环的关系

`/pm-guide` 不插入正常修改循环。

正常修改循环：

```text
发现问题 -> /pm-fix
继续发现问题 -> /pm-fix
本批改完 -> /pm-fix-review
需要阶段审查 -> 手动执行对应 review
```

`/pm-guide` 只在 PM 迷路、需要判断当前状态或下一步时使用。

### 13.11 快照 diff 与低 token 修改识别

业务项目不强制使用 git。PMFlow runtime 不能依赖业务项目 git；git diff 只能作为可选优化。

默认机制：

```text
PM 修改人读物
-> /pm-fix
-> 先用 .pmflow/snapshots/ 与当前人读物做 deterministic diff
-> 只把变更片段交给 AI
-> AI 匹配机读锚点、分析影响范围、同步机读物和下游产物
```

快照位置示例：

```text
.pmflow/snapshots/design/design.last-synced.md
.pmflow/snapshots/wireframe/wireframe.last-synced.md
.pmflow/snapshots/prd/prd.last-synced.md
.pmflow/snapshots/prototype/prototype.last-synced.md
```

快照只在“同步干净”时更新：

- 阶段 writer 生成完成，并同步机读物后。
- `/pm-fix` 完成同步，并通过局部检查后。
- `/pm-fix-review` 确认本批变更已收口后。
- 阶段 review 通过后。

禁止在 PM 刚手工修改人读物后立即更新快照，否则未同步变更会被吞掉。

token 控制规则：

- 禁止把当前全文和快照全文同时交给模型比较。
- 必须先由确定性 diff 工具生成最小变更片段。
- AI 只读取 diff 片段、相关机读锚点分片和必要的人读上下文。
- 如果存在 git diff，可以作为辅助；如果 git diff 为空、太乱或业务项目没有 git，必须退回 snapshot diff。

diff 分级处理：

| diff 规模 | 处理 |
|---|---|
| 小 diff | 直接给 AI 分析 |
| 中 diff | 按章节或锚点分组，逐组处理 |
| 大 diff | 先生成变更摘要和候选锚点，询问 PM 是否分批处理 |
| 超大 diff | 拒绝一次性处理，要求拆分或按阶段处理 |

建议阈值：

| 指标 | 建议 |
|---|---|
| 单次 diff 上下文 | 不超过 200 行 |
| 单个变更组 | 不超过 50 行上下文 |
| 变更组数量 | 超过 10 个先汇总，不逐项展开 |
| 删除或新增超过全文 30% | 视为大改，不能当普通 fix |

该机制的目标是让 PM 可以只说：

```text
/pm-fix
我改完了，看一下。
```

AI 必须自己通过快照 diff 识别修改，而不是要求 PM 花时间描述改了哪里。

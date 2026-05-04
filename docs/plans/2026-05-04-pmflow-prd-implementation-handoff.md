# PMFlow PRD 阶段实施交接

日期：2026-05-04

## 1. 本轮目标

本轮实现新主链 PRD 阶段：

```text
wireframe-review -> /pm-prd -> /pm-prd-review -> /pm-prototype
```

完成后：

- `/pm-prd` 在 `workflow_mode: new_main` 下不再是 placeholder。
- `/pm-prd-review` 在 `workflow_mode: new_main` 下不再是 placeholder。
- `output/prd/prd.md` 成为完整人读 PRD 主稿。
- `.pmflow/metadata/prd/` 能支持字段、页面、区域、动作、规则、验收之间的反查。
- `/pm-guide` 能从 PRD writer/reviewer 的状态结果继续路由。

本轮不实现：

- prototype writer/reviewer。
- DOCX 导出。
- 完整 `/pm-fix` snapshot diff runtime。
- 复杂流程图生成。
- legacy PRD 链路重构。

## 2. 必读文件

执行前先读：

```text
AGENTS.md
docs/plans/2026-05-04-pmflow-prd-writing-design.md
docs/plans/2026-05-04-markdown-wireframe-design.md
contracts/new-main-chain.md
contracts/gates.md
contracts/human-sync.md
contracts/snapshot-diff.md
schemas/status.schema.yaml
skills/pm-guide/SKILL.md
skills/pm-wireframe/SKILL.md
skills/pm-wireframe-reviewer/SKILL.md
profiles/wireframe.profile.yaml
scripts/pmflow-new-main-e2e-smoke.py
```

同时读取当前 PRD 相关旧文件，判断哪些要保留 legacy、哪些要给 new_main 新增独立文件：

```text
commands/pm-prd.md
commands/pm-prd-review.md
skills/prd-writer/SKILL.md
skills/prd-reviewer/SKILL.md
profiles/prd.profile.yaml
profiles/prd-review.profile.yaml
templates/prd.md
references/prd-writing.md
```

## 3. 实施原则

### 3.1 新旧链路分离

PRD legacy 链路继续保留。

新主链不要复用 legacy 的 BRD / UC / solution / prototype confirmed 前置口径。新主链 PRD 的前置是：

```text
workflow_mode = new_main
wireframe-review verdict = pass 或 warn
wireframe-review reviewed_artifact = artifacts.wireframe 最新产物
wireframe-review reviewed_metadata = 当前 wireframe metadata
```

为了避免污染 legacy，建议新增：

```text
skills/pm-prd/SKILL.md
skills/pm-prd-reviewer/SKILL.md
profiles/prd-new-main.profile.yaml
profiles/prd-review-new-main.profile.yaml
references/prd-action-examples.md
```

保留旧文件：

```text
skills/prd-writer/SKILL.md
skills/prd-reviewer/SKILL.md
profiles/prd.profile.yaml
profiles/prd-review.profile.yaml
```

旧文件若要改，只改明显冲突的 command 分流或注释，不重写 legacy 逻辑。

### 3.2 人读 PRD

人读 PRD 固定输出：

```text
output/prd/prd.md
```

这份文件用于研发评审和公司归档，后续可转换 DOCX。

人读 PRD 保持干净正文：

- 写项目内容、业务规则、页面说明、字段、权限、验收。
- 不写内部路径。
- 不写 metadata 字段。
- 不写 review 字段。
- 不写稳定 ID。
- 不写 trace block。
- 不写 AI 协作痕迹。

页面编号 `P-01`、`P-02A` 可以出现在正文中，用作人读定位。稳定 ID 只进入 metadata。

### 3.3 机读 PRD metadata

PRD metadata 的目录可以由实现侧微调，但必须支持以下能力：

```text
字段 -> 页面 -> 区域 -> 动作 -> 使用方式
页面 -> 字段
动作 -> 字段 / 规则 / 验收
数据字典字段 -> 详细需求说明落点
详细需求说明字段 -> 数据字典主定义
PRD 内容 -> design / wireframe 来源
```

建议目录：

```text
.pmflow/metadata/prd/index.yaml
.pmflow/metadata/prd/dictionary.yaml
.pmflow/metadata/prd/pages/*.yaml
.pmflow/metadata/prd/rules.yaml
.pmflow/metadata/prd/trace.yaml
```

如果实现侧采用不同文件名，必须在 `index.yaml` 中给出索引，确保 reviewer 和 `/pm-fix` 能反查。

字段落点关系必须至少记录：

```text
字段名
字段主定义位置
页面名或页面编号
区域名
动作名
使用方式
来源 design 对象
```

`usage` 不要求 PM 确认枚举名称，但实现侧必须能区分这些使用方式：

```text
展示
筛选
编辑
只读
校验
状态判断
权限判断
计算
导入
导出
验收依据
```

## 4. PRD 人读骨架

`templates/prd.md` 更新为人读骨架，只保留结构，不放执行说明。

固定章节：

```text
# PRD：{项目名称}

## 一、文档概述
## 二、范围
## 三、业务流程
## 四、用户角色与权限
## 五、数据字典
## 六、详细需求说明
## 七、验收标准汇总
## 八、风险与待确认
```

按需章节：

```text
## 公共模块说明
## 系统依赖
## 非功能要求
## 数据影响范围
## 建议实施顺序
## 附录
```

按需章节只有存在真实约束时出现。

## 5. PRD 写法规则

把写法规则沉淀到：

```text
references/prd-writing.md
references/prd-action-examples.md
```

`references/prd-writing.md` 写规则和判定。

`references/prd-action-examples.md` 写目标样例和非目标样例。

`SKILL.md` 只引用这两个文件，不把大量样例塞进 skill。

### 5.1 页面写法

每个页面先写：

```markdown
### （一）P-01 资产库管理页

**页面目标**：由运营部维护标准物资目录，作为服务区申请入库时的标准物资选择来源。

**关联功能点**：标准物资资料维护、标准物资批量导入、标准物资详情查看、标准物资编辑、标准物资删除控制

页面由筛选区、列表区、操作区组成。筛选区负责缩小查询范围，列表区负责展示标准物资摘要和引用状态，操作区负责新增、编辑、删除、导入、导出等动作。
```

然后按用户动作展开：

```text
查询标准物资
新增标准物资
编辑标准物资
删除标准物资
批量导入标准物资
查看标准物资详情
```

### 5.2 动作复杂度判定

简单动作：

- 只触发一个明确结果。
- 不改业务状态。
- 不涉及复杂校验。
- 不涉及审批、异步、批量、导入导出。

普通动作：

- 列表查询、详情查看、普通跳转、普通筛选。
- 需要写字段、排序、分页、空状态、加载失败。

复杂动作：

- 新增、编辑、提交、暂存、删除、审批、确认、驳回。
- 会创建、修改、删除或提交业务数据。
- 会改变单据、资产、任务、流程状态。
- 涉及表单字段、校验、成功反馈、失败提示。

高风险动作：

- 涉及库存、数量、金额、财务、权限、跨服务区、跨系统。
- 涉及批量操作、导入导出、异步任务、并发冲突。
- 涉及核心业务对象状态流转或数据回写。

### 5.3 动作写法目标

动作说明采用自然段、短列表和必要的顺序列表组合，不固定栏目。

动作完成后，正文应自然回答：

- 谁触发。
- 在什么状态下触发。
- 页面展示哪些关键字段。
- 用户填写或选择哪些字段。
- 系统校验什么。
- 校验通过后状态或数据如何变化。
- 成功后页面如何反馈。
- 失败时如何提示。
- 是否影响数量、权限、状态、验收或下游页面。

这些信息不要求按固定小标题出现。

### 5.4 字段写法

字段在详细需求说明中自然出现。

目标写法：

```markdown
列表展示入库申请单编号、入库申请名称、申请服务区、所在区域、发起方式、申请人、目标服务区、入库状态、申请时间、操作入口。无匹配数据时，列表区显示"暂无入库记录"。
```

目标写法：

```markdown
服务区管理员点击"新增入库"按钮，打开入库申请弹窗，通过物资选择器从资产库选择标准物资，填写存放位置、数量、税后单价、备注后提交。申请服务区默认当前服务区（只读），所在区域关联带出。
```

详细需求说明不做页面字段摘要表。

数据字典是字段主定义区。详细需求说明是字段使用区。metadata 负责把两者连接起来。

## 6. 样例库第一批

`references/prd-action-examples.md` 第一批覆盖 10 类场景：

1. 列表查询页。
2. 新增/编辑表单。
3. 审批/确认动作。
4. 导入/导出。
5. 详情页。
6. 状态流转。
7. 批量操作。
8. 数据统计页。
9. 物资/对象选择器。
10. 跨页面跳转。

每类样例必须包含：

```text
适用场景
目标写法
非目标写法
非目标写法的问题
metadata 需要记录的字段关系
```

非目标写法至少覆盖两类：

- 内容太空，缺业务细节。
- 栏目齐全但机械填空。

## 7. Writer SOP

新增 `skills/pm-prd/SKILL.md`，控制在 300 行以内。

### 7.1 前置读取

读取：

```text
contracts/new-main-chain.md
contracts/gates.md
contracts/human-sync.md
contracts/snapshot-diff.md
schemas/status.schema.yaml
profiles/prd-new-main.profile.yaml
templates/prd.md
references/prd-writing.md
references/prd-action-examples.md
references/writing-principles.md
.pmflow/status.yaml
output/design/design.md
.pmflow/metadata/design/index.yaml
output/wireframe/wireframe.md
.pmflow/metadata/wireframe/index.yaml
最近一次 wireframe-review 结果
```

按需读取 design / wireframe metadata 分片，不一次性全量读取所有分片。

### 7.2 前置检查

全部满足才执行：

```text
workflow_mode = new_main
current_stage = wireframe 或 prd
artifacts.design 非空
artifacts.wireframe 非空
review_results 中最近一次 wireframe reviewer_check verdict 为 pass 或 warn
wireframe review reviewed_artifact 等于 artifacts.wireframe 最新产物
wireframe review reviewed_metadata 等于当前 wireframe metadata
不存在 status: open 的 fix_debts
```

前置失败时停止，并说明缺什么。不写 `output/prd/prd.md`，不写 PRD metadata，不更新 status，不提示 `/pm-prototype`。

### 7.3 生成顺序

执行顺序：

```text
读取状态和前置基线
-> 规划 PRD 章节
-> 生成数据字典
-> 逐页生成详细需求说明
-> 每页生成 metadata 和摘要
-> 生成业务流程、权限、验收、风险
-> 回查字段一致性
-> 写人读 PRD
-> 写 metadata
-> 写 snapshot
-> 更新 status
-> 输出 /pm-prd-review
```

数据字典先生成，详细需求说明逐页生成，验收标准最后回写。

### 7.4 输出

写入：

```text
output/prd/prd.md
.pmflow/metadata/prd/index.yaml
.pmflow/metadata/prd/dictionary.yaml
.pmflow/metadata/prd/pages/*.yaml
.pmflow/metadata/prd/rules.yaml
.pmflow/metadata/prd/trace.yaml
.pmflow/snapshots/prd/prd.last-synced.md
```

更新 `.pmflow/status.yaml`：

```yaml
current_stage: prd
artifacts:
  prd:
    - output/prd/prd.md
snapshot_records:
  - stage: prd
    artifact: output/prd/prd.md
    snapshot: .pmflow/snapshots/prd/prd.last-synced.md
```

输出：

```text
PRD 生成完成。

产物：
- output/prd/prd.md
- .pmflow/metadata/prd/index.yaml
- .pmflow/snapshots/prd/prd.last-synced.md

需要独立审查：
- 字段与数据字典是否一致
- 页面动作是否覆盖核心流程
- 规则、权限、异常、验收是否完整
- PRD 是否可直接评审和归档

下一步唯一建议：/pm-prd-review
```

## 8. Reviewer SOP

新增 `skills/pm-prd-reviewer/SKILL.md`，控制在 300 行以内。

### 8.1 前置读取

读取：

```text
contracts/new-main-chain.md
contracts/gates.md
contracts/human-sync.md
schemas/status.schema.yaml
profiles/prd-review-new-main.profile.yaml
output/prd/prd.md
.pmflow/metadata/prd/index.yaml
.pmflow/metadata/prd/dictionary.yaml
.pmflow/metadata/prd/pages/*.yaml
.pmflow/metadata/prd/rules.yaml
.pmflow/metadata/prd/trace.yaml
design / wireframe 的必要 metadata
.pmflow/status.yaml
```

### 8.2 前置检查

全部满足才审查：

```text
workflow_mode = new_main
artifacts.prd 包含 output/prd/prd.md
output/prd/prd.md 存在
.pmflow/metadata/prd/index.yaml 存在
PRD metadata 能反查字段、页面、动作、规则、验收
```

前置失败时停止。不写 review 文件，不更新 `status.review_results`，不提示 `/pm-prototype`。

### 8.3 检查项

逐项检查：

| 检查项 | pass | warn | fail |
|---|---|---|---|
| 归档可读性 | 研发只读 PRD 能理解范围、页面、规则、验收 | 个别概念需补充但不影响评审 | 需要反复回看 design/wireframe 才能理解 |
| 正文写法 | 页面按目标、功能点、区域职责、动作自然展开 | 个别动作略空或略模板化 | 大量机械填空或只写泛泛功能 |
| 页面覆盖 | design 核心页面都有 PRD 章节 | 边缘页面略简 | 核心页面缺失 |
| 动作覆盖 | 核心动作有触发、结果、状态或异常说明 | 边缘动作可补充 | 提交、审批、确认、导入导出等关键动作缺规则 |
| 字段一致性 | 正文字段与数据字典能双向反查 | 边缘字段落点可补 | 正文字段无字典定义，或字典核心字段无正文落点 |
| 规则覆盖 | 业务规则、异常、权限、验收覆盖核心流程 | 边缘规则待补 | 核心规则、权限或验收缺失 |
| 来源追溯 | PRD 内容能追溯到 design 或 wireframe | 个别来源不完整 | 出现未确认扩展或来源断裂 |
| 人机分离 | 人读 PRD 干净 | 不适用 | 出现内部路径、metadata 字段、review 字段、trace block |

字段一致性判定：

- 正文字段和数据字典不一致：fail。
- 正文出现字段但数据字典无主定义：fail。
- 数据字典核心字段没有页面/动作/规则/验收落点：fail。
- 数据字典边缘字段落点不足：warn。
- 文风机械但信息完整：warn；影响研发理解或归档质量时 fail。

### 8.4 输出

写入：

```text
.pmflow/reviews/prd-review-{timestamp}.yaml
```

追加同一条记录到 `.pmflow/status.yaml` 的 `review_results`：

```yaml
stage: prd
check_type: reviewer_check
verdict: pass | warn | fail
reviewed_artifact: output/prd/prd.md
reviewed_metadata: .pmflow/metadata/prd/index.yaml
checks_detail: []
fail_reasons: []
warnings: []
checked_at: ""
reviewer: pm-prd-reviewer
```

reviewer 不修改 `current_stage`。

pass / warn 输出：

```text
PRD 审查完成。

整体判定：pass / warn

逐项结果：
- 归档可读性：...
- 正文写法：...
- 页面覆盖：...
- 动作覆盖：...
- 字段一致性：...
- 规则覆盖：...
- 来源追溯：...
- 人机分离：...

下一步唯一建议：/pm-prototype
```

fail 输出：

```text
PRD 审查未通过。

阻断项：
- ...

下一步唯一建议：/pm-prd
```

如果问题来自 design 或 wireframe 基线变化，建议 `/pm-fix`，但不自动执行。

## 9. Command 和 guide 路由

更新 `commands/pm-prd.md`：

- `workflow_mode: new_main` 触发 `pm-prd`。
- `workflow_mode: legacy` 保留 `prd-writer`。
- new_main 不读取 confirmed BRD/UC/solution/prototype。
- new_main 不提示 `/pm-confirm`。

更新 `commands/pm-prd-review.md`：

- `workflow_mode: new_main` 触发 `pm-prd-reviewer`。
- `workflow_mode: legacy` 保留 `prd-reviewer`。
- new_main pass/warn 只提示 `/pm-prototype`。
- new_main fail 只回 `/pm-prd` 或建议 `/pm-fix`。
- new_main 不提示 `/pm-confirm`。

检查 `skills/pm-guide/SKILL.md`：

- `current_stage: prd` 且 artifacts.prd 为空 -> `/pm-prd`
- artifacts.prd 非空且无 prd review -> `/pm-prd-review`
- prd review fail -> `/pm-prd`
- prd review pass/warn -> `/pm-prototype`
- open `fix_debts` 仍最高优先 -> `/pm-fix-review`

## 10. 测试要求

更新 `scripts/pmflow-new-main-e2e-smoke.py`，必须检查：

1. 不再要求 `entities/*.yaml`。
2. 不再要求 `field_usage.yaml`。
3. 不再要求 `relations.yaml`。
4. 要求 `dictionary.yaml` 存在。
5. 要求 `pages/*.yaml` 存在。
6. 要求 `rules.yaml` 存在。
7. 要求 `trace.yaml` 存在。
8. `pages/*.yaml` 的 `field_id` 能在 `dictionary.yaml` 找到。
9. `rules.yaml` 的 `field_id` 能在 `dictionary.yaml` 找到。
10. `trace.yaml` 只做来源追溯，不做字段落点总表。
11. `index.yaml` 不保存字段主定义。
12. 人读 PRD 不出现内部路径、metadata 字段、review 字段、trace block、稳定 ID。

必须运行：

```powershell
python scripts\pmflow-new-main-e2e-smoke.py
python scripts\pmflow-gate-boundary-smoke.py
python scripts\pmflow-gate-runtime-smoke.py
git diff --check
```

## 11. 完成标准

本轮完成时，Claude 输出：

```text
已完成：
- ...

修改文件：
- ...

测试结果：
- pmflow-new-main-e2e-smoke.py：...
- pmflow-gate-boundary-smoke.py：...
- pmflow-gate-runtime-smoke.py：...
- git diff --check：...

未解决问题：
- ...

需要 Codex 验收：
- ...

下一步建议：
- ...
```

不要提交，不要推送。

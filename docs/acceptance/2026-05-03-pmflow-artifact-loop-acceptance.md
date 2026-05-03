# PMFlow 生成物链路与修改循环验收文档

日期：2026-05-03

## 1. 验收目标

本验收文档用于检查 PMFlow 是否按新的生成物链路和修改循环工作。

验收重点不是“文件是否生成”，而是：

- AI 是否生成后停止。
- review 是否只给建议，不自动推进。
- 下游是否只能使用已 review 的最新上游产物。
- 修改前是否做 impact analysis。
- 局部修改是否能发现同文档和跨文档关联点。
- `design-pack` 变化是否能按指定范围同步到下游产物。

## 2. 新主链验收

### 2.1 命令入口

必须存在或设计明确：

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

不通过表现：

- 仍把 `/pm-brd` 和 `/pm-uc` 作为新项目主入口。
- review 通过后自动执行下一阶段命令。
- `/pm-fix` 直接改文件，没有先输出影响范围。

### 2.2 阶段顺序

推荐主链：

```text
alignment -> design-pack -> wireframe -> prd -> prototype
```

验收点：

- `alignment` 面向需求方对齐，不承担详细字段设计。
- `design-pack` 承担功能清单、页面清单、数据字典、系统流程。
- `wireframe` 承担图形化需求理解和偏差发现。
- `prd` 承担研发对齐、评审和归档。
- `prototype` 承担正式交互原型和评审展示。

## 3. Review 准出验收

每个 review 必须输出：

```yaml
stage: <stage>
check_type: reviewer_check
verdict: pass | warn | fail
reviewed_artifact: <当前阶段最新人读产物>
reviewed_metadata: <当前阶段最新 metadata>
checked_at: <ISO8601 时间>
```

验收规则：

| 场景 | 预期 |
|---|---|
| review verdict = fail | 不得建议进入下一阶段 |
| review verdict = warn | 可建议下一阶段，但必须记录风险和待确认问题 |
| review verdict = pass | 可建议下一阶段，但不得自动执行 |
| review 后产物被修改 | 下一阶段命令必须拒绝继续，提示重新 review |
| review 缺少 reviewed_artifact | 不得放行 |
| review 缺少 reviewed_metadata | 不得放行 |

必须检查输出措辞：

```text
未发现阻断问题，建议可以进入下一阶段。
下一步请手动执行：/pm-xxx
```

不得出现：

```text
我将继续为你生成下一阶段产物。
已自动进入下一阶段。
已顺手生成 PRD / 原型。
```

## 4. /pm-guide 验收

`/pm-guide` 只允许做导航判断。

必须能判断：

- 当前阶段。
- 最新产物。
- 最新 review 是否绑定最新产物。
- 是否存在 fail。
- 是否需要重新 review。
- 唯一下一步建议。

不允许：

- 扫描项目目录后生成需求。
- 自动调用 writer。
- 自动调用 review。
- 自动推进阶段。

## 5. /pm-fix 验收

### 5.1 固定流程

`/pm-fix` 必须先输出影响范围，不得直接改文件。

最小输出：

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

如果没有关联点，必须输出：

```text
未发现同产物或跨产物关联点，本次可只改指定位置。
```

### 5.2 修改类型识别

必须识别四类修改：

| 类型 | 描述 | 验收要求 |
|---|---|---|
| `local_patch` | 修改某个产物某一点 | 仍需检查同产物和跨产物关联 |
| `batch_patch` | 修改某个产物同类问题 | 必须列受影响对象 |
| `baseline_sync` | 修改 design-pack 并同步下游 | 必须列 source_stage 和 target_stages |
| `impact_patch` | 局部修改触发关联检查 | 所有 fix 的必经检查 |

## 6. 局部修改关联检查

场景：

```text
PM 在 PRD 第一节修改了一个业务范围或术语。
```

AI 必须检查：

- PRD 范围章节。
- PRD 详细需求说明。
- PRD 业务规则。
- PRD 权限矩阵。
- PRD 数据字典。
- PRD 异常处理。
- PRD 验收标准。
- `design-pack` 中的功能清单、页面清单、数据字典、系统流程。
- `wireframe` 中相关页面或流程。
- `prototype` 中相关页面、字段、按钮或状态。

不通过表现：

- 只改用户指出的一句，不检查第三节、第四节或验收标准。
- 修改字段名后不检查数据字典和页面字段。
- 修改流程后不检查状态、权限、异常和验收。

## 7. 批量修改验收

场景：

```text
把原型中所有列表页的筛选区改成统一样式。
```

AI 必须输出：

- 匹配到的页面清单。
- 不属于列表页的排除清单或排除原因。
- 本次只影响 prototype，还是也影响 wireframe / PRD。
- 修改后需要执行哪个 review。

不通过表现：

- 只改一个页面。
- 未列影响范围。
- 擅自修改 PRD 或 design-pack。

## 8. Design-pack 同步验收

场景：

```text
把 design-pack 中“计划类型”改为枚举，并同步 PRD 和 prototype。
```

AI 必须：

1. 先判断这是 `baseline_sync`。
2. 修改 `design-pack`。
3. 找到 PRD 中字段、页面、规则、验收的关联点。
4. 找到 prototype 中对应表单、详情、列表、筛选的关联点。
5. 只同步用户指定的 PRD 和 prototype。
6. 明确说明未同步的 wireframe 是否存在风险。
7. 输出 diff 摘要。
8. 建议重新执行对应 review。

不通过表现：

- 只改 PRD，不改 design-pack。
- 改了所有下游产物但用户没有指定。
- 未说明未同步产物的风险。

## 9. 跨阶段基线验收

下一阶段启动前必须校验上游最新产物和 review 绑定一致。

示例：

```text
PM 修改了 design-pack。
然后直接执行 /pm-prd。
```

预期：

```text
拒绝执行 /pm-prd。
原因：design-pack 已在上次 review 后变更，请先执行 /pm-design-review，并按需要同步 wireframe / PRD / prototype。
```

不通过表现：

- 使用旧 review 继续生成 PRD。
- 自动帮 PM 补 review。
- 自动同步下游后继续执行。

## 10. 人读与机读分离验收

人读产物不得出现：

- 本地绝对路径。
- `reviewed_artifact`
- `reviewed_metadata`
- `machine_profile`
- `internal_path`
- `anchor_id`
- `rules_ref`
- `prototype_ref`

metadata/review/status 可以记录机器路径和追溯字段。

## 11. 锚点与追溯验收

### 11.1 人读物锚点检查

人读产物不得出现复杂机器 ID：

- `REQ-*`
- `TASK-*`
- `PAGE-*`
- `ENTITY-*`
- `FIELD-*`
- `FLOW-*`
- `STATE-*`
- `RULE-*`
- `AC-*`
- `DEC-*`
- `REL-*`

允许出现轻量阅读编号，例如：

```text
P-01 年度审计计划列表页
R-03 提交审批规则
```

但不得把这些阅读编号用于机器追溯。

不通过表现：

- PRD 正文中出现 `FIELD-PLAN-TYPE`。
- 原型说明中出现 `REL-003`。
- 需求对齐稿中出现 `.pmflow/metadata/...` 路径。

### 11.2 机读物稳定 ID 检查

metadata 中的对象必须有稳定 ID。

必须检查：

- 每个需求点、用户任务、页面、实体、字段、流程、状态、规则、验收标准有 ID。
- 同一业务语义在多次生成或局部修改后 ID 不变。
- 名称微调不导致 ID 改变。
- 语义变化时记录 version 或 change event。

不通过表现：

- 页面顺序调整后所有 `PAGE-*` 重新编号。
- 字段名轻微改写后生成了新的 `FIELD-*`，旧 ID 丢失。
- 同一个字段在 PRD 和 prototype 中对应两个不同 ID。

### 11.3 relations 检查

必须存在关系文件或等价结构，至少支持：

| relation type | 用途 |
|---|---|
| `derived_from` | 当前对象来自哪个上游对象 |
| `appears_in` | 字段、规则、流程出现在哪个页面或产物 |
| `validated_by` | 对象被哪个验收标准覆盖 |
| `depends_on` | 对象依赖哪个流程、状态或字段 |
| `supersedes` | 对象替代了哪个旧对象 |

reviewer 必须检查：

- relation 指向的 ID 是否存在。
- 下游新增对象是否能追溯到 design-pack。
- 人读产物出现的关键对象是否能在 metadata 中找到 ID。
- metadata 中的 ID 是否在应该出现的人读产物或下游产物中出现。
- relation 是否断裂、重复、冲突或循环。

不通过表现：

- PRD 新增字段，但 design-pack 中没有对应 ID 或 `derived_from`。
- prototype 出现新页面，但没有来自 design-pack / wireframe / PRD 的关系。
- 验收标准覆盖了不存在的规则 ID。

### 11.4 metadata 分片检查

不得把完整世界状态塞进单个 metadata 文件。

建议上限：

| 文件 | 上限 |
|---|---|
| `status.yaml` | 200 行 |
| `index.yaml` | 300 行 |
| 单个主题 metadata | 500 行 |
| 单个 detail metadata | 200 行 |
| 单个 review 文件 | 300 行 |

验收时检查：

- 是否存在 `index.yaml` 或等价索引。
- 是否按对象类型或主题拆分 metadata。
- writer/reviewer 是否只读取任务相关分片。
- 超过上限的文件是否继续拆分。

不通过表现：

- 单个 metadata 文件超过 3000 行。
- PRD writer 默认读取全部 metadata。
- review 文件记录大量全文内容而不是问题、ID 和关系。

### 11.5 防幻觉检查

reviewer 应通过 ID 和 relations 判断幻觉或未确认扩展。

场景：

```text
PRD 中出现“计划归档规则”。
```

预期检查：

```text
1. PRD metadata 中是否有 RULE-* 对象。
2. RULE-* 是否 derived_from design-pack 中的规则或流程。
3. RULE-* 是否 appears_in 对应页面或流程。
4. RULE-* 是否 validated_by 至少一个 AC-*。
5. 如果找不到来源，判定为未确认扩展或幻觉风险。
```

不通过表现：

- reviewer 只读人读 PRD，凭语感判断“看起来合理”。
- reviewer 没有检查 ID 来源。
- reviewer 没有检查关系覆盖。

## 12. Skill 编写规范验收

后续所有 PMFlow skill 应按本轮确认的 testany 基准执行：

| 规范项 | 要求 |
|---|---|
| 命名 | 英文 kebab-case |
| 必须文件 | `SKILL.md` |
| 行数限制 | `< 300 行` |
| 语言 | 中文，技术术语可保留英文 |
| Frontmatter | 必须包含触发词 |
| 示例 | 必须有使用示例 |

不通过表现：

- `SKILL.md` 无 frontmatter。
- 没有触发词。
- 没有使用示例。
- 超过 300 行且没有拆分到 `references/` 或 `contracts/`。

## 13. 回归测试建议

至少补充这些测试场景：

1. `alignment` 多轮对齐后再进入 `design-pack`。
2. `design-pack` review fail 阻断 `wireframe`。
3. `wireframe` 发现页面结构问题，但只修改 wireframe，不改 design-pack。
4. PRD 第一节修改术语，AI 发现第三节、第四节和验收标准关联点。
5. design-pack 字段变更，同步 PRD 和 prototype，不同步 wireframe。
6. prototype 批量修改所有列表页筛选区。
7. review 后修改上游产物，下游命令拒绝继续。
8. 人读产物不泄漏 metadata 或内部路径。
9. PRD 新增字段但缺少 design-pack 来源 ID，reviewer 判定为未确认扩展。
10. metadata 超过行数上限时，验收要求拆分。
11. 字段名称微调后 ID 保持稳定。

## 14. 验收结论格式

后续 Codex 验收按此格式输出：

```text
结论：通过 / 暂不通过 / 不通过

P0 问题：
- ...

P1 问题：
- ...

可以保留的设计：
- ...

必须修改的文件：
- ...

建议下一步：
- ...
```

P0 判定：

- 自动跨阶段。
- 旧 review 放行新产物。
- `/pm-fix` 不做 impact analysis 直接改文件。
- `design-pack` 事实基线变化后未同步或未提示下游风险。
- 下游产物出现无法追溯到 design-pack 的关键对象。
- 单个 metadata 文件膨胀为完整世界状态，导致 writer/reviewer 必须全量读取。

P1 判定：

- skill 不符合编写规范。
- review 输出缺少绑定字段。
- 修改范围说明不完整。
- 人读产物有轻微模板感或章节冗余。
- ID 稳定性规则不完整。
- relations 覆盖不完整但未造成关键对象幻觉。

## 15. 本轮追加验收项

本节记录 2026-05-03 继续讨论后的新增验收标准。若与前文旧口径冲突，以本节为准。

### 15.1 `/pm-input` 验收

`/pm-input` 是材料盘点入口，不是正式方案生成入口。

必须输出：

- 材料清单。
- 材料来源。
- 材料性质。
- 约束强度。
- 需求一句话摘要。
- 建设类型初判。
- 缺口与冲突清单。
- 待补充问题清单。
- 是否可以进入 `/pm-align`。

必须支持 `pass / warn / fail`：

| 结果 | 验收含义 |
|---|---|
| `pass` | 材料足够清楚，可进入 `/pm-align` |
| `warn` | 材料不完整，但足够形成对齐问题，可进入 `/pm-align` |
| `fail` | 基本需求对象、目标或材料来源不清，不能进入 `/pm-align` |

不通过表现：

- 要求材料完整才允许进入 `/pm-align`。
- 在 `/pm-input` 生成解决方案、详细页面、字段、流程。
- 把背景材料默认当成需求方确认事实。
- 漏掉需求方明确提供或认可的材料。

### 15.2 `/pm-align` 验收

`/pm-align` 必须支持多轮对齐。

必须支持输入方式：

- 基于上一版对齐稿继续补充。
- 在 AI 会话中直接补充需求方说明、流程图、字段表、截图、规则。
- 处理需求方改口径。
- 复查 PM 手工修改后的对齐稿。
- 关闭或新增待确认问题。

必须输出：

- 需求对齐稿。
- 本轮变更摘要。
- 已确认内容。
- 待确认问题。
- 冲突和风险。
- 建设类型判断及依据。
- 范围边界。
- 是否建议执行 `/pm-align-review`。

不通过表现：

- 直接生成详细设计。
- 展开页面清单、字段清单、权限矩阵、状态机。
- 把 PM 假设当需求方确认。
- 把新增材料默认当作已采纳设计。
- 自动进入 `/pm-design`。

### 15.3 `/pm-align-review` 方法论验收

`/pm-align-review` 必须检查方法论结果，不得只检查章节格式。

必须检查：

- 已提供材料是否完整登记。
- 关键材料是否标记来源和约束强度。
- 是否从材料提取目标、角色、场景、字段线索、流程线索、规则线索。
- 材料缺口是否转成可问需求方的问题。
- 需求目标是否清楚。
- 建设类型是否有依据。
- 范围边界是否可用。
- 关键角色、主场景和用户路径雏形是否足够。
- 业务方向是否合理且未越界到详细设计。
- 多轮新增、覆盖、冲突和已关闭问题是否处理干净。

P0 不通过：

- 关键材料未登记。
- 建设类型无依据。
- 范围边界不可用。
- 主角色或主场景缺失。
- 材料冲突没有暴露。
- 把 PM 假设、旧系统现状、参考材料当成需求方确认事实。
- 对齐稿已经写成详细设计。

### 15.4 `/pm-design` 验收

`/pm-design` 只能基于已通过 `/pm-align-review` 的需求对齐基线建设详细设计。

必须拒绝：

- 未执行 `/pm-align-review`。
- `align-review` 为 `fail`。
- `align` 产物在 review 后被修改。
- 存在阻断级材料缺口或建设类型冲突。

必须体现“结构化设计建设法”：

- 目标转能力。
- 场景转任务。
- 任务转功能。
- 功能转页面。
- 对象转数据字典。
- 任务转系统流程。
- 流程转状态。
- 角色转权限。
- 认可材料逐项处理。
- 遗留问题影响标记。

不通过表现：

- 在 design 阶段重新判断建设类型。
- 在 design 阶段重新解释原始材料。
- 把新材料悄悄并入设计。
- 扩大或改变 align 已确认范围。
- 发现前置冲突后继续生成。

### 15.5 人读物上下文防爆验收

上下文防爆必须从 `/pm-design` 人读物生成阶段开始。

验收规则：

- PM 主要阅读入口可以集中为 `output/design/design.md`。
- AI 不得一次性长文生成完整大型 design。
- 大型 design 必须先生成设计索引，再分片生成、局部自检、最终组装。
- 后续 writer/reviewer 不得默认完整读取 `output/design/design.md`。
- 后续 writer/reviewer 必须先读 metadata index，再按任务读取相关分片和必要的人读摘录。

不通过表现：

- `/pm-design` 一次性生成 2000 行以上完整详细设计。
- design 后半段明显变粗、变短、像清单补齐。
- 后续 `/pm-prd` 默认读取完整 `design.md`。
- 只做 metadata 分片，但人读 design 仍一次性长文生成。

### 15.6 人机同步验收

PM 修改人读物后，下一次进入 writer/reviewer 前必须完成人机同步。

验收规则：

- 人读物编号只服务阅读顺序，不得作为稳定锚点。
- 阅读编号允许由 `/pm-fix` 自动重排。
- PM 不负责维护稳定锚点。
- 稳定锚点只存在于机读物。
- 机读锚点不随排序、章节号、展示编号变化。
- `/pm-fix` 必须识别新增、删除、移动、改名、改内容。
- `/pm-fix` 必须更新机读物、关系、来源追溯和影响范围。
- 无法判断人读改动对应哪个机读锚点时，必须停止询问 PM。

不通过表现：

- PM 插入一个页面后，要求 PM 手工重排所有页面编号。
- 页面排序变化导致所有 `PAGE-*` ID 重建。
- 人读物新增字段，但 metadata 中没有对应字段记录。
- 人读物删除页面，但 metadata 仍把该页面作为有效对象。
- 人读物和机读物不一致时仍允许进入下一阶段 writer/reviewer。

### 15.7 `/pm-fix` 验收

`/pm-fix` 是变更同步中枢，必须同时支持人机同步和跨产物同步。

固定流程必须包括：

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

必须支持变更等级：

| 等级 | 含义 | 验收要求 |
|---|---|---|
| L1 | 文案、标题、说明补充 | 通常只需 fix-review |
| L2 | 单页面交互、单字段说明、局部规则 | fix-review 后按需阶段 review |
| L3 | 新增/删除页面、字段、流程节点、权限规则 | fix-review 后通常需要对应阶段 review |
| L4 | 跨模块主流程、核心业务对象、多个下游产物 | fix-review 后必须阶段 review |
| L5 | 需求目标、范围、建设类型变化 | 不按 fix 处理，回到 align |

示例验收：

```text
/pm-fix
待审批列表中点击详情应该是跳转新页面操作，而不是展开抽屉。
```

预期：

- 能定位“待审批列表”和“详情操作”。
- 能判断当前是 prototype 偏差，还是 design 基线变更。
- 若上游定义为跳转页，只修 prototype 和相关 metadata。
- 若上游也定义为抽屉，必须同步 design、wireframe、PRD、prototype。
- 若无法唯一定位“待审批列表”，停止询问。
- 若需要新增详情页，必须更新页面清单、页面关系、PRD 页面说明、原型路由和机读关系。

不通过表现：

- 只改 prototype，不检查 design / wireframe / PRD。
- 不判断已有详情页是否存在。
- 不处理返回列表、筛选保留、入口关系等关联点。
- 改完后不记录复查债务。

### 15.8 `/pm-fix-review` 验收

`/pm-fix-review` 负责本轮修改收口，支持连续多次 `/pm-fix` 后统一检查。

固定流程必须包括：

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

验收规则：

- 多次 `/pm-fix` 可以累计复查债务，不强制每次立刻 review。
- `/pm-fix-review` 必须合并同阶段 review 债务。
- `/pm-fix-review` 必须按上游到下游判断仍需哪些阶段 review。
- “待收口项”必须具体到对象、产物和问题，不能只写“建议再检查”。
- 若没有待收口项，必须明确输出是否还需要阶段准出 review。

不通过表现：

- 连续多次 `/pm-fix` 后只能逐条 review，不能合并。
- `/pm-fix-review` 只复述变更，不检查同类关联点。
- `/pm-fix-review` 把正常修改循环强制绕到 `/pm-guide`。
- 必须阶段 review 的债务没有落状态，靠 PM 记忆。

### 15.9 `/pm-guide` 与修改循环验收

`/pm-guide` 只做导航，不插入正常修改循环。

正常修改循环：

```text
发现问题 -> /pm-fix
继续发现问题 -> /pm-fix
本批改完 -> /pm-fix-review
需要阶段审查 -> 手动执行对应 review
```

验收规则：

- `/pm-guide` 可以在 PM 迷路时读取状态并给唯一建议。
- `/pm-guide` 不应成为 `/pm-fix` 后的必经收口动作。
- `/pm-guide` 不应替代 `/pm-fix-review`。
- 有未收口变更时，`/pm-guide` 可以提示执行 `/pm-fix-review`。

不通过表现：

- 每次 `/pm-fix` 后都强制执行 `/pm-guide`。
- `/pm-guide` 直接关闭复查债务。
- `/pm-guide` 自动执行阶段 review 或下一阶段 writer。

### 15.10 快照 diff 验收

业务项目不强制使用 git。PMFlow 必须在无 git 的业务项目中支持 `/pm-fix` 自动识别人读物变更。

必须支持：

- 使用 `.pmflow/snapshots/` 中的上次同步快照与当前人读物做 diff。
- 有 git 时可辅助读取 git diff。
- git 不存在、git diff 为空或 git diff 太乱时，仍可使用 snapshot diff。
- PM 只输入“我改完了，看一下”时，`/pm-fix` 能自动识别变更片段。

快照更新规则：

- 阶段 writer 生成完成并同步机读物后，可以更新快照。
- `/pm-fix` 完成同步并通过局部检查后，可以更新快照。
- `/pm-fix-review` 确认本批变更收口后，可以更新快照。
- 阶段 review 通过后，可以更新快照。
- PM 刚手工修改人读物但尚未同步时，不得更新快照。

token 控制验收：

- `/pm-fix` 不得把当前全文和快照全文同时交给模型比较。
- 必须先用确定性 diff 工具生成最小变更片段。
- AI 只读取 diff 片段、相关机读锚点分片和必要的人读上下文。
- 单次 diff 上下文建议不超过 200 行。
- 单个变更组建议不超过 50 行上下文。
- 变更组超过 10 个时，应先汇总，不逐项展开。
- 删除或新增超过全文 30% 时，应视为大改，不能当普通 fix。

不通过表现：

- 业务项目没有 git 时 `/pm-fix` 无法识别 PM 手改内容。
- 要求 PM 必须描述自己改了哪里。
- 把 `design.last-synced.md` 全文和当前 `design.md` 全文都塞进模型上下文。
- 用户只改 5 行，却让 AI 重读 2000 行人读稿。
- PM 手改后立即覆盖快照，导致变更消失。
- 大 diff 不分组、不摘要、不询问，直接一次性处理。

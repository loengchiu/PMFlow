# 人机同步契约

PM 可以直接修改人读主稿。任何人读物被修改后，下一次进入 writer/reviewer 前必须完成人机同步。

## 1. 核心原则

```text
人读物用自然名称，机读物用稳定 ID。
ID 不暴露给需求方和评审会读者。
metadata 分片与 trace 负责追溯、防幻觉和同步修改。
人读物是事实主体，metadata 是外部轻量索引。
```

## 2. 人读物编号规则

- 人读物编号不等于稳定锚点。
- 人读物可以有阅读编号（如 P-01、R-03），但编号只服务阅读顺序。
- 阅读编号允许由 `/pm-fix` 自动重排。
- PM 不负责维护稳定锚点。
- 稳定锚点只存在于机读物。
- 机读锚点不随排序、章节号、展示编号变化。

## 3. 人读物禁止出现的内容

人读产物不得出现：

- 本地绝对路径
- `reviewed_artifact` / `reviewed_metadata`
- `machine_profile` / `internal_path`
- `anchor_id` / `rules_ref` / `prototype_ref`
- 复杂机器 ID（如 `REQ-*`、`PAGE-*`、`FIELD-*`、`REL-*`）

## 4. 稳定 ID 规则

机读 ID 一旦生成，只要业务语义没有变化，就不得因为章节顺序、页面排序、标题微调而变化。

```yaml
id: FIELD-PLAN-TYPE
human_name: 计划类型
```

如果人读名称从"计划类型"改成"审计计划类型"，但语义仍是同一个字段，ID 保持不变。

如果语义发生变化，保留原 ID，但必须记录 version 或 change event：

```yaml
id: FIELD-PLAN-TYPE
version: 2
change_event: CHANGE-20260503-001
```

## 5. 阶段 writer 多轮同步职责

阶段 writer 包括 /pm-align、/pm-design、/pm-wireframe、/pm-prd、/pm-prototype。

当用户再次执行当前阶段命令并提供补充、修正、撤销、确认时，writer 必须：

- 先读取当前阶段已有的人读产物、metadata 和 snapshot。
- 判断用户输入影响的业务对象、字段、页面、流程、规则或原型交互。
- 同步更新当前阶段人读产物、metadata、snapshot 和 `.pmflow/status.yaml` 中 artifacts 和 snapshot_records。
- 不允许只更新人读物，不更新 metadata。
- 不允许只更新 metadata，不更新人读物。
- 无法判断影响对象时，必须停止询问 PM，不得猜。
- 同步完成后才允许输出下一步 review 命令。

## 6. /pm-fix 同步职责

`/pm-fix` 负责：

- 识别新增、删除、移动、改名、改内容。
- 更新机读物、关系、来源追溯和影响范围。
- 重排阅读编号。
- 输出影响范围。

如果无法判断人读改动对应哪个机读锚点，**必须停止询问 PM，不能猜**。

## 7. 同步完成标志

人机同步完成的标志：

- 人读物内容与机读物一致。
- 快照已更新（`snapshot_records` 中对应 stage 的 `synced_at` 已刷新）。
- 受影响的 metadata 分片与 trace 已更新。

## 7.1 轻量 metadata 同步

- metadata 同步指同步索引、relations、anchors、source_refs、revision、coverage，不是同步正文副本。
- 人读物和 metadata 不一致的定义：
  - 人读物中存在关键对象但 metadata 无索引。
  - metadata 中对象在人读物中已删除或失效。
  - relations/source_refs 指向不存在或错误对象。
  - metadata 状态与人读物事实冲突。
  - revision 未更新。
- metadata 不需要也不得复述完整人读正文。

## 8. 快照更新权限

只有以下角色可以在同步完成时更新 snapshot：

- 阶段 writer（生成完成并同步机读物后）
- `/pm-fix`（完成同步并通过局部检查后）
- `/pm-fix-review`（确认本批变更已收口后）

**阶段 reviewer 不更新 snapshot**。阶段 reviewer 只写 `.pmflow/reviews/*.yaml` 和 `status.review_results`。/pm-fix-review 不属于阶段 reviewer，可按收口规则更新 snapshot。

## 9. 同类关联点检测

用户提出任一修改点时，writer 或 /pm-fix 必须检查同类关联点。

同类关联点包括：

- 同一业务对象在多个章节的描述
- 同一字段在数据字典、页面说明、规则、验收中的出现
- 同一操作在列表页、详情页、流程图、PRD、原型中的出现
- 同一状态/枚举/权限规则在多个模块中的出现
- 同一交互模式在多个页面中的出现

不得只修改用户点名的一处，而不检查其他同类位置。能确定属于同一业务规则的，列出影响范围并同步修改。不能确定是否应同步的，必须向 PM 提问。不得静默保留明显冲突的旧口径。

## 10. metadata repair mode

当 reviewer 发现仅 metadata / index / relation / source_refs / revision 不一致时：

- 不得要求 PM 手工修改机读文件。
- 应建议回到当前阶段 writer。
- 当前阶段 writer 必须进入 metadata repair mode：
  - 读取 review 结果
  - 自动修复 metadata
  - 不必要时不修改人读产物
  - 只刷新 metadata_revision
  - 完成后要求重新 review

## 11. 禁止行为

- PM 插入一个页面后，要求 PM 手工重排所有页面编号。
- 页面排序变化导致所有 `PAGE-*` ID 重建。
- 人读物新增字段，但 metadata 中没有对应字段记录。
- 人读物删除页面，但 metadata 仍把该页面作为有效对象。
- 人读物和机读物不一致时仍允许进入下一阶段 writer/reviewer。
- reviewer 要求 PM 手工修改 metadata 文件。

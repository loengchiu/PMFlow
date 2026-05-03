# 人机同步契约

PM 可以直接修改人读主稿。任何人读物被修改后，下一次进入 writer/reviewer 前必须完成人机同步。

## 1. 核心原则

```text
人读物用自然名称，机读物用稳定 ID。
ID 不暴露给需求方和评审会读者。
relations 负责追溯、防幻觉和同步修改。
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

## 5. /pm-fix 同步职责

`/pm-fix` 负责：

- 识别新增、删除、移动、改名、改内容。
- 更新机读物、关系、来源追溯和影响范围。
- 重排阅读编号。
- 输出影响范围。

如果无法判断人读改动对应哪个机读锚点，**必须停止询问 PM，不能猜**。

## 6. 同步完成标志

人机同步完成的标志：

- 人读物内容与机读物一致。
- 快照已更新（`snapshot_records` 中对应 stage 的 `synced_at` 已刷新）。
- 受影响的 relations 已更新。

## 7. 禁止行为

- PM 插入一个页面后，要求 PM 手工重排所有页面编号。
- 页面排序变化导致所有 `PAGE-*` ID 重建。
- 人读物新增字段，但 metadata 中没有对应字段记录。
- 人读物删除页面，但 metadata 仍把该页面作为有效对象。
- 人读物和机读物不一致时仍允许进入下一阶段 writer/reviewer。

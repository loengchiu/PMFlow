# 主链路契约

## 1. 阶段顺序

```text
input -> align -> design -> wireframe -> prd -> prototype
```

## 2. 推进机制

- writer 执行成功后更新 `current_stage`、`artifacts`、metadata、snapshot 和 `stage_revisions`。
- reviewer 不推进 `current_stage`，只写 review 文件并追加 `status.review_results`。
- review verdict 为 `fail` 时阻断进入下一阶段。
- review verdict 为 `pass` 或 `warn` 时，只能给出下一步唯一建议，由 PM 手动执行下一命令。
- 存在 open `fix_debts` 时，必须先执行 `pm-fix-review` 收口。

## 2.1 版本标识（revision）

- 阶段 writer 每次首次生成或多轮更新，必须产生新的 `artifact_revision` 和 `metadata_revision`（ISO 时间格式）。
- 更新 `status.yaml` 的 `stage_revisions[stage]`。
- metadata 文件中也记录本轮 `metadata_revision`。
- reviewer 写 `review_results` 时必须绑定当前阶段 `artifact_revision` 和 `metadata_revision`。
- 下游 writer 和 pm-guide 判断 review 是否有效时，必须同时校验路径和 revision。路径一致但 revision 不一致时，视为过期，不得放行下一阶段。
- 当前阶段多轮更新后，旧 review 自动失效，必须重新执行对应 reviewer。

## 3. 上游绑定

进入下游 writer 前必须校验上游最近一条有效 self_check 或 reviewer_check：

- `verdict` 为 `pass` 或 `warn`
- `reviewed_artifact` 等于上游最新人读产物路径
- `reviewed_metadata` 等于上游最新 metadata 入口路径
- `reviewed_artifact_revision` 等于上游 `stage_revisions` 最新 `artifact_revision`
- `reviewed_metadata_revision` 等于上游 `stage_revisions` 最新 `metadata_revision`

## 3.1 阶段递进基线

PMFlow 使用"阶段递进基线"，不是后续永远以 align 为事实基线。

### 阶段基线定义

- **input**：材料来源索引，不是事实基线。
- **align**：第一个需求事实基线，约束 design 的目标、范围、建设类型、一期/二期边界、主角色和主流程方向。
- **design**：详细设计事实基线，review 通过后成为 wireframe / PRD / prototype 的主要事实来源。
- **wireframe**：页面组织和交互表达基线，review 通过后成为 PRD / prototype 的页面表达参考。
- **PRD**：研发评审与归档基线，review 通过后成为 prototype 的正式需求说明来源之一。
- **prototype**：高保真交互表达基线，review 通过后作为主链终点产物。

### 阶段细化规则

- 当前阶段可以在职责范围内细化、补充和修正上游内容。
- design 可以补功能清单、页面清单、数据字典、系统流程、业务规则、MVP 优先级。
- wireframe 可以调整页面组织、跳转关系和信息呈现方式。
- PRD 可以把 design/wireframe 细化为研发可评审的自然语言需求。
- prototype 可以把 PRD/wireframe 转成高保真交互表达。
- 只有改变上游核心目标、范围、建设类型、一期/二期边界或主流程方向时，才必须回到对应上游阶段。
- 下游阶段应读取最近已通过 review 的上游基线，不得直接采用 input 旧结论，也不得永远回到 align 判断所有事实。

### 事实基线规则

- input 是材料盘点和来源索引，不是需求事实基线。
- align 是进入 design 的第一个需求事实基线。
- design 及后续阶段读取需求事实时，以各阶段最新基线为准，不直接采用 input 旧结论。
- 已被 align 覆盖、修正、否定的 input 旧口径，不得作为 warning 或 fail。

## 4. 阶段循环规则

- 当前阶段 review 前，用户继续补充内容，应继续使用当前阶段命令。
- 当前阶段命令负责多轮更新和同步，不使用 /pm-fix。
- 当前阶段 reviewer fail 后，回到当前阶段命令修正。
- 阶段通过 review 后，如果 PM 再做局部修改，才使用 /pm-fix。
- 需求目标、范围、建设类型变化，回到 /pm-align，不按 /pm-fix 处理。

## 5. reviewer 规则

reviewer 必须独立读取被审产物和对应 metadata，不能只复述 writer 自检。

reviewer 输出：

- `.pmflow/reviews/<stage>-review-<timestamp>.yaml`
- 追加一条 `status.review_results`
- 下一步唯一建议

reviewer 不改写被审产物，不生成新的业务产物。

## 6. 轻量 metadata 约束

- 所有阶段 writer 必须遵守 `contracts/lightweight-metadata.md`。
- 所有 reviewer 必须按轻量 metadata 口径审查。
- 阶段递进基线继续有效。

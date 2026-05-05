# 门禁契约

## 1. verdict 语义

| verdict | 含义 | 后续行为 |
|---|---|---|
| pass | 满足进入下一阶段条件 | 建议下一步命令，PM 手动执行 |
| warn | 存在可接受风险或待 PM 知情项 | 记录 warning，建议下一步命令，PM 手动执行 |
| fail | 存在阻断问题 | 回到当前阶段修正，不得推荐下一阶段 |

## 2. 通用门禁顺序

1. 先检查未收口 `fix_debts`。
2. 再检查当前阶段产物是否存在。
3. 再检查对应 self_check 或 reviewer_check 是否存在。
4. 再检查 verdict。
5. 再检查 `reviewed_artifact`、`reviewed_metadata` 是否绑定最新产物。
6. 再检查 `reviewed_artifact_revision`、`reviewed_metadata_revision` 是否等于 `stage_revisions` 中当前阶段最新 revision。路径一致但 revision 不一致时，视为"产物已更新但尚未重新 review"，不得放行。

## 3. writer 门禁

writer 进入前必须确认上游已通过：

- input 之后读取 input self_check
- align/design/wireframe/prd/prototype 之前读取上游 reviewer_check

上游 check 为 `fail`、缺失或绑定过期时，writer 停止，不写产物，不更新 status。

## 4. reviewer 门禁

reviewer 进入前必须确认：

- 当前阶段产物存在
- 当前阶段 metadata 存在
- 上游最新有效 check 未失效

reviewer 只审查当前阶段是否可进入下一阶段，不替 writer 修改产物。

## 4.1 轻量 metadata 门禁

- review 不检查 metadata 是否复述正文。
- review 检查 metadata 是否能追溯、定位、覆盖和绑定 revision。
- metadata 轻量化违规可作为 fail：例如 metadata 大段复制正文、出现禁止字段、缺少关键对象索引。

## 5. PM ownership gate

PM ownership gate 通过“PM 手动执行下一命令”体现。

AI 完成当前阶段后必须停止，不得自动进入下一阶段。

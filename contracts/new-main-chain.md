# 主链路契约

## 1. 阶段顺序

```text
input -> align -> design -> wireframe -> prd -> prototype
```

## 2. 推进机制

- writer 执行成功后更新 `current_stage`、`artifacts`、metadata 和 snapshot。
- reviewer 不推进 `current_stage`，只写 review 文件并追加 `status.review_results`。
- review verdict 为 `fail` 时阻断进入下一阶段。
- review verdict 为 `pass` 或 `warn` 时，只能给出下一步唯一建议，由 PM 手动执行下一命令。
- 存在 open `fix_debts` 时，必须先执行 `pm-fix-review` 收口。

## 3. 上游绑定

进入下游 writer 前必须校验上游最近一条有效 self_check 或 reviewer_check：

- `verdict` 为 `pass` 或 `warn`
- `reviewed_artifact` 等于上游最新人读产物路径
- `reviewed_metadata` 等于上游最新 metadata 入口路径

## 4. reviewer 规则

reviewer 必须独立读取被审产物和对应 metadata，不能只复述 writer 自检。

reviewer 输出：

- `.pmflow/reviews/<stage>-review-<timestamp>.yaml`
- 追加一条 `status.review_results`
- 下一步唯一建议

reviewer 不改写被审产物，不生成新的业务产物。

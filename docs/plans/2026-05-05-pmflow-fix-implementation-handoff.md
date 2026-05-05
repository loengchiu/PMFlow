# PMFlow fix 闭环实施交接

## 任务目标

完善 PMFlow `/pm-fix` 与 `/pm-fix-review` 第一版闭环。

只做 skill、contract、schema、smoke 层，不做真实业务项目产物生成，不做 `change` / `review-pack` / `export`，不提交、不推送。

## 工作目录

```text
D:\work\PMFlow
```

## 必读文件

```text
AGENTS.md
commands/pm-fix.md
commands/pm-fix-review.md
skills/pm-fix/SKILL.md
skills/pm-fix-reviewer/SKILL.md
contracts/review-debt.md
contracts/human-sync.md
contracts/snapshot-diff.md
schemas/status.schema.yaml
skills/pm-guide/SKILL.md
scripts/pmflow-new-main-e2e-smoke.py
```

## 一、修正现有冲突

修正 `skills/pm-fix/SKILL.md` 使用示例。

当前示例中如果仍出现下面这类输出，需要删除或改写：

```text
下一步建议：/pm-prototype-review
下一步建议：/pm-design-review
下一步建议：/pm-wireframe-review
下一步建议：/pm-prd-review
```

现行口径：

- 只要本轮写入 `status: open` 的 `fix_debts`，下一步唯一建议必须是 `/pm-fix-review`。
- 阶段 review 只由 `/pm-fix-review` 根据 `needs_stage_review` 给出。

示例统一改成：

```text
/pm-fix 完成修改或登记债务
fix_debts 已登记
下一步唯一建议：/pm-fix-review
```

同步检查：

```text
commands/pm-fix.md
commands/pm-fix-review.md
```

确保命令文件与上述口径一致。

## 二、补齐 fix_debts 结构

更新：

```text
schemas/status.schema.yaml
contracts/review-debt.md
```

`fix_debts` 每条记录补齐以下字段：

```yaml
debt_id: DEBT-{timestamp}
change_level: L1 | L2 | L3 | L4 | L5
source_stage: design | wireframe | prd | prototype
affected_stages: []
description: ""
affected_objects: []
changed_files: []
metadata_files: []
snapshot_files: []
sync_status: synced | partial | pending | blocked
needs_stage_review: []
created_at: ""
status: open | closed
closed_at: ""
close_reason: ""
```

字段含义：

- `changed_files`：本次实际修改过的人读产物或原型文件。
- `metadata_files`：本次同步修改过的 metadata 文件。
- `snapshot_files`：本次更新过的 snapshot 文件。
- `sync_status`：
  - `synced`：人读物、metadata、snapshot 已同步。
  - `partial`：已修改部分文件，但仍有明确待同步项。
  - `pending`：只登记债务，尚未实际修改。
  - `blocked`：无法定位对象或属于 L5，不继续执行。
- `needs_stage_review`：由 `/pm-fix` 初判，最终由 `/pm-fix-review` 合并后给出建议。

## 三、强化 /pm-fix SOP

更新：

```text
skills/pm-fix/SKILL.md
```

保持 `<300` 行。

必须写清楚执行顺序：

1. 读取 status。
2. 如果 `current_stage = uninitialized`，停止。
3. 如果已有 open L5 debt，停止，提示回到 `/pm-align`。
4. 读取 PM 输入。
5. 读取相关 snapshot：`.pmflow/snapshots/<stage>/<stage>.last-synced.*`。
6. 读取当前人读产物。
7. 做 diff 判断：
   - PM 明确描述了修改点时，以 PM 描述为主。
   - PM 只说“我改了文档，你同步一下”时，必须用 snapshot diff 找出变更片段。
   - 不得把全文和快照全文一起塞进上下文。
8. 根据 diff 或 PM 描述定位对象：
   - 页面
   - 字段
   - 流程
   - 规则
   - 操作
   - 原型交互
9. 无法唯一定位对象时停止询问，不得猜。
10. 判断变更等级 L1-L5。
11. 判断影响阶段。
12. 对 L1/L2：
   - 可局部修改相关产物。
   - 同步 metadata。
   - 更新 snapshot。
   - 写 `sync_status: synced` 或 `partial`。
13. 对 L3/L4：
   - 可以在能明确同步的范围内局部修改。
   - 必须登记 `needs_stage_review`。
   - 若无法安全同步，只登记 `sync_status: pending`。
14. 对 L5：
   - 不按 fix 修改。
   - 登记或提示回到 `/pm-align`。
15. 写入 `fix_debts`。
16. 输出下一步唯一建议：`/pm-fix-review`。
17. 停止。

## 四、强化 /pm-fix-review SOP

更新：

```text
skills/pm-fix-reviewer/SKILL.md
```

保持 `<300` 行。

必须写清楚：

1. 读取所有 open `fix_debts`。
2. 如果没有 open debt，停止。
3. 合并 `affected_stages` / `affected_objects`。
4. 检查 `changed_files` 是否存在。
5. 检查 `metadata_files` 是否存在。
6. 检查 `snapshot_files` 是否存在。
7. 检查 `sync_status`：
   - `blocked` -> fail
   - `pending` -> warn 或 fail，取决于是否影响主链继续
   - `partial` -> warn
   - `synced` -> 可 pass
8. 检查同类关联点：
   - 同字段在多个页面出现。
   - 同操作在 PRD 和 prototype 都出现。
   - 上游 design 修改但下游 prd/prototype 未同步。
9. 合并 `needs_stage_review`。
10. 写 `.pmflow/reviews/fix-review-{timestamp}.yaml`。
11. verdict 为 pass/warn 时：
   - 关闭已收口 debt。
   - 写 `closed_at`。
   - 写 `close_reason`。
12. verdict 为 fail 时：
   - 不关闭 debt。
   - 输出待处理项。
13. 输出下一步：
   - fail：继续 `/pm-fix`。
   - pass/warn 且 `needs_stage_review` 非空：提示手动执行对应阶段 review。
   - pass/warn 且不需要阶段 review：提示回到正常主链，由 PM 手动执行下一命令或 `/pm-guide` 查看。

## 五、更新 contract

更新：

```text
contracts/review-debt.md
contracts/human-sync.md
contracts/snapshot-diff.md
```

要求：

- contract 只放跨 skill 硬约束。
- 不写长解释。
- 不写一次性讨论背景。
- 明确 snapshot diff 是 `/pm-fix` 的确定性输入来源，不是主流程脚本驱动。
- 明确 reviewer 不更新 snapshot。
- 只有 writer、fix、fix-review 可以在同步完成时更新 snapshot。

## 六、补 smoke 测试

更新：

```text
scripts/pmflow-new-main-e2e-smoke.py
```

新增测试：

1. `/pm-fix` 示例不直接推荐阶段 review。

断言 `skills/pm-fix/SKILL.md` 示例区不包含：

```text
下一步建议：/pm-design-review
下一步建议：/pm-wireframe-review
下一步建议：/pm-prd-review
下一步建议：/pm-prototype-review
```

2. `/pm-fix` 示例必须包含：

```text
下一步唯一建议：/pm-fix-review
```

3. status schema 的 `fix_debts` 包含：

```text
changed_files
metadata_files
snapshot_files
sync_status
close_reason
```

4. `sync_status` 枚举包含：

```text
synced
partial
pending
blocked
```

5. `/pm-fix-reviewer` 包含：

```text
合并 open fix_debts
检查 changed_files / metadata_files / snapshot_files
检查 sync_status
合并 needs_stage_review
pass/warn 关闭 debt
fail 不关闭 debt
```

6. pm-guide 仍保持：

```text
open fix_debts 最高优先推荐 /pm-fix-review
```

## 七、运行验证

执行：

```text
python scripts\pmflow-new-main-e2e-smoke.py
python scripts\pmflow-gate-boundary-smoke.py
python scripts\pmflow-gate-runtime-smoke.py
git diff --check
git status --short
```

## 八、输出结果

最后输出：

```text
修改了哪些文件
/pm-fix 做到了什么
/pm-fix-review 做到了什么
新增了哪些测试
三组 smoke 结果
git diff --check 结果
当前 git status
```

## 禁止事项

- 不提交。
- 不推送。
- 不使用 PowerShell 脚本。
- 不新增 change / review-pack / export。
- 不改主链阶段顺序。
- 不把 `/pm-confirm` 接回 new_main。
- 不把脚本变成主流程执行层。
- 不做真实业务项目产物生成。

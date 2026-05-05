# PMFlow

PMFlow 是一套用于 B 端中后台需求工作的 Claude Code skills。它把一个模糊需求拆成可控的阶段，让 PM 逐步产出需求对齐稿、详细设计、线框说明、正式 PRD 和高保真 HTML 原型。

PMFlow 的核心原则：AI 负责生成、检查和同步；PM 负责阅读、修改和手动决定是否进入下一步。

## 适用场景

- 新建系统、模块或功能。
- 现有系统优化迭代。
- 既有功能改造 + 新功能补充的混合需求。
- 需求材料不完整，需要先吸收材料、暴露缺口、再逐步补齐。
- PRD、线框、原型之间需要反复同步修改，避免字段、页面、流程、规则脱钩。

## 安装

当前发布包支持 Claude Code 和 Trae-CN。

```bash
cd D:\work\PMFlow
python install.py install --host claude-code
python install.py verify --host claude-code
```

Trae-CN：

```bash
python install.py install --host trae-cn
python install.py verify --host trae-cn
```

看到下面输出表示安装成功：

```text
pmflow-verify:ok
```

卸载：

```bash
python install.py remove --host claude-code
python install.py remove --host trae-cn
```

详细安装说明见 `docs/usage/claude-install.md`。

## 第一次使用

1. 打开业务项目目录，不是在 PMFlow 仓库里写业务产物。

```bash
cd D:\work\你的业务项目
```

2. 在 Claude Code 里执行：

```text
/pm-input
```

也可以说：

```text
初始化 PMFlow。这里是需求材料：...
```

3. PMFlow 会在业务项目目录下创建：

```text
.pmflow/   # 状态、metadata、review、snapshot，给 AI 和脚本读
output/    # PM、需求方、研发可读产物
```

不要把业务项目的 `.pmflow/` 和 `output/` 写回 PMFlow 仓库。

## 日常怎么跑

不确定当前该做什么时，执行：

```text
/pm-guide
```

`/pm-guide` 只读取 `.pmflow/status.yaml`，判断当前阶段和唯一下一步。它不会扫描业务文件，也不会自动推进流程。

主链路：

```text
/pm-input
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
```

每一步完成后，AI 必须停下。你需要阅读产物、必要时手动修改，然后再决定是否执行下一条命令。

## 每个阶段产出什么

| 命令 | 产出 | 你要看什么 |
|---|---|---|
| `/pm-input` | 材料吸收记录、建设类型、缺口问题 | AI 有没有漏掉你给的材料，需求方认可的表格/字段/流程有没有被记录 |
| `/pm-align` | 需求对齐稿 | 对需求方的理解、目标、范围、方案方向是否准确 |
| `/pm-align-review` | 对齐稿审查结果 | 是否还有遗漏、误解、越界设计 |
| `/pm-design` | 功能清单、页面清单、数据字典、系统流程、规则设计 | 详细设计是否完整，字段/页面/流程/规则是否能支撑后续 PRD |
| `/pm-design-review` | 设计审查结果 | design 是否能进入线框和 PRD |
| `/pm-wireframe` | 线框说明稿 | 页面组织、跳转、主流程和字段落点是否直观 |
| `/pm-wireframe-review` | 线框审查结果 | 是否发现 design 阶段没暴露的问题 |
| `/pm-prd` | 正式 PRD | 文风是否自然，字段与详细说明是否一致，能否给研发评审 |
| `/pm-prd-review` | PRD 审查结果 | 是否可评审、可归档，是否有追溯缺口 |
| `/pm-prototype` | 高保真 HTML 原型 | 页面是否符合 PRD 和现有 UI 风格，主流程能否点击走通 |
| `/pm-prototype-review` | 原型审查结果 | 原型是否覆盖页面、字段、操作、流程和规则 |

## 修改怎么做

如果你在任意阶段发现问题，执行：

```text
/pm-fix 待审批列表中点击详情应该跳转新页面，而不是展开抽屉。
```

`/pm-fix` 会做三件事：

1. 定位修改对象。
2. 判断影响 design、wireframe、PRD、prototype 中哪些产物。
3. 修改能安全同步的文件，并登记 `fix_debts`。

只要产生 open 状态的 `fix_debts`，下一步必须执行：

```text
/pm-fix-review
```

`/pm-fix-review` 用来收口本批修改，判断是否还需要重新跑某个阶段的 review。你可以连续执行多次 `/pm-fix`，最后统一执行一次 `/pm-fix-review`。

## 人读物和机读物

PMFlow 每个阶段通常会同时写两类文件。

人读物在 `output/`：

```text
output/align/
output/design/
output/wireframe/
output/prd/
output/prototype/
```

这些文件给 PM、需求方和研发看。人读物里不应该出现内部路径、metadata 字段、review 字段或机器 ID。

机读物在 `.pmflow/`：

```text
.pmflow/status.yaml
.pmflow/metadata/
.pmflow/reviews/
.pmflow/snapshots/
```

这些文件给 AI 和校验脚本读，用于阶段判断、来源追溯、review 绑定和修改同步。

## 推进规则

- writer 负责生成当前阶段产物。
- reviewer 负责独立审查当前阶段产物。
- reviewer 通过后也不会自动进入下一阶段。
- 下一阶段只能由 PM 手动执行下一条命令。
- review 不会自动触发，仍由 PM 手动执行 `/pm-xxx-review`。
- PMFlow 不使用 hook 自动推进或自动 review。
- 有未收口的 `/pm-fix` 债务时，`/pm-guide` 会优先推荐 `/pm-fix-review`。
- 当前发布版不使用 `/pm-confirm`。

## Review 执行方式

推荐在新会话或独立 agent 中执行 review，确保审查独立于 writer 会话。

- Claude Code：可使用 subagent 或新会话执行 reviewer。
- Trae-CN：默认按独立审查模式执行。
- 其他宿主：默认按独立审查模式执行。

独立审查模式要求 reviewer 重新读取 status、产物、metadata 和 profile，不依赖 writer 会话结论。详见 `contracts/reviewer-independence.md`。

## 常见情况

### 不知道下一步做什么

执行：

```text
/pm-guide
```

### 需求方又补了材料

如果还在 input/align 阶段，直接回到对应阶段补充：

```text
/pm-input 需求方补了一份字段表，你看一下。
/pm-align 需求方补了流程图，更新对齐稿。
```

`/pm-input` 只列问题，不回答问题。回答问题在 `/pm-align` 阶段处理：

- 简短事实可以在执行 `/pm-align` 时直接补充，例如 `/pm-align 审批层级是两级`。
- 字段表、流程图、截图、会议纪要这类成批材料，先放到业务项目文件里，再执行 `/pm-input 文件路径是 ...`。如果是大批原始材料再回 `/pm-input`，新增少量材料可在 `/pm-align` 时提供。
- 需要需求方确认的问题，先问需求方，拿到确认后在 `/pm-align` 中补充。

人读稿里的问题编号只用 `1`、`2`、`3`，复杂 ID 只保留在 `.pmflow/metadata/` 里。

如果已经进入 design、PRD 或 prototype，使用：

```text
/pm-fix 需求方补充了字段表，需要同步到设计、PRD 和原型。
```

### 我手动改了文档

执行：

```text
/pm-fix 我手动改了 PRD，请对比 snapshot 并同步 metadata 和下游影响。
```

PMFlow 会用 `.pmflow/snapshots/` 里的快照做 diff，不要求你重新描述每一处修改。

### PRD 或原型发现设计问题

用 `/pm-fix` 描述问题。它会判断需要回到 design、wireframe、PRD 还是 prototype，并通过 `/pm-fix-review` 收口。

## 发布包结构

| 目录 | 说明 |
|---|---|
| `skills/` | 每个命令的执行 SOP |
| `contracts/` | 跨 skill 的硬约束 |
| `profiles/` | 阶段产物的机读契约 |
| `schemas/` | 状态结构 schema |
| `references/` | 写法参考、方法论、示例 |
| `templates/` | 人读产物骨架 |
| `scripts/python/` | 安装和 smoke 校验脚本 |
| `docs/usage/` | 安装和使用说明 |

## 开发和验收

修改 PMFlow 自身后，跑：

```bash
cd D:\work\PMFlow
python scripts/python/pmflow-smoke.py
python install.py verify --host claude-code
git diff --check
```

期望结果：

```text
pmflow-smoke:ok
pmflow-verify:ok
```

`git diff --check` 没有错误即可。Windows 下出现 LF/CRLF 提示不算失败。

## 什么时候推送

确认以下条件满足后再提交推送：

- 发布包里没有过程文档、临时测试夹具、旧命令入口。
- `skills/` 只保留当前主链和 fix 链。
- `README.md`、`AGENTS.md`、`pm-guide` 的主链路口径一致。
- smoke、安装校验、diff check 都通过。

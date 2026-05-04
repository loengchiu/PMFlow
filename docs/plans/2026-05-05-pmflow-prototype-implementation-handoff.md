# PMFlow Prototype 阶段实施交接

日期：2026-05-05

## 1. 本轮目标

本轮实现新主链 prototype 阶段：

```text
prd-review -> /pm-prototype -> /pm-prototype-review -> 主链路完成
```

完成后：

- `/pm-prototype` 在 `workflow_mode: new_main` 下不再是 placeholder。
- `/pm-prototype-review` 在 `workflow_mode: new_main` 下不再是 placeholder。
- `output/prototype/index.html` 成为可本地打开的高保真 HTML 原型。
- `.pmflow/metadata/prototype/index.yaml` 能支持页面、字段、动作、流程和来源反查。
- `/pm-guide` 能在 prototype review pass/warn 后输出主链路完成。

本轮不实现：

- DOCX export。
- 工程化前端构建。
- 真实接口联调。
- 完整 `/pm-fix` snapshot diff runtime。
- legacy prototype 链路重构。

## 2. 必读文件

执行前先读：

```text
AGENTS.md
docs/plans/2026-05-05-pmflow-prototype-design.md
references/prototype-ui-style.md
docs/plans/2026-05-04-pmflow-prd-writing-design.md
docs/plans/2026-05-04-markdown-wireframe-design.md
contracts/new-main-chain.md
contracts/gates.md
contracts/human-sync.md
contracts/snapshot-diff.md
schemas/status.schema.yaml
skills/pm-guide/SKILL.md
skills/pm-prd/SKILL.md
skills/pm-prd-reviewer/SKILL.md
profiles/prd-new-main.profile.yaml
profiles/prd-review-new-main.profile.yaml
scripts/pmflow-new-main-e2e-smoke.py
```

同时读取当前 prototype 命令与 skill 文件：

```text
commands/pm-prototype.md
commands/pm-prototype-review.md
skills/pm-prototype/SKILL.md
skills/pm-prototype-reviewer/SKILL.md
```

## 3. 新旧链路分离

只实现 `workflow_mode: new_main` 的 `/pm-prototype` 和 `/pm-prototype-review`。

不要复用旧 `prototype-designer` / `prototype-reviewer` 的 confirmed 前置口径。

新主链 prototype 前置是：

```text
workflow_mode = new_main
current_stage = prd 或 prototype
artifacts.prd 包含 output/prd/prd.md
review_results 中最近一次 prd reviewer_check verdict 为 pass 或 warn
prd review reviewed_artifact = artifacts.prd 最新产物
prd review reviewed_metadata = .pmflow/metadata/prd/index.yaml
不存在 status: open 的 fix_debts
```

前置失败时：

- 停止。
- 说明缺什么。
- 不写 `output/prototype/`。
- 不写 `.pmflow/metadata/prototype/`。
- 不更新 `status.yaml`。
- 不提示主链路完成。

## 4. 原型定位

`/pm-prototype` 生成高保真 HTML 业务原型。

页面内容来自：

```text
PRD + wireframe + metadata + PM 注释
```

视觉表达参考现有 UI 设计稿：

- 左侧导航。
- 顶部一级导航。
- 浅灰背景。
- 白色内容卡片。
- 蓝色主色和选中态。
- 表格、筛选、tab、状态标签、表单、详情分组、时间线等中后台组件语言。

现有 UI 设计稿已转写为文字基准：

```text
references/prototype-ui-style.md
```

Claude 不能读取图片时，以该文件为准，不得只凭“参考设计稿”自由发挥。

页面结构由 PRD 和 wireframe 决定。组件按页面类型选择，不固定强塞。

## 5. Writer 输入

`skills/pm-prototype/SKILL.md` 前置读取：

```text
.pmflow/status.yaml
contracts/new-main-chain.md
contracts/gates.md
contracts/human-sync.md
schemas/status.schema.yaml
references/prototype-ui-style.md
output/prd/prd.md
.pmflow/metadata/prd/index.yaml
.pmflow/metadata/prd/dictionary.yaml
.pmflow/metadata/prd/pages/*.yaml
.pmflow/metadata/prd/rules.yaml
.pmflow/metadata/prd/trace.yaml
output/wireframe/wireframe.md
.pmflow/metadata/wireframe/index.yaml
output/design/design.md（按需）
.pmflow/metadata/design/index.yaml（按需）
最近一次 prd-review 结果
```

读取策略：

- 先读 PRD metadata index。
- 按页面读取 `pages/*.yaml`。
- 只读取当前页面相关字段、规则、wireframe 信息。
- 不一次性读完整大型 PRD 和全部 metadata。

## 6. Writer 生成顺序

`/pm-prototype` 按以下顺序执行：

```text
读取状态和前置基线
-> 校验 prd review pass/warn 且绑定最新 PRD
-> 读取 PRD 页面清单、字段、动作、规则
-> 读取 wireframe 页面结构和跳转
-> 识别页面类型
-> 规划原型页面和主流程
-> 生成 HTML/CSS/JS
-> 写 prototype metadata
-> 写 snapshot
-> 更新 status
-> 输出 /pm-prototype-review
```

页面类型只用于选择组件：

| 页面类型 | 常用组件 |
|---|---|
| 列表管理页 | 筛选区、操作区、表格、状态标签、分页 |
| 详情页 | 分组信息、图片 / 附件占位、明细表、记录区、时间线 |
| 配置页 | tab、配置行、开关、输入框、保存按钮 |
| 看板页 | 指标卡、图表、监控区、趋势图 |
| 审批页 | 详情信息、审批动作、审批记录、状态流转 |
| 表单页 | 分组表单、校验提示、提交 / 取消按钮 |

这些组件按需使用，不改变 PRD 定义。

## 7. Writer 输出

写入：

```text
output/prototype/index.html
output/prototype/assets/（按需）
.pmflow/metadata/prototype/index.yaml
.pmflow/snapshots/prototype/prototype.last-synced.html
```

`index.html` 第一版可以内嵌 CSS / JS。代码明显过长时拆分：

```text
output/prototype/assets/style.css
output/prototype/assets/app.js
```

更新 `.pmflow/status.yaml`：

```yaml
current_stage: prototype
artifacts:
  prototype:
    - output/prototype/index.html
snapshot_records:
  - stage: prototype
    artifact: output/prototype/index.html
    snapshot: .pmflow/snapshots/prototype/prototype.last-synced.html
```

输出：

```text
高保真原型生成完成。

产物：
- output/prototype/index.html
- .pmflow/metadata/prototype/index.yaml
- .pmflow/snapshots/prototype/prototype.last-synced.html

需要独立审查：
- 页面是否覆盖 PRD 核心页面
- 字段、动作、状态是否和 PRD 一致
- 主流程是否能点击走通
- 视觉是否贴近现有系统设计稿
- 是否新增未确认业务逻辑

下一步唯一建议：/pm-prototype-review
```

## 8. Prototype metadata

`.pmflow/metadata/prototype/index.yaml` 至少记录：

```yaml
prototype:
  artifact: output/prototype/index.html
  source_prd_artifact: output/prd/prd.md
  source_prd_metadata: .pmflow/metadata/prd/index.yaml
  source_wireframe_artifact: output/wireframe/wireframe.md
  source_wireframe_metadata: .pmflow/metadata/wireframe/index.yaml

pages:
  - page_id: PROTO-PAGE-001
    page_name: 页面名称
    page_type: 列表管理页
    prd_page_ref: PRD-PAGE-001
    wireframe_page_ref: WIREFRAME-PAGE-001
    prototype_anchor: "#page-001"
    fields:
      - field_id: PRD-FIELD-001
        field_name: 字段名
        visible: true
        location: 列表区
    actions:
      - action_id: PRD-ACT-001
        action_name: 查看详情
        visible: true
        interaction: 点击后切换到详情页

flows:
  - id: PROTO-FLOW-001
    name: 查看详情
    steps:
      - page: PROTO-PAGE-001
        action: PRD-ACT-001
      - page: PROTO-PAGE-002
```

metadata 用于 reviewer 和 `/pm-fix` 反查，不进入原型可见页面。

## 9. Reviewer 输入

`skills/pm-prototype-reviewer/SKILL.md` 前置读取：

```text
.pmflow/status.yaml
contracts/new-main-chain.md
contracts/gates.md
schemas/status.schema.yaml
output/prototype/index.html
.pmflow/metadata/prototype/index.yaml
output/prd/prd.md
.pmflow/metadata/prd/index.yaml
.pmflow/metadata/prd/dictionary.yaml
.pmflow/metadata/prd/pages/*.yaml
.pmflow/metadata/prd/rules.yaml
output/wireframe/wireframe.md
.pmflow/metadata/wireframe/index.yaml
```

前置检查：

```text
workflow_mode = new_main
artifacts.prototype 包含 output/prototype/index.html
output/prototype/index.html 存在
.pmflow/metadata/prototype/index.yaml 存在
prototype metadata 能反查页面、字段、动作、流程、来源
```

前置失败时停止，不写 review，不更新 status，不提示主链完成。

## 10. Reviewer 检查项

逐项检查：

| 检查项 | pass | warn | fail |
|---|---|---|---|
| 可打开性 | index.html 可本地打开 | 个别资源缺失但主体可看 | 主文件缺失或无法打开 |
| 页面覆盖 | PRD 核心页面均有原型表达 | 边缘页面可补 | 核心页面缺失 |
| 字段覆盖 | 核心字段在对应页面可见或可交互 | 边缘字段可补 | 核心字段缺失或错位 |
| 动作覆盖 | 核心动作有入口和反馈 | 边缘动作可补 | 核心动作缺失 |
| 流程走通 | 主流程可点击走通 | 边缘分支可补 | 主流程断裂 |
| 规则表达 | 核心校验、状态、权限、异常有可见表达 | 边缘规则可补 | 核心规则不可见 |
| UI 一致性 | 贴近现有中后台设计稿 | 个别样式粗糙 | 风格明显偏离业务系统 |
| 范围一致 | 未新增 PRD 未确认内容 | 个别文案需对齐 | 新增未确认字段、动作、状态或流程 |
| 人机分离 | 页面不展示内部 metadata/review/稳定 ID | 不适用 | 页面出现内部字段或调试信息 |

判定规则：

- 核心页面缺失：fail。
- 主流程不可点击走通：fail。
- 核心字段和 PRD / dictionary 不一致：fail。
- 新增未确认业务流程：fail。
- UI 细节略粗糙但不影响评审：warn。
- 主流程、核心字段、核心动作、视觉语言均满足：pass。

## 11. Reviewer 输出

写入：

```text
.pmflow/reviews/prototype-review-{timestamp}.yaml
```

追加同一条记录到 `.pmflow/status.yaml` 的 `review_results`：

```yaml
stage: prototype
check_type: reviewer_check
verdict: pass | warn | fail
reviewed_artifact: output/prototype/index.html
reviewed_metadata: .pmflow/metadata/prototype/index.yaml
checks_detail: []
fail_reasons: []
warnings: []
checked_at: ""
reviewer: pm-prototype-reviewer
```

reviewer 不修改 `current_stage`。

pass / warn 输出：

```text
原型审查完成。

整体判定：pass / warn

逐项结果：
- 可打开性：...
- 页面覆盖：...
- 字段覆盖：...
- 动作覆盖：...
- 流程走通：...
- 规则表达：...
- UI 一致性：...
- 范围一致：...
- 人机分离：...

下一步唯一建议：主链路完成。如需修改，执行 /pm-fix。
```

fail 输出：

```text
原型审查未通过。

阻断项：
- ...

下一步唯一建议：/pm-prototype
```

如果问题来自 PRD / wireframe / design 基线变化，建议 `/pm-fix`，但不自动执行。

## 12. Command 和 guide 路由

更新 `commands/pm-prototype.md`：

- `workflow_mode: new_main` 触发 `pm-prototype`。
- 不触发旧 prototype-designer。
- 不提示 `/pm-confirm`。
- 完成后只提示 `/pm-prototype-review`。

更新 `commands/pm-prototype-review.md`：

- `workflow_mode: new_main` 触发 `pm-prototype-reviewer`。
- 不触发旧 prototype-reviewer。
- pass/warn 输出主链路完成。
- fail 回 `/pm-prototype` 或建议 `/pm-fix`。
- 不提示 `/pm-confirm`。

检查 `skills/pm-guide/SKILL.md`：

- `current_stage: prd` 且 prd review pass/warn -> `/pm-prototype`
- `current_stage: prototype` 且 artifacts.prototype 为空 -> `/pm-prototype`
- artifacts.prototype 非空且无 prototype review -> `/pm-prototype-review`
- prototype review fail -> `/pm-prototype`
- prototype review pass/warn -> 主链路完成。如需修改用 `/pm-fix`
- open `fix_debts` 仍最高优先 -> `/pm-fix-review`

## 13. 测试要求

更新 `scripts/pmflow-new-main-e2e-smoke.py`，至少新增：

1. `/pm-prototype` command new_main 不再 placeholder。
2. `/pm-prototype-review` command new_main 不再 placeholder。
3. `skills/pm-prototype/SKILL.md` 存在，含 workflow_mode、prd-review 绑定、输出 index.html、metadata、snapshot、status 更新。
4. `skills/pm-prototype-reviewer/SKILL.md` 存在，含 review_results 回写、reviewed_artifact、reviewed_metadata。
5. mock 状态：prd-review pass/warn 后 `/pm-guide` 推荐 `/pm-prototype`。
6. mock 状态：`/pm-prototype` 后 artifacts.prototype 存在，guide 推荐 `/pm-prototype-review`。
7. mock 状态：prototype-review pass/warn 后 guide 输出主链路完成。
8. mock 状态：prototype-review fail 后 guide 推荐 `/pm-prototype`。
9. 全流程 new_main 不出现 `/pm-confirm`。
10. `output/prototype/index.html` 存在。
11. `.pmflow/metadata/prototype/index.yaml` 存在。
12. 原型 skill 明确页面结构来自 PRD/wireframe，UI 参考现有设计稿，组件按页面类型选择。
13. 原型 skill 明确读取 `references/prototype-ui-style.md` 作为 UI 风格基准。

必须运行：

```powershell
python scripts\pmflow-new-main-e2e-smoke.py
python scripts\pmflow-gate-boundary-smoke.py
python scripts\pmflow-gate-runtime-smoke.py
git diff --check
```

## 14. 完成标准

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

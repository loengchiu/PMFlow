# PMFlow 审查手册（给 Codex）

本文件用于 Codex 后续验收 DeepSeek 的 PMFlow 实现结果。验收重点不是“文件有没有生成”，而是“运行模型是否避免旧坑，并能提升产物质量”。

## 1. 审查顺序

按下面顺序审查：

1. 项目结构。
2. 入口与命令。
3. skill 分层。
4. PM ownership gate。
5. writer/reviewer 分离。
6. metadata/profile/schema/lint。
7. 真实项目回归。
8. 文风和产物可读性。

不要先陷入某个模板细节。先判断运行模型是否正确。

## 2. 必查文件

至少检查：

```text
AGENTS.md
prd.machine.yaml
handoff.md
anti-patterns.md
USER-GUIDE.md
commands/
skills/
contracts/
profiles/
schemas/
references/
templates/
scripts/
```

如果 DeepSeek 没有生成这些目录或文件，先判断是否有合理替代。没有合理替代则不通过。

## 3. P0 验收项

任一项不满足，直接判为不通过。

### 3.1 新项目启动不自动生成产物

检查：

- 无状态文件时，`pm-guide` 只能提示初始化和输入方式。
- 不得扫描项目文件后直接生成 BRD/disc。

不通过表现：

- “我已根据项目文件生成首轮问题。”
- “我自动读取了当前目录所有文档作为需求背景。”

### 3.2 每阶段必须停下

检查：

- brd 完成后只提示 `/pm-uc`。
- uc 完成后只提示 `/pm-solution`。
- solution review 通过后只提示 `/pm-proto` 或 `/pm-prd`。
- prototype review 通过后只提示 `/pm-prd`。

不通过表现：

- solution 写完直接做 prototype。
- prototype 写完直接做 PRD。
- PRD 写完直接给评审结论。

### 3.3 writer/reviewer 必须分离

检查：

- solution-writer 和 solution-reviewer 至少是明确分开的两个 skill 或两个命令。
- prototype-designer 和 prototype-reviewer 分离。
- prd-writer 和 prd-reviewer 分离。

不通过表现：

- writer 末尾写几句“自检通过”冒充 reviewer。
- reviewer 没有独立读取 profile/metadata。

### 3.4 人读/机读必须分离

检查：

- `output/` 只放人读产物。
- `.pmflow/metadata/` 放机读 metadata。
- 人读产物不得出现 `anchor_id`、`rules_ref`、`prototype_ref`、复杂组合编号、本地绝对路径。

### 3.5 不得恢复旧 OMP 主流程

检查：

- 不得出现旧 `.ohmypm/status.json` 作为主状态。
- 不得使用旧 `omp-*` 作为唯一命令体系。
- 不得恢复自然语言自动路由。
- 不得恢复 ps1 主流程。

## 4. P1 验收项

这些问题必须修正后才能进入真实项目试用。

### 4.1 `pm-guide` 是否真正有用

必须能回答：

- 当前项目有没有初始化。
- 当前有什么已确认产物。
- 当前缺什么。
- 当前唯一下一步是什么。
- 为什么不能自动推进。

### 4.2 brd-interviewer 是否区分输入类型

必须区分：

- 原始需求。
- 背景材料。
- 会后回答。
- 补充证据。

如果用户补充项目背景，不能回填到会后回答里。

### 4.3 uc-interviewer 是否产出用户路径

必须产出：

- 用户角色。
- 任务目标。
- 主路径。
- 分支路径。
- 状态变化。
- 待确认缺口。

这份产物要能服务 solution 和 prototype。

### 4.4 solution-writer 是否提前暴露字段和流程

必须检查：

- 页面是否有关键字段或字段分组。
- 列表页是否有默认展示字段。
- 表单/详情页是否说明主要字段范围。
- 提交/审批/退回/撤回/归档是否有流程口径。
- 建设类型判断是否正确。

### 4.5 prototype-designer 是否用信息架构

必须检查：

- 列表字段不是随便摆。
- 详情页有分区逻辑。
- 表单字段分组合理。
- 操作按钮位置符合用户任务。
- 主流程能走通。

### 4.6 PRD 是否能独立归档

必须检查：

- PRD 不依赖原型才能读懂。
- 业务规则、异常、权限、数据字典、验收标准完整。
- 字段变更能和数据字典同步。
- 不出现“详见原型”“原型已说明”。

## 5. 真实项目回归

至少用三组真实案例验收。

### 5.1 审计系统

路径：

```text
D:\work\交投软件中心\审计系统
```

必查：

- 参考三方系统但全新部署/代码/数据库/实例，建设类型应为新建。
- 年度审计计划列表有关键字段。
- 年度审计计划详情/表单有字段或字段分组。
- 提交审批有流程口径。
- 小改动只输出影响范围和局部 diff。

### 5.2 公众服务管理

路径：

```text
D:\work\交投软件中心\智慧服务区\公众服务管理
```

必查：

- 项目背景不会被当成第一轮回答。
- 多轮会面问题只问差量。
- 阶段必须由 PM 确认后推进。

### 5.3 智慧服务区资产管理

路径：

```text
D:\work\交投软件中心\智慧服务区\物业管理\资产管理
```

必查：

- PRD 文风接近已认可版本。
- 原型页面结构清楚。
- 页面、字段、动作、数据字典不脱钩。

## 6. 推荐检查命令

按实际项目结构调整：

```powershell
Set-Location -LiteralPath 'D:\work\PMFlow'
git status --short
git diff --check
rg -n "PowerShell|ps1|自然语言自动|自动进入|详见原型|原型已说明|anchor_id|rules_ref|prototype_ref|M\\d{2}-P\\d{2}-A\\d{2}" .
rg -n "writer|reviewer|PM ownership|pm_confirmed|metadata|profile" .
```

如果有 Python 脚本：

```powershell
python -m py_compile scripts\*.py
python scripts\pmflow-lint.py --help
```

## 7. 审查输出格式

Codex 审查时按这个格式输出：

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

## 8. 最终判断

如果 PMFlow 只是把旧 OMP 换了名字，不通过。

如果 PMFlow 能做到：

- 显式入口。
- 阶段停顿。
- writer/reviewer 分离。
- metadata 不露出。
- solution 阶段能暴露字段和流程。
- prototype 阶段能体现信息架构。
- PRD 可独立归档。

则可以进入真实试用。

# PMFlow 交接手册

本文件用于把旧 OMP、ShitPM、testany-eng 的经验交给新项目执行者。先理解这些经验，再开始设计和实现。

## 1. 为什么要新起 PMFlow

旧 OMP 已经能把 `disc -> solution -> proto -> prd -> review` 跑完，但它的质量主要靠用户试用后不断发现问题、再补规则。

这带来几个问题：

- 规则越来越多，但质量不一定稳定。
- 旧机制残留会污染新判断。
- skill 职责混杂，writer 和 reviewer 没有真正分离。
- 自然语言触发容易导致误读、跳步和自动推进。
- AI 做完后 PM 没有真正掌握产物。

PMFlow 不是旧 OMP 的文件级重构，而是重新定义一套 PM 掌控型 workflow。

## 2. 旧 OMP 可以继承什么

可以继承经验，不继承运行时。

可继承：

- 显式命令优于自然语言自动路由。
- 模板、skill、contract、reference 必须分层。
- 人读产物和机读产物必须分离。
- `output/` 只放人读产物。
- 内部状态、metadata、review-pack 放隐藏目录。
- PowerShell 主流程容易引发编码和运行问题，应避免。
- 小改动不能整篇重写。
- 每个阶段完成后必须停下。

不要继承：

- 旧 `.ohmypm/status.json` 结构。
- 旧 contracts 全量内容。
- 旧自然语言路由逻辑。
- 旧 OMP 的 skill 命名和阶段边界。
- 旧 lint 的所有职责。

## 3. ShitPM 给 PMFlow 的经验

ShitPM 的优势：

- PRD 文风比较稳定。
- 页面结构、字段、流程能较好落到 PRD。
- 产物不太容易露出 AI 味。
- 命令入口明确。
- 状态文件能避免完全靠短期上下文。

ShitPM 的不足：

- 后期改需求时，上下游同步困难。
- 字段变化可能只改了字典表，没同步到详细需求说明。
- 自动检查不够深，容易只检查上游不检查下游。
- AI 可以帮你做完，但 PM 有时没有真正掌握内容。

PMFlow 要吸收 ShitPM 的文风和命令稳定性，但要加强：

- 字段、页面、流程、数据字典联动。
- 局部 diff 和影响范围判断。
- PM ownership gate。
- reviewer 独立检查。

## 4. testany-eng 给 PMFlow 的经验

testany-eng 的强点不在于文件多，而在于工程思想成熟。

值得学习：

- `/guide` 先判断当前项目有什么、到哪一步、下一步用哪个 skill。
- interviewer / writer / reviewer 拆得清。
- Phase 0 上下文收集很硬。
- traceability metadata 是一等公民。
- reviewer 不是装饰，而是独立门禁。
- reference 很丰富，但不挤进主流程。
- README 能告诉用户现在该用哪个 skill。
- scripts 只做确定性校验和聚合。

不应照搬：

- API / HLD / LLD / Test Strategy / Test Spec 全链路。
- 全自动工程交付流水线。
- 文档内嵌 `TRACEABILITY-METADATA` 的可见形式。
- 过重的测试和运维链路。

PMFlow 的学习方式：

- 结构上学 testany-eng。
- 范围上保持 PMFlow 聚焦。
- 只覆盖 B 端中后台 PM 需求交付链路。

## 5. 为什么不能全自动

PMFlow 的用户是 PM。PM 后续要负责：

- 和需求方解释方案。
- 在评审会上回答问题。
- 和研发确认字段、流程、边界。
- 归档 PRD。
- 后续处理变更。

如果 AI 一口气从输入做到 PRD，PM 短期省时间，但会丢失对需求的掌握。

所以 PMFlow 必须坚持：

- 每阶段产出后停下。
- PM 阅读、理解、确认后才能继续。
- AI 不替 PM 悄悄完成全链路。
- 下一阶段必须由 PM 显式命令触发。

这不是效率倒退，而是为了确保 PM 仍然是需求掌控者。

## 6. 真实踩坑记录

### 6.1 背景材料被误当会后回答

用户补充项目背景后，AI 把它当作第一轮会后回答，直接回填问题并进入第二轮。

PMFlow 必须区分：

- 原始需求。
- 背景材料。
- 会后回答。
- 补充证据。

### 6.2 solution 漏字段

审计系统项目里，年度审计计划详情和新建计划没有写清计划字段。

PMFlow 的 solution-writer 必须在方案阶段就暴露关键字段或字段分组，不能等到 PRD 才首次出现。

### 6.3 列表页缺少 UI/UX 判断

年度审计计划有几十个字段，但列表页应该只展示用户最关心的字段。

PMFlow 必须在 solution 和 prototype 阶段使用信息架构判断：

- 列表默认展示什么。
- 详情承载什么。
- 表单怎么分组。
- 筛选项怎么取舍。

### 6.4 审批流程没写清

出现“提交审批”，但没有说明审批从哪来、到哪去、通过/驳回后状态如何变化。

PMFlow 必须在 solution 阶段写流程口径，在 PRD 阶段写规则和异常。

### 6.5 建设类型误判

审计系统是参考三方旧系统，但部署、代码、数据库、运行实例都是新的，应判为新建，不是混合。

判断规则：

- 改现有系统：迭代。
- 全新系统，只参考旧资料：新建。
- 同时改存量系统并新增独立部分：混合。

### 6.6 小改动整篇重写

用户随便改一点，AI 就输出新版本整篇 solution，导致难以看 diff，且烧 token。

PMFlow 的 fix/change 必须先判断影响范围，优先局部 diff。

## 7. PMFlow 第一版重点

先不要追求完整生态。

第一版只做强链路：

```text
pm-guide
brd-interviewer
uc-interviewer
solution-writer
solution-reviewer
prototype-designer
prototype-reviewer
prd-writer
prd-reviewer
```

等这条链路在真实项目跑通，再做 fix/change。

## 8. 成功标准

PMFlow 第一版成功，不是因为它生成了很多文件，而是因为：

- PM 知道当前处在哪一步。
- AI 不会跳过 PM 确认。
- 每个阶段有明确输入输出。
- reviewer 能指出 writer 漏掉的东西。
- solution 阶段能提前暴露字段、流程、页面问题。
- prototype 阶段页面布局不再完全靠 AI 经验。
- PRD 能独立归档，不需要研发翻原型才能理解规则。
- 小改动能同步关联位置。

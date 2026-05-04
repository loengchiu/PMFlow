# PMFlow 高保真原型阶段设计

日期：2026-05-05

## 1. 设计结论

PMFlow 的 prototype 阶段直接生成高保真 HTML 原型：

```text
/pm-prototype = 基于 design + wireframe + PRD + PM 注释，生成贴近现有系统 UI 的高保真业务原型。
```

不再拆低保真 / 中保真 / 高保真。前置阶段已经有：

- `design`：模块清单、页面清单、功能清单、数据字典、系统流程。
- `wireframe`：页面结构、跳转关系、主流程草图、字段 / 操作 / 状态落点。
- `prd`：正式需求说明、字段规则、操作规则、验收标准。
- PM 注释：对 PRD、wireframe、页面交互或视觉表达的补充意见。

prototype 阶段的任务是把这些内容变成可点击、可评审、研发能理解的 HTML 原型。

现有 UI 设计稿已经转写为文字基准：

```text
references/prototype-ui-style.md
```

不能读取图片的执行器必须读取该文件，不得只凭“参考设计稿”自由发挥。

## 2. 原型定位

原型用于：

- 产品评审会走查页面和流程。
- 需求方理解页面组织、操作路径和关键状态。
- 研发理解页面布局、字段呈现、操作入口、状态反馈。
- PM 发现 PRD 和 wireframe 在图形化表达中暴露出的遗漏或偏差。

原型不承担：

- 重新设计需求范围。
- 替代 PRD 写业务规则。
- 接入真实后端接口。
- 复刻蓝湖或设计稿的像素级细节。
- 生成生产可上线前端工程。

原型应做到：

- 看起来像现有系统的一部分。
- 页面结构和字段来自 PRD / wireframe。
- 关键流程能点通。
- 关键状态、权限、异常、空状态有可见表达。
- 本地打开即可查看，不依赖复杂安装。

## 3. 输入来源

`/pm-prototype` 读取：

```text
.pmflow/status.yaml
references/prototype-ui-style.md
output/design/design.md
.pmflow/metadata/design/index.yaml
output/wireframe/wireframe.md
.pmflow/metadata/wireframe/index.yaml
output/prd/prd.md
.pmflow/metadata/prd/index.yaml
.pmflow/metadata/prd/dictionary.yaml
.pmflow/metadata/prd/pages/*.yaml
.pmflow/metadata/prd/rules.yaml
.pmflow/metadata/prd/trace.yaml
最近一次 prd-review 结果
PM 注释或 /pm-fix 已收口结果
```

读取策略：

- 先读 PRD metadata index。
- 再按页面读取对应 `pages/*.yaml`。
- 需要字段属性时读取 `dictionary.yaml` 相关字段。
- 需要业务规则时读取 `rules.yaml` 相关规则。
- 需要来源校验时读取 `trace.yaml`。
- 不一次性把完整 PRD 正文、完整 metadata 和完整原型代码全部塞进上下文。

## 4. 结构来源与视觉来源

prototype 的页面结构由 PRD、wireframe、metadata、PM 注释决定。

UI 表达参考现有系统设计稿。当前 UI 基准来自“交投智慧服务区管理平台”示例，风格特征为：

- 左侧模块导航。
- 顶部一级业务域导航。
- 内容区浅灰背景。
- 白色卡片承载页面主体。
- 蓝色作为主色和选中态。
- 中后台高密度信息布局。
- 表格、筛选区、状态标签、分页、tab、配置行、详情分组、时间线是常用组件。
- 主按钮蓝色，辅助操作使用描边或弱化按钮，导出类操作可使用橙色描边。

这些是视觉语言，不是页面内容清单。

执行器以 `references/prototype-ui-style.md` 为准。图片设计稿只作为该文本基准的来源，不要求执行器直接读取图片。

```text
页面内容由 PRD / wireframe / metadata / PM 注释决定。
UI 表达参考现有设计稿。
组件按页面类型选择，不固定强塞。
```

## 5. 页面类型与组件选择

`/pm-prototype` 先识别页面类型，再选择合适组件。页面类型只影响组件选择，不改变 PRD 定义。

| 页面类型 | 常用组件 |
|---|---|
| 列表管理页 | 筛选区、操作区、表格、状态标签、分页、查看 / 编辑 / 删除入口 |
| 详情页 | 分组信息、图片 / 附件占位、明细表、记录区、时间线 |
| 配置页 | tab、配置行、开关、数字输入、文本输入、保存按钮 |
| 看板页 | 指标卡、图表、监控区、趋势图、概览表 |
| 审批页 | 详情信息、审批动作、审批记录、状态流转 |
| 表单页 | 分组表单、必填标识、校验提示、提交 / 取消按钮 |
| 监控页 | 实时状态、视频 / 图像占位、切换按钮、趋势图、告警入口 |

组件选择原则：

- PRD 定义的字段必须在对应页面有可见位置。
- PRD 定义的操作必须有可点击入口或明确不可用状态。
- wireframe 定义的跳转关系要能在原型中走通。
- PRD 中没有的字段、操作、状态、流程不进入原型。
- 页面类型只帮助选择表达方式，不生成额外需求。

## 6. 输出形态

第一版 prototype 使用静态 HTML / CSS / JavaScript：

```text
output/prototype/index.html
output/prototype/assets/
.pmflow/metadata/prototype/index.yaml
.pmflow/snapshots/prototype/prototype.last-synced.html
```

采用静态 HTML 的理由：

- PM、需求方、研发可以直接打开。
- 不需要安装依赖。
- AI 修改成本低。
- 适合评审会展示和快速迭代。
- 后续如需要工程化前端，可以另起任务。

`index.html` 可以内嵌 CSS / JS；当代码明显过长时，可以拆成：

```text
output/prototype/index.html
output/prototype/assets/style.css
output/prototype/assets/app.js
```

拆分只为可维护性，不引入构建工具。

## 7. 原型 metadata

prototype metadata 用于让 reviewer 和 `/pm-fix` 反查页面、动作、字段、跳转和来源。

建议结构：

```yaml
prototype:
  artifact: output/prototype/index.html
  source_prd_artifact: output/prd/prd.md
  source_prd_metadata: .pmflow/metadata/prd/index.yaml
  source_wireframe_artifact: output/wireframe/wireframe.md
  source_wireframe_metadata: .pmflow/metadata/wireframe/index.yaml

pages:
  - page_id: PROTO-PAGE-INBOUND-LIST
    page_name: 入库申请列表页
    prd_page_ref: PRD-PAGE-INBOUND-LIST
    wireframe_page_ref: WIREFRAME-PAGE-INBOUND-LIST
    prototype_anchor: "#page-inbound-list"
    page_type: 列表管理页
    fields:
      - field_id: PRD-FIELD-INBOUND-NO
        visible: true
        location: 列表区
    actions:
      - action_id: PRD-ACT-VIEW-INBOUND
        visible: true
        interaction: 点击后切换到详情页
    states:
      - state_name: 已离场
        visual: 绿色状态标签

flows:
  - id: PROTO-FLOW-VIEW-DETAIL
    name: 查看详情
    steps:
      - page: PROTO-PAGE-INBOUND-LIST
        action: PRD-ACT-VIEW-INBOUND
      - page: PROTO-PAGE-INBOUND-DETAIL
```

metadata 只服务内部校验，不进入人读原型页面。

## 8. 交互范围

第一版高保真原型至少支持：

- 顶部和左侧导航的当前态切换。
- 列表页筛选、重置、查看详情。
- tab 切换。
- 表单输入、保存反馈、校验提示。
- 弹窗打开、确认、取消。
- 详情页返回列表。
- 状态标签和关键状态变化的展示。
- 空状态、加载失败或无数据状态的基本表达。

具体支持哪些交互，取决于 PRD 和 wireframe。

交互实现可以使用 mock 数据。mock 数据要贴近业务字段，不使用无意义占位。

## 9. 样式规则

原型视觉应贴近现有中后台 UI：

- 主色：蓝色当前态、主按钮、tab 下划线。
- 背景：页面浅灰，卡片白底。
- 边框：浅灰线条，表格边界清晰。
- 字号：中后台常规字号，不做营销页大标题。
- 圆角：小圆角，避免过度卡片化。
- 表格：高密度、清晰列头、状态标签、操作列。
- 表单：标签左侧或上方对齐，控件规整，保存按钮明确。
- 详情：分组标题清楚，字段排布留白充足。
- 图表：可用静态 SVG / CSS / 简化图表表达，不强依赖图表库。
- 视频 / 图片：用业务占位或可用素材占位，标注状态。

原型不能变成 landing page、营销页、炫酷大屏或装饰性 demo。

## 10. Reviewer 检查目标

`/pm-prototype-review` 独立审查原型，不复述 writer 自检。

检查项：

| 检查项 | 目标 |
|---|---|
| 可打开性 | `output/prototype/index.html` 可本地打开 |
| 页面覆盖 | PRD 核心页面在原型中有对应页面或状态 |
| 字段覆盖 | PRD 核心字段在对应页面可见或可交互 |
| 动作覆盖 | PRD 核心动作有可点击入口或明确状态 |
| 流程走通 | wireframe / PRD 的主流程能点击走通 |
| 规则表达 | 核心校验、权限、状态、异常有可见表达 |
| UI 一致性 | 视觉语言贴近现有系统设计稿 |
| 范围一致 | 未新增 PRD 未定义的业务字段、操作、状态、流程 |
| metadata 绑定 | reviewed_artifact 和 reviewed_metadata 绑定最新原型 |
| 人机分离 | 原型页面不展示内部 metadata、review 字段、稳定 ID |

判定：

- 核心页面缺失：fail。
- 核心动作不可走通：fail。
- 字段和 PRD / dictionary 不一致：fail。
- 原型新增未确认业务流程：fail。
- 视觉细节略粗糙但不影响评审：warn。
- 边缘页面交互不完整但主流程可评审：warn。
- 主流程、核心字段、核心动作、风格均满足：pass。

## 11. 路由

新主链路由：

```text
prd-review pass/warn -> /pm-prototype
/pm-prototype -> /pm-prototype-review
prototype-review pass/warn -> 主链路完成
prototype-review fail -> /pm-prototype 或 /pm-fix
```

reviewer 不推进阶段，不自动执行下一命令。PM 手动执行下一步。

`/pm-fix` 仍是后续完整化重点。prototype 实现完成后，fix 需要支持：

- PM 修改 PRD 后同步 prototype。
- PM 修改 prototype 后反查是否影响 PRD / wireframe / design。
- 多次 fix 后由 `/pm-fix-review` 收口。

## 12. 验收标准

prototype 阶段实现后，应满足：

1. `/pm-prototype` 不再是 placeholder。
2. `/pm-prototype-review` 不再是 placeholder。
3. PRD review pass/warn 后，`pm-guide` 推荐 `/pm-prototype`。
4. `/pm-prototype` 生成 `output/prototype/index.html`。
5. 原型可本地打开。
6. 原型页面结构来自 PRD / wireframe，不强塞固定组件。
7. 原型视觉贴近现有系统设计稿。
8. 原型支持主流程点击走查。
9. `.pmflow/metadata/prototype/index.yaml` 记录页面、动作、字段、流程、来源。
10. `/pm-prototype-review` 写入 `.pmflow/reviews/prototype-review-{timestamp}.yaml` 并追加 `status.review_results`。
11. prototype review pass/warn 后，`pm-guide` 输出主链路完成。
12. new_main 全流程不接回 `/pm-confirm`。

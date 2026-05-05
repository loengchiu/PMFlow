# 轻量 metadata 契约

## 1. 定位

- metadata 是外部轻量索引，不是人读物副本。
- 人读物是事实主体。
- metadata 负责：稳定 ID、索引、anchors、source_refs、relations、revision、status、coverage、review/fix 定位。

## 2. 通用结构

推荐统一结构：

```yaml
artifact:
  stage: ""
  artifact_path: ""
  metadata_path: ""
  artifact_revision: ""
  metadata_revision: ""

entities:
  pages: []
  fields: []
  rules: []
  flows: []
  roles: []
  scenarios: []

relations: []
coverage: []
waivers: []
```

`relations`、`coverage`、`waivers` 即使为空也应保留，用于 /pm-fix 关联点检测、review 覆盖检查和例外记录。

## 3. 字段轻量化规则

- name/title 不超过 40 字
- short_statement 不超过 80 字
- note 不超过 60 字
- 单个 entity 不超过 25 行
- 单个页面/字段/规则 metadata 分片不超过 300 行
- metadata 文件不得复述人读正文

## 4. 允许保留的字段

- 短 title / name
- 短 statement（建议 80 字以内）
- id
- status
- scope
- priority
- source_refs
- anchors
- relations
- coverage
- revision
- open_questions / risks 的短句
- 页面、字段、规则、流程、角色、场景、交互的对象索引

## 5. 禁止字段

metadata 不得出现以下字段：

- full_content
- paragraph
- page_body
- section_body
- html_body
- detail_text
- long_description
- raw_markdown
- raw_html
- copied_text
- full_acceptance_text

## 6. 禁止行为

- 不得把完整正文、完整页面说明、完整 PRD 段落、完整 HTML、长篇 description 写入 metadata。
- metadata 不得作为第二份 PRD / 第二份 design / 第二份 prototype。
- metadata 不得复述人读物的大段自然语言。
- metadata 字段若像正文段落，应改为 anchor/source_ref/relation，不进入 metadata。

## 7. 各阶段 metadata 定位

### input

- 材料索引、缺口/冲突索引、短线索、source_refs。
- 不是事实基线。
- 禁止长正文复制。

### align

- 需求事实摘要（短 statement）、scope、roles、scenarios、questions、risks、source_refs、relations。
- 不保存长篇业务方向正文副本。
- 是第一个需求事实基线，但 metadata 仍是轻量索引。

### design

- 页面/字段/规则/流程/角色/场景索引。
- 禁止复述完整功能说明。
- 字段只保存 id、name、type/category、anchors、used_by、source_refs、status。
- 页面只保存 id、name、anchors、fields、actions、rules、source_refs、status。
- 规则只保存 id、name、short_statement、anchors、source_refs、relations。
- 是详细设计事实基线，人读 design.md 承载完整说明。

### wireframe

- 页面结构索引、跳转关系、状态/空态/异常态索引。
- 不复述线框说明全文。
- 页面/跳转/状态用 anchors + relations。

### prd

- dictionary/pages/rules/trace 结构轻量化。
- dictionary.yaml：字段主索引，不写长字段说明。
- pages/*.yaml：只记录字段落点、动作落点、规则引用、anchors、source_refs，不复述页面正文。
- rules.yaml：只记录规则短句、锚点、source_refs。
- trace.yaml：只记录来源关系。
- PRD 人读稿承载正式自然语言。

### prototype

- 页面、组件、交互、流程、PRD source refs、anchors。
- 不保存 HTML 正文、CSS、完整组件结构。

## 8. writer 规则

- writer 写 metadata 时只写索引、anchors、source_refs、relations、revision、coverage。
- 不得写长正文副本。
- 不得使用禁止字段。
- 多轮更新时同步索引/关系/revision，而不是复制更新后的正文。

## 9. review 规则

- reviewer 不要求 metadata 复述正文。
- reviewer 检查 metadata 是否能定位人读物关键对象。
- reviewer 检查 relations/source_refs 是否完整。
- reviewer 检查 metadata 是否遗漏关键对象或保留已删除对象。
- 人读物与 metadata 的"不一致"指索引/关系/状态/来源与人读物冲突，不是要求 metadata 逐字复述人读物。

## 10. fix 规则

- /pm-fix 更新人读物后，只同步索引、relations、anchors、source_refs、revision、coverage。
- 不把修改后的正文复制进 metadata。

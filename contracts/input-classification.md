# 输入分类契约

brd-interviewer 和 uc-interviewer 共用。所有进入 interviewer 的输入材料必须按以下四类区分。

## 1. 四类输入

| 类型 | 英文标识 | 来源 | 性质 |
|------|---------|------|------|
| 原始需求 | raw_request | PM 口头描述、需求方直接表述 | 目标：要解决什么问题 |
| 背景材料 | background_material | 文档、旧系统截图、组织架构、流程文件 | 事实补充：现状是什么 |
| 会后回答 | interview_answer | 需求方对具体问题的回复 | 澄清：对问题的回应 |
| 补充证据 | supplementary_evidence | 数据导出、日志、报表、原型截图 | 佐证：支持或修正判断 |

## 2. 区分规则

### 2.1 不得混淆

- **背景材料不是会后回答**：PM 提供的文档、旧系统资料、流程说明是背景，不是需求方对问题的回答。背景材料只能用于补事实，不能当作"需求方已确认"。
- **会后回答必须能对应具体问题**：每条会后回答必须能追溯到 interviewer 提出的具体问题。无法对应问题的回答视为未分类材料，记录到 open_questions。
- **原始需求是起点，不是终点**：原始需求可能模糊、矛盾、遗漏。interviewer 的工作是把原始需求问成可判断的业务目标/用户任务，不是复述原始需求。

### 2.2 标签规则

每条输入在 metadata 中必须标注：

```yaml
source_type: raw_request | background_material | interview_answer | supplementary_evidence
source_description: 简短说明来源
mapped_question_id: 仅 interview_answer 必填，对应问题 ID
confidence: confirmed | inferred | unconfirmed
```

### 2.3 未确认项处理

- `confidence: unconfirmed` 的输入不得作为唯一决策依据
- 未确认项必须写入 open_questions
- 未确认项不影响 pass/warn/fail 判定时走 warn 路径，影响时走 fail 路径

## 3. interviewer 如何使用四类输入

### brd-interviewer

- 原始需求 → 提炼业务目标、范围边界
- 背景材料 → 了解现状、识别约束
- 会后回答 → 填充业务目标细节、确认优先级
- 补充证据 → 校验业务目标是否成立

### uc-interviewer

- 原始需求 → 识别用户角色（不新增角色）
- 背景材料 → 理解现有流程和痛点
- 会后回答 → 确认用户任务、场景、异常路径
- 补充证据 → 校验用户路径是否覆盖真实场景

## 4. 禁止事项

- 不得将同一份材料同时标为 background_material 和 interview_answer
- 不得在未提问的情况下虚构 interview_answer
- 不得将 interviewer 自身的推测标为 confirmed
- 不得将背景材料的组织架构直接当作用户角色（必须经需求方确认）

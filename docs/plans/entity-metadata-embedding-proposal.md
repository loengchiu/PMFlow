# 实体 metadata 嵌入页面方案

## 1. 现状

### 1.1 当前结构

PRD 生成后，metadata 分为 6 类文件：

```
.pmflow/metadata/prd/
  index.yaml          # 总索引
  pages/*.yaml        # 页面 metadata（区域、动作、字段落点）
  entities/*.yaml     # 实体 metadata（数据字典字段主定义）
  rules/*.yaml        # 业务规则
  field_usage.yaml    # 字段落点关系（字段→页面→区域→动作→用途）
  relations.yaml      # PRD 与 design/wireframe 追溯关系
```

同一个实体（如"入库申请"）的字段定义只写在 `entities/*.yaml` 中，但字段的使用信息（在哪些页面、哪个区域、什么用途）分散在 `pages/*.yaml` 和 `field_usage.yaml` 中。

### 1.2 当前方式的好处

- 实体字段主定义单一来源，改一处即可
- 数据字典直接从 `entities/*.yaml` 生成

### 1.3 当前方式的问题

- **维护成本高**：需要维护 `field_usage.yaml` 和 `relations.yaml` 两个关联文件
- **双向反查复杂**：reviewer 需要检查字段↔页面↔区域↔动作↔规则↔验收的 6 向反查关系
- **profile 膨胀**：reviewer profile 需要声明 6 条 `metadata_reachable` 检查
- **跨文件读取多**：生成 PRD、线框图时需要同时读取 pages + entities + field_usage 三类文件
- **生产验证**：审计系统项目的 manifest（3889 行、38 页）未使用独立实体 metadata，质量合格

---

## 2. 提议方案

### 2.1 核心规则

> 实体定义嵌入第一次出现该实体的页面 metadata，其他页面通过引用使用。

### 2.2 新结构

```
.pmflow/metadata/prd/
  index.yaml          # 总索引（含实体索引：实体名→定义所在页面）
  pages/*.yaml        # 页面 metadata（含实体定义 + 引用）
  rules/*.yaml        # 业务规则
  relations.yaml      # PRD 与 design/wireframe 追溯关系
```

删除：
- `entities/*.yaml`（合并到 pages）
- `field_usage.yaml`（合并到 pages）

### 2.3 具体写法

**实体定义页面**（第一次出现的页面）：

```yaml
# pages/P02-入库申请.yaml
page_id: PRD-PAGE-入库申请
page_name: 入库申请页
page_code: P-02

entities:
  - id: PRD-ENT-入库申请
    name: 入库申请
    fields:
      - id: PRD-FIELD-申请单编号
        name: 入库申请单编号
        type: string
        length: 20
        required: true
        description: 系统自动生成，格式为 RK-YYYYMMDD-NNN
      - id: PRD-FIELD-数量
        name: 数量
        type: integer
        required: true
        min: 1
      # ... 其他字段

regions:
  - name: 列表区
    fields:
      - ref: PRD-FIELD-申请单编号
        usage: display
      - ref: PRD-FIELD-数量
        usage: display

actions:
  - id: PRD-ACT-新增入库
    name: 新增入库
    trigger: 点击"新增入库"按钮
    fields:
      - ref: PRD-FIELD-数量
        usage: edit
        validate: 必须大于 0，且为整数
```

**引用页面**（后续出现的页面）：

```yaml
# pages/P03-入库详情.yaml
page_id: PRD-PAGE-入库详情
page_name: 入库详情页
page_code: P-03

entity_refs:
  - ref: PRD-ENT-入库申请
    source_page: PRD-PAGE-入库申请

regions:
  - name: 基本信息区
    fields:
      - ref: PRD-FIELD-申请单编号
        usage: readonly
      - ref: PRD-FIELD-数量
        usage: readonly
```

### 2.4 index.yaml 中的实体索引

```yaml
# index.yaml 增加实体索引
entities:
  - id: PRD-ENT-入库申请
    name: 入库申请
    defined_in: PRD-PAGE-入库申请    # 定义所在页面
    referenced_by:                     # 被哪些页面引用
      - PRD-PAGE-入库详情
      - PRD-PAGE-入库审核
    field_count: 15
```

---

## 3. 各阶段影响

### 3.1 PRD 生成

| 步骤 | 当前方式 | 提议方式 |
|------|---------|---------|
| 生成数据字典 | 读 `entities/*.yaml` | 从各页面 metadata 中提取实体定义 |
| 逐页生成详细需求 | 读 `pages/*.yaml` + `field_usage.yaml` | 只读 `pages/*.yaml`（实体定义已在内） |
| 字段一致性检查 | 双向反查 6 个文件 | 页面内自包含，跨页面通过 `entity_refs` 引用 |

**结论**：PRD 生成更简单，不需要跨读三类文件。

### 3.2 线框图生成

| 需要什么 | 当前方式 | 提议方式 |
|---------|---------|---------|
| 页面字段列表 | 读 `pages/*.yaml` + `field_usage.yaml` | 只读 `pages/*.yaml` |
| 字段属性（类型、必填） | 读 `entities/*.yaml` | 从定义页面读，或通过 `entity_refs` 找到定义页面 |

**结论**：线框图生成更简单。字段属性在定义页面中，引用页面通过 `entity_refs` 可定位。

### 3.3 原型生成

原型主要关注页面结构和交互，几乎不需要实体 metadata。

**结论**：无影响。

### 3.4 Reviewer 审查

| 检查项 | 当前方式 | 提议方式 |
|-------|---------|---------|
| 字段一致性 | 双向反查 field_usage ↔ entities | 页面内自包含检查 + 跨页面引用检查 |
| metadata_reachable | 6 条独立检查 | 简化为：实体定义页面可被引用页面找到 |
| 人机分离 | 不变 | 不变 |

**结论**：审查逻辑简化。

---

## 4. 需要讨论的问题

### 4.1 实体定义放在哪个页面？

选项 A：放在**列表页**（通常是最先出现的页面）

- 优点：列表页通常是用户第一个看到的页面
- 缺点：列表页只展示部分字段，实体定义可能不完整

选项 B：放在**字段最全的页面**（通常是详情页或表单页）

- 优点：实体定义最完整
- 缺点：详情页不一定是最先生成的页面

选项 C：放在**第一个引用该实体字段最多的页面**

- 优点：定义和使用在同一处，减少引用
- 缺点：判断规则不够直观

**建议**：选项 B（字段最全的页面）。理由：实体定义的完整性比"谁先出现"更重要。

### 4.2 字段属性变更时的影响范围？

如果"数量"字段的类型从 integer 改为 decimal：

- 当前方式：改 `entities/*.yaml` 一处，所有页面自动生效
- 提议方式：改定义页面一处，引用页面通过 `ref` 自动生效（因为引用的是 ID，不是属性）

**结论**：两种方式的影响范围一样——都是改一处。因为引用页面用的是 `ref: PRD-FIELD-数量`，不重复写字段属性。

### 4.3 数据字典怎么生成？

当前：直接读 `entities/*.yaml`。

提议：从各页面 metadata 中提取 `entities` 块，合并生成数据字典。或者在 index.yaml 的实体索引中记录定义位置，按需读取。

### 4.4 是否保留 field_usage.yaml？

提议删除。字段落点信息直接写在页面 metadata 的 `regions.fields` 和 `actions.fields` 中，用 `ref` 引用字段 ID + `usage` 标注用途。

如果需要全局查询"哪些页面用到了字段 X"，可以通过 index.yaml 的实体索引 + 遍历页面 metadata 的引用实现。

---

## 5. 迁移成本

如果决定切换，需要：

1. 修改 `profiles/prd-new-main.profile.yaml` 的 `machine_output_requirements`：删除 `entities` 和 `field_usage`，调整 `pages` 结构
2. 修改 `skills/pm-prd/SKILL.md` 的生成顺序和输出描述
3. 修改 `skills/pm-prd-reviewer/SKILL.md` 的 metadata_reachable 检查逻辑
4. 修改 `references/prd-action-examples.md` 的 metadata 示例
5. 更新 e2e 测试中的 metadata 相关断言

迁移成本中等，主要改动在 profile 和 SKILL.md，不涉及 contracts 和 templates。

---

## 6. 结论

| 维度 | 当前方式 | 提议方式 |
|------|---------|---------|
| 文件数量 | 6 类 | 4 类（减少 entities 和 field_usage） |
| 维护成本 | 高（多文件同步） | 中（页面内自包含） |
| reviewer 复杂度 | 高（6 向反查） | 中（页面内 + 引用检查） |
| 数据字典生成 | 直接读取 | 需要提取（略复杂） |
| 字段属性一致性 | 单一来源 | 单一来源（通过 ref） |
| 生产验证 | 有（审计系统） | 无（需要验证） |

---

## 7. 评审结论

**结论**：
- 不采用"实体定义嵌入页面 metadata"作为最终方案。
- 采纳其简化思路：删除独立 `field_usage.yaml`，字段落点回到页面 metadata。
- 保留独立 `dictionary.yaml` 作为字段主定义唯一来源。
- 使用 `trace.yaml` 替代宽泛 `relations.yaml`，只负责 design / wireframe 来源追溯。
- 最终结构为 `index.yaml` + `dictionary.yaml` + `pages/*.yaml` + `rules.yaml` + `trace.yaml`。

**最终 metadata 结构**：

```
.pmflow/metadata/prd/
  index.yaml          # 文件索引（只作为索引，不保存字段主定义）
  dictionary.yaml     # 字段主定义唯一来源
  pages/*.yaml        # 页面 metadata（含字段落点，引用 dictionary.yaml 的 field_id）
  rules.yaml          # 业务规则、异常、权限、验收标准
  trace.yaml          # PRD 与 design/wireframe 的来源追溯关系
```

**删除的文件**：
- `entities/*.yaml`（字段主定义统一到 dictionary.yaml）
- `field_usage.yaml`（字段落点回到 pages/*.yaml）
- `relations.yaml`（改为 trace.yaml，只做来源追溯）

**优势**：
- 文件数量从 6 类减少到 5 类
- 字段主定义唯一来源（dictionary.yaml）
- 字段落点在页面 metadata 中自包含
- reviewer 检查逻辑简化
- index.yaml 不再作为字段事实源

---
name: pm-guide
description: PMFlow 流程导航。读取状态文件，判断当前阶段和唯一下一步。
triggers: ["/pm-guide"]
tags: [pmflow, guide, router]
---

# pm-guide SOP

## 1. 前置读取

执行前必须读取：

- `contracts/gates.md`
- `contracts/new-main-chain.md`
- `schemas/status.schema.yaml`

禁止读取任何项目业务文件。

## 2. 状态检测

### 2.1 `.pmflow/status.yaml` 不存在

项目未初始化。

输出：

- 状态：未初始化
- 下一步唯一建议：`/pm-input`
- 提示：请提供需求材料、截图、文档路径或口头描述

不得自动创建 `.pmflow/`、`status.yaml`，不得扫描项目文件充当需求。

### 2.2 `.pmflow/status.yaml` 存在

读取 `status.yaml`，先判断未收口变更，再判断阶段路由。

## 3. 未收口变更

在阶段路由之前检查 `fix_debts`。

- 存在 `status: open` 的债务：下一步唯一建议 `pm-fix-review`
- 不存在 open 债务：继续阶段路由

## 4. 阶段路由

读取 `current_stage`、`artifacts`、`review_results`，按以下顺序判断：

```text
uninitialized
  -> /pm-input

input
  -> input self_check fail：/pm-input
  -> artifacts.input 为空：/pm-input
  -> 无 input self_check：/pm-input
  -> input self_check pass/warn：/pm-align

align
  -> align review fail：/pm-align
  -> artifacts.align 为空：/pm-align
  -> 无 align review：/pm-align-review
  -> align review pass/warn：/pm-design

design
  -> design review fail：/pm-design
  -> artifacts.design 为空：/pm-design
  -> 无 design review：/pm-design-review
  -> design review pass/warn：/pm-wireframe

wireframe
  -> wireframe review fail：/pm-wireframe
  -> artifacts.wireframe 为空：/pm-wireframe
  -> 无 wireframe review：/pm-wireframe-review
  -> wireframe review pass/warn：/pm-prd

prd
  -> prd review fail：/pm-prd
  -> artifacts.prd 为空：/pm-prd
  -> 无 prd review：/pm-prd-review
  -> prd review pass/warn：/pm-prototype

prototype
  -> prototype review fail：/pm-prototype
  -> artifacts.prototype 为空：/pm-prototype
  -> 无 prototype review：/pm-prototype-review
  -> prototype review pass/warn：主链路完成；如需修改执行 /pm-fix
```

review 结果判断必须取对应 stage 的最近一条记录。

## 5. 输出格式

```text
项目状态：[uninitialized | input | align | design | wireframe | prd | prototype]
当前阶段：[阶段名]

已有产物：
- ...

待处理：
- ...

下一步唯一建议：/pm-xxx

不能自动推进的原因：...
```

## 6. 停止条件

- 输出状态判断和唯一建议后必须停止。
- 不得自动执行下一步命令。
- 不得询问“要我帮你执行吗”。
- 不得同时推荐多个下一步。

## 7. 禁止行为

- 不得在未初始化项目中扫描业务文件。
- 不得自动创建状态文件。
- 不得推荐跳过阶段的路径。
- 不得包含业务分析或需求判断。
- 不得替代 `pm-fix-review` 关闭复查债务。

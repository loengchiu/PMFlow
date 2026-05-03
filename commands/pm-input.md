---
description: 材料盘点。识别材料来源、性质、缺口和冲突，判断是否足够进入需求对齐。
argument-hint: 可附带需求背景、需求方原话、字段表、流程图、截图、旧系统资料、会议纪要等材料
---

# pm-input

触发 skill：`pm-input`

## 输入

- PM 提供的需求材料（文本、文档路径、截图、口头描述等）
- `.pmflow/status.yaml`（读取当前状态，可能不存在）

## 输出

- `output/input/input-{timestamp}.md`（人读材料盘点稿）
- `.pmflow/metadata/input/input-{timestamp}.yaml`（机读 metadata）
- `.pmflow/status.yaml`（创建或更新）

## 不做什么

- 不生成解决方案、详细页面、字段、流程
- 不把背景材料默认当成需求方确认事实
- 完成后只提示 /pm-align（pass 或 warn）或补材料（fail）
- 不自动执行 /pm-align

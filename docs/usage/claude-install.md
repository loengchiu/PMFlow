# PMFlow 安装指南

当前支持：

- Claude Code：`--host claude-code`
- Trae-CN：`--host trae-cn`

## 安装到 Claude Code

```bash
cd D:\work\PMFlow
python install.py install --host claude-code
python install.py verify --host claude-code
```

安装内容：

- `C:\Users\guduj\.claude\pmflow` → junction 到 PMFlow 仓库
- `C:\Users\guduj\.claude\skills\pm-*` → junction 到 PMFlow 的 14 个 skill
- `C:\Users\guduj\.claude\CLAUDE.md` 中写入 PMFlow Global Rules block

## 安装到 Trae-CN

```bash
cd D:\work\PMFlow
python install.py install --host trae-cn
python install.py verify --host trae-cn
```

安装内容：

- `C:\Users\guduj\.trae-cn\pmflow` → junction 到 PMFlow 仓库
- `C:\Users\guduj\.trae-cn\skills\pm-*` → junction 到 PMFlow 的 14 个 skill
- `C:\Users\guduj\.trae-cn\rules\pmflow-global.md` → PMFlow 全局触发规则

## 校验

输出 `pmflow-verify:ok` 表示安装完整。

安装后打开对应 IDE，输入 `/pm-guide` 或 `/pm-input`。能看到或触发 `pm-*` skill，即表示命令入口可用。

## 移除

Claude Code：

```bash
python install.py remove --host claude-code
```

Trae-CN：

```bash
python install.py remove --host trae-cn
```

移除内容：

- 删除对应宿主下的 `pmflow` junction
- 删除对应宿主 `skills\pm-*` junction
- 删除或移除对应宿主的 PMFlow 全局规则

移除时只处理 PMFlow 管理的 junction 和规则文件，不影响 OMP、ShitPM 或用户已有内容。

## 首次业务项目使用

1. 打开业务项目目录（如 `cd D:\work\MyProject`）。
2. 执行 `/pm-input` 或说“初始化 PMFlow”。
3. PMFlow 会在业务项目目录下创建 `.pmflow/` 和 `output/`。

业务项目的产物写在业务项目自身目录，不写入 PMFlow 仓库。

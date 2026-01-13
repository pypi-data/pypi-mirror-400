# ESN Tool 使用指南

ESN Tool 是一个用于管理多个 Git 项目的 CLI 工具，支持批量 Git 操作、AI 自动生成提交信息和交互式工具集合。

## 目录

- [安装](#安装)
- [配置](#配置)
- [命令](#命令)
  - [esn acm - 自动提交](#esn-acm---自动提交)
  - [esn git - 批量 Git 操作](#esn-git---批量-git-操作)
  - [esn config - 配置管理](#esn-config---配置管理)
  - [esn tools - 工具集合 TUI](#esn-tools---工具集合-tui)

---

## 安装

### 前提条件

- Python 3.12 或更高版本

### 方式一：使用 pip 安装（推荐国内用户）

```bash
# 使用清华镜像安装
pip install esn-tool -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 方式二：使用 pipx 安装（隔离环境）

```bash
# 安装 pipx（如果还没有）
pip install pipx -i https://pypi.tuna.tsinghua.edu.cn/simple

# 安装 esn-tool
pipx install esn-tool --pip-args="-i https://pypi.tuna.tsinghua.edu.cn/simple"
```

### 方式三：使用 uv 安装

```bash
# 安装 uv
pip install uv -i https://pypi.tuna.tsinghua.edu.cn/simple

# 安装 esn-tool
uv tool install esn-tool --index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

### 方式四：从源码本地安装（开发模式）

适用于需要修改代码或使用最新开发版本的场景。

```bash
# 克隆仓库
git clone https://github.com/your-username/esn-tools.git
cd esn-tools

# 方法 A：使用 uv tool 安装（推荐）
uv tool install --editable .

# 方法 B：使用 uv pip 安装
uv sync
uv pip install -e .

# 方法 C：使用 pip 安装
pip install -e . -i https://pypi.tuna.tsinghua.edu.cn/simple
```

> **提示**：`-e` 参数表示可编辑模式安装，修改源码后无需重新安装即可生效。

### 验证安装

```bash
esn --version
esn --help
```

### 升级

```bash
# pip 升级
pip install --upgrade esn-tool -i https://pypi.tuna.tsinghua.edu.cn/simple

# 或 pipx 升级
pipx upgrade esn-tool

# 或 uv 升级
uv tool upgrade esn-tool --index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

### 卸载

```bash
# pip 卸载
pip uninstall esn-tool

# 或 pipx 卸载
pipx uninstall esn-tool

# 或 uv 卸载
uv tool uninstall esn-tool
```

---

## 配置

首次使用前，需要配置 AI 接口。运行以下命令进入交互式配置：

```bash
esn config
```

在配置界面中：
- 使用 **↑↓** 选择配置项
- 按 **Enter** 编辑选中项
- 选择 **保存并退出** 完成配置

### 配置项说明

| 配置项 | 说明 | 示例 |
|--------|------|------|
| API Key | AI 接口的 API Key | `sk-xxxxxxxxxxxx` |
| Base URL | API 地址 | `https://api.siliconflow.cn/v1` |
| Model | 使用的模型 | `Qwen/Qwen2.5-32B-Instruct` |

### 配置文件位置

配置保存在 `~/.esntool/config.json`

---

## 命令

### esn acm - 自动提交

**ACM (Auto Commit Message)** 命令用于自动生成 Git 提交信息并提交。

#### 工作流程

1. 扫描指定目录下的所有一级 Git 仓库
2. 检测每个仓库的待提交文件
3. 显示交互式文件选择器，选择要提交的文件
4. 调用 AI 生成符合 Conventional Commits 规范的提交信息
5. 确认后执行 `git add` 和 `git commit`

#### 基本用法

```bash
# 在当前目录下扫描所有 Git 项目
esn acm

# 指定目录
esn acm -d /path/to/projects

# 自动暂存所有更改
esn acm -a

# 跳过文件选择，使用所有更改
esn acm -y

# 启用 AI 代码审查
esn acm -r

# 指定 AI 模型
esn acm -m Qwen/Qwen2.5-72B-Instruct
```

#### 选项

| 选项 | 说明 |
|------|------|
| `-d, --directory` | 指定要搜索的目录，默认为当前目录 |
| `-m, --model` | 指定 AI 模型 |
| `-a, --auto-stage` | 自动暂存所有更改后再生成提交信息 |
| `-y, --yes` | 跳过确认直接提交 |
| `-r, --review` | 启用 AI 代码审查（默认启用） |
| `-R, --no-review` | 禁用 AI 代码审查 |

#### 交互式文件选择器

在文件选择界面中：

| 快捷键 | 功能 |
|--------|------|
| `空格` | 选择/取消选择当前文件 |
| `a` | 全选 |
| `n` | 全不选 |
| `c` | 确认选择，进入下一步 |
| `q` | 取消操作 |
| `Tab` | 在文件列表和 Diff 预览之间切换焦点 |
| `←` / `→` | 切换焦点 |
| `j` / `k` | 在 Diff 预览区滚动 |

#### 生成的提交信息格式

遵循 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

```
<type>(<scope>): <subject>

<body>
```

类型包括：
- `feat`: 新功能
- `fix`: 修复 Bug
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 重构
- `perf`: 性能优化
- `test`: 测试相关
- `chore`: 构建或辅助工具变动

---

### esn git - 批量 Git 操作

对当前目录下的所有 Git 项目批量执行 Git 命令。

#### 工作流程

1. 扫描指定目录下的所有一级子文件夹
2. 筛选出包含 `.git` 目录的 Git 仓库
3. 对每个仓库执行相同的 Git 命令
4. 汇总显示执行结果

#### 基本用法

```bash
# 拉取所有项目的最新代码
esn git pull

# 查看所有项目的状态
esn git status

# 切换所有项目到 main 分支
esn git checkout main

# 创建新分支（所有项目）
esn git checkout -b feature/new-branch

# 获取所有远程更新
esn git fetch --all

# 指定目录
esn git -d /path/to/projects pull

# 显示详细输出
esn git -v status
```

#### 选项

| 选项 | 说明 |
|------|------|
| `-d, --directory` | 指定要搜索的目录，默认为当前目录 |
| `-v, --verbose` | 显示详细输出 |

#### 输出示例

```
📂 在 /path/to/projects 下找到 5 个 Git 项目
执行命令: git pull

┏━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ 项目          ┃ 状态   ┃ 信息                   ┃
┡━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━┩
│ project-1    │ ✓     │ Already up to date.    │
│ project-2    │ ✓     │ Fast-forward           │
│ project-3    │ ✗     │ error: cannot pull...  │
└──────────────┴───────┴────────────────────────┘

完成: 2 成功, 1 失败
```

---

### esn config - 配置管理

管理 ESN Tool 的配置，包括 AI 接口设置等。

```bash
esn config
```

进入交互式配置界面，可以设置：
- API Key
- Base URL  
- Model

配置保存在 `~/.esntool/config.json`

---

### esn tools - 工具集合 TUI

启动交互式工具集合界面，提供多种实用工具。

```bash
esn tools
```

#### 包含的工具

| 工具 | 说明 |
|------|------|
| 📋 配置工具 | AI 配置和项目管理 |
| 🔀 Git 工具 | Git 批量操作界面 |
| 💻 系统信息 | 查看系统和 Python 环境信息 |

#### 快捷键

| 快捷键 | 功能 |
|--------|------|
| `←`/`→` | 切换工具列表和内容区域 |
| `↑`/`↓` | 导航工具列表 |
| `Enter` | 选择工具 |
| `Q` | 退出应用 |

---

## 常见问题

### API 请求失败

确保已正确配置 API Key 和 Base URL：

```bash
esn config
```

如果报错，会显示详细的错误信息，包括 HTTP 状态码和 API 返回的错误消息。

### 命令未找到

确保已正确安装：

```bash
uv tool list
```

如果 `esn-tool` 不在列表中，执行：

```bash
uv tool install esn-tool
```

### 更新到最新版本

```bash
uv tool upgrade esn-tool
```

---

## 依赖

| 包 | 用途 |
|----|------|
| `click` | 命令行框架 |
| `rich` | 终端美化输出 |
| `httpx` | HTTP 客户端 |
| `questionary` | 交互式提示 |
| `textual` | TUI 界面框架 |

---

## 开发

### 安装开发依赖

```bash
uv sync
```

### 运行测试

```bash
uv run pytest
```

### 代码格式化

```bash
uv run ruff format src/
uv run ruff check src/ --fix
```

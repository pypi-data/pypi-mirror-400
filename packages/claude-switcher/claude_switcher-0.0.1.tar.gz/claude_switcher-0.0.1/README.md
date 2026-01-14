# Claude模型切换器

一个简单的工具，用于在不同的Claude模型之间自由切换。

## 功能特性

- 支持多种Claude模型切换
- 可配置的模型参数
- 命令行界面操作
- 交互式菜单选择
- 支持Kimi、DeepSeek等第三方模型API

## 安装

从PyPI安装（推荐）：

```bash
pip install claude-switcher
```

或使用uv安装：

```bash
uv pip install claude-switcher
```

从源码安装（开发模式）：

```bash
pip install -e .
```

## 使用方法

安装后，你可以使用 `claude-switch` 命令来启动工具。

### 交互式菜单（无参数运行）

```bash
claude-switch
```

### 直接选择模型运行

```bash
claude-switch kimi
```

或

```bash
claude-switch deepseek
```

### 支持的模型

目前支持以下模型配置：

- Kimi (`kimi`) - Moonshot API
- DeepSeek (`deepseek`) - DeepSeek API
- 以及其他在配置文件中定义的模型

## 第三方API支持

本工具支持通过Anthropic兼容的API端点访问第三方AI模型，例如：

- Kimi (Moonshot API)
- DeepSeek (DeepSeek API)
- 以及其他兼容Anthropic API格式的模型

## 配置文件

模型配置存储在用户主目录下的 `~/.claude_switcher/claude_models.json` 文件中。首次运行时会自动创建默认配置模板，您需要编辑该文件填入API密钥等信息。

## 项目结构

```
claude_switcher/
├── main.py                    # 主入口文件
├── pyproject.toml             # 项目配置
├── README.md                  # 项目说明
├── launcher/                  # 启动器模块
│   ├── __init__.py
│   ├── launcher.py            # 启动器主类
│   ├── config_handler.py      # 配置文件处理器
│   ├── claude_runner.py       # Claude运行器
│   └── menu_handler.py        # 菜单处理器
└── .gitignore                 # Git忽略文件
```

## 依赖要求

- Python >= 3.11
- Claude Code CLI 工具 (通过 npm 安装: `npm install -g @anthropic-ai/claude-code`)

注意：Claude Code CLI 是必须的，因为此工具实际上是设置环境变量来控制Claude命令的行为。

## 许可证

本项目采用 Apache License 2.0 许可证。详情请参阅 [LICENSE](./LICENSE) 文件。

## 配置说明

首次运行工具时，会自动创建配置文件 `~/.claude_switcher/claude_models.json`，其中包含默认的模型配置模板。你需要：

1. 编辑配置文件，将 `YOUR_*_API_KEY_HERE` 替换为真实的API密钥
2. 根据需要修改API端点和其他参数
3. 保存配置文件后即可使用

每个模型配置包含以下字段：
- `description`: 模型的描述信息
- `env`: 环境变量配置，包括API基础URL、认证令牌、超时时间、模型名称等
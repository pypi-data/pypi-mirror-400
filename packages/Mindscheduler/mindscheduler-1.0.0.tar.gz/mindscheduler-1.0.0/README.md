# MindScheduler

<div align="center">

**一个轻量级、模块化的 LLM 增强型技能调度框架**

基于 Markdown 定义的技能管理 + 可扩展的 LLM 智能调度

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.0.0-orange.svg)]()
[![Tests](https://img.shields.io/badge/tests-194%20passed-brightgreen.svg)]()

</div>

---

## ✨ 特性

- 📝 **Markdown 驱动** - 使用 Markdown + Front Matter 定义技能，易于编写和维护
- 🤖 **LLM 增强** - 可选的智能意图理解和参数提取（OpenAI 兼容）
- 🎯 **规则匹配** - 关键词匹配 + 语义匹配双重兜底
- 🔌 **模块化设计** - 核心功能、解析器、LLM 集成、可观测性清晰分层
- 🔐 **权限控制** - 文件访问白名单、网络访问控制
- 🛠️ **依赖管理** - 自动检测和安装 Python 依赖包
- 📊 **监控集成** - 通过回调机制集成到你现有的监控系统
- 🧪 **测试覆盖** - 完整的单元测试和集成测试

## 🚀 快速开始

### 安装

```bash
pip install skillscheduler
```

### 两种调用方式

MindScheduler 提供两种技能调用方式：

#### 1. `run()` - 直接执行

适用于明确知道技能名称和参数的场景：

```python
from skill_scheduler import SkillScheduler

scheduler = SkillScheduler(skills_dir="./skills")

# 直接执行：需要明确指定技能名和参数
result = scheduler.run("file-counter", {
    "file": "data.txt",
    "mode": "lines"
})

if result["success"]:
    print(result["output"])
```

**特点**：高效、直接，适用于程序化调用和批处理

#### 2. `ask()` - 智能调用

适用于自然语言交互场景：

```python
# 启用 LLM（可选）
scheduler = MindScheduler(
    skills_dir="./skills",
    enable_llm=True,
    llm_api_key="sk-xxx"
)

# 自然语言调用：系统自动匹配技能并提取参数
result = scheduler.ask("帮我统计 data.txt 的行数")
print(result["output"])
```

**特点**：智能理解意图，适用于 AI Agent 和交互式场景

### CLI 工具

```bash
# 执行技能
skill-scheduler -s skills run file-counter -p file=data.txt -p mode=lines

# 列出所有技能
skill-scheduler -s skills list

# 查看技能详情
skill-scheduler -s skills info file-counter
```

## 📁 项目结构

```
skill_scheduler/
├── __init__.py              # 主入口
├── cli.py                   # CLI 工具
│
├── core/                    # 核心功能
│   ├── scheduler.py         # 主调度器
│   ├── skill.py             # 技能类和管理器
│   ├── executor.py          # 执行器
│   └── matcher.py           # 技能匹配器
│
├── parsers/                 # 解析器
│   └── markdown_parser.py   # Markdown + Front Matter 解析
│
├── llm/                     # LLM 集成
│   ├── base.py              # LLM 适配器基类
│   └── openai.py            # OpenAI 实现
│
├── observability/           # 可观测性（可选）
│   ├── logging_config.py    # 日志配置工具
│   └── metrics.py           # 监控回调系统
│
└── utils/                   # 工具类
    ├── config.py            # 配置类
    └── prompts.py           # 提示词管理
```

## 📖 更多文档

- **[技能编写指南.md](技能编写指南.md)** - 如何创建 skill.md 文件，包含完整格式说明和最佳实践
- **[使用及配置说明.md](使用及配置说明.md)** - 完整的安装、配置、API 参考和故障排查
- [完整内容模板.md](完整内容模板.md) - skill.md 完整内容模板参考

## 🎯 技能定义示例

### 最简格式

只需 `name` 和 `description` 两个必需字段：

```markdown
---
name: hello-world
description: 打印问候语
---

# Hello World

打印 Hello World 消息。
```

### 完整格式

```markdown
---
name: file-counter
description: 统计文件的行数、词数和字符数
version: 1.0.0
tags: [file, text, analysis]
dependencies: []
timeout: 30
script: "scripts/counter.py"

inputs:
  file:
    type: string
    required: true
    description: "文件路径"
  mode:
    type: string
    required: false
    default: "lines"
    description: "统计模式：lines, words, chars"

permissions:
  read_file: ["*.txt", "*.md", "*.csv"]
  write_file: []
  network: false
---

# File Counter

统计文本文件的行数、词数和字符数。
```

**完整的 skill.md 编写指南**：请参考 [技能编写指南.md](技能编写指南.md) 和 [完整内容模板.md](完整内容模板.md)

## 🔧 高级功能

### LLM 增强

```python
import os
os.environ["OPENAI_API_KEY"] = "sk-xxx"

scheduler = MindScheduler(
    skills_dir="./skills",
    enable_llm=True,
    llm_api_key=os.getenv("OPENAI_API_KEY")
)

# 自然语言调用
result = scheduler.ask("帮我统计 data.txt 的词数")
```

### 日志配置

```python
from skill_scheduler.observability.logging_config import configure_logging

# 配置日志
configure_logging(
    level="INFO",
    format_type="json",
    output_file="app.log"
)
```

### 监控集成

```python
from skill_scheduler.observability.metrics import (
    InMemoryMetricsCallback,
    register_callback,
    get_registry
)

# 注册监控
metrics = InMemoryMetricsCallback()
register_callback(metrics)

# 创建带监控的调度器
scheduler = MindScheduler(
    skills_dir="./skills",
    metrics_registry=get_registry()
)
```

**更多高级功能**：请参考 [使用及配置说明.md](使用及配置说明.md)

---

## 核心特性对比

| 特性 | `run()` | `ask()` |
|------|---------|---------|
| **调用方式** | 直接指定技能名和参数 | 自然语言描述需求 |
| **参数要求** | 必须明确提供所有参数 | 自动从查询中提取 |
| **使用 LLM** | 否 | 是（可选） |
| **适用场景** | 程序化调用、批处理 | AI Agent、交互式场景 |
| **执行效率** | 高（直接执行） | 中（需要分析意图） |

---

## 🧪 测试

```bash
# 运行所有测试
pytest tests/ -v

# 运行特定测试
pytest tests/test_markdown_parser.py -v
```

## 🤝 贡献

欢迎贡献！请查看 [CONTRIBUTING.md](CONTRIBUTING.md)

## 📄 许可证

[MIT License](LICENSE)

---

<div align="center">

Made with ❤️ by MindScheduler Contributors

</div>

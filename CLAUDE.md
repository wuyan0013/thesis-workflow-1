# CLAUDE.md

This file provides guidance to Droid Code (droid.ai/code) when working with code in this repository.

## 项目概述

基于 Claude API 的本科毕业论文自动生成工具，专为国家开放大学（广西）设计。支持论文生成、答辩稿生成、论文降重、降 AIGC 率等功能。

## 常用命令

```bash
# 安装依赖
pip install -r requirements.txt

# 命令行运行
python main.py -c examples/sample_thesis.yaml
python main.py -t "论文主题" -m "专业" -a "作者"
python main.py -i  # 交互模式

# Web GUI（推荐）
streamlit run app_streamlit.py     # 主应用：论文生成
streamlit run app_tools.py         # 工具箱：降重/降AIGC

# Gradio GUI
python app.py
```

## 架构设计

### 核心模块 (`src/`)

| 模块 | 职责 |
|------|------|
| `workflow.py` | 主工作流，含 `ThesisWorkflow`、`ThesisConfig` 数据类 |
| `claude_client.py` | Claude API 客户端，CLI/SDK 双模式，含 `ThesisGenerator` |
| `text_processor.py` | 文本处理器，降重/降 AIGC 率功能 |
| `docx_builder.py` | Word 文档生成，国开大格式规范 |
| `config.py` | 配置管理，YAML + 环境变量 |

### Web 应用

| 文件 | 功能 |
|------|------|
| `app_streamlit.py` | 主 GUI：5 步流程（选专业→选题→章节→生成→答辩稿） |
| `app_tools.py` | 工具箱 GUI：降重 + 降 AIGC 率 |
| `pages/1_论文降重.py` | Streamlit 多页面：降重功能 |
| `pages/2_降AIGC率.py` | Streamlit 多页面：降 AIGC 功能 |

### 数据流

```
论文生成：
  用户输入 → ThesisWorkflow.generate_thesis()
    → generate_outline() → generate_section() × N
    → generate_abstract() → generate_references()
    → DocxBuilder.save() → .docx

文本处理：
  用户输入 → TextProcessor
    → reduce_plagiarism() / reduce_aigc_rate()
    → ProcessResult
```

## 配置

### 环境变量

- `ANTHROPIC_API_KEY`: Claude API 密钥（SDK 模式必需）
- `ANTHROPIC_BASE_URL`: API 代理地址（可选）
- `CLAUDE_MODEL`: 模型名称，默认 `claude-opus-4-5-20251101`

### 配置文件

- `config/config.yaml`: 主配置
- `.env`: 环境变量

## 关键实现

### Claude 客户端双模式

```python
# CLI 模式（默认，无需 API Key）
client = ClaudeClient(use_cli=True)

# SDK 模式（需 API Key，支持流式）
client = ClaudeClient(use_cli=False)
```

### 文本处理器

```python
from src.text_processor import TextProcessor, RewriteIntensity, HumanizeStyle

processor = TextProcessor()

# 降重
result = processor.reduce_plagiarism(text, intensity=RewriteIntensity.MEDIUM)

# 降 AIGC 率
result = processor.reduce_aigc_rate(text, style=HumanizeStyle.ACADEMIC)
```

### 论文生成器

```python
generator = ThesisGenerator(client)

# 生成广西特色选题
topics = generator.generate_topics("行政管理", 5)

# 生成答辩稿
defense = generator.generate_defense_paper(title, abstract, chapters)
```

### 文档格式规范

- 标题编号：`一、` `（一）` `1、`
- 正文：宋体 12pt，1.5 倍行距
- 一级标题：黑体 18pt 加粗
- 二级标题：黑体 15pt 加粗
- 三级标题：黑体 12pt 加粗

### 反 AI 检测策略

- 句式多样化（短/中/长句混合）
- 自然过渡词（此外、然而、因此）
- 禁止机械分点（首先...其次...最后...）
- 禁止第一人称（笔者认为、本文认为）
- 添加学术谦虚表达
- 人格化改写技巧

## 依赖库

核心：`anthropic`、`python-docx`、`pyyaml`、`rich`、`click`、`jinja2`

Web：`streamlit`、`gradio`

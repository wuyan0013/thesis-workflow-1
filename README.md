# Thesis Workflow 论文工作流

本科毕业论文自动生成工具，基于 Claude API 和 python-docx。

## 功能特点

- 🤖 **AI驱动**：使用 Claude API 生成高质量论文内容
- 📝 **Word输出**：自动生成符合学校格式的 .docx 文件
- 🎯 **多专业支持**：适配各专业论文写作需求
- ⚙️ **灵活配置**：支持 YAML 配置文件自定义
- 🚀 **Claude Code集成**：可在 Claude Code 中直接调用

## 快速开始

### 1. 安装依赖

```bash
cd thesis-workflow
pip install -r requirements.txt
```

### 2. 配置 API 密钥

复制环境变量示例文件：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入你的 Claude API 密钥：

```
ANTHROPIC_API_KEY=your-api-key-here
```

### 3. 配置论文信息

复制配置文件示例：

```bash
cp config/config.example.yaml config/config.yaml
```

编辑 `config/config.yaml` 填入学校和格式信息。

### 4. 生成论文

**方式一：使用配置文件**

```bash
python main.py -c examples/sample_thesis.yaml
```

**方式二：命令行参数**

```bash
python main.py -t "论文主题" -m "专业" -a "作者姓名"
```

**方式三：交互模式**

```bash
python main.py -i
```

## 项目结构

```
thesis-workflow/
├── main.py                  # 主入口
├── requirements.txt         # Python依赖
├── config/
│   ├── config.example.yaml  # 配置示例
│   └── config.yaml          # 实际配置（需创建）
├── src/
│   ├── __init__.py
│   ├── config.py            # 配置管理
│   ├── claude_client.py     # Claude API 客户端
│   ├── docx_builder.py      # Word文档构建器
│   └── workflow.py          # 主工作流
├── prompts/
│   ├── system.md            # 系统提示词
│   ├── outline.md           # 大纲生成提示词
│   └── section.md           # 章节生成提示词
├── templates/               # Word模板（可选）
├── examples/
│   └── sample_thesis.yaml   # 论文配置示例
└── output/                  # 生成的论文
```

## 在 Claude Code 中使用

你可以在 Claude Code 对话中直接调用此工作流：

```python
# 在 Claude Code 中执行
import sys
sys.path.insert(0, "E:/Github_daylight/thesis-workflow")

from src.workflow import quick_generate

# 快速生成论文
output = quick_generate(
    topic="人工智能在教育领域的应用研究",
    major="教育技术学",
    author="张三",
    student_id="2021001234",
    supervisor="李四 教授"
)
print(f"论文已生成：{output}")
```

## 配置说明

### 论文配置文件 (YAML)

```yaml
# 基本信息
title: "论文标题"
topic: "研究主题"
major: "专业名称"

# 作者信息
author: "作者姓名"
student_id: "学号"
supervisor: "指导教师"

# 论文要求
word_count: 12000
requirements: "特殊要求说明"

# 章节配置（可选）
chapters:
  - title: "第一章 绪论"
    requirements: "章节具体要求"
    word_count: 2000
```

### 系统配置 (config.yaml)

```yaml
# Claude API 配置
claude:
  api_key: "your-api-key"  # 建议使用环境变量
  model: "claude-sonnet-4-20250514"
  max_tokens: 4096

# 论文格式配置
thesis:
  university: "XX大学"
  college: "XX学院"
  font:
    title: "黑体"
    body: "宋体"
```

## 注意事项

1. **API 密钥安全**：请勿将 API 密钥提交到版本控制
2. **学术诚信**：生成的内容仅供参考，请确保符合学校要求
3. **格式调整**：可能需要根据学校具体要求微调 Word 格式

## License

MIT License

## 作者

daylight

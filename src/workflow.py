# -*- coding: utf-8 -*-
"""
主工作流模块
整合所有模块，提供完整的论文生成工作流
适配国家开放大学本科毕业论文格式
"""

from pathlib import Path
from typing import Optional, List
from dataclasses import dataclass, field
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel

from .config import get_config
from .claude_client import ClaudeClient, ThesisGenerator
from .docx_builder import DocxBuilder

# 在 Streamlit 环境下禁用 rich 的终端输出，避免 Windows 编码问题
import sys
import io

# 检测是否在 Streamlit 环境中运行
_in_streamlit = 'streamlit' in sys.modules

if _in_streamlit:
    # Streamlit 环境：使用静默的 Console（输出到 StringIO）
    console = Console(file=io.StringIO(), force_terminal=False)
else:
    # 正常终端环境
    console = Console()


@dataclass
class ChapterConfig:
    """章节配置"""
    title: str  # 章节标题（不含编号，如"绪论"而非"一、绪论"）
    requirements: str = ""  # 章节要求
    word_count: int = 1500  # 目标字数
    subsections: List[dict] = field(default_factory=list)  # 子章节


@dataclass
class ThesisConfig:
    """论文配置"""

    # 基本信息
    title: str
    topic: str
    major: str

    # 作者信息
    author: str = ""
    student_id: str = ""
    supervisor: str = ""

    # 论文要求
    word_count: int = 10000
    requirements: str = ""

    # 章节配置
    chapters: List[dict] = field(default_factory=list)

    # 生成的内容
    outline: str = ""
    abstract_cn: str = ""
    abstract_en: str = ""
    keywords_cn: List[str] = field(default_factory=list)
    keywords_en: List[str] = field(default_factory=list)
    sections: dict = field(default_factory=dict)  # {章节标题: 内容}
    references: List[str] = field(default_factory=list)
    acknowledgement: str = ""


class ThesisWorkflow:
    """论文生成工作流"""

    def __init__(self, use_cli: bool = False):
        """
        初始化工作流

        Args:
            use_cli: 是否使用CLI模式，默认False使用SDK模式（中转站API）
        """
        self.config = get_config()
        self.client = ClaudeClient(use_cli=use_cli)
        self.generator = ThesisGenerator(self.client)

    def generate_topics(self, major: str, count: int = 5) -> List[str]:
        """
        根据专业生成与广西相关的论文主题

        Args:
            major: 专业名称
            count: 生成主题数量

        Returns:
            主题列表
        """
        console.print(f"[blue]正在为 {major} 专业生成广西特色论文选题...[/blue]")
        topics = self.generator.generate_topics(major, count)
        console.print(f"[green]✓[/green] 生成了 {len(topics)} 个广西特色选题")
        return topics

    def generate_thesis(self, thesis_config: ThesisConfig) -> Path:
        """
        生成完整论文

        Args:
            thesis_config: 论文配置

        Returns:
            生成的文件路径
        """
        console.print(Panel.fit(
            f"[bold blue]开始生成论文[/bold blue]\n"
            f"主题：{thesis_config.topic}\n"
            f"专业：{thesis_config.major}",
            title="论文工作流"
        ))

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            # 1. 生成大纲
            task = progress.add_task("生成论文大纲...", total=None)
            thesis_config.outline = self.generator.generate_outline(
                thesis_config.topic,
                thesis_config.major,
                thesis_config.requirements
            )
            progress.remove_task(task)
            console.print("[green]✓[/green] 大纲生成完成")

            # 2. 解析或使用默认章节结构
            if not thesis_config.chapters:
                thesis_config.chapters = self._get_default_chapters(thesis_config.major)

            # 3. 生成各章节内容
            for chapter in thesis_config.chapters:
                task = progress.add_task(
                    f"生成章节：{chapter['title']}...", total=None
                )

                # 构建上下文
                context = self._build_context(thesis_config)

                content = self.generator.generate_section(
                    chapter["title"],
                    chapter.get("requirements", ""),
                    context,
                    chapter.get("word_count", 1500)
                )
                thesis_config.sections[chapter["title"]] = content
                progress.remove_task(task)
                console.print(f"[green]✓[/green] {chapter['title']} 生成完成")

            # 4. 生成摘要
            task = progress.add_task("生成摘要...", total=None)
            thesis_summary = self._summarize_content(thesis_config.sections)

            thesis_config.abstract_cn = self.generator.generate_abstract(
                thesis_summary, "chinese"
            )
            thesis_config.keywords_cn = self.generator.generate_keywords(
                thesis_summary, 5
            )
            progress.remove_task(task)
            console.print("[green]✓[/green] 摘要生成完成")

            # 5. 生成参考文献（如果没有预设）
            if not thesis_config.references:
                task = progress.add_task("生成参考文献...", total=None)
                thesis_config.references = self.generator.generate_references(
                    thesis_config.topic,
                    thesis_config.major,
                    10  # 生成10条参考文献
                )
                progress.remove_task(task)
                console.print("[green]✓[/green] 参考文献生成完成")

            # 6. 构建Word文档
            task = progress.add_task("构建Word文档...", total=None)
            output_path = self._build_document(thesis_config)
            progress.remove_task(task)
            console.print(f"[green]✓[/green] 文档保存至：{output_path}")

        console.print(Panel.fit(
            f"[bold green]论文生成完成！[/bold green]\n"
            f"文件位置：{output_path}",
            title="完成"
        ))

        return output_path

    def _get_default_chapters(self, major: str) -> List[dict]:
        """
        获取默认章节结构（文科专业通用）

        Args:
            major: 专业名称

        Returns:
            章节配置列表
        """
        return [
            {
                "title": "绪论",
                "requirements": "介绍研究背景、研究目的与意义、研究方法与内容",
                "word_count": 1300
            },
            {
                "title": "相关概念与理论基础",
                "requirements": "界定核心概念，阐述理论基础",
                "word_count": 1600
            },
            {
                "title": "现状分析",
                "requirements": "分析研究对象的发展现状",
                "word_count": 1600
            },
            {
                "title": "问题成因分析",
                "requirements": "分析问题产生的原因",
                "word_count": 1600
            },
            {
                "title": "对策与建议",
                "requirements": "针对问题提出具体可行的解决对策",
                "word_count": 1600
            },
            {
                "title": "结论",
                "requirements": "总结研究主要结论，指出研究局限性",
                "word_count": 700
            },
        ]

    def _build_context(self, thesis_config: ThesisConfig) -> str:
        """构建上下文摘要"""
        context_parts = [
            f"论文主题：{thesis_config.topic}",
            f"专业：{thesis_config.major}",
        ]

        if thesis_config.outline:
            context_parts.append(f"论文大纲：\n{thesis_config.outline[:500]}")

        if thesis_config.sections:
            context_parts.append("已完成章节摘要：")
            for title, content in thesis_config.sections.items():
                summary = content[:300] + "..." if len(content) > 300 else content
                context_parts.append(f"【{title}】{summary}")

        return "\n\n".join(context_parts)

    def _summarize_content(self, sections: dict) -> str:
        """汇总论文内容用于生成摘要"""
        return "\n\n".join(
            f"## {title}\n{content[:800]}"
            for title, content in sections.items()
        )

    def _build_document(self, thesis_config: ThesisConfig) -> Path:
        """构建Word文档（国开大格式）"""
        builder = DocxBuilder()

        # 1. 添加目录
        builder.add_toc()

        # 2. 添加摘要
        builder.add_abstract(
            thesis_config.abstract_cn,
            thesis_config.keywords_cn,
        )

        # 3. 添加正文各章节
        for chapter in thesis_config.chapters:
            title = chapter["title"]
            content = thesis_config.sections.get(title, "")

            # 添加一级标题
            builder.add_heading1(title)

            # 解析并添加内容
            self._add_chapter_content(builder, content)

        # 4. 添加参考文献
        if thesis_config.references:
            builder.add_references(thesis_config.references)

        # 5. 保存
        filename = thesis_config.title.replace(" ", "_")
        return builder.save(filename)

    def _add_chapter_content(self, builder: DocxBuilder, content: str) -> None:
        """
        解析章节内容并添加到文档

        Args:
            builder: 文档构建器
            content: 章节内容（可能包含子标题）
        """
        lines = content.strip().split('\n')
        current_paragraph = []

        for line in lines:
            line = line.strip()

            if not line:
                if current_paragraph:
                    builder.add_paragraph(' '.join(current_paragraph))
                    current_paragraph = []
                continue

            # 检测二级标题（（一）xxx 或 ## xxx 格式）
            if line.startswith('（') and '）' in line[:6]:
                if current_paragraph:
                    builder.add_paragraph(' '.join(current_paragraph))
                    current_paragraph = []
                # 提取标题文本
                title_text = line.split('）', 1)[-1].strip()
                builder.add_heading2(title_text)
            elif line.startswith('## '):
                if current_paragraph:
                    builder.add_paragraph(' '.join(current_paragraph))
                    current_paragraph = []
                builder.add_heading2(line[3:])
            # 检测三级标题（1. xxx 或 ### xxx 格式）
            elif line.startswith('### '):
                if current_paragraph:
                    builder.add_paragraph(' '.join(current_paragraph))
                    current_paragraph = []
                builder.add_heading3(line[4:])
            elif len(line) > 2 and line[0].isdigit() and line[1] == '.':
                if current_paragraph:
                    builder.add_paragraph(' '.join(current_paragraph))
                    current_paragraph = []
                title_text = line.split('.', 1)[-1].strip()
                builder.add_heading3(title_text)
            else:
                # 普通段落文本
                current_paragraph.append(line)

        # 处理最后一个段落
        if current_paragraph:
            builder.add_paragraph(' '.join(current_paragraph))


def quick_generate(
    topic: str,
    major: str,
    author: str = "",
    **kwargs
) -> Path:
    """
    快速生成论文

    Args:
        topic: 论文主题
        major: 专业
        author: 作者
        **kwargs: 其他配置

    Returns:
        生成的文件路径
    """
    thesis_config = ThesisConfig(
        title=topic,
        topic=topic,
        major=major,
        author=author,
        **kwargs
    )

    workflow = ThesisWorkflow()
    return workflow.generate_thesis(thesis_config)

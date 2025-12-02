"""
主工作流模块
整合所有模块，提供完整的论文生成工作流
"""

from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.markdown import Markdown

from .config import get_config
from .claude_client import ClaudeClient, ThesisGenerator
from .docx_builder import DocxBuilder

console = Console()


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
    chapters: list[dict] = field(default_factory=list)

    # 生成的内容
    outline: str = ""
    abstract_cn: str = ""
    abstract_en: str = ""
    keywords_cn: list[str] = field(default_factory=list)
    keywords_en: list[str] = field(default_factory=list)
    sections: dict[str, str] = field(default_factory=dict)
    references: list[str] = field(default_factory=list)
    acknowledgement: str = ""


class ThesisWorkflow:
    """论文生成工作流"""

    def __init__(self):
        self.config = get_config()
        self.client = ClaudeClient()
        self.generator = ThesisGenerator(self.client)

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

            # 2. 生成各章节内容
            if not thesis_config.chapters:
                thesis_config.chapters = self._parse_chapters(thesis_config.outline)

            for chapter in thesis_config.chapters:
                task = progress.add_task(
                    f"生成章节：{chapter['title']}...", total=None
                )

                # 获取上下文
                context = self._build_context(thesis_config.sections)

                content = self.generator.generate_section(
                    chapter["title"],
                    chapter.get("requirements", ""),
                    context,
                    chapter.get("word_count", 1500)
                )
                thesis_config.sections[chapter["title"]] = content
                progress.remove_task(task)
                console.print(f"[green]✓[/green] {chapter['title']} 生成完成")

            # 3. 生成摘要
            task = progress.add_task("生成摘要...", total=None)
            thesis_summary = self._summarize_content(thesis_config.sections)

            thesis_config.abstract_cn = self.generator.generate_abstract(
                thesis_summary, "chinese"
            )
            thesis_config.abstract_en = self.generator.generate_abstract(
                thesis_summary, "english"
            )
            thesis_config.keywords_cn = self.generator.generate_keywords(
                thesis_summary, 5
            )
            thesis_config.keywords_en = [
                kw for kw in thesis_config.keywords_cn  # 简化处理
            ]
            progress.remove_task(task)
            console.print("[green]✓[/green] 摘要生成完成")

            # 4. 构建Word文档
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

    def _parse_chapters(self, outline: str) -> list[dict]:
        """从大纲解析章节结构"""
        # 简化实现：返回默认章节结构
        return [
            {"title": "第一章 绪论", "word_count": 2000},
            {"title": "第二章 理论基础与文献综述", "word_count": 2500},
            {"title": "第三章 研究设计与方法", "word_count": 2000},
            {"title": "第四章 研究结果与分析", "word_count": 2500},
            {"title": "第五章 结论与建议", "word_count": 1500},
        ]

    def _build_context(self, sections: dict[str, str]) -> str:
        """构建上下文摘要"""
        if not sections:
            return ""

        context_parts = []
        for title, content in sections.items():
            # 取每节的前200字作为摘要
            summary = content[:200] + "..." if len(content) > 200 else content
            context_parts.append(f"{title}：{summary}")

        return "\n".join(context_parts)

    def _summarize_content(self, sections: dict[str, str]) -> str:
        """汇总论文内容"""
        return "\n\n".join(
            f"## {title}\n{content[:500]}"
            for title, content in sections.items()
        )

    def _build_document(self, thesis_config: ThesisConfig) -> Path:
        """构建Word文档"""
        builder = DocxBuilder()

        # 添加封面
        builder.add_cover_page(
            title=thesis_config.title,
            author=thesis_config.author,
            student_id=thesis_config.student_id,
            major=thesis_config.major,
            supervisor=thesis_config.supervisor,
        )

        # 添加摘要
        builder.add_abstract(
            thesis_config.abstract_cn,
            thesis_config.keywords_cn,
            thesis_config.abstract_en,
            thesis_config.keywords_en,
        )

        # 添加正文
        for title, content in thesis_config.sections.items():
            builder.add_content(f"# {title}\n\n{content}")

        # 添加参考文献
        if thesis_config.references:
            builder.add_references(thesis_config.references)

        # 添加致谢
        if thesis_config.acknowledgement:
            builder.add_acknowledgement(thesis_config.acknowledgement)

        # 保存
        filename = thesis_config.title.replace(" ", "_")
        return builder.save(filename)


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

#!/usr/bin/env python3
"""
论文工作流 - 主入口
使用方法：python main.py --config examples/sample_thesis.yaml
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

import click
import yaml
from rich.console import Console
from rich.panel import Panel

from src.workflow import ThesisWorkflow, ThesisConfig

console = Console()


@click.command()
@click.option(
    "--config", "-c",
    type=click.Path(exists=True),
    help="论文配置文件路径 (YAML格式)"
)
@click.option(
    "--topic", "-t",
    type=str,
    help="论文主题"
)
@click.option(
    "--major", "-m",
    type=str,
    help="专业"
)
@click.option(
    "--author", "-a",
    type=str,
    default="",
    help="作者姓名"
)
@click.option(
    "--interactive", "-i",
    is_flag=True,
    help="交互模式"
)
def main(config, topic, major, author, interactive):
    """
    论文工作流 - 本科毕业论文自动生成工具

    使用配置文件：
        python main.py -c examples/sample_thesis.yaml

    快速生成：
        python main.py -t "论文主题" -m "专业" -a "作者"

    交互模式：
        python main.py -i
    """
    console.print(Panel.fit(
        "[bold blue]论文工作流 v0.1.0[/bold blue]\n"
        "本科毕业论文自动生成工具",
        title="Thesis Workflow"
    ))

    try:
        if config:
            # 从配置文件加载
            thesis_config = load_config(config)
        elif interactive:
            # 交互模式
            thesis_config = interactive_mode()
        elif topic and major:
            # 命令行参数
            thesis_config = ThesisConfig(
                title=topic,
                topic=topic,
                major=major,
                author=author,
            )
        else:
            console.print("[yellow]请提供配置文件或使用交互模式[/yellow]")
            console.print("使用 --help 查看帮助信息")
            return

        # 执行工作流
        workflow = ThesisWorkflow()
        output_path = workflow.generate_thesis(thesis_config)

        console.print(f"\n[bold green]论文已生成：{output_path}[/bold green]")

    except Exception as e:
        console.print(f"[bold red]错误：{e}[/bold red]")
        raise


def load_config(config_path: str) -> ThesisConfig:
    """从YAML文件加载配置"""
    with open(config_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    return ThesisConfig(
        title=data.get("title", data.get("topic", "")),
        topic=data.get("topic", ""),
        major=data.get("major", ""),
        author=data.get("author", ""),
        student_id=data.get("student_id", ""),
        supervisor=data.get("supervisor", ""),
        word_count=data.get("word_count", 10000),
        requirements=data.get("requirements", ""),
        chapters=data.get("chapters", []),
        references=data.get("references", []),
        acknowledgement=data.get("acknowledgement", ""),
    )


def interactive_mode() -> ThesisConfig:
    """交互模式收集配置"""
    console.print("\n[bold]请输入论文信息：[/bold]\n")

    topic = console.input("[cyan]论文主题：[/cyan]")
    major = console.input("[cyan]专业：[/cyan]")
    author = console.input("[cyan]作者姓名：[/cyan]")
    student_id = console.input("[cyan]学号：[/cyan]")
    supervisor = console.input("[cyan]指导教师：[/cyan]")

    word_count_str = console.input("[cyan]目标字数 (默认10000)：[/cyan]")
    word_count = int(word_count_str) if word_count_str else 10000

    requirements = console.input("[cyan]特殊要求 (可选)：[/cyan]")

    return ThesisConfig(
        title=topic,
        topic=topic,
        major=major,
        author=author,
        student_id=student_id,
        supervisor=supervisor,
        word_count=word_count,
        requirements=requirements,
    )


if __name__ == "__main__":
    main()

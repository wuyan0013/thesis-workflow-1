"""
Claude API 客户端
负责与Claude API交互，生成论文内容
"""

from typing import Optional, Generator
from anthropic import Anthropic
from rich.console import Console

from .config import get_config

console = Console()


class ClaudeClient:
    """Claude API 客户端"""

    def __init__(self, api_key: Optional[str] = None):
        config = get_config()
        self.api_key = api_key or config.claude_api_key
        self.model = config.claude_model
        self.max_tokens = config.max_tokens

        if not self.api_key:
            raise ValueError("未设置 ANTHROPIC_API_KEY，请在 .env 文件中配置")

        self.client = Anthropic(api_key=self.api_key)

    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        生成文本内容

        Args:
            prompt: 用户提示词
            system_prompt: 系统提示词
            max_tokens: 最大token数

        Returns:
            生成的文本内容
        """
        messages = [{"role": "user", "content": prompt}]

        kwargs = {
            "model": self.model,
            "max_tokens": max_tokens or self.max_tokens,
            "messages": messages,
        }

        if system_prompt:
            kwargs["system"] = system_prompt

        response = self.client.messages.create(**kwargs)
        return response.content[0].text

    def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
    ) -> Generator[str, None, None]:
        """
        流式生成文本内容

        Args:
            prompt: 用户提示词
            system_prompt: 系统提示词
            max_tokens: 最大token数

        Yields:
            生成的文本片段
        """
        messages = [{"role": "user", "content": prompt}]

        kwargs = {
            "model": self.model,
            "max_tokens": max_tokens or self.max_tokens,
            "messages": messages,
        }

        if system_prompt:
            kwargs["system"] = system_prompt

        with self.client.messages.stream(**kwargs) as stream:
            for text in stream.text_stream:
                yield text


class ThesisGenerator:
    """论文内容生成器"""

    def __init__(self, client: Optional[ClaudeClient] = None):
        self.client = client or ClaudeClient()

    def generate_outline(self, topic: str, major: str, requirements: str = "") -> str:
        """
        生成论文大纲

        Args:
            topic: 论文主题
            major: 专业
            requirements: 额外要求

        Returns:
            论文大纲（Markdown格式）
        """
        system_prompt = """你是一位资深的学术论文写作专家，擅长指导本科生完成毕业论文。
你需要根据给定的主题和专业，生成一份详细的论文大纲。
大纲应该包含：
1. 摘要结构要点
2. 各章节标题和子标题
3. 每个章节的核心内容概述
4. 预计字数分配建议"""

        prompt = f"""请为以下论文生成详细大纲：

【论文主题】{topic}
【专业】{major}
【额外要求】{requirements if requirements else "无"}

请生成结构清晰、逻辑严谨的论文大纲。"""

        return self.client.generate(prompt, system_prompt)

    def generate_section(
        self,
        section_title: str,
        section_requirements: str,
        context: str = "",
        word_count: int = 1000,
    ) -> str:
        """
        生成论文章节内容

        Args:
            section_title: 章节标题
            section_requirements: 章节要求
            context: 上下文（前面章节的摘要）
            word_count: 目标字数

        Returns:
            章节内容
        """
        system_prompt = """你是一位资深的学术论文写作专家。
请根据要求撰写论文章节内容。
要求：
1. 语言学术化、严谨
2. 逻辑清晰、论证充分
3. 适当使用专业术语
4. 保持与上下文的连贯性"""

        prompt = f"""请撰写以下论文章节：

【章节标题】{section_title}
【章节要求】{section_requirements}
【上下文】{context if context else "这是论文的开始部分"}
【目标字数】约{word_count}字

请撰写该章节的完整内容。"""

        return self.client.generate(prompt, system_prompt, max_tokens=word_count * 2)

    def generate_abstract(
        self,
        thesis_content: str,
        language: str = "chinese",
    ) -> str:
        """
        生成论文摘要

        Args:
            thesis_content: 论文主要内容摘要
            language: 语言（chinese/english）

        Returns:
            摘要内容
        """
        lang_instruction = "中文" if language == "chinese" else "英文"

        system_prompt = f"""你是一位学术论文写作专家。
请根据论文内容生成{lang_instruction}摘要。
摘要应包含：
1. 研究背景和目的
2. 研究方法
3. 主要发现/结论
4. 研究意义
字数控制在300-500字。"""

        prompt = f"""请根据以下论文内容生成{lang_instruction}摘要：

{thesis_content}"""

        return self.client.generate(prompt, system_prompt)

    def generate_keywords(self, thesis_content: str, count: int = 5) -> list[str]:
        """
        生成关键词

        Args:
            thesis_content: 论文内容
            count: 关键词数量

        Returns:
            关键词列表
        """
        prompt = f"""请从以下论文内容中提取{count}个核心关键词，用逗号分隔：

{thesis_content}

只输出关键词，不要其他内容。"""

        result = self.client.generate(prompt)
        return [kw.strip() for kw in result.split("，") if kw.strip()][:count]

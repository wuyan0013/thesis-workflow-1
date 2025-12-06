# -*- coding: utf-8 -*-
"""
文本处理模块
提供论文降重和降AIGC率功能
基于 Claude API 实现智能改写
"""

from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from enum import Enum


class RewriteIntensity(Enum):
    """改写强度"""
    LIGHT = "light"      # 轻度：保持原意，微调表达
    MEDIUM = "medium"    # 中度：同义替换+句式重组
    HEAVY = "heavy"      # 重度：大幅改写，保留核心观点


class HumanizeStyle(Enum):
    """人格化风格"""
    ACADEMIC = "academic"    # 学术风格：保持专业性
    NATURAL = "natural"      # 自然风格：偏口语化
    MIXED = "mixed"          # 混合风格：学术为主，适度口语


@dataclass
class ProcessResult:
    """处理结果"""
    original: str           # 原文
    processed: str          # 处理后的文本
    changes_count: int      # 修改数量
    similarity: float       # 与原文相似度（估计值）
    details: Dict[str, Any] # 详细信息


class TextProcessor:
    """
    文本处理器
    提供论文降重和降AIGC率功能
    """

    def __init__(self, client=None, use_cli: bool = False, api_key: str = None, base_url: str = None, model: str = None):
        """
        初始化文本处理器

        Args:
            client: ClaudeClient 实例，如果为空则自动创建
            use_cli: 是否使用 Claude CLI（默认 False，使用 SDK 模式）
            api_key: API Key（可选，为空则从 .env 读取）
            base_url: API Base URL（可选，为空则从 .env 读取）
            model: 模型名称（可选，为空则从 .env 读取）
        """
        if client is None:
            from .claude_client import ClaudeClient
            client = ClaudeClient(use_cli=use_cli, api_key=api_key, base_url=base_url, model=model)
        self.client = client

    def reduce_plagiarism(
        self,
        text: str,
        intensity: RewriteIntensity = RewriteIntensity.MEDIUM,
        preserve_terms: Optional[List[str]] = None,
        min_paragraph_length: int = 50
    ) -> ProcessResult:
        """
        论文降重：降低查重率

        Args:
            text: 原始文本
            intensity: 改写强度（轻度/中度/重度）
            preserve_terms: 需要保留的专业术语列表
            min_paragraph_length: 最小段落长度（低于此长度的段落不处理）

        Returns:
            ProcessResult: 处理结果
        """
        if not text or len(text.strip()) < min_paragraph_length:
            return ProcessResult(
                original=text,
                processed=text,
                changes_count=0,
                similarity=1.0,
                details={"skipped": True, "reason": "文本过短"}
            )

        terms_instruction = ""
        if preserve_terms:
            terms_instruction = f"\n### 必须保留的专业术语（不可替换）\n{', '.join(preserve_terms)}"

        intensity_instructions = {
            RewriteIntensity.LIGHT: """
### 轻度改写策略
- 仅替换部分同义词（约30%）
- 保持原有句式结构
- 调整个别语序
- 添加/删除少量修饰语""",
            RewriteIntensity.MEDIUM: """
### 中度改写策略
- 同义词替换（约60%）
- 句式结构重组
- 主动句与被动句转换
- 长句拆分或短句合并
- 调整段落内部语序""",
            RewriteIntensity.HEAVY: """
### 重度改写策略
- 大幅同义词替换（约80%）
- 完全重构句式结构
- 段落结构重新组织
- 引入新的表达方式
- 保留核心观点但彻底改变表述"""
        }

        prompt = f"""你是一位专业的学术写作专家。请对以下学术文本进行降重改写，使其能够通过知网、维普、万方等查重系统检测。

## 原始文本
{text}

## 改写要求
{intensity_instructions[intensity]}
{terms_instruction}

### 核心原则
1. **保持原意**：改写后必须完整保留原文的学术观点和论证逻辑
2. **学术规范**：保持学术论文的专业性和严谨性
3. **自然流畅**：改写后的文本要通顺自然，不能有机器翻译的痕迹
4. **引用保留**：如有引用标注[1][2]等，必须保留在合适位置

### 改写技巧
- 使用同义词替换：如"研究"→"探讨/分析/考察"
- 调整句式：如"A导致B"→"B是由A引起的"
- 拆分长句：将复杂长句拆分为多个短句
- 合并短句：将多个简单句合并为复合句
- 变换语序：调整主语、谓语、宾语的顺序
- 添加过渡：适当添加"此外""同时""与此同时"等过渡词

### 禁止事项
- 不要改变原文的核心论点
- 不要添加原文没有的观点
- 不要删除重要的论证内容
- 不要使用口语化表达
- 不要翻译成其他语言

## 输出要求
直接输出改写后的文本，不要有任何解释或说明。"""

        processed = self.client.generate(prompt)

        # 估算修改数量和相似度
        original_chars = set(text)
        processed_chars = set(processed)
        common_chars = original_chars & processed_chars
        similarity = len(common_chars) / max(len(original_chars), 1) * 0.7

        return ProcessResult(
            original=text,
            processed=processed.strip(),
            changes_count=self._estimate_changes(text, processed),
            similarity=similarity,
            details={
                "intensity": intensity.value,
                "preserved_terms": preserve_terms or [],
                "original_length": len(text),
                "processed_length": len(processed)
            }
        )

    def reduce_aigc_rate(
        self,
        text: str,
        style: HumanizeStyle = HumanizeStyle.ACADEMIC,
        preserve_terms: Optional[List[str]] = None
    ) -> ProcessResult:
        """
        降AIGC率：降低AI检测率

        Args:
            text: 原始文本
            style: 人格化风格（学术/自然/混合）
            preserve_terms: 需要保留的专业术语列表

        Returns:
            ProcessResult: 处理结果
        """
        if not text or len(text.strip()) < 30:
            return ProcessResult(
                original=text,
                processed=text,
                changes_count=0,
                similarity=1.0,
                details={"skipped": True, "reason": "文本过短"}
            )

        terms_instruction = ""
        if preserve_terms:
            terms_instruction = f"\n### 必须保留的专业术语\n{', '.join(preserve_terms)}"

        style_instructions = {
            HumanizeStyle.ACADEMIC: """
### 学术风格人格化
- 保持专业学术语言
- 引入学术谦虚表达：「初步分析表明」「现有研究认为」「从某种程度上」
- 使用学术过渡词：「基于此」「由此可见」「综上所述」
- 添加适度的学术性不确定表达：「可能」「或许」「在一定程度上」""",
            HumanizeStyle.NATURAL: """
### 自然风格人格化
- 适当引入口语化表达
- 使用更多日常用语替换学术用语
- 加入个人观察视角
- 使用更灵活的句式结构""",
            HumanizeStyle.MIXED: """
### 混合风格人格化
- 以学术风格为主
- 在合适的地方加入自然表达
- 保持专业性的同时增加可读性
- 适度使用第一人称视角（如「研究过程中发现」）"""
        }

        prompt = f"""你是一位经验丰富的人类学术写作专家。请对以下文本进行人格化改写，使其更像人类写作，能够通过 ZeroGPT、GPTZero、AIGC检测器等AI检测工具。

## 原始文本
{text}

## 人格化要求
{style_instructions[style]}
{terms_instruction}

### AI检测工具的判断依据（需要规避）
1. **词汇分布均匀**：AI倾向于使用均匀分布的词汇，人类会有偏好和重复
2. **句式过于工整**：AI生成的句子结构往往过于规整
3. **缺乏个人视角**：AI缺乏主观性和个人经验
4. **过度完美**：AI文本往往逻辑过于清晰，缺少人类的"瑕疵"
5. **缺乏自然过渡**：AI的段落过渡往往生硬

### 人格化技巧
1. **添加学术谦虚表达**
   - 「根据现有资料分析」
   - 「初步研究表明」
   - 「从实地调研情况来看」
   - 「在一定程度上可以认为」

2. **引入主观视角**
   - 「通过对XX的深入了解，发现...」
   - 「在研究过程中注意到...」
   - 「从访谈情况来看...」

3. **增加自然过渡**
   - 「值得注意的是」
   - 「令人关注的是」
   - 「有意思的是」
   - 「需要指出的是」

4. **适度引入"不完美"**
   - 适当使用长句和复杂句式
   - 保留一些"冗余"的修饰语
   - 使用一些非常见的表达方式

5. **句式多样化**
   - 混合使用主动句和被动句
   - 交替使用长句和短句
   - 避免连续使用相同的句式结构

### 禁止事项
- 不要改变原文的核心观点
- 不要删除重要论证内容
- 不要添加无关的个人经验
- 不要过度口语化（除非选择自然风格）
- 保留引用标注

## 输出要求
直接输出改写后的文本，不要有任何解释或说明。"""

        processed = self.client.generate(prompt)

        return ProcessResult(
            original=text,
            processed=processed.strip(),
            changes_count=self._estimate_changes(text, processed),
            similarity=0.6,  # 人格化改写通常有较大变化
            details={
                "style": style.value,
                "preserved_terms": preserve_terms or [],
                "original_length": len(text),
                "processed_length": len(processed)
            }
        )

    def process_batch(
        self,
        paragraphs: List[str],
        mode: str = "plagiarism",  # "plagiarism" or "aigc"
        **kwargs
    ) -> List[ProcessResult]:
        """
        批量处理多个段落

        Args:
            paragraphs: 段落列表
            mode: 处理模式 ("plagiarism" 降重 / "aigc" 降AIGC率)
            **kwargs: 其他参数传递给对应的处理方法

        Returns:
            List[ProcessResult]: 处理结果列表
        """
        results = []
        processor = self.reduce_plagiarism if mode == "plagiarism" else self.reduce_aigc_rate

        for para in paragraphs:
            if para.strip():
                result = processor(para, **kwargs)
                results.append(result)

        return results

    def _estimate_changes(self, original: str, processed: str) -> int:
        """估算修改数量（基于字符差异）"""
        # 简单估算：计算不同字符的数量
        original_chars = list(original)
        processed_chars = list(processed)

        # 使用最长公共子序列的近似计算
        min_len = min(len(original_chars), len(processed_chars))
        max_len = max(len(original_chars), len(processed_chars))

        if min_len == 0:
            return max_len

        # 统计位置匹配的字符
        matches = sum(1 for i in range(min_len) if original_chars[i] == processed_chars[i])

        # 估算修改数量
        changes = max_len - matches
        return max(0, changes)

    def split_paragraphs(self, text: str) -> List[str]:
        """将文本分割为段落"""
        paragraphs = []
        for para in text.split('\n'):
            para = para.strip()
            if para:
                paragraphs.append(para)
        return paragraphs

    def merge_results(self, results: List[ProcessResult]) -> str:
        """合并处理结果为完整文本"""
        return '\n\n'.join(r.processed for r in results if r.processed)

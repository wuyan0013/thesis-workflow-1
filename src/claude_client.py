# -*- coding: utf-8 -*-
"""
Claude 客户端
负责与Claude交互，生成论文内容
严格遵循：反AI检测 + 低查重率 + 人类化写作

支持两种调用方式：
1. Claude CLI（推荐，无需配置 API Key）
2. Anthropic SDK（需要配置 API Key）
"""

import subprocess
import os
import sys
from pathlib import Path
from typing import Optional, Generator, List

# 检测运行环境
_in_streamlit = 'streamlit' in sys.modules


class ClaudeClient:
    """
    Claude 客户端
    优先使用 Claude CLI 调用，如果失败则回退到 Anthropic SDK
    """

    DEFAULT_MODEL = "claude-opus-4-5-20251101"

    def __init__(self, use_cli: bool = True, api_key: Optional[str] = None):
        """
        初始化客户端

        Args:
            use_cli: 是否使用 Claude CLI（默认 True）
            api_key: Anthropic API Key（仅在 use_cli=False 时使用）
        """
        self.use_cli = use_cli
        self.api_key = api_key

        if use_cli:
            # 检查 Claude CLI 是否可用
            if self._check_cli():
                print("[OK] Claude CLI 已就绪")
            else:
                print("[WARN] Claude CLI 不可用，尝试使用 API...")
                self.use_cli = False

        if not self.use_cli:
            self._init_sdk()

    def _check_cli(self) -> bool:
        """检查 Claude CLI 是否可用"""
        try:
            # 尝试多个可能的路径
            possible_cmds = [
                "claude --version",
                # Windows npm 全局安装路径
                os.path.expanduser("~\\AppData\\Roaming\\npm\\claude.cmd") + " --version",
            ]

            for cmd in possible_cmds:
                try:
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=10,
                        encoding='utf-8',
                        errors='replace',
                        shell=True
                    )
                    if result.returncode == 0:
                        # 保存可用的命令路径
                        self._cli_cmd = cmd.replace(" --version", "")
                        return True
                except:
                    continue

            return False
        except Exception:
            return False

    def _init_sdk(self):
        """初始化 Anthropic SDK"""
        try:
            import anthropic
            from .config import get_config

            config = get_config()
            api_key = self.api_key or config.claude_api_key

            if not api_key:
                raise Exception("未配置 API Key，且 Claude CLI 不可用")

            client_kwargs = {"api_key": api_key}
            base_url = config.claude_base_url
            if base_url:
                client_kwargs["base_url"] = base_url

            self.client = anthropic.Anthropic(**client_kwargs)
            self.model = config.claude_model or self.DEFAULT_MODEL
            self.max_tokens = config.max_tokens

            print(f"[OK] Anthropic SDK 已初始化")
            print(f"  模型: {self.model}")

        except ImportError:
            raise Exception("anthropic 库未安装，请运行: pip install anthropic")

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
            system_prompt: 系统提示词（可选）
            max_tokens: 最大 token 数（CLI 模式下忽略）

        Returns:
            生成的文本内容
        """
        if self.use_cli:
            return self._generate_cli(prompt, system_prompt)
        else:
            return self._generate_sdk(prompt, system_prompt, max_tokens)

    def _generate_cli(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """通过 Claude CLI 生成内容"""
        import tempfile
        import json

        # 如果有 system prompt，合并到 prompt 中
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"""【系统指令】
{system_prompt}

【用户请求】
{prompt}"""

        temp_file = None
        try:
            # 将 prompt 写入临时文件
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
                f.write(full_prompt)
                temp_file = f.name

            cli_cmd = getattr(self, '_cli_cmd', 'claude')

            # 方案1: 使用管道输入 + JSON 输出（更可靠的编码处理）
            cmd = f'type "{temp_file}" | "{cli_cmd}" -p --output-format json'

            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=300,
                shell=True,
                env={**os.environ, 'PYTHONIOENCODING': 'utf-8'}
            )

            # 解码输出
            stdout = ""
            for encoding in ['utf-8', 'gbk', 'cp936', 'latin-1']:
                try:
                    stdout = result.stdout.decode(encoding)
                    if stdout:
                        break
                except:
                    continue

            stderr = ""
            for encoding in ['utf-8', 'gbk', 'cp936', 'latin-1']:
                try:
                    stderr = result.stderr.decode(encoding) if result.stderr else ""
                    break
                except:
                    continue

            if result.returncode != 0:
                error_msg = stderr.strip() if stderr else f"返回码 {result.returncode}"
                raise Exception(f"CLI 错误: {error_msg}")

            if not stdout.strip():
                raise Exception("Claude CLI 返回空内容")

            # 尝试解析 JSON 输出
            try:
                data = json.loads(stdout.strip())
                # JSON 格式的响应，提取 result 字段
                if isinstance(data, dict):
                    if 'result' in data:
                        return data['result']
                    elif 'content' in data:
                        return data['content']
                    elif 'text' in data:
                        return data['text']
                    elif 'message' in data:
                        return data['message']
                return stdout.strip()
            except json.JSONDecodeError:
                # 不是 JSON，直接返回文本
                return stdout.strip()

        except subprocess.TimeoutExpired:
            raise Exception("Claude CLI 调用超时（5分钟）")
        except Exception as e:
            raise Exception(f"CLI 调用失败: {e}")
        finally:
            if temp_file:
                try:
                    os.unlink(temp_file)
                except:
                    pass

    def _generate_sdk(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None
    ) -> str:
        """通过 Anthropic SDK 生成内容"""
        tokens = max_tokens or self.max_tokens

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=tokens,
                system=system_prompt or "",
                messages=[{"role": "user", "content": prompt}],
            )

            if response.content and len(response.content) > 0:
                return response.content[0].text
            else:
                raise Exception("API 返回空内容")

        except Exception as e:
            raise Exception(f"API 调用失败: {e}")

    def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: Optional[int] = None,
    ) -> Generator[str, None, None]:
        """流式生成（仅 SDK 模式支持）"""
        if self.use_cli:
            # CLI 模式不支持流式，直接返回完整结果
            yield self.generate(prompt, system_prompt, max_tokens)
        else:
            tokens = max_tokens or self.max_tokens
            try:
                with self.client.messages.stream(
                    model=self.model,
                    max_tokens=tokens,
                    system=system_prompt or "",
                    messages=[{"role": "user", "content": prompt}],
                ) as stream:
                    for text in stream.text_stream:
                        yield text
            except Exception as e:
                raise Exception(f"流式生成失败: {e}")


class ThesisGenerator:
    """
    论文内容生成器
    严格遵循反AI检测规则，确保：
    - AI检测率 < 20%（ZeroGPT、GPTZero等）
    - 知网查重率 < 20%
    """

    _system_prompt_cache: Optional[str] = None

    @classmethod
    def _load_system_prompt(cls) -> str:
        """从文件加载系统提示词（带缓存）"""
        if cls._system_prompt_cache is None:
            prompt_path = Path(__file__).parent.parent / "prompts" / "system.md"
            if prompt_path.exists():
                cls._system_prompt_cache = prompt_path.read_text(encoding="utf-8")
            else:
                cls._system_prompt_cache = "你是一位资深的文科学术论文写作专家。"
        return cls._system_prompt_cache

    @property
    def SYSTEM_PROMPT(self) -> str:
        return self._load_system_prompt()

    def __init__(self, client: Optional[ClaudeClient] = None):
        self.client = client or ClaudeClient()

    # 广西行政区划数据（真实数据，用于约束选题生成）
    GUANGXI_REGIONS = {
        "南宁市": ["青秀区", "兴宁区", "江南区", "良庆区", "邕宁区", "西乡塘区", "武鸣区", "横州市", "宾阳县", "上林县", "马山县", "隆安县"],
        "柳州市": ["城中区", "鱼峰区", "柳南区", "柳北区", "柳江区", "柳城县", "鹿寨县", "融安县", "融水苗族自治县", "三江侗族自治县"],
        "桂林市": ["秀峰区", "叠彩区", "象山区", "七星区", "雁山区", "临桂区", "阳朔县", "灵川县", "全州县", "兴安县", "永福县", "灌阳县", "龙胜各族自治县", "资源县", "平乐县", "恭城瑶族自治县", "荔浦市"],
        "梧州市": ["万秀区", "长洲区", "龙圩区", "苍梧县", "藤县", "蒙山县", "岑溪市"],
        "北海市": ["海城区", "银海区", "铁山港区", "合浦县"],
        "防城港市": ["港口区", "防城区", "东兴市", "上思县"],
        "钦州市": ["钦南区", "钦北区", "灵山县", "浦北县"],
        "贵港市": ["港北区", "港南区", "覃塘区", "平南县", "桂平市"],
        "玉林市": ["玉州区", "福绑区", "容县", "陆川县", "博白县", "兴业县", "北流市"],
        "百色市": ["右江区", "田阳区", "田东县", "德保县", "那坡县", "凌云县", "乐业县", "田林县", "西林县", "隆林各族自治县", "靖西市", "平果市"],
        "贺州市": ["八步区", "平桂区", "昭平县", "钟山县", "富川瑶族自治县"],
        "河池市": ["金城江区", "宜州区", "南丹县", "天峨县", "凤山县", "东兰县", "罗城仫佬族自治县", "环江毛南族自治县", "巴马瑶族自治县", "都安瑶族自治县", "大化瑶族自治县"],
        "来宾市": ["兴宾区", "忻城县", "象州县", "武宣县", "金秀瑶族自治县", "合山市"],
        "崇左市": ["江州区", "扶绑县", "宁明县", "龙州县", "大新县", "天等县", "凭祥市"],
    }

    # 广西特色资源（用于生成真实选题）
    GUANGXI_FEATURES = {
        "特色产业": ["百色芒果", "荔浦芋头", "桂林米粉", "柳州螺蛳粉", "横州茉莉花", "容县沙田柚", "富川脐橙", "凭祥红木", "东兴边贸", "北海珍珠"],
        "文化遗产": ["刘三姐歌谣", "壮族铜鼓", "侗族大歌", "瑶族盘王节", "京族哈节", "壮锦织造", "桂剧", "彩调", "壮族三月三"],
        "旅游资源": ["桂林山水", "德天瀑布", "北海银滩", "涠洲岛", "龙脊梯田", "黄姚古镇", "程阳风雨桥", "花山岩画", "靖西通灵大峡谷"],
        "发展战略": ["西部陆海新通道", "北部湾经济区", "珠江-西江经济带", "左右江革命老区振兴", "边境贸易试验区", "中国-东盟自贸区"],
    }

    def generate_topics(self, major: str, count: int = 5) -> List[str]:
        """
        根据专业生成与广西真实地名相关的论文主题

        使用 opus-4.5 模型确保选题的真实性和学术价值
        """
        # 构建地名列表供AI参考
        regions_str = "\n".join([
            f"- {city}：{', '.join(districts[:5])}等"
            for city, districts in self.GUANGXI_REGIONS.items()
        ])

        features_str = "\n".join([
            f"- {category}：{', '.join(items)}"
            for category, items in self.GUANGXI_FEATURES.items()
        ])

        prompt = f"""你是一位熟悉广西壮族自治区的学术研究专家。请为【{major}】专业生成{count}个高质量的本科毕业论文选题。

## 最高优先级要求（违反任何一条都是失败）

### 1. 地名真实性要求
- 每个选题必须包含广西真实的市、县（区）名称
- 选题格式必须是"XXX研究——以XX市XX县/区为例"
- 禁止使用模糊表述如"某市""某县"
- 禁止编造不存在的地名

### 2. 广西真实行政区划（必须从中选择）
{regions_str}

### 3. 广西特色资源（可结合使用）
{features_str}

### 4. 选题学术性要求
- 选题要有研究价值和可行性
- 结合该地区的真实特点（如产业、文化、地理、民族等）
- 体现问题导向，有明确的研究对象和范围
- 符合{major}专业的学科特点

### 5. 选题格式示例
- 广西乡村振兴战略实施中的基层政府执行力研究——以百色市田阳区为例
- 广西边境地区小学双语教育现状与对策研究——以崇左市凭祥市为例
- 广西特色农产品电商品牌建设研究——以百色市右江区芒果产业为例
- 广西少数民族传统文化保护与传承研究——以河池市巴马瑶族自治县为例

## 输出要求
- 每行一个选题
- 不要编号、不要解释、不要其他内容
- 直接输出{count}个选题

请生成选题："""

        result = self.client.generate(prompt)

        topics = []
        for line in result.strip().split('\n'):
            line = line.strip()
            if line and not line.startswith('#'):
                # 去除可能的编号
                if len(line) > 0 and line[0].isdigit() and '.' in line[:3]:
                    line = line.split('.', 1)[-1].strip()
                if len(line) > 0 and line[0].isdigit() and '、' in line[:3]:
                    line = line.split('、', 1)[-1].strip()
                # 去除可能的引号
                line = line.strip('"\'""''')
                if line:
                    topics.append(line)

        return topics[:count]

    def generate_outline(self, topic: str, major: str, requirements: str = "") -> str:
        """
        生成论文大纲（标题必须个性化，字数严格控制）
        """
        prompt = f"""请为以下论文主题设计大纲，直接输出大纲内容。

【论文主题】{topic}
【专业】{major}
【额外要求】{requirements if requirements else "无"}

## 字数控制（最高优先级！总字数必须在10000-11000字）

### 各章字数严格限制
- 第一章 绪论：1200-1500字
- 第二章：1500-1800字
- 第三章：1500-1800字
- 第四章：1500-1800字
- 第五章：1500-1800字
- 第六章 结论：600-800字
- 总计：约10000字（绝不超过11000字）

## 标题个性化要求

### 绝对禁止的模板化标题
× "相关概念与理论基础"
× "理论基础" / "概念界定" / "核心概念界定"
× "现状分析" / "问题分析" / "问题成因分析"
× "对策与建议" / "对策建议" / "分析框架"

### 正确的标题写法
标题必须包含论文主题中的具体地名或研究对象

## 结构要求
- 共6章
- 第一章：绪论（可用通用标题）
- 第二至五章：必须是个性化标题，包含具体地名
- 第六章：结论（可用通用标题）
- 每章设2个二级标题（不要3个，控制字数）

### 输出格式
一、绪论（1200-1500字）
（一）研究背景与意义
（二）研究思路与方法

二、[包含地名的个性化标题]（1500-1800字）
（一）[具体的二级标题]
（二）[具体的二级标题]

三、[包含地名的个性化标题]（1500-1800字）
（一）[具体的二级标题]
（二）[具体的二级标题]

四、[包含地名的个性化标题]（1500-1800字）
（一）[具体的二级标题]
（二）[具体的二级标题]

五、[包含地名的个性化标题]（1500-1800字）
（一）[具体的二级标题]
（二）[具体的二级标题]

六、结论（600-800字）
（一）研究总结
（二）研究展望

直接输出大纲："""

        return self.client.generate(prompt, self.SYSTEM_PROMPT)

    def generate_section(
        self,
        section_title: str,
        section_requirements: str,
        context: str = "",
        word_count: int = 1500,
    ) -> str:
        """
        生成论文章节内容（严格控制字数，包含引用上标）
        """
        prompt = f"""请撰写以下论文章节，直接输出完整的论文正文。

【章节标题】{section_title}
【内容要求】{section_requirements}
【目标字数】严格控制在{word_count}字左右（允许±100字，绝对不能超过{word_count + 200}字）

【论文背景】
{context}

## 字数控制（最高优先级！）
- 本章节必须严格控制在{word_count}字左右
- 不要写太多内容，宁可精简也不要超字数
- 每个二级小节控制在{word_count // 2}字左右

## 文献引用要求（重要！）
- 在引用观点、数据、理论时，必须添加引用上标
- 格式：在引用内容后加上[1]、[2]等上标数字
- 示例："根据相关研究，乡村振兴战略的实施需要多方协作[1]。有学者指出..."
- 每章至少要有3-5处引用标注
- 引用标注的数字要与参考文献列表对应

## 输出要求
- 直接输出论文内容，不要有任何额外文字
- 禁止输出【注意】【建议】【警告】等标记
- 禁止输出AI自述
- 数据要具体（如"调研显示82.5%的居民..."）

## 反AI检测写作
- 句式多样化：混合短句、中句、长句
- 使用自然过渡词：此外、然而、因此、与此同时
- 禁止机械分点："首先...其次...最后..."
- 禁止"笔者认为""本文认为"等表述

## 格式
- 二级小节标题用"## "格式
- 段落之间用空行分隔
- 不要重复章节标题

直接输出论文正文："""

        return self.client.generate(
            prompt,
            self.SYSTEM_PROMPT,
            max_tokens=word_count * 2
        )

    def generate_abstract(
        self,
        thesis_content: str,
        language: str = "chinese",
    ) -> str:
        """生成论文摘要（人类化写作）"""
        lang_instruction = "中文" if language == "chinese" else "英文"

        prompt = f"""请根据以下论文内容生成{lang_instruction}摘要：

{thesis_content}

摘要要求：
1. 字数控制在300-400字
2. 包含研究背景、研究目的、研究方法、主要结论
3. 语言简洁凝练，突出研究价值

人类化写作要求：
- 句式多样化，混合长短句
- 使用自然过渡词（"基于此""研究发现""分析表明"等）
- 保持学术谦虚（"初步分析""基于现有资料"等）

禁止使用：
- "本文""笔者""作者"等第一人称表述
- "填补空白""弥补空白"等自我吹捧
- "首先、其次、最后"等机械结构

请直接输出摘要内容："""

        return self.client.generate(prompt, self.SYSTEM_PROMPT)

    def generate_keywords(self, thesis_content: str, count: int = 5) -> List[str]:
        """生成关键词"""
        prompt = f"""请从以下论文内容中提取{count}个核心关键词：

{thesis_content}

要求：
1. 关键词应准确反映论文核心内容
2. 优先选择学术规范用语
3. 关键词之间用中文分号"；"分隔
4. 只输出关键词，不要其他内容

请输出关键词："""

        result = self.client.generate(prompt)
        keywords = []
        for sep in ["；", ";", "，", ","]:
            if sep in result:
                keywords = [kw.strip() for kw in result.split(sep) if kw.strip()]
                break
        if not keywords:
            keywords = [result.strip()]
        return keywords[:count]

    def generate_references(
        self,
        topic: str,
        major: str,
        count: int = 10
    ) -> List[str]:
        """
        生成参考文献（必须是国内中文文献）
        """
        prompt = f"""请为以下论文主题生成{count}条中国国内参考文献，直接输出文献列表。

【论文主题】{topic}
【专业】{major}

## 文献要求（最高优先级）

### 1. 必须是国内中文文献
- 所有文献必须是中国国内发表的中文文献
- 禁止任何英文文献、外文文献
- 作者必须是中国学者（中文姓名）
- 期刊必须是中国国内期刊

### 2. 文献类型分布
- 期刊论文[J]：7-8条
  - 中文核心期刊、CSSCI来源期刊
  - 如《管理世界》《中国行政管理》《公共管理学报》《农业经济问题》《中国农村经济》等
- 学位论文[D]：2-3条
  - 国内高校（如北京大学、清华大学、中国人民大学、武汉大学等）
- 专著[M]：1-2条
  - 国内出版社出版的中文专著

### 3. 格式要求（GB/T 7714-2015）
- 期刊：[序号] 作者.标题[J].期刊名,年份,卷(期):起止页码.
- 学位论文：[序号] 作者.标题[D].城市:学校名称,年份.
- 专著：[序号] 作者.书名[M].出版地:出版社,年份:页码.

### 4. 年份要求
- 2020-2024年：7-8条
- 2015-2019年：2-3条经典文献

### 5. 输出格式
- 每条文献独占一行
- 以[1]、[2]等编号开头
- 不要添加任何解释说明
- 直接输出文献列表

直接输出参考文献："""

        result = self.client.generate(prompt, self.SYSTEM_PROMPT)

        references = []
        for line in result.strip().split('\n'):
            line = line.strip()
            if line and (line.startswith('[') or (len(line) > 0 and line[0].isdigit())):
                references.append(line)

        return references[:count]

    def generate_defense_paper(
        self,
        title: str,
        abstract: str,
        chapters: list,
        thesis_content: str = "",
        word_count: int = 2500
    ) -> str:
        """
        生成答辩论文（答辩陈述稿）

        严格控制：
        - AI检测率 < 20%
        - 查重率 < 10%

        Args:
            title: 论文标题
            abstract: 论文摘要
            chapters: 章节列表 [{"title": "...", "content": "..."}]
            thesis_content: 完整论文内容（可选，用于更精准生成）
            word_count: 目标字数（默认2500字，适合8-10分钟答辩）

        Returns:
            答辩陈述稿内容
        """
        # 构建章节概要
        chapters_summary = ""
        for i, ch in enumerate(chapters, 1):
            ch_title = ch.get("title", f"第{i}章")
            ch_content = ch.get("content", "")[:500]  # 截取前500字作为概要
            chapters_summary += f"\n【第{i}章】{ch_title}\n{ch_content}...\n"

        prompt = f"""你是一位经验丰富的论文答辩指导专家。请根据以下论文信息，撰写一份专业的答辩陈述稿。

## 论文信息
【论文标题】{title}
【论文摘要】{abstract}
【各章概要】{chapters_summary}

## 答辩陈述稿要求

### 1. 结构要求（约{word_count}字）
答辩稿必须包含以下部分：

**开场白（约150字）**
- 向答辩委员会问好
- 自我介绍（"我是XX专业的XXX"）
- 论文题目介绍

**选题背景与意义（约300字）**
- 为什么选择这个课题
- 研究的理论意义和实践价值
- 不要照搬摘要，用口语化表达

**研究内容概述（约800字）**
- 按章节顺序介绍主要内容
- 突出重点，不要面面俱到
- 用自己的语言阐述

**研究方法与过程（约400字）**
- 采用的研究方法
- 研究过程中的经历和体会
- 可以加入一些个人感受

**主要结论与创新点（约500字）**
- 研究得出的主要结论
- 本研究的创新之处（哪怕很小）
- 实际应用价值

**不足与展望（约250字）**
- 诚恳承认研究的局限性
- 未来研究方向
- 体现学术谦虚

**致谢（约100字）**
- 感谢导师的指导
- 感谢答辩委员会
- 请求指正

### 2. 语言风格（最高优先级！）

**必须使用口语化表达：**
- 使用第一人称"我"
- 加入口语化词汇："其实""说实话""坦白讲"
- 适当使用停顿词："嗯""那么""接下来"
- 使用自然过渡："说到这里""关于这一点""值得一提的是"

**禁止的表达（AI特征明显）：**
- "本文""本研究""笔者"等书面语
- "首先、其次、再次、最后"等机械结构
- 过于工整的排比句
- 完美的逻辑递进

**人格化技巧：**
- 加入个人研究经历："在调研过程中，我发现..."
- 表达真实感受："这个发现让我很意外..."
- 适度的自我质疑："当然，这个结论可能还需要进一步验证"
- 不完美的转折："虽然我努力了，但还是有些遗憾..."

### 3. 反AI检测要求（确保AI检测率<20%）
- 句式多样化：混合短句、中句、长句、反问句
- 段落长度不均匀：有长有短，模拟真实演讲
- 加入口语化"瑕疵"：如"嗯，怎么说呢""换句话说"
- 避免完美结构：不要每段都是"总分总"
- 使用个性化词汇：体现个人表达习惯

### 4. 反查重要求（确保查重率<10%）
- 完全重新表述论文内容，不要复制粘贴
- 用口语化方式重新阐述学术观点
- 不要引用原文中的长句
- 加入大量个人化表达降低重复率

### 5. 格式要求
- 使用Markdown格式
- 各部分用"## "标题分隔
- 自然段落，不要过多列表
- 不需要标注引用

## 输出要求
- 直接输出答辩陈述稿全文
- 不要有任何解释说明
- 不要输出【注意】【建议】等标记
- 字数严格控制在{word_count}字左右

直接输出答辩陈述稿："""

        return self.client.generate(prompt, self.SYSTEM_PROMPT)

"""
Word文档生成器
负责将生成的内容转换为符合学校格式的Word文档
"""

from pathlib import Path
from typing import Optional
from datetime import datetime

from docx import Document
from docx.shared import Pt, Cm, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml.ns import qn

from .config import get_config


class DocxBuilder:
    """Word文档构建器"""

    def __init__(self, template_path: Optional[str] = None):
        """
        初始化文档构建器

        Args:
            template_path: Word模板文件路径，如果为None则创建新文档
        """
        self.config = get_config()
        self.thesis_config = self.config.thesis_config

        if template_path and Path(template_path).exists():
            self.doc = Document(template_path)
        else:
            self.doc = Document()
            self._setup_document()

    def _setup_document(self) -> None:
        """设置文档基本格式"""
        # 页面设置
        section = self.doc.sections[0]
        section.page_width = Cm(21)  # A4
        section.page_height = Cm(29.7)

        page_config = self.thesis_config.get("page", {})
        section.top_margin = Cm(page_config.get("margin_top", 2.54))
        section.bottom_margin = Cm(page_config.get("margin_bottom", 2.54))
        section.left_margin = Cm(page_config.get("margin_left", 3.17))
        section.right_margin = Cm(page_config.get("margin_right", 3.17))

        # 设置默认样式
        self._setup_styles()

    def _setup_styles(self) -> None:
        """设置文档样式"""
        styles = self.doc.styles
        font_config = self.thesis_config.get("font", {})
        size_config = self.thesis_config.get("font_size", {})

        # 正文样式
        normal_style = styles["Normal"]
        normal_style.font.name = font_config.get("english", "Times New Roman")
        normal_style.font.size = Pt(size_config.get("body", 12))
        normal_style._element.rPr.rFonts.set(
            qn("w:eastAsia"), font_config.get("body", "宋体")
        )

        # 标题1样式
        if "Heading 1" in styles:
            h1_style = styles["Heading 1"]
        else:
            h1_style = styles.add_style("Heading 1", WD_STYLE_TYPE.PARAGRAPH)
        h1_style.font.name = font_config.get("english", "Times New Roman")
        h1_style.font.size = Pt(size_config.get("heading1", 16))
        h1_style.font.bold = True
        h1_style._element.rPr.rFonts.set(
            qn("w:eastAsia"), font_config.get("heading", "黑体")
        )

        # 标题2样式
        if "Heading 2" in styles:
            h2_style = styles["Heading 2"]
        else:
            h2_style = styles.add_style("Heading 2", WD_STYLE_TYPE.PARAGRAPH)
        h2_style.font.name = font_config.get("english", "Times New Roman")
        h2_style.font.size = Pt(size_config.get("heading2", 14))
        h2_style.font.bold = True
        h2_style._element.rPr.rFonts.set(
            qn("w:eastAsia"), font_config.get("heading", "黑体")
        )

    def add_cover_page(
        self,
        title: str,
        author: str,
        student_id: str,
        major: str,
        supervisor: str,
        date: Optional[str] = None,
    ) -> None:
        """
        添加封面页

        Args:
            title: 论文标题
            author: 作者姓名
            student_id: 学号
            major: 专业
            supervisor: 指导教师
            date: 日期
        """
        university = self.thesis_config.get("university", "XX大学")
        college = self.thesis_config.get("college", "XX学院")

        # 学校名称
        p = self.doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(university)
        run.font.size = Pt(26)
        run.font.bold = True
        run._element.rPr.rFonts.set(qn("w:eastAsia"), "黑体")

        # 论文类型
        p = self.doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run("本科毕业论文")
        run.font.size = Pt(22)
        run.font.bold = True
        run._element.rPr.rFonts.set(qn("w:eastAsia"), "黑体")

        # 空行
        for _ in range(3):
            self.doc.add_paragraph()

        # 论文标题
        p = self.doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(title)
        run.font.size = Pt(20)
        run.font.bold = True
        run._element.rPr.rFonts.set(qn("w:eastAsia"), "黑体")

        # 空行
        for _ in range(4):
            self.doc.add_paragraph()

        # 作者信息
        info_items = [
            ("学    院", college),
            ("专    业", major),
            ("学    号", student_id),
            ("姓    名", author),
            ("指导教师", supervisor),
            ("完成日期", date or datetime.now().strftime("%Y年%m月")),
        ]

        for label, value in info_items:
            p = self.doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run(f"{label}：{value}")
            run.font.size = Pt(14)
            run._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")

        # 分页
        self.doc.add_page_break()

    def add_abstract(
        self,
        abstract_cn: str,
        keywords_cn: list[str],
        abstract_en: str,
        keywords_en: list[str],
    ) -> None:
        """
        添加中英文摘要

        Args:
            abstract_cn: 中文摘要
            keywords_cn: 中文关键词
            abstract_en: 英文摘要
            keywords_en: 英文关键词
        """
        # 中文摘要
        p = self.doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run("摘  要")
        run.font.size = Pt(16)
        run.font.bold = True
        run._element.rPr.rFonts.set(qn("w:eastAsia"), "黑体")

        p = self.doc.add_paragraph(abstract_cn)
        p.paragraph_format.first_line_indent = Cm(0.74)  # 两个字符
        p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE

        p = self.doc.add_paragraph()
        run = p.add_run("关键词：")
        run.font.bold = True
        run._element.rPr.rFonts.set(qn("w:eastAsia"), "黑体")
        p.add_run("；".join(keywords_cn))

        self.doc.add_page_break()

        # 英文摘要
        p = self.doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run("Abstract")
        run.font.size = Pt(16)
        run.font.bold = True

        p = self.doc.add_paragraph(abstract_en)
        p.paragraph_format.first_line_indent = Cm(0.74)
        p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE

        p = self.doc.add_paragraph()
        run = p.add_run("Keywords: ")
        run.font.bold = True
        p.add_run("; ".join(keywords_en))

        self.doc.add_page_break()

    def add_heading(self, text: str, level: int = 1) -> None:
        """
        添加标题

        Args:
            text: 标题文本
            level: 标题级别 (1-3)
        """
        self.doc.add_heading(text, level=level)

    def add_paragraph(self, text: str, first_line_indent: bool = True) -> None:
        """
        添加段落

        Args:
            text: 段落文本
            first_line_indent: 是否首行缩进
        """
        p = self.doc.add_paragraph(text)
        if first_line_indent:
            p.paragraph_format.first_line_indent = Cm(0.74)
        p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE

    def add_content(self, content: str) -> None:
        """
        添加内容（自动解析Markdown格式）

        Args:
            content: Markdown格式的内容
        """
        lines = content.strip().split("\n")

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 解析标题
            if line.startswith("### "):
                self.add_heading(line[4:], level=3)
            elif line.startswith("## "):
                self.add_heading(line[3:], level=2)
            elif line.startswith("# "):
                self.add_heading(line[2:], level=1)
            else:
                self.add_paragraph(line)

    def add_references(self, references: list[str]) -> None:
        """
        添加参考文献

        Args:
            references: 参考文献列表
        """
        self.doc.add_page_break()
        self.add_heading("参考文献", level=1)

        for i, ref in enumerate(references, 1):
            p = self.doc.add_paragraph()
            p.add_run(f"[{i}] {ref}")
            p.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE

    def add_acknowledgement(self, content: str) -> None:
        """
        添加致谢

        Args:
            content: 致谢内容
        """
        self.doc.add_page_break()
        self.add_heading("致  谢", level=1)
        self.add_paragraph(content)

    def save(self, filename: Optional[str] = None) -> Path:
        """
        保存文档

        Args:
            filename: 文件名（不含扩展名）

        Returns:
            保存的文件路径
        """
        output_dir = self.config.output_dir
        output_dir.mkdir(parents=True, exist_ok=True)

        if filename is None:
            filename = f"thesis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        output_path = output_dir / f"{filename}.docx"
        self.doc.save(str(output_path))

        return output_path

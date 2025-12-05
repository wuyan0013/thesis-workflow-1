# -*- coding: utf-8 -*-
"""
论文框架编辑器 - Gradio 可视化界面（简化版）
"""

import sys
import json
import tempfile
from pathlib import Path
from datetime import datetime

import gradio as gr

# 添加 src 到路径
sys.path.insert(0, str(Path(__file__).parent))

from src.workflow import ThesisWorkflow, ThesisConfig


# 默认章节配置
DEFAULT_CHAPTERS_JSON = json.dumps([
    {"title": "绪论", "requirements": "研究背景、目的与意义、国内外研究现状、研究方法", "word_count": 2000},
    {"title": "相关概念与理论基础", "requirements": "核心概念界定、理论基础和分析框架", "word_count": 2000},
    {"title": "现状分析", "requirements": "研究对象的发展现状、存在的问题", "word_count": 2500},
    {"title": "问题成因分析", "requirements": "问题产生的原因，多角度剖析", "word_count": 2000},
    {"title": "对策与建议", "requirements": "具体可行的解决对策和建议", "word_count": 2000},
    {"title": "结论", "requirements": "主要结论、研究局限性和未来方向", "word_count": 1000},
], ensure_ascii=False, indent=2)


def preview_config(major, topic, chapters_json):
    """预览配置"""
    try:
        chapters = json.loads(chapters_json) if chapters_json else []
        total_words = sum(ch.get("word_count", 0) for ch in chapters)
        return f"""
**专业**: {major or '未填写'}
**主题**: {topic or '未填写'}
**章节数**: {len(chapters)}
**目标总字数**: {total_words}
**预计生成时间**: 约 {len(chapters) * 2} 分钟

**章节列表**:
""" + "\n".join([f"- {ch['title']} ({ch['word_count']}字)" for ch in chapters])
    except:
        return "配置解析错误，请检查JSON格式"


def generate_thesis(major, topic, chapters_json, progress=gr.Progress()):
    """生成论文"""
    if not major or not major.strip():
        return None, "请填写论文专业！"

    if not topic or not topic.strip():
        return None, "请填写论文主题！"

    try:
        chapters = json.loads(chapters_json) if chapters_json else []
    except:
        return None, "章节配置JSON格式错误！"

    if not chapters:
        return None, "至少需要一个章节！"

    try:
        progress(0, desc="初始化...")

        config = ThesisConfig(
            title=topic.strip(),
            topic=topic.strip(),
            major=major.strip(),
            chapters=chapters
        )

        progress(0.1, desc="开始生成论文...")

        workflow = ThesisWorkflow()
        output_path = workflow.generate_thesis(config)

        progress(1.0, desc="完成！")

        return str(output_path), f"论文生成成功！\n文件: {output_path}"

    except Exception as e:
        return None, f"生成失败: {str(e)}"


def save_template(major, topic, chapters_json):
    """保存模板"""
    try:
        chapters = json.loads(chapters_json) if chapters_json else []
        template = {
            "major": major or "",
            "topic": topic or "",
            "chapters": chapters,
            "created_at": datetime.now().isoformat()
        }
        temp_file = tempfile.NamedTemporaryFile(
            mode='w', suffix='.json', delete=False, encoding='utf-8'
        )
        json.dump(template, temp_file, ensure_ascii=False, indent=2)
        temp_file.close()
        return temp_file.name
    except:
        return None


def load_template(file):
    """加载模板"""
    if file is None:
        return "", "", DEFAULT_CHAPTERS_JSON
    try:
        with open(file.name, 'r', encoding='utf-8') as f:
            template = json.load(f)
        major = template.get("major", "")
        topic = template.get("topic", "")
        chapters_json = json.dumps(template.get("chapters", []), ensure_ascii=False, indent=2)
        return major, topic, chapters_json
    except:
        return "", "", DEFAULT_CHAPTERS_JSON


# 创建界面
with gr.Blocks(title="论文框架编辑器") as demo:
    gr.Markdown("# 论文框架编辑器")
    gr.Markdown("编辑论文章节结构，一键生成符合国开大格式的完整论文")

    with gr.Row():
        major = gr.Textbox(label="专业", placeholder="如：行政管理")
        topic = gr.Textbox(label="论文主题", placeholder="如：乡村振兴背景下农村电商发展问题研究")

    gr.Markdown("### 章节配置 (JSON格式)")
    chapters_json = gr.Code(
        value=DEFAULT_CHAPTERS_JSON,
        language="json",
        label="章节配置",
        lines=15
    )

    with gr.Row():
        preview_btn = gr.Button("预览配置")
        generate_btn = gr.Button("生成论文", variant="primary")

    preview_output = gr.Markdown(label="配置预览")
    status_output = gr.Textbox(label="状态", interactive=False)
    file_output = gr.File(label="下载论文")

    gr.Markdown("---")
    gr.Markdown("### 模板管理")
    with gr.Row():
        save_btn = gr.Button("保存模板")
        template_file = gr.File(label="上传模板")
        load_btn = gr.Button("加载模板")

    save_output = gr.File(label="下载模板")

    # 事件绑定
    preview_btn.click(preview_config, [major, topic, chapters_json], preview_output)
    generate_btn.click(generate_thesis, [major, topic, chapters_json], [file_output, status_output])
    save_btn.click(save_template, [major, topic, chapters_json], save_output)
    load_btn.click(load_template, template_file, [major, topic, chapters_json])


if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=7860, inbrowser=True)

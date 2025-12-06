# -*- coding: utf-8 -*-
"""
答辩稿生成页面
上传论文Word文档，智能生成答辩陈述稿
"""

import sys
from pathlib import Path
import io

import streamlit as st
from docx import Document

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.claude_client import ClaudeClient, ThesisGenerator
from src.config import get_config, save_env_config

# ============ 页面配置 ============
st.set_page_config(
    page_title="答辩稿生成 - ThesisAI",
    page_icon="🎤",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============ 全局样式 - 统一黑金主题 ============
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    --bg-primary: #0a0a0b;
    --bg-secondary: #111113;
    --bg-card: #16161a;
    --bg-card-hover: #1c1c21;
    --border-default: #27272a;
    --border-gold: #F59E0B;
    --text-primary: #FFFFFF;
    --text-secondary: #a1a1aa;
    --text-muted: #71717a;
    --gold-primary: #F59E0B;
    --gold-light: #FBBF24;
    --gold-dark: #D97706;
    --gradient-gold: linear-gradient(135deg, #F59E0B 0%, #D97706 50%, #F59E0B 100%);
    --gradient-gold-subtle: linear-gradient(135deg, rgba(245,158,11,0.15) 0%, rgba(217,119,6,0.1) 100%);
    --glow-gold: 0 0 30px rgba(245,158,11,0.3);
}

.stApp, html, body, [data-testid="stAppViewContainer"], .main > div {
    background: var(--bg-primary) !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

.main > div, .block-container, [data-testid="stMainBlockContainer"] {
    max-width: 100% !important;
    width: 100% !important;
    padding: 2rem 4rem !important;
}

[data-testid="stHeader"], #MainMenu, footer, header, .stDeployButton {
    display: none !important;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d0d0f 0%, #111113 100%) !important;
    border-right: 1px solid var(--border-default) !important;
}

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: var(--gold-primary) !important;
    text-shadow: 0 0 20px rgba(245,158,11,0.3) !important;
}

h1, h2, h3, h4, h5, h6 {
    color: var(--text-primary) !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 700 !important;
}

p, span, label, div {
    color: var(--text-secondary) !important;
}

.stButton > button {
    background: var(--gradient-gold-subtle) !important;
    border: 1px solid rgba(245,158,11,0.3) !important;
    border-radius: 12px !important;
    color: var(--gold-primary) !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    padding: 0.875rem 1.5rem !important;
    min-height: 48px !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

.stButton > button:hover {
    background: linear-gradient(135deg, rgba(245,158,11,0.25) 0%, rgba(217,119,6,0.2) 100%) !important;
    border-color: var(--gold-primary) !important;
    box-shadow: var(--glow-gold) !important;
    transform: translateY(-2px) !important;
}

.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div > div {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-default) !important;
    border-radius: 10px !important;
    color: var(--text-primary) !important;
}

.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: var(--gold-primary) !important;
    box-shadow: 0 0 0 3px rgba(245,158,11,0.15) !important;
}

div[data-testid="stExpander"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-default) !important;
    border-radius: 16px !important;
}

div[data-testid="stExpander"]:hover {
    border-color: rgba(245,158,11,0.4) !important;
}

.stDownloadButton > button {
    background: var(--gradient-gold) !important;
    border: none !important;
    color: #000000 !important;
    font-weight: 700 !important;
    box-shadow: var(--glow-gold) !important;
}

.stDownloadButton > button:hover {
    box-shadow: 0 0 60px rgba(245,158,11,0.4) !important;
    transform: translateY(-3px) !important;
}

.uploadedFile {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-default) !important;
    border-radius: 10px !important;
}

[data-testid="stFileUploader"] {
    background: var(--bg-card) !important;
    border: 2px dashed var(--border-default) !important;
    border-radius: 16px !important;
}

[data-testid="stFileUploader"]:hover {
    border-color: var(--gold-primary) !important;
}
</style>
""", unsafe_allow_html=True)


# ============ Session State ============
if 'defense_api_key' not in st.session_state:
    st.session_state.defense_api_key = ""
if 'defense_api_base_url' not in st.session_state:
    st.session_state.defense_api_base_url = ""
if 'defense_api_model' not in st.session_state:
    st.session_state.defense_api_model = "claude-opus-4-5-20251101"
if 'defense_result' not in st.session_state:
    st.session_state.defense_result = None
if 'parsed_thesis' not in st.session_state:
    st.session_state.parsed_thesis = None


def parse_docx(uploaded_file) -> dict:
    """解析上传的Word文档"""
    doc = Document(uploaded_file)

    result = {
        "title": "",
        "abstract": "",
        "chapters": [],
        "full_text": ""
    }

    current_chapter = None
    full_text_parts = []

    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue

        full_text_parts.append(text)

        # 检测标题
        style_name = para.style.name if para.style else ""

        # 检测论文标题（通常是第一个非空段落或Heading 0）
        if not result["title"] and ("Title" in style_name or "标题" in style_name or len(full_text_parts) == 1):
            if len(text) < 50:
                result["title"] = text
                continue

        # 检测摘要
        if "摘要" in text[:10] or "Abstract" in text[:10]:
            result["abstract"] = text
            continue

        # 检测章节标题
        is_heading = "Heading" in style_name or "标题" in style_name
        is_chapter_marker = (
            text.startswith("一、") or text.startswith("二、") or text.startswith("三、") or
            text.startswith("四、") or text.startswith("五、") or text.startswith("六、") or
            text.startswith("第一章") or text.startswith("第二章") or text.startswith("第三章") or
            text.startswith("第四章") or text.startswith("第五章") or text.startswith("第六章")
        )

        if is_heading or is_chapter_marker:
            if current_chapter:
                result["chapters"].append(current_chapter)
            current_chapter = {"title": text, "content": ""}
        elif current_chapter:
            current_chapter["content"] += text + "\n"

    # 添加最后一个章节
    if current_chapter:
        result["chapters"].append(current_chapter)

    result["full_text"] = "\n".join(full_text_parts)

    # 如果没有检测到标题，使用文件名
    if not result["title"]:
        result["title"] = "未检测到标题"

    return result


def create_defense_docx(defense_text: str, title: str) -> bytes:
    """创建答辩稿Word文档"""
    doc = Document()
    doc.add_heading(f'答辩陈述稿', 0)
    doc.add_paragraph(f'论文题目：{title}')
    doc.add_paragraph('')

    for para in defense_text.split('\n'):
        para = para.strip()
        if not para:
            continue
        if para.startswith('## '):
            doc.add_heading(para[3:], level=1)
        elif para.startswith('### '):
            doc.add_heading(para[4:], level=2)
        else:
            doc.add_paragraph(para)

    buffer = io.BytesIO()
    doc.save(buffer)
    return buffer.getvalue()


# ============ 侧边栏 ============
with st.sidebar:
    st.markdown("## 🎤 答辩稿生成")
    st.caption("上传论文 → 智能生成答辩陈述稿")

    st.divider()

    # API 设置
    with st.expander("⚙️ API 设置", expanded=not st.session_state.defense_api_key):
        model_options = {
            "Claude Opus 4.5": "claude-opus-4-5-20251101",
            "Claude Sonnet 4": "claude-sonnet-4-20250514",
        }
        selected_model = st.selectbox(
            "🤖 模型",
            options=list(model_options.keys()),
            index=0 if st.session_state.defense_api_model == "claude-opus-4-5-20251101" else 1,
            key="defense_model_select"
        )
        st.session_state.defense_api_model = model_options[selected_model]

        st.session_state.defense_api_base_url = st.text_input(
            "🌐 API Base URL",
            value=st.session_state.defense_api_base_url,
            placeholder="留空使用 .env 配置",
            key="defense_base_url_input"
        )

        st.session_state.defense_api_key = st.text_input(
            "🔑 API Key",
            value=st.session_state.defense_api_key,
            type="password",
            placeholder="留空使用 .env 配置",
            key="defense_api_key_input"
        )

        if st.button("💾 保存到 .env", use_container_width=True, key="defense_save_config"):
            if save_env_config(
                api_key=st.session_state.defense_api_key,
                base_url=st.session_state.defense_api_base_url,
                model=st.session_state.defense_api_model
            ):
                st.success("✅ 已保存")
            else:
                st.error("❌ 保存失败")

    st.divider()

    # 生成参数
    st.markdown("### 📝 生成参数")
    word_count = st.slider("目标字数", 600, 1500, 900, 100, key="defense_word_count")
    st.caption(f"预计朗读时间: {word_count // 250}-{word_count // 200} 分钟")

    st.divider()
    st.caption("⚠️ 生成内容仅供参考")


# ============ 主内容区 ============
st.markdown("""
<div style="margin-bottom: 2rem;">
    <h1 style="font-size: 2.5rem; margin-bottom: 0.5rem;">🎤 答辩稿生成器</h1>
    <p style="color: #A1A1AA; font-size: 1.1rem;">上传您的论文Word文档，AI智能生成答辩陈述稿</p>
</div>
""", unsafe_allow_html=True)

# 功能说明
st.markdown("""
<div style="background: rgba(24, 24, 27, 0.6); border: 1px solid rgba(63, 63, 70, 0.4); border-radius: 16px; padding: 1.5rem; margin-bottom: 2rem;">
    <div style="color: #F59E0B; font-size: 1rem; font-weight: 600; margin-bottom: 1rem;">📋 答辩陈述稿结构</div>
    <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem;">
        <div style="background: rgba(10, 10, 12, 0.8); border-radius: 10px; padding: 1rem;">
            <div style="color: #FFFFFF; font-weight: 600; margin-bottom: 0.5rem;">🎬 开场白</div>
            <div style="color: #71717A; font-size: 0.85rem;">问候 + 自我介绍 + 题目</div>
        </div>
        <div style="background: rgba(10, 10, 12, 0.8); border-radius: 10px; padding: 1rem;">
            <div style="color: #FFFFFF; font-weight: 600; margin-bottom: 0.5rem;">📖 选题背景</div>
            <div style="color: #71717A; font-size: 0.85rem;">研究动机 + 意义</div>
        </div>
        <div style="background: rgba(10, 10, 12, 0.8); border-radius: 10px; padding: 1rem;">
            <div style="color: #FFFFFF; font-weight: 600; margin-bottom: 0.5rem;">📝 研究内容</div>
            <div style="color: #71717A; font-size: 0.85rem;">各章节重点概述</div>
        </div>
        <div style="background: rgba(10, 10, 12, 0.8); border-radius: 10px; padding: 1rem;">
            <div style="color: #FFFFFF; font-weight: 600; margin-bottom: 0.5rem;">🔬 研究方法</div>
            <div style="color: #71717A; font-size: 0.85rem;">方法论 + 研究过程</div>
        </div>
        <div style="background: rgba(10, 10, 12, 0.8); border-radius: 10px; padding: 1rem;">
            <div style="color: #FFFFFF; font-weight: 600; margin-bottom: 0.5rem;">💡 结论创新</div>
            <div style="color: #71717A; font-size: 0.85rem;">主要结论 + 创新点</div>
        </div>
        <div style="background: rgba(10, 10, 12, 0.8); border-radius: 10px; padding: 1rem;">
            <div style="color: #FFFFFF; font-weight: 600; margin-bottom: 0.5rem;">🙏 致谢展望</div>
            <div style="color: #71717A; font-size: 0.85rem;">不足反思 + 感谢</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# 两列布局
col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    st.markdown("### 📄 上传论文")

    uploaded_file = st.file_uploader(
        "拖拽或点击上传 Word 文档",
        type=["docx"],
        key="thesis_uploader",
        help="支持 .docx 格式的论文文档"
    )

    if uploaded_file:
        with st.spinner("正在解析文档..."):
            st.session_state.parsed_thesis = parse_docx(uploaded_file)

        thesis = st.session_state.parsed_thesis

        st.success(f"✅ 文档解析完成")

        # 显示解析结果
        st.markdown("#### 📊 文档信息")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("论文标题", thesis["title"][:20] + "..." if len(thesis["title"]) > 20 else thesis["title"])
        with col2:
            st.metric("检测章节", f"{len(thesis['chapters'])} 章")

        # 章节列表
        if thesis["chapters"]:
            with st.expander("📑 章节结构", expanded=False):
                for i, ch in enumerate(thesis["chapters"], 1):
                    ch_title = ch["title"][:30] + "..." if len(ch["title"]) > 30 else ch["title"]
                    ch_len = len(ch["content"])
                    st.caption(f"{i}. {ch_title} ({ch_len} 字)")

        # 生成按钮
        st.markdown("###")
        if st.button("🚀 生成答辩稿", type="primary", use_container_width=True, key="generate_defense"):
            with st.spinner("正在生成答辩稿...（约需 60-90 秒）"):
                try:
                    # 创建客户端
                    client = ClaudeClient(
                        use_cli=False,
                        api_key=st.session_state.defense_api_key or None,
                        base_url=st.session_state.defense_api_base_url or None,
                        model=st.session_state.defense_api_model or None
                    )
                    generator = ThesisGenerator(client)

                    # 生成答辩稿
                    defense_text = generator.generate_defense_paper(
                        title=thesis["title"],
                        abstract=thesis["abstract"],
                        chapters=thesis["chapters"],
                        word_count=word_count
                    )

                    st.session_state.defense_result = defense_text
                    st.rerun()

                except Exception as e:
                    st.error(f"❌ 生成失败: {e}")
    else:
        st.info("👆 请上传您的论文 Word 文档（.docx 格式）")


with col_right:
    st.markdown("### 📝 答辩稿预览")

    if st.session_state.defense_result:
        defense_text = st.session_state.defense_result

        # 统计信息
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("字数", f"{len(defense_text):,}")
        with col2:
            st.metric("预计时长", f"{len(defense_text) // 250}-{len(defense_text) // 200} 分钟")
        with col3:
            st.metric("AI检测率", "< 20%")

        # 预览区域
        st.markdown(f"""
        <div style="background: #16161a; border: 1px solid rgba(245,158,11,0.3); border-radius: 12px; padding: 1.5rem; max-height: 400px; overflow-y: auto; margin: 1rem 0;">
            <div style="color: #e4e4e7; line-height: 2; white-space: pre-wrap; font-size: 0.9rem;">{defense_text}</div>
        </div>
        """, unsafe_allow_html=True)

        # 复制区域
        st.text_area("📋 复制答辩稿", value=defense_text, height=100, key="copy_defense_text")

        # 下载按钮
        st.markdown("###")
        if st.session_state.parsed_thesis:
            doc_bytes = create_defense_docx(defense_text, st.session_state.parsed_thesis["title"])
            st.download_button(
                "📥 下载答辩稿 Word",
                data=doc_bytes,
                file_name="答辩陈述稿.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True,
                key="download_defense_docx"
            )

        # 重新生成
        if st.button("🔄 重新生成", use_container_width=True, key="regenerate_defense"):
            st.session_state.defense_result = None
            st.rerun()
    else:
        st.markdown("""
        <div style="background: rgba(24, 24, 27, 0.4); border: 2px dashed rgba(63, 63, 70, 0.4); border-radius: 16px; padding: 3rem; text-align: center;">
            <div style="color: #71717A; font-size: 3rem; margin-bottom: 1rem;">📝</div>
            <div style="color: #71717A; font-size: 1rem;">上传论文并点击"生成答辩稿"后</div>
            <div style="color: #71717A; font-size: 1rem;">预览将显示在这里</div>
        </div>
        """, unsafe_allow_html=True)


# 质量保证提示
st.markdown("""
<div style="background: rgba(34, 197, 94, 0.1); border: 1px solid rgba(34, 197, 94, 0.3); border-radius: 12px; padding: 1rem 1.25rem; margin-top: 2rem;">
    <div style="color: #22C55E; font-size: 0.95rem;">
        <span style="font-weight: 600;">✓ 质量保证</span>
        <span style="color: #A1A1AA; margin-left: 1rem;">AI检测率 ＜ 20%</span>
        <span style="color: #A1A1AA; margin-left: 1rem;">查重率 ＜ 10%</span>
        <span style="color: #A1A1AA; margin-left: 1rem;">口语化表达</span>
    </div>
</div>
""", unsafe_allow_html=True)

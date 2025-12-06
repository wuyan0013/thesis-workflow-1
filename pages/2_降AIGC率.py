# -*- coding: utf-8 -*-
"""
降AIGC率页面
通过人格化改写降低AI检测率
支持：Word文档上传处理 + 文段单独处理（双模式）
"""

import sys
from pathlib import Path
import io

import streamlit as st
from docx import Document

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.text_processor import TextProcessor, HumanizeStyle
from src.config import get_config

# ============ 页面配置 ============
st.set_page_config(
    page_title="降AIGC率 - ThesisAI",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============ 全局样式 ============
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    --bg-primary: #0a0a0b;
    --bg-secondary: #111113;
    --bg-card: #16161a;
    --border-default: #27272a;
    --gold-primary: #F59E0B;
    --gold-light: #FBBF24;
    --text-primary: #FFFFFF;
    --text-secondary: #a1a1aa;
    --text-muted: #71717a;
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

.stButton > button[kind="primary"],
.stButton > button[data-testid="stBaseButton-primary"] {
    background: var(--gradient-gold) !important;
    border: none !important;
    color: #000000 !important;
    font-weight: 700 !important;
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

[data-testid="stFileUploader"] {
    background: var(--bg-card) !important;
    border: 2px dashed var(--border-default) !important;
    border-radius: 16px !important;
}

[data-testid="stFileUploader"]:hover {
    border-color: var(--gold-primary) !important;
}

/* Tab 样式 */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background: var(--bg-card) !important;
    border-radius: 12px;
    padding: 4px;
}

.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--text-muted) !important;
    border-radius: 8px;
    padding: 8px 16px;
}

.stTabs [aria-selected="true"] {
    background: var(--gradient-gold-subtle) !important;
    color: var(--gold-primary) !important;
    border: 1px solid rgba(245,158,11,0.3) !important;
}

[data-testid="stMetric"] {
    background: linear-gradient(145deg, var(--bg-card) 0%, var(--bg-secondary) 100%) !important;
    border: 1px solid var(--border-default) !important;
    border-radius: 16px !important;
    padding: 1.5rem !important;
}

[data-testid="stMetricLabel"] {
    color: var(--text-muted) !important;
}

[data-testid="stMetricValue"] {
    color: var(--gold-primary) !important;
    text-shadow: 0 0 20px rgba(245,158,11,0.3) !important;
}
</style>
""", unsafe_allow_html=True)


# ============ Session State ============
if 'aigc_result' not in st.session_state:
    st.session_state.aigc_result = None
if 'aigc_doc_result' not in st.session_state:
    st.session_state.aigc_doc_result = None
if 'aigc_parsed_doc' not in st.session_state:
    st.session_state.aigc_parsed_doc = None


def parse_docx_for_humanize(uploaded_file) -> dict:
    """
    解析Word文档，提取可处理的段落
    严格保留：标题、摘要、目录、参考文献、章节标题
    仅处理：正文段落（>50字的普通段落）
    """
    doc = Document(uploaded_file)
    result = {
        "paragraphs": [],
        "processable_indices": [],
        "total_count": 0,
        "processable_count": 0
    }

    skip_keywords = [
        "摘要", "Abstract", "ABSTRACT",
        "目录", "目 录", "Contents",
        "参考文献", "参 考 文 献", "References",
        "致谢", "致 谢", "鸣谢",
        "附录", "附 录", "Appendix",
        "关键词", "Keywords"
    ]

    chapter_markers = [
        "一、", "二、", "三、", "四、", "五、", "六、", "七、", "八、", "九、", "十、",
        "（一）", "（二）", "（三）", "（四）", "（五）", "（六）", "（七）", "（八）",
        "1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9.",
        "第一章", "第二章", "第三章", "第四章", "第五章", "第六章",
        "绑论", "结论"
    ]

    in_references = False

    for idx, para in enumerate(doc.paragraphs):
        text = para.text.strip()
        style_name = para.style.name if para.style else ""

        para_info = {
            "index": idx,
            "text": text,
            "style": style_name,
            "processable": False,
            "skip_reason": ""
        }

        if not text:
            para_info["skip_reason"] = "空段落"
            result["paragraphs"].append(para_info)
            continue

        if "参考文献" in text or "References" in text:
            in_references = True

        if in_references:
            para_info["skip_reason"] = "参考文献区域"
            result["paragraphs"].append(para_info)
            continue

        if "Heading" in style_name or "标题" in style_name:
            para_info["skip_reason"] = "标题样式"
            result["paragraphs"].append(para_info)
            continue

        if any(text.startswith(kw) or kw in text[:20] for kw in skip_keywords):
            para_info["skip_reason"] = "特殊区域"
            result["paragraphs"].append(para_info)
            continue

        if any(text.startswith(marker) for marker in chapter_markers):
            para_info["skip_reason"] = "章节标题"
            result["paragraphs"].append(para_info)
            continue

        if len(text) < 50:
            para_info["skip_reason"] = "段落过短"
            result["paragraphs"].append(para_info)
            continue

        para_info["processable"] = True
        result["processable_indices"].append(idx)
        result["paragraphs"].append(para_info)

    result["total_count"] = len(doc.paragraphs)
    result["processable_count"] = len(result["processable_indices"])
    return result


def create_processed_docx(original_file, parsed_doc: dict, processed_texts: dict) -> bytes:
    """创建处理后的Word文档，仅替换正文段落，保留原格式"""
    original_file.seek(0)
    doc = Document(original_file)

    for idx, new_text in processed_texts.items():
        if idx < len(doc.paragraphs):
            para = doc.paragraphs[idx]
            if para.runs:
                para.runs[0].text = new_text
                for run in para.runs[1:]:
                    run.text = ""
            else:
                para.text = new_text

    buffer = io.BytesIO()
    doc.save(buffer)
    return buffer.getvalue()


def get_processor():
    """获取文本处理器实例（使用SDK模式+.env配置）"""
    config = get_config()
    return TextProcessor(
        use_cli=False,
        api_key=config.claude_api_key,
        base_url=config.claude_base_url,
        model=config.claude_model
    )


# ============ 侧边栏 ============
with st.sidebar:
    st.markdown("## 🤖 降AIGC率")
    st.caption("人格化改写 · 通过AI检测")

    st.divider()

    st.markdown("### ⚙️ 人格化设置")
    style_options = {
        "学术风格": HumanizeStyle.ACADEMIC,
        "自然风格": HumanizeStyle.NATURAL,
        "混合风格": HumanizeStyle.MIXED,
    }
    selected_style = st.selectbox(
        "人格化风格",
        options=list(style_options.keys()),
        index=0,
        key="style_select",
        help="学术风格：保持专业性\n自然风格：偏口语化\n混合风格：学术为主，适度口语"
    )
    style = style_options[selected_style]

    st.markdown("""
    <div style="background: rgba(24, 24, 27, 0.6); border-radius: 10px; padding: 1rem; margin-top: 1rem;">
        <div style="color: #71717A; font-size: 0.85rem;">
            <b>学术风格</b>：添加学术谦虚表达<br>
            <b>自然风格</b>：引入口语化表达<br>
            <b>混合风格</b>：学术为主，适度自然
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    preserve_terms_input = st.text_input(
        "保留术语（用逗号分隔）",
        placeholder="例：机器学习,深度神经网络",
        help="这些专业术语在改写时会被保留",
        key="preserve_terms"
    )
    preserve_terms = [t.strip() for t in preserve_terms_input.split(",") if t.strip()] if preserve_terms_input else None

    st.divider()
    st.caption("⚠️ 生成内容仅供参考")


# ============ 主内容区 ============
st.markdown("""
<div style="margin-bottom: 2rem;">
    <h1 style="font-size: 2.5rem; margin-bottom: 0.5rem;">🤖 降AIGC率</h1>
    <p style="color: #A1A1AA; font-size: 1.1rem;">通过人格化改写降低AI检测率，适用于ZeroGPT、GPTZero等检测工具</p>
</div>
""", unsafe_allow_html=True)

# ============ 双模式标签页 ============
tab_doc, tab_text = st.tabs(["📄 Word文档处理", "📝 文段单独处理"])

# ============ Tab 1: Word文档处理 ============
with tab_doc:
    st.markdown("""
    <div style="background: rgba(245,158,11,0.1); border: 1px solid rgba(245,158,11,0.3); border-radius: 12px; padding: 1rem; margin-bottom: 1.5rem;">
        <div style="color: #F59E0B; font-weight: 600;">📋 处理规则</div>
        <div style="color: #A1A1AA; font-size: 0.9rem; margin-top: 0.5rem;">
            仅处理正文段落（>50字），严格保留：标题、摘要、目录、参考文献、章节标题、致谢、附录
        </div>
    </div>
    """, unsafe_allow_html=True)

    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("### 📄 上传论文")
        uploaded_file = st.file_uploader(
            "拖拽或点击上传 Word 文档",
            type=["docx"],
            key="aigc_uploader",
            help="支持 .docx 格式的论文文档"
        )

        if uploaded_file:
            with st.spinner("正在解析文档..."):
                st.session_state.aigc_parsed_doc = parse_docx_for_humanize(uploaded_file)

            parsed = st.session_state.aigc_parsed_doc
            st.success("✅ 文档解析完成")

            col1, col2 = st.columns(2)
            with col1:
                st.metric("总段落数", parsed["total_count"])
            with col2:
                st.metric("可处理段落", parsed["processable_count"])

            with st.expander("📑 段落详情", expanded=False):
                for p in parsed["paragraphs"][:20]:
                    if p["text"]:
                        status = "✅ 可处理" if p["processable"] else f"⏭️ 跳过({p['skip_reason']})"
                        st.caption(f"{status}: {p['text'][:50]}...")

            st.markdown("###")
            if st.button("🚀 开始人格化处理", type="primary", use_container_width=True, key="process_aigc_doc"):
                processor = get_processor()
                processed_texts = {}
                progress_bar = st.progress(0, text="准备处理...")

                processable = [(i, p) for i, p in enumerate(parsed["paragraphs"]) if p["processable"]]
                total = len(processable)

                for idx, (para_idx, para_info) in enumerate(processable):
                    progress_bar.progress((idx + 1) / total, text=f"处理中 {idx + 1}/{total}")
                    result = processor.reduce_aigc_rate(para_info["text"], style=style, preserve_terms=preserve_terms)
                    processed_texts[para_info["index"]] = result.processed

                st.session_state.aigc_doc_result = processed_texts
                progress_bar.progress(1.0, text="✅ 处理完成!")
                st.rerun()
        else:
            st.info("👆 请上传您的论文 Word 文档（.docx 格式）")

    with col_right:
        st.markdown("### 📥 下载结果")

        if st.session_state.aigc_doc_result and uploaded_file:
            st.success(f"✅ 已处理 {len(st.session_state.aigc_doc_result)} 个段落")

            doc_bytes = create_processed_docx(
                uploaded_file,
                st.session_state.aigc_parsed_doc,
                st.session_state.aigc_doc_result
            )

            st.download_button(
                "📥 下载人格化后的论文",
                data=doc_bytes,
                file_name="论文_人格化版.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True,
                key="download_aigc_doc"
            )

            if st.button("🔄 重新处理", use_container_width=True, key="reset_aigc_doc"):
                st.session_state.aigc_doc_result = None
                st.session_state.aigc_parsed_doc = None
                st.rerun()
        else:
            st.markdown("""
            <div style="background: rgba(24, 24, 27, 0.4); border: 2px dashed rgba(63, 63, 70, 0.4); border-radius: 16px; padding: 3rem; text-align: center;">
                <div style="color: #71717A; font-size: 3rem; margin-bottom: 1rem;">📥</div>
                <div style="color: #71717A;">处理完成后可在此下载</div>
            </div>
            """, unsafe_allow_html=True)

# ============ Tab 2: 文段单独处理 ============
with tab_text:
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("### 📝 输入原文")
        original_text = st.text_area(
            "粘贴需要人格化的文本",
            height=300,
            placeholder="在此粘贴需要降低AIGC检测率的论文段落...",
            key="aigc_text_input"
        )

        if original_text:
            st.caption(f"当前字数: {len(original_text)}")

        if st.button("🚀 开始人格化", type="primary", disabled=not original_text, use_container_width=True, key="process_aigc_text"):
            with st.spinner("正在智能改写..."):
                processor = get_processor()
                result = processor.reduce_aigc_rate(original_text, style=style, preserve_terms=preserve_terms)
                st.session_state.aigc_result = result
                st.rerun()

    with col_right:
        st.markdown("### 📄 处理结果")

        if st.session_state.aigc_result:
            result = st.session_state.aigc_result

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("原文字数", result.details.get('original_length', len(result.original)))
            with col2:
                st.metric("处理后字数", result.details.get('processed_length', len(result.processed)))
            with col3:
                st.metric("人格化风格", selected_style)

            st.text_area(
                "人格化后的文本",
                value=result.processed,
                height=300,
                key="aigc_result_output"
            )

            if st.button("🔄 重新处理", use_container_width=True, key="reset_aigc_text"):
                st.session_state.aigc_result = None
                st.rerun()
        else:
            st.markdown("""
            <div style="background: rgba(24, 24, 27, 0.4); border: 2px dashed rgba(63, 63, 70, 0.4); border-radius: 16px; padding: 3rem; text-align: center;">
                <div style="color: #71717A; font-size: 3rem; margin-bottom: 1rem;">📄</div>
                <div style="color: #71717A;">处理结果将显示在这里</div>
            </div>
            """, unsafe_allow_html=True)

# 质量提示
st.markdown("""
<div style="background: rgba(34, 197, 94, 0.1); border: 1px solid rgba(34, 197, 94, 0.3); border-radius: 12px; padding: 1rem 1.25rem; margin-top: 2rem;">
    <div style="color: #22C55E; font-size: 0.95rem;">
        <span style="font-weight: 600;">✓ 质量保证</span>
        <span style="color: #A1A1AA; margin-left: 1rem;">添加人类写作特征</span>
        <span style="color: #A1A1AA; margin-left: 1rem;">学术谦虚表达</span>
        <span style="color: #A1A1AA; margin-left: 1rem;">自然语言过渡</span>
        <span style="color: #A1A1AA; margin-left: 1rem;">AI检测率 ＜ 20%</span>
    </div>
</div>
""", unsafe_allow_html=True)

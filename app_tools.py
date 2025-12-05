# -*- coding: utf-8 -*-
"""
论文工具箱 - Streamlit 应用
提供论文降重和降AIGC率功能
"""

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent))

from src.text_processor import TextProcessor, RewriteIntensity, HumanizeStyle

# ============ 页面配置 ============
st.set_page_config(
    page_title="ThesisAI 工具箱",
    page_icon="🛠️",
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
    padding: 0.75rem 1rem !important;
}

.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: var(--gold-primary) !important;
    box-shadow: 0 0 0 3px rgba(245,158,11,0.15), var(--glow-gold) !important;
}

div[data-testid="stExpander"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-default) !important;
    border-radius: 16px !important;
    overflow: hidden !important;
}

div[data-testid="stExpander"]:hover {
    border-color: rgba(245,158,11,0.4) !important;
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

div[data-testid="stAlert"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-default) !important;
    border-radius: 12px !important;
    border-left: 4px solid var(--gold-primary) !important;
}

.stProgress > div > div > div {
    background: var(--gradient-gold) !important;
}

.stProgress > div > div {
    background: var(--bg-card) !important;
}

hr {
    border: none !important;
    height: 1px !important;
    background: linear-gradient(90deg, transparent, var(--border-default) 20%, var(--border-default) 80%, transparent) !important;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 8px !important;
    background: transparent !important;
}

.stTabs [data-baseweb="tab"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-default) !important;
    border-radius: 10px !important;
    color: var(--text-secondary) !important;
    padding: 0.75rem 1.5rem !important;
}

.stTabs [aria-selected="true"] {
    background: var(--gradient-gold-subtle) !important;
    border-color: var(--gold-primary) !important;
    color: var(--gold-primary) !important;
}

.result-box {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-default) !important;
    border-radius: 12px !important;
    padding: 1.5rem !important;
    margin: 1rem 0 !important;
}

.comparison-header {
    display: flex !important;
    justify-content: space-between !important;
    align-items: center !important;
    margin-bottom: 1rem !important;
}

.stat-badge {
    background: rgba(245, 158, 11, 0.1) !important;
    border: 1px solid rgba(245, 158, 11, 0.3) !important;
    border-radius: 8px !important;
    padding: 4px 12px !important;
    color: var(--gold-primary) !important;
    font-size: 0.85rem !important;
}
</style>
""", unsafe_allow_html=True)

# ============ Session State ============
if 'processor' not in st.session_state:
    st.session_state.processor = None
if 'result' not in st.session_state:
    st.session_state.result = None
if 'processing' not in st.session_state:
    st.session_state.processing = False


def get_processor():
    """获取文本处理器实例"""
    if st.session_state.processor is None:
        st.session_state.processor = TextProcessor()
    return st.session_state.processor


# ============ 侧边栏 ============
with st.sidebar:
    st.markdown("## 🛠️ ThesisAI 工具箱")
    st.caption("v1.0 · 论文智能处理")

    st.divider()

    st.markdown("### 📋 功能介绍")
    st.markdown("""
    **论文降重**
    - 降低知网、维普、万方查重率
    - 同义词替换 + 句式重组
    - 保持原文学术性

    **降AIGC率**
    - 通过 ZeroGPT、GPTZero 检测
    - 人格化改写
    - 增加人类写作特征
    """)

    st.divider()

    st.markdown("### ⚙️ API 状态")
    try:
        processor = get_processor()
        st.success("✓ Claude API 已就绪")
    except Exception as e:
        st.error(f"✗ API 连接失败: {e}")

    st.divider()

    # 返回主应用链接
    st.markdown("### 🔗 快捷链接")
    st.markdown("[📄 返回论文生成器](http://localhost:8501)")

    st.divider()
    st.caption("⚠️ 处理结果仅供参考")


# ============ 主内容区 ============

# 标题区域
st.markdown("""<div style="margin: 1rem 0 2rem 0;">
    <span style="background: rgba(245,158,11,0.12); border: 1px solid rgba(245,158,11,0.25); border-radius: 24px; padding: 10px 24px; color: #F59E0B; font-size: 1rem; font-weight: 500;">🛠️ 论文工具箱</span>
    <h1 style="font-size: 2.5rem; font-weight: 800; color: #FFFFFF; margin: 1.5rem 0 0.5rem 0;">智能论文优化工具</h1>
    <p style="color: #9CA3AF; font-size: 1.1rem; margin: 0;">基于 Claude API，提供<span style="color: #F59E0B; font-weight: 600;">论文降重</span>和<span style="color: #F59E0B; font-weight: 600;">降AIGC率</span>功能</p>
</div>""", unsafe_allow_html=True)

# 功能选项卡
tab1, tab2 = st.tabs(["📉 论文降重", "🤖 降AIGC率"])

# ============ 论文降重 Tab ============
with tab1:
    st.markdown("### 📉 论文降重")
    st.markdown("通过智能改写降低论文查重率，适用于知网、维普、万方等检测系统")

    col1, col2 = st.columns([2, 1])

    with col1:
        plagiarism_text = st.text_area(
            "输入需要降重的文本",
            height=300,
            placeholder="请粘贴需要降重的论文段落...\n\n支持多段落处理，每个段落会单独进行优化。",
            key="plagiarism_input"
        )

    with col2:
        st.markdown("#### ⚙️ 降重设置")

        intensity = st.selectbox(
            "改写强度",
            options=["轻度", "中度", "重度"],
            index=1,
            help="轻度：保持原意，微调表达\n中度：同义替换+句式重组\n重度：大幅改写，保留核心观点"
        )

        intensity_map = {
            "轻度": RewriteIntensity.LIGHT,
            "中度": RewriteIntensity.MEDIUM,
            "重度": RewriteIntensity.HEAVY
        }

        preserve_terms_input = st.text_input(
            "保留术语（用逗号分隔）",
            placeholder="例：乡村振兴,基层治理,公共服务",
            help="这些专业术语在改写时会被保留"
        )

        preserve_terms = [t.strip() for t in preserve_terms_input.split(",") if t.strip()] if preserve_terms_input else None

        st.markdown("---")

        st.markdown("#### 📊 预计效果")
        if intensity == "轻度":
            st.metric("预计降重效果", "10-20%")
            st.caption("适合已经较低的查重率")
        elif intensity == "中度":
            st.metric("预计降重效果", "20-40%")
            st.caption("适合一般查重率")
        else:
            st.metric("预计降重效果", "40-60%")
            st.caption("适合较高查重率")

    if st.button("🚀 开始降重", type="primary", use_container_width=True, key="btn_plagiarism"):
        if plagiarism_text.strip():
            with st.spinner("正在处理中，请稍候...（约需30-60秒）"):
                try:
                    processor = get_processor()
                    result = processor.reduce_plagiarism(
                        plagiarism_text,
                        intensity=intensity_map[intensity],
                        preserve_terms=preserve_terms
                    )
                    st.session_state.result = result
                    st.session_state.result_type = "plagiarism"
                except Exception as e:
                    st.error(f"处理失败: {e}")
        else:
            st.warning("请输入需要降重的文本")

    # 显示结果
    if st.session_state.result and st.session_state.get("result_type") == "plagiarism":
        result = st.session_state.result

        st.markdown("### 📋 处理结果")

        # 统计信息
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("原文字数", f"{result.details.get('original_length', 0)} 字")
        with col2:
            st.metric("处理后字数", f"{result.details.get('processed_length', 0)} 字")
        with col3:
            change_rate = abs(result.details.get('processed_length', 0) - result.details.get('original_length', 0)) / max(result.details.get('original_length', 1), 1) * 100
            st.metric("变化率", f"{change_rate:.1f}%")

        # 对比展示
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 📝 原文")
            st.markdown(f"""<div style="background: #16161a; border: 1px solid #27272a; border-radius: 12px; padding: 1rem; max-height: 400px; overflow-y: auto;">
                <p style="color: #a1a1aa; line-height: 1.8; white-space: pre-wrap;">{result.original}</p>
            </div>""", unsafe_allow_html=True)

        with col2:
            st.markdown("#### ✨ 降重后")
            st.markdown(f"""<div style="background: #16161a; border: 1px solid rgba(245,158,11,0.3); border-radius: 12px; padding: 1rem; max-height: 400px; overflow-y: auto;">
                <p style="color: #e4e4e7; line-height: 1.8; white-space: pre-wrap;">{result.processed}</p>
            </div>""", unsafe_allow_html=True)

        # 复制按钮
        st.text_area("复制结果", value=result.processed, height=100, key="copy_plagiarism")


# ============ 降AIGC率 Tab ============
with tab2:
    st.markdown("### 🤖 降AIGC率")
    st.markdown("通过人格化改写降低AI检测率，适用于 ZeroGPT、GPTZero 等检测工具")

    col1, col2 = st.columns([2, 1])

    with col1:
        aigc_text = st.text_area(
            "输入需要处理的文本",
            height=300,
            placeholder="请粘贴需要降低AIGC检测率的论文段落...\n\n本工具会增加人类写作特征，使文本更像人类撰写。",
            key="aigc_input"
        )

    with col2:
        st.markdown("#### ⚙️ 人格化设置")

        style = st.selectbox(
            "人格化风格",
            options=["学术风格", "自然风格", "混合风格"],
            index=0,
            help="学术风格：保持专业性\n自然风格：偏口语化\n混合风格：学术为主，适度口语"
        )

        style_map = {
            "学术风格": HumanizeStyle.ACADEMIC,
            "自然风格": HumanizeStyle.NATURAL,
            "混合风格": HumanizeStyle.MIXED
        }

        aigc_preserve_terms_input = st.text_input(
            "保留术语（用逗号分隔）",
            placeholder="例：机器学习,深度神经网络",
            help="这些专业术语在改写时会被保留",
            key="aigc_terms"
        )

        aigc_preserve_terms = [t.strip() for t in aigc_preserve_terms_input.split(",") if t.strip()] if aigc_preserve_terms_input else None

        st.markdown("---")

        st.markdown("#### 📊 人格化策略")
        if style == "学术风格":
            st.info("✓ 添加学术谦虚表达\n✓ 使用学术过渡词\n✓ 保持专业术语")
        elif style == "自然风格":
            st.info("✓ 引入口语化表达\n✓ 增加个人视角\n✓ 使用灵活句式")
        else:
            st.info("✓ 学术风格为主\n✓ 适度自然表达\n✓ 平衡专业与可读")

    if st.button("🚀 开始处理", type="primary", use_container_width=True, key="btn_aigc"):
        if aigc_text.strip():
            with st.spinner("正在处理中，请稍候...（约需30-60秒）"):
                try:
                    processor = get_processor()
                    result = processor.reduce_aigc_rate(
                        aigc_text,
                        style=style_map[style],
                        preserve_terms=aigc_preserve_terms
                    )
                    st.session_state.result = result
                    st.session_state.result_type = "aigc"
                except Exception as e:
                    st.error(f"处理失败: {e}")
        else:
            st.warning("请输入需要处理的文本")

    # 显示结果
    if st.session_state.result and st.session_state.get("result_type") == "aigc":
        result = st.session_state.result

        st.markdown("### 📋 处理结果")

        # 统计信息
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("原文字数", f"{result.details.get('original_length', 0)} 字")
        with col2:
            st.metric("处理后字数", f"{result.details.get('processed_length', 0)} 字")
        with col3:
            st.metric("人格化风格", result.details.get('style', 'academic'))

        # 对比展示
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 📝 原文")
            st.markdown(f"""<div style="background: #16161a; border: 1px solid #27272a; border-radius: 12px; padding: 1rem; max-height: 400px; overflow-y: auto;">
                <p style="color: #a1a1aa; line-height: 1.8; white-space: pre-wrap;">{result.original}</p>
            </div>""", unsafe_allow_html=True)

        with col2:
            st.markdown("#### ✨ 人格化后")
            st.markdown(f"""<div style="background: #16161a; border: 1px solid rgba(245,158,11,0.3); border-radius: 12px; padding: 1rem; max-height: 400px; overflow-y: auto;">
                <p style="color: #e4e4e7; line-height: 1.8; white-space: pre-wrap;">{result.processed}</p>
            </div>""", unsafe_allow_html=True)

        # 复制按钮
        st.text_area("复制结果", value=result.processed, height=100, key="copy_aigc")


# ============ 底部信息 ============
st.markdown("---")
st.markdown("""<div style="display: flex; justify-content: space-between; padding: 1rem 0;">
    <span style="color: #52525B; font-size: 0.85rem;">⚠️ 处理结果仅供参考，请在提交前进行人工审核和查重检测</span>
    <span style="color: #52525B; font-size: 0.85rem;">ThesisAI 工具箱 v1.0 · Powered by Claude API</span>
</div>""", unsafe_allow_html=True)

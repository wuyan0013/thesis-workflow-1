# -*- coding: utf-8 -*-
"""
广西国开大论文生成器 - Streamlit GUI v8.0
High-end SaaS · Dark Mode · Rendered Visual Cards · No HTML Tags Visible
"""

import sys
from pathlib import Path

# 确保在导入其他模块前加载 .env
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent / ".env", override=True)

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent))

from src.workflow import ThesisWorkflow, ThesisConfig
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
import io

# ============ 页面配置 ============
st.set_page_config(
    page_title="ThesisAI Pro",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============ 专业配置 ============
MAJORS = {
    "行政管理": {"code": "PA", "icon": "⚖️", "color": "#FF9500", "tags": ["乡村振兴", "政务服务", "绩效评估"]},
    "工商管理": {"code": "BA", "icon": "💼", "color": "#FF9500", "tags": ["数字化转型", "品牌建设", "跨境电商"]},
    "汉语言文学": {"code": "CL", "icon": "📚", "color": "#FF9500", "tags": ["桂剧", "刘三姐", "壮族文化"]},
    "小学教育": {"code": "PE", "icon": "🎓", "color": "#FF9500", "tags": ["留守儿童", "双语教育", "乡村教师"]},
}

DEFAULT_CHAPTERS = [
    {"title": "绪论", "requirements": "研究背景、目的与意义、国内外研究现状、研究方法", "word_count": 2000},
    {"title": "相关概念与理论基础", "requirements": "核心概念界定、理论基础和分析框架", "word_count": 2000},
    {"title": "现状分析", "requirements": "研究对象的发展现状、取得的成效", "word_count": 2500},
    {"title": "存在问题及原因分析", "requirements": "存在的主要问题、问题成因的多角度剖析", "word_count": 2500},
    {"title": "对策与建议", "requirements": "具体可行的解决对策和政策建议", "word_count": 2000},
    {"title": "结论", "requirements": "总结研究主要结论，指出研究局限性和未来研究方向", "word_count": 1000},
]

# ============ 全局样式 - 统一黑金主题 v9.0 ============
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

/* ===== 根变量定义 ===== */
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
    --glow-gold-strong: 0 0 60px rgba(245,158,11,0.4), 0 0 100px rgba(245,158,11,0.2);
}

/* ===== 全局背景 ===== */
.stApp, html, body, [data-testid="stAppViewContainer"], .main > div {
    background: var(--bg-primary) !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}

/* ===== 布局 ===== */
.main > div, .block-container, [data-testid="stMainBlockContainer"] {
    max-width: 100% !important;
    width: 100% !important;
    padding: 2rem 4rem !important;
}

[data-testid="stMainBlockContainer"] {
    display: flex !important;
    flex-direction: column !important;
    min-height: calc(100vh - 2rem) !important;
    gap: 0.5rem !important;
}

/* ===== 隐藏默认UI ===== */
[data-testid="stHeader"], #MainMenu, footer, header, .stDeployButton {
    display: none !important;
}

/* ===== 侧边栏 - 黑金主题 ===== */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d0d0f 0%, #111113 100%) !important;
    border-right: 1px solid var(--border-default) !important;
}

section[data-testid="stSidebar"] > div {
    background: transparent !important;
}

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: var(--gold-primary) !important;
    text-shadow: 0 0 20px rgba(245,158,11,0.3) !important;
}

/* ===== 文本颜色 ===== */
h1, h2, h3, h4, h5, h6 {
    color: var(--text-primary) !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 700 !important;
}

p, span, label, div {
    color: var(--text-secondary) !important;
}

strong, b {
    color: var(--text-primary) !important;
}

a {
    color: var(--gold-primary) !important;
    text-decoration: none !important;
}

a:hover {
    color: var(--gold-light) !important;
    text-shadow: var(--glow-gold) !important;
}

/* ===== 按钮 - 统一黑金风格 ===== */
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
    box-shadow: 0 2px 8px rgba(0,0,0,0.3) !important;
}

.stButton > button:hover {
    background: linear-gradient(135deg, rgba(245,158,11,0.25) 0%, rgba(217,119,6,0.2) 100%) !important;
    border-color: var(--gold-primary) !important;
    color: var(--gold-light) !important;
    box-shadow: var(--glow-gold), 0 4px 16px rgba(0,0,0,0.4) !important;
    transform: translateY(-2px) !important;
}

.stButton > button:active {
    transform: translateY(0) !important;
}

/* 主要按钮 - 金色填充 */
.stButton > button[kind="primary"],
.stButton > button[data-testid="stBaseButton-primary"] {
    background: var(--gradient-gold) !important;
    border: none !important;
    color: #000000 !important;
    font-weight: 700 !important;
    box-shadow: var(--glow-gold) !important;
}

.stButton > button[kind="primary"]:hover,
.stButton > button[data-testid="stBaseButton-primary"]:hover {
    background: linear-gradient(135deg, #FBBF24 0%, #F59E0B 50%, #FBBF24 100%) !important;
    box-shadow: var(--glow-gold-strong) !important;
    transform: translateY(-3px) !important;
}

/* 侧边栏按钮 */
section[data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    border: 1px solid var(--border-default) !important;
    color: var(--text-muted) !important;
    min-height: 40px !important;
    padding: 0.5rem 1rem !important;
}

section[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(245,158,11,0.1) !important;
    border-color: var(--gold-primary) !important;
    color: var(--gold-primary) !important;
    box-shadow: 0 0 20px rgba(245,158,11,0.2) !important;
    transform: none !important;
}

/* ===== 输入框 - 黑金边框 ===== */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div > div,
.stNumberInput > div > div > input {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-default) !important;
    border-radius: 10px !important;
    color: var(--text-primary) !important;
    padding: 0.75rem 1rem !important;
    transition: all 0.3s ease !important;
}

.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus,
.stNumberInput > div > div > input:focus {
    border-color: var(--gold-primary) !important;
    box-shadow: 0 0 0 3px rgba(245,158,11,0.15), var(--glow-gold) !important;
    outline: none !important;
}

.stTextInput > div > div > input:hover,
.stTextArea > div > div > textarea:hover,
.stNumberInput > div > div > input:hover {
    border-color: rgba(245,158,11,0.5) !important;
}

.stTextInput > div > div > input::placeholder,
.stTextArea > div > div > textarea::placeholder {
    color: var(--text-muted) !important;
}

/* ===== 展开面板 - 黑金卡片 ===== */
div[data-testid="stExpander"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-default) !important;
    border-radius: 16px !important;
    overflow: hidden !important;
    transition: all 0.3s ease !important;
    margin-bottom: 0.75rem !important;
}

div[data-testid="stExpander"]:hover {
    border-color: rgba(245,158,11,0.4) !important;
    box-shadow: 0 0 25px rgba(245,158,11,0.1), 0 4px 20px rgba(0,0,0,0.3) !important;
}

div[data-testid="stExpander"] summary {
    color: var(--text-primary) !important;
    font-weight: 600 !important;
    padding: 1rem 1.25rem !important;
    background: linear-gradient(90deg, rgba(245,158,11,0.05) 0%, transparent 100%) !important;
}

div[data-testid="stExpander"] summary:hover {
    background: linear-gradient(90deg, rgba(245,158,11,0.1) 0%, transparent 100%) !important;
}

div[data-testid="stExpander"] > div > div {
    background: var(--bg-card) !important;
    padding: 0 1.25rem 1.25rem 1.25rem !important;
}

/* ===== 指标卡片 - 黑金渐变 ===== */
[data-testid="stMetric"] {
    background: linear-gradient(145deg, var(--bg-card) 0%, var(--bg-secondary) 100%) !important;
    border: 1px solid var(--border-default) !important;
    border-radius: 16px !important;
    padding: 1.5rem !important;
    transition: all 0.3s ease !important;
}

[data-testid="stMetric"]:hover {
    border-color: rgba(245,158,11,0.4) !important;
    box-shadow: 0 0 30px rgba(245,158,11,0.15) !important;
}

[data-testid="stMetricLabel"] {
    color: var(--text-muted) !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.5px !important;
}

[data-testid="stMetricValue"] {
    color: var(--gold-primary) !important;
    font-size: 1.75rem !important;
    font-weight: 700 !important;
    text-shadow: 0 0 20px rgba(245,158,11,0.3) !important;
}

[data-testid="stMetricDelta"] {
    color: #22C55E !important;
}

/* ===== 提示框 - 黑金边框 ===== */
div[data-testid="stAlert"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-default) !important;
    border-radius: 12px !important;
    border-left: 4px solid var(--gold-primary) !important;
}

div[data-testid="stAlert"] > div {
    color: var(--text-secondary) !important;
}

/* 成功提示 */
.stSuccess {
    border-left-color: #22C55E !important;
}

/* 警告提示 */
.stWarning {
    border-left-color: var(--gold-primary) !important;
}

/* 错误提示 */
.stError {
    border-left-color: #EF4444 !important;
}

/* ===== 进度条 - 金色渐变 ===== */
.stProgress > div > div > div {
    background: var(--gradient-gold) !important;
    box-shadow: 0 0 10px rgba(245,158,11,0.5) !important;
}

.stProgress > div > div {
    background: var(--bg-card) !important;
    border-radius: 10px !important;
}

/* ===== 分割线 ===== */
hr {
    border: none !important;
    height: 1px !important;
    background: linear-gradient(90deg, transparent, var(--border-default) 20%, var(--border-default) 80%, transparent) !important;
    margin: 1.5rem 0 !important;
}

/* ===== 下载按钮特殊样式 ===== */
.stDownloadButton > button {
    background: var(--gradient-gold) !important;
    border: none !important;
    color: #000000 !important;
    font-weight: 700 !important;
    padding: 1rem 2rem !important;
    font-size: 1.1rem !important;
    box-shadow: var(--glow-gold) !important;
}

.stDownloadButton > button:hover {
    box-shadow: var(--glow-gold-strong) !important;
    transform: translateY(-3px) !important;
}

/* ===== 选题卡片 ===== */
.topic-card {
    background: var(--bg-card) !important;
    border: 1px solid var(--border-default) !important;
    border-radius: 12px !important;
    padding: 1rem 1.25rem !important;
    margin-bottom: 0.5rem !important;
    transition: all 0.3s ease !important;
}

.topic-card:hover {
    border-color: var(--gold-primary) !important;
    background: var(--bg-card-hover) !important;
    box-shadow: var(--glow-gold), 0 4px 16px rgba(0,0,0,0.3) !important;
    transform: translateX(8px) !important;
}

/* ===== Caption ===== */
.stCaption, [data-testid="stCaptionContainer"] {
    color: var(--text-muted) !important;
}

/* ===== 代码块 ===== */
code {
    background: var(--bg-card) !important;
    color: var(--gold-primary) !important;
    padding: 2px 8px !important;
    border-radius: 6px !important;
    border: 1px solid var(--border-default) !important;
}

/* ===== Spinner ===== */
.stSpinner > div {
    border-top-color: var(--gold-primary) !important;
}

/* ===== 统计卡片容器 ===== */
.stat-card {
    background: linear-gradient(145deg, var(--bg-card) 0%, var(--bg-secondary) 100%) !important;
    border: 1px solid var(--border-default) !important;
    border-radius: 20px !important;
    padding: 2rem !important;
    text-align: center !important;
    transition: all 0.3s ease !important;
}

.stat-card:hover {
    border-color: rgba(245,158,11,0.4) !important;
    box-shadow: var(--glow-gold) !important;
    transform: translateY(-4px) !important;
}

.stat-value {
    color: var(--gold-primary) !important;
    font-size: 2.5rem !important;
    font-weight: 700 !important;
    text-shadow: 0 0 30px rgba(245,158,11,0.4) !important;
}

.stat-label {
    color: var(--text-muted) !important;
    font-size: 0.9rem !important;
    margin-top: 0.5rem !important;
    font-weight: 500 !important;
}

/* ===== 页面标题金色下划线 ===== */
.page-title {
    position: relative !important;
    display: inline-block !important;
}

.page-title::after {
    content: '' !important;
    position: absolute !important;
    bottom: -8px !important;
    left: 0 !important;
    width: 60px !important;
    height: 3px !important;
    background: var(--gradient-gold) !important;
    border-radius: 2px !important;
}
</style>
""", unsafe_allow_html=True)

# ============ Session State ============
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'major' not in st.session_state:
    st.session_state.major = ""
if 'topics' not in st.session_state:
    st.session_state.topics = []
if 'selected_topic' not in st.session_state:
    st.session_state.selected_topic = ""
if 'chapters' not in st.session_state:
    st.session_state.chapters = [ch.copy() for ch in DEFAULT_CHAPTERS]
if 'workflow' not in st.session_state:
    st.session_state.workflow = None
if 'thesis_config' not in st.session_state:
    st.session_state.thesis_config = None
if 'thesis_output' not in st.session_state:
    st.session_state.thesis_output = None
if 'api_base_url' not in st.session_state:
    st.session_state.api_base_url = ""  # 留空则使用.env配置
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""  # 留空则使用.env配置
if 'api_model' not in st.session_state:
    st.session_state.api_model = ""  # 留空则使用.env配置
if 'show_api_key' not in st.session_state:
    st.session_state.show_api_key = False

def get_workflow():
    """获取工作流实例（通过中转站API调用）"""
    # 每次都重新创建以使用最新的API设置
    from src.claude_client import ClaudeClient, ThesisGenerator
    
    # 前端设置（可为空，空值会自动使用.env配置）
    api_key = st.session_state.api_key
    base_url = st.session_state.api_base_url
    model = st.session_state.api_model
    
    # 创建工作流（传入前端设置，后端会自动处理空值回退）
    workflow = ThesisWorkflow(
        use_cli=False, 
        api_key=api_key, 
        base_url=base_url, 
        model=model
    )
    
    st.session_state.workflow = workflow
    return st.session_state.workflow

def reset():
    st.session_state.step = 1
    st.session_state.major = ""
    st.session_state.topics = []
    st.session_state.selected_topic = ""
    st.session_state.chapters = [ch.copy() for ch in DEFAULT_CHAPTERS]
    st.session_state.workflow = None
    st.session_state.thesis_config = None
    st.session_state.thesis_output = None

# ============ 侧边栏 ============
with st.sidebar:
    st.markdown("## 📄 ThesisAI")
    st.caption("v8.0 · High-end GUI Edition")

    st.divider()

    # 当前状态
    if st.session_state.major:
        cfg = MAJORS[st.session_state.major]
        st.markdown(f"### {cfg['icon']} 当前专业")
        st.markdown(f"**{cfg['code']}** {st.session_state.major}")

        # 标签胶囊
        tags_container = st.container()
        with tags_container:
            cols = st.columns(len(cfg['tags']))
            for i, tag in enumerate(cfg['tags']):
                cols[i].caption(f"`{tag}`")

        st.divider()

    if st.session_state.selected_topic:
        st.markdown("### 📝 论文主题")
        st.info(st.session_state.selected_topic[:50] + "..." if len(st.session_state.selected_topic) > 50 else st.session_state.selected_topic)
        st.divider()

    # 进度指示
    st.markdown("### 📊 当前进度")
    progress_val = (st.session_state.step - 1) / 4
    st.progress(progress_val)

    steps_text = ["选择专业", "确定选题", "编辑章节", "生成论文"]
    for i, txt in enumerate(steps_text, 1):
        if i < st.session_state.step:
            st.markdown(f"✅ ~~{txt}~~")
        elif i == st.session_state.step:
            st.markdown(f"🔶 **{txt}** ←")
        else:
            st.markdown(f"⬜ {txt}")

    st.divider()

    if st.button("🔄 重新开始", use_container_width=True):
        reset()
        st.rerun()

    st.divider()
    st.caption("⚠️ 内容仅供学术参考")
    


# ============ 主内容区 ============

# ============ 步骤 1: 选择专业 ============
if st.session_state.step == 1:
    # 标题区域
    st.markdown("""<div style="margin: 2rem 0;">
        <span style="background: rgba(245,158,11,0.12); border: 1px solid rgba(245,158,11,0.25); border-radius: 24px; padding: 10px 24px; color: #F59E0B; font-size: 1rem; font-weight: 500;">🎓 广西国开大专用</span>
        <h1 style="font-size: 3.5rem; font-weight: 800; color: #FFFFFF; margin: 1.5rem 0 0.5rem 0; line-height: 1.1;">智能论文生成器</h1>
        <p style="color: #9CA3AF; font-size: 1.15rem; margin: 0; line-height: 1.6;">基于 Claude Opus 4.5，为您生成具有<span style="color: #F59E0B; font-weight: 600;">广西本土特色</span>的高质量学术论文</p>
    </div>""", unsafe_allow_html=True)

    # API 设置（紧凑单行布局）
    with st.expander("⚙️ API 设置" + (" ✅" if st.session_state.api_key else ""), expanded=not st.session_state.api_key):
        c1, c2, c3, c4 = st.columns([1.2, 2, 2, 1])
        model_options = {"Opus 4.5": "claude-opus-4-5-20251101", "Sonnet 4": "claude-sonnet-4-20250514"}
        with c1:
            sel = st.selectbox("模型", list(model_options.keys()), index=0 if st.session_state.api_model in ["", "claude-opus-4-5-20251101"] else 1, key="m_sel", label_visibility="collapsed")
            st.session_state.api_model = model_options[sel]
        with c2:
            st.session_state.api_base_url = st.text_input("Base URL", value=st.session_state.api_base_url, placeholder="Base URL (可选)", key="m_url", label_visibility="collapsed")
        with c3:
            st.session_state.api_key = st.text_input("API Key", value=st.session_state.api_key, type="password", placeholder="API Key (留空用.env)", key="m_key", label_visibility="collapsed")
        with c4:
            if st.button("💾 保存", key="m_save", use_container_width=True):
                from src.config import save_env_config
                if save_env_config(api_key=st.session_state.api_key, base_url=st.session_state.api_base_url, model=st.session_state.api_model):
                    st.toast("✅ 已保存到 .env")
                else:
                    st.toast("❌ 保存失败")

    # 流程说明
    st.markdown("""<div style="background: rgba(24, 24, 27, 0.4); border: 1px solid rgba(63, 63, 70, 0.3); border-radius: 12px; padding: 1rem 1.25rem; margin: 1.5rem 0;">
        <div style="color: #A1A1AA; font-size: 0.9rem;">
            <span style="color: #F59E0B; font-weight: 600;">完整流程：</span>
            <span style="color: #71717A;">步骤1</span> 选择专业 →
            <span style="color: #71717A;">步骤2</span> 确定选题 →
            <span style="color: #71717A;">步骤3</span> 编辑章节 →
            <span style="color: #71717A;">步骤4</span> 生成论文 
        </div>
    </div>""", unsafe_allow_html=True)

    # 专业选择区：4列并排
    st.markdown("""<div style="display: flex; align-items: center; gap: 0.75rem; margin: 2rem 0 1rem 0;">
        <span style="background: rgba(245, 158, 11, 0.15); color: #F59E0B; padding: 4px 10px; border-radius: 6px; font-size: 0.8rem; font-weight: 600;">步骤 1</span>
        <span style="color: #FFFFFF; font-size: 1.1rem; font-weight: 600;">选择您的专业方向</span>
    </div>""", unsafe_allow_html=True)

    major_items = list(MAJORS.items())
    mcols = st.columns(4, gap="medium")

    for idx in range(4):
        name, cfg = major_items[idx]
        with mcols[idx]:
            if st.button(f"{cfg['icon']} {name}", key=f"sel_{idx}", use_container_width=True):
                st.session_state.major = name
                with st.spinner("正在生成选题...（首次可能需要30-60秒）"):
                    wf = get_workflow()
                    st.session_state.topics = wf.generate_topics(name, 5)
                    st.session_state.step = 2
                    st.rerun()

    # 统计卡片 - 嵌入式沉稳风格（无悬浮效果）
    st.markdown("""<div style="display: flex; gap: 2rem; margin: 3rem 0;">
        <div style="flex:1; background: rgba(10, 10, 12, 0.9); border: 1px solid rgba(39, 39, 42, 0.4); border-radius: 20px; padding: 2rem; text-align: center; box-shadow: inset 0 2px 8px rgba(0, 0, 0, 0.4);">
            <div style="color: #F59E0B; font-size: 2.5rem; font-weight: 700; text-shadow: 0 0 30px rgba(245, 158, 11, 0.4);">4+</div>
            <div style="color: #71717A; font-size: 0.95rem; margin-top: 0.75rem; font-weight: 500;">专业方向</div>
        </div>
        <div style="flex:1; background: rgba(10, 10, 12, 0.9); border: 1px solid rgba(39, 39, 42, 0.4); border-radius: 20px; padding: 2rem; text-align: center; box-shadow: inset 0 2px 8px rgba(0, 0, 0, 0.4);">
            <div style="color: #F59E0B; font-size: 2.5rem; font-weight: 700; text-shadow: 0 0 30px rgba(245, 158, 11, 0.4);">12K+</div>
            <div style="color: #71717A; font-size: 0.95rem; margin-top: 0.75rem; font-weight: 500;">目标字数</div>
        </div>
        <div style="flex:1; background: rgba(10, 10, 12, 0.9); border: 1px solid rgba(39, 39, 42, 0.4); border-radius: 20px; padding: 2rem; text-align: center; box-shadow: inset 0 2px 8px rgba(0, 0, 0, 0.4);">
            <div style="color: #F59E0B; font-size: 2.5rem; font-weight: 700; text-shadow: 0 0 30px rgba(245, 158, 11, 0.4);">24/7</div>
            <div style="color: #71717A; font-size: 0.95rem; margin-top: 0.75rem; font-weight: 500;">AI 驱动</div>
        </div>
        <div style="flex:1; background: rgba(10, 10, 12, 0.9); border: 1px solid rgba(39, 39, 42, 0.4); border-radius: 20px; padding: 2rem; text-align: center; box-shadow: inset 0 2px 8px rgba(0, 0, 0, 0.4);">
            <div style="color: #F59E0B; font-size: 2.5rem; font-weight: 700; text-shadow: 0 0 30px rgba(245, 158, 11, 0.4);">100%</div>
            <div style="color: #71717A; font-size: 0.95rem; margin-top: 0.75rem; font-weight: 500;">原创内容</div>
        </div>
    </div>""", unsafe_allow_html=True)

    # 特性列表
    st.markdown("""<div style="display: flex; gap: 3rem; margin: 1rem 0 2rem 0;">
        <span style="color: #A1A1AA;"><span style="color: #22C55E;">✓</span> 自动生成大纲</span>
        <span style="color: #A1A1AA;"><span style="color: #22C55E;">✓</span> 智能章节撰写</span>
        <span style="color: #A1A1AA;"><span style="color: #22C55E;">✓</span> 参考文献整理</span>
        <span style="color: #A1A1AA;"><span style="color: #22C55E;">✓</span> 一键导出Word</span>
    </div>""", unsafe_allow_html=True)

    # 底部信息
    st.markdown("""<div style="padding-top: 2rem; border-top: 1px solid #27272A; display: flex; justify-content: space-between;">
        <span style="color: #52525B; font-size: 0.85rem;">⚠️ 生成内容仅供学术参考，提交前请进行查重检测</span>
        <span style="color: #52525B; font-size: 0.85rem;">ThesisAI Pro v8.0 · Powered by Claude Opus 4.5</span>
    </div>""", unsafe_allow_html=True)

# ============ 步骤 2: 选择选题 ============
elif st.session_state.step == 2:
    cfg = MAJORS.get(st.session_state.major, {})

    # CSS控制最大宽度，无需嵌套列
    st.markdown(f"## {cfg.get('icon', '📝')} 选择论文主题")
    st.markdown(f"已为 **{st.session_state.major}** 专业生成 {len(st.session_state.topics)} 个广西特色选题")

    st.markdown("###")

    # 选题卡片列表
    for idx, topic in enumerate(st.session_state.topics, 1):
        col1, col2 = st.columns([6, 1])
        with col1:
            st.markdown(f"""
            <div class='topic-card' style='
                background: #18181B;
                border: 1px solid #27272A;
                border-radius: 12px;
                padding: 1rem 1.25rem;
                display: flex;
                align-items: center;
                gap: 1rem;
            '>
                <span style='
                    background: rgba(245, 158, 11, 0.1);
                    color: #F59E0B;
                    padding: 6px 12px;
                    border-radius: 8px;
                    font-family: monospace;
                    font-weight: 700;
                    font-size: 0.85rem;
                '>{idx:02d}</span>
                <span style='color: #E4E4E7; font-size: 0.95rem;'>{topic}</span>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            if st.button(f"选择", key=f"topic_{idx}", use_container_width=True):
                st.session_state.selected_topic = topic
                st.session_state.step = 3
                st.rerun()

    st.markdown("###")
    st.divider()

    # 自定义主题
    st.markdown("#### 💡 或输入自定义主题")
    custom_topic = st.text_input("自定义主题", placeholder="输入您的广西特色论文主题...", label_visibility="collapsed")

    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("← 返回上一步", use_container_width=True):
            st.session_state.step = 1
            st.rerun()
    with col2:
        if st.button("🔄 重新生成", use_container_width=True):
            with st.spinner("重新生成选题..."):
                wf = get_workflow()
                st.session_state.topics = wf.generate_topics(st.session_state.major, 5)
                st.rerun()
    with col3:
        if st.button("使用自定义主题 →", disabled=not custom_topic.strip(), use_container_width=True):
            st.session_state.selected_topic = custom_topic.strip()
            st.session_state.step = 3
            st.rerun()

# ============ 步骤 3: 编辑章节 ============
elif st.session_state.step == 3:
    cfg = MAJORS.get(st.session_state.major, {})

    # CSS控制最大宽度
    st.markdown("## 📑 编辑章节结构")

    # 信息卡片
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("专业方向", f"{cfg.get('code', '')} {st.session_state.major}")
    with col2:
        st.metric("章节数量", len(st.session_state.chapters))
    with col3:
        total_words = sum(ch['word_count'] for ch in st.session_state.chapters)
        st.metric("目标字数", f"{total_words:,}")

    st.info(f"📝 **论文主题:** {st.session_state.selected_topic}")

    st.markdown("###")

    # 章节编辑器
    chapters = st.session_state.chapters
    to_delete = []

    for idx, ch in enumerate(chapters):
        with st.expander(f"📖 第 {idx+1} 章: {ch['title']}", expanded=(idx == 0)):
            col1, col2 = st.columns([3, 1])
            with col1:
                chapters[idx]['title'] = st.text_input("章节标题", value=ch['title'], key=f"title_{idx}")
            with col2:
                chapters[idx]['word_count'] = st.number_input("目标字数", value=ch['word_count'], min_value=500, max_value=10000, step=500, key=f"words_{idx}")

            chapters[idx]['requirements'] = st.text_area("内容要求", value=ch['requirements'], key=f"req_{idx}", height=80)

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                if idx > 0 and st.button("⬆️ 上移", key=f"up_{idx}"):
                    chapters[idx], chapters[idx-1] = chapters[idx-1], chapters[idx]
                    st.rerun()
            with col2:
                if idx < len(chapters)-1 and st.button("⬇️ 下移", key=f"down_{idx}"):
                    chapters[idx], chapters[idx+1] = chapters[idx+1], chapters[idx]
                    st.rerun()
            with col4:
                if st.button("🗑️ 删除", key=f"del_{idx}"):
                    to_delete.append(idx)

    if to_delete:
        for i in sorted(to_delete, reverse=True):
            chapters.pop(i)
        st.session_state.chapters = chapters
        st.rerun()

    if st.button("➕ 添加新章节", use_container_width=True):
        chapters.append({"title": "新章节", "requirements": "请填写内容要求", "word_count": 2000})
        st.rerun()

    st.markdown("###")
    st.divider()

    # 操作按钮
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("← 返回上一步", use_container_width=True):
            st.session_state.step = 2
            st.rerun()
    with col2:
        if st.button("🚀 开始生成论文", type="primary", use_container_width=True):
            st.session_state.chapters = chapters
            st.session_state.step = 4
            st.rerun()
    with col3:
        if st.button("🔄 重置", use_container_width=True):
            st.session_state.chapters = [ch.copy() for ch in DEFAULT_CHAPTERS]
            st.rerun()

# ============ 步骤 4: 生成论文 ============
elif st.session_state.step == 4:
    # CSS控制最大宽度
    st.markdown("## ⚡ 生成论文")

    # 配置摘要
    col1, col2, col3 = st.columns(3)
    with col1:
        cfg = MAJORS.get(st.session_state.major, {})
        st.metric("专业", f"{cfg.get('icon', '')} {st.session_state.major}")
    with col2:
        st.metric("章节", len(st.session_state.chapters))
    with col3:
        total = sum(ch['word_count'] for ch in st.session_state.chapters)
        st.metric("目标字数", f"{total:,}")

    st.info(f"📝 {st.session_state.selected_topic}")

    st.markdown("###")

    # 生成过程
    progress_bar = st.progress(0, text="准备开始...")
    status_text = st.empty()
    log_container = st.container()

    try:
        config = ThesisConfig(
            title=st.session_state.selected_topic,
            topic=st.session_state.selected_topic,
            major=st.session_state.major,
            chapters=st.session_state.chapters
        )

        wf = get_workflow()
        logs = []

        def add_log(icon, msg):
            logs.append(f"{icon} {msg}")
            with log_container:
                for log in logs[-8:]:
                    st.caption(log)

        # 生成大纲
        progress_bar.progress(5, text="📋 生成论文大纲...")
        status_text.markdown("### 📋 正在生成论文大纲...")
        add_log("🔄", "开始生成论文大纲")
        config.outline = wf.generator.generate_outline(config.topic, config.major, "")
        add_log("✅", "大纲生成完成")

        # 生成各章节
        total_chapters = len(config.chapters)
        for idx, ch in enumerate(config.chapters):
            pct = 10 + int((idx + 1) / total_chapters * 60)
            progress_bar.progress(pct, text=f"📝 撰写: {ch['title']}")
            status_text.markdown(f"### 📝 正在撰写: {ch['title']}")
            add_log("🔄", f"撰写章节: {ch['title']}")

            ctx = wf._build_context(config)
            content = wf.generator.generate_section(ch['title'], ch.get('requirements', ''), ctx, ch.get('word_count', 1500))
            config.sections[ch['title']] = content
            add_log("✅", f"{ch['title']} 完成 ({ch['word_count']} 字)")

        # 生成摘要
        progress_bar.progress(75, text="📄 生成摘要...")
        status_text.markdown("### 📄 正在生成摘要与关键词...")
        add_log("🔄", "提炼摘要与关键词")
        summary = wf._summarize_content(config.sections)
        config.abstract_cn = wf.generator.generate_abstract(summary, "chinese")
        config.keywords_cn = wf.generator.generate_keywords(summary, 5)
        add_log("✅", "摘要生成完成")

        # 生成参考文献
        progress_bar.progress(85, text="📚 整理参考文献...")
        status_text.markdown("### 📚 正在整理参考文献...")
        add_log("🔄", "整理参考文献")
        config.references = wf.generator.generate_references(config.topic, config.major, 10)
        add_log("✅", f"参考文献整理完成 ({len(config.references)} 条)")

        # 构建文档
        progress_bar.progress(95, text="📦 构建Word文档...")
        status_text.markdown("### 📦 正在构建Word文档...")
        add_log("🔄", "生成Word文档")
        output = wf._build_document(config)
        add_log("✅", "文档构建完成")

        # 保存配置到 session state（供步骤5使用）
        st.session_state.thesis_config = config
        st.session_state.thesis_output = output

        # 完成
        progress_bar.progress(100, text="✅ 完成!")
        status_text.empty()

        st.balloons()

        # 成功提示
        st.success("🎉 **论文生成完成!** 文档已准备就绪")

        # 统计
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("完成章节", f"{len(config.chapters)} 章", delta="100%")
        with col2:
            st.metric("总字数", f"{total:,}", delta="达标")
        with col3:
            st.metric("参考文献", f"{len(config.references)} 条")

        # 下载按钮（缓存文件数据避免重复读取导致状态问题）
        st.markdown("###")
        if 'thesis_file_data' not in st.session_state or st.session_state.get('thesis_file_path') != output:
            with open(output, 'rb') as f:
                st.session_state.thesis_file_data = f.read()
                st.session_state.thesis_file_path = output

        st.download_button(
            "📥 下载 Word 文档",
            data=st.session_state.thesis_file_data,
            file_name=Path(output).name,
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True,
            key="download_thesis_word"
        )

        st.caption(f"📁 文件路径: `{output}`")

        st.warning("⚠️ **注意:** 生成内容仅供参考，建议替换为真实文献，提交前务必进行查重检测。")

        # 答辩稿工具提示
        st.markdown("###")
        st.markdown("""<div style="background: rgba(245,158,11,0.1); border: 1px solid rgba(245,158,11,0.3); border-radius: 12px; padding: 1.25rem; margin: 1rem 0;">
            <div style="color: #F59E0B; font-size: 1rem; font-weight: 600; margin-bottom: 0.5rem;">🎓 需要生成答辩稿吗？</div>
            <div style="color: #A1A1AA; font-size: 0.9rem;">请使用左侧导航栏的「🎤 答辩稿生成」工具，上传论文Word文档即可自动生成</div>
        </div>""", unsafe_allow_html=True)

        if st.button("🆕 开始新论文", use_container_width=True):
            reset()
            st.rerun()

    except Exception as e:
        st.error(f"❌ 生成失败: {e}")
        import traceback
        with st.expander("查看错误详情"):
            st.code(traceback.format_exc())

        st.markdown("###")
        st.divider()

        if st.button("🆕 开始新论文", use_container_width=True):
            reset()
            st.rerun()

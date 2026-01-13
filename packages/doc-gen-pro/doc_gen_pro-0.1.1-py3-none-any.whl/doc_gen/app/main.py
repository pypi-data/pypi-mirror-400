import streamlit as st
import sys
import os
import base64

try:
    from doc_gen.core.error_handler import logger, get_user_friendly_message
except ImportError as e:
    import logging
    logger = logging.getLogger(__name__)
    logger.error(f"无法导入错误处理模块: {str(e)}")
    
    def get_user_friendly_message(error):
        return str(error)


CSS_STYLES = """
<style>
/* 全局样式 */
.stApp {
    background-image: url('BACKGROUND_URL');
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
    background-repeat: no-repeat;
}

/* 半透明遮罩层 - 让内容在背景图片上更清晰 */
.main .block-container {
    background-color: rgba(255, 255, 255, 0.92);
    backdrop-filter: blur(10px);
    border-radius: 15px;
    padding: 2rem;
    margin-top: 1rem;
    border: 1px solid rgba(255, 255, 255, 0.3);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

/* 侧边栏半透明 */
[data-testid="stSidebar"] {
    background-color: rgba(248, 250, 255, 0.0);
    border-right: 1px solid #bee3f8;
}

/* 侧边栏标题样式 */
.sidebar-header {
    font-size: 1.3rem;
    font-weight: 700;
    padding: 1rem;
    background: linear-gradient(135deg, #3498db 0%, #5dade2 100%);
    border-radius: 0 0 12px 12px;
    margin: -1rem -1rem 1rem -1rem;
    text-align: center;
    color: white;
    box-shadow: 0 2px 8px rgba(52, 152, 219, 0.3);
}

/* 全局样式 */
.main {
    padding: 2rem;
}

/* 按钮样式 - 圆角、阴影、悬停效果 */
.stButton > button {
    border-radius: 8px;
    padding: 0.5rem 1.5rem;
    font-weight: 500;
    transition: all 0.3s ease;
    border: none;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    background-color: #3498db;
    color: white;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
    background-color: #2980b9;
}

.stButton > button:active {
    transform: translateY(0);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

/* 输入框样式 - 圆角、边框、焦点效果 */
.stTextInput > div > div > input {
    border-radius: 8px;
    border: 1px solid #dee2e6;
    padding: 0.5rem 1rem;
    transition: border-color 0.3s ease, box-shadow 0.3s ease;
}

.stTextInput > div > div > input:focus {
    border-color: #3498db;
    box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
    outline: none;
}

/* 文本区域样式 */
.stTextArea > div > div > textarea {
    border-radius: 8px;
    border: 1px solid #dee2e6;
    padding: 0.5rem 1rem;
    transition: border-color 0.3s ease, box-shadow 0.3s ease;
}

.stTextArea > div > div > textarea:focus {
    border-color: #3498db;
    box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
    outline: none;
}

/* 选择框样式 */
.stSelectbox > div > div > select {
    border-radius: 8px;
    border: 1px solid #dee2e6;
    padding: 0.5rem 1rem;
    transition: border-color 0.3s ease;
}

/* 文件树样式 */
.streamlit-tree-select {
    border-radius: 8px;
    padding: 1rem;
    background-color: #f0f2f6;
    border: 1px solid #dee2e6;
}

.file-tree-node {
    padding: 0.5rem;
    border-radius: 4px;
    transition: background-color 0.2s ease;
    cursor: pointer;
}

.file-tree-node:hover {
    background-color: #e9ecef;
}

.file-tree-folder {
    font-weight: 500;
    color: #3498db;
}

.file-tree-file {
    color: #6c757d;
    transition: all 0.2s ease;
}

.file-tree-file:hover {
    color: #495057;
    transform: scale(1.05);
}

/* 文件浏览器导航按钮样式 */
button[key^="nav_"] {
    min-width: 40px !important;
    padding: 0.4rem !important;
    font-size: 1.2rem !important;
}

/* 文件夹按钮样式优化 */
button[key^="folder_"] {
    background-color: #f8f9fa !important;
    color: #3498db !important;
    border: 1px solid #dee2e6 !important;
    text-align: left !important;
    font-size: 0.9rem !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
}

button[key^="folder_"]:hover {
    background-color: #e9ecef !important;
    border-color: #3498db !important;
}

/* 面包屑导航样式 */
.breadcrumb {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 1rem 0;
    font-size: 0.875rem;
    color: #6c757d;
}

.breadcrumb a {
    color: #3498db;
    text-decoration: none;
    transition: color 0.2s ease;
    font-weight: 500;
}

.breadcrumb a:hover {
    color: #2980b9;
    text-decoration: underline;
}

.breadcrumb-separator {
    color: #dee2e6;
    margin: 0 4px;
}

.breadcrumb-current {
    color: #262730;
    font-weight: 500;
}

/* 卡片样式 */
.card {
    background-color: white;
    border-radius: 8px;
    padding: 1.5rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    margin-bottom: 1rem;
    border: 1px solid #dee2e6;
    transition: box-shadow 0.3s ease;
}

.card:hover {
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.card-header {
    font-size: 1.25rem;
    font-weight: 600;
    color: #262730;
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid #f0f2f6;
}

.card-body {
    color: #6c757d;
    line-height: 1.6;
}

/* 进度条样式 */
.stProgress > div > div {
    background-color: #3498db;
    border-radius: 4px;
}

/* 成功消息样式 */
.stSuccess {
    background-color: #d4edda;
    border-color: #c3e6cb;
    color: #155724;
    border-radius: 8px;
    padding: 1rem;
}

/* 错误消息样式 */
.stError {
    background-color: #f8d7da;
    border-color: #f5c6cb;
    color: #721c24;
    border-radius: 8px;
    padding: 1rem;
}

/* 警告消息样式 */
.stWarning {
    background-color: #fff3cd;
    border-color: #ffeaa7;
    color: #856404;
    border-radius: 8px;
    padding: 1rem;
}

/* 信息消息样式 */
.stInfo {
    background-color: #d1ecf1;
    border-color: #bee5eb;
    color: #0c5460;
    border-radius: 8px;
    padding: 1rem;
}

/* 侧边栏样式优化 */
.css-1d391kg {
    padding: 2rem 1rem;
}

/* 文件上传器样式 */
.stFileUploader {
    border-radius: 8px;
    border: 2px dashed #dee2e6;
    padding: 1rem;
    transition: border-color 0.3s ease;
}

.stFileUploader:hover {
    border-color: #3498db;
}

/* 下载按钮样式 */
.stDownloadButton > button {
    border-radius: 8px;
    padding: 0.5rem 1.5rem;
    font-weight: 500;
    transition: all 0.3s ease;
    border: none;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    background-color: #2ecc71;
    color: white;
}

.stDownloadButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
    background-color: #27ae60;
}

/* 标签页样式 */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 8px 8px 0 0;
    padding: 0.5rem 1rem;
    font-weight: 500;
}

/* 数据框样式 */
.stDataFrame {
    border-radius: 8px;
    overflow: hidden;
}

/* 代码块样式 */
.stCodeBlock {
    border-radius: 8px;
    border: 1px solid #dee2e6;
}

/* 标题样式优化 */
h1 {
    color: #262730;
    font-weight: 700;
    margin-bottom: 1.5rem;
}

h2 {
    color: #262730;
    font-weight: 600;
    margin-bottom: 1rem;
    margin-top: 2rem;
}

h3 {
    color: #3498db;
    font-weight: 600;
    margin-bottom: 0.75rem;
    margin-top: 1.5rem;
}

/* 链接样式 */
a {
    color: #3498db;
    text-decoration: none;
    transition: color 0.2s ease;
}

a:hover {
    color: #2980b9;
    text-decoration: underline;
}

/* 分隔线样式 */
hr {
    border: none;
    border-top: 2px solid #f0f2f6;
    margin: 2rem 0;
}

/* 列表样式 */
ul, ol {
    line-height: 1.8;
    color: #6c757d;
}

/* 多选框样式优化 */
.stMultiSelect > div > div {
    border-radius: 8px;
    border: 1px solid #dee2e6;
}

.stMultiSelect [data-baseweb="tag"] {
    background-color: #3498db;
    border-radius: 4px;
    margin: 2px;
}

/* 分隔线样式增强 */
hr {
    margin: 1.5rem 0 !important;
    border-top: 1px solid #e9ecef !important;
}

/* 容器间距优化 */
.element-container {
    margin-bottom: 0.5rem;
}

/* 标题间距优化 */
.card-header + .card-body {
    margin-top: 0.5rem;
}

/* 响应式调整 */
@media (max-width: 768px) {
    .main .block-container {
        padding: 1rem;
    }
    
    .card {
        padding: 1rem;
    }
    
    .stButton > button {
        width: 100%;
        margin-bottom: 0.5rem;
    }
    
    /* 移动端文件夹和文件显示优化 */
    button[key^="folder_"] {
        font-size: 0.8rem !important;
    }
}
</style>
"""


def inject_custom_css():
    """注入自定义 CSS 样式"""
    background_image_path = os.path.join(
        os.path.dirname(__file__), "static", "background.jpg"
    )

    if os.path.exists(background_image_path):
        with open(background_image_path, "rb") as img_file:
            img_data = base64.b64encode(img_file.read()).decode()
            background_url = f"data:image/jpeg;base64,{img_data}"
    else:
        background_url = "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"

    css_content = CSS_STYLES.replace("url('BACKGROUND_URL')", f"url('{background_url}')")
    st.markdown(css_content, unsafe_allow_html=True)


# 设置页面配置
try:
    st.set_page_config(
        layout="wide",
        page_title="源代码文档生成器",
        page_icon="🚀",
        initial_sidebar_state="expanded"
    )
except Exception as e:
    logger.error(f"页面配置失败: {str(e)}")
    st.error(f"⚠️ 页面配置失败: {get_user_friendly_message(e)}")

# 注入自定义 CSS 样式
try:
    inject_custom_css()
except Exception as e:
    logger.warning(f"CSS 注入失败: {str(e)}")

# 定义页面
try:
    generator_page = st.Page(
        "pages/generator.py",
        title="文档生成器",
        icon="📄"
    )

    about_page = st.Page(
        "pages/about.py",
        title="关于",
        icon="ℹ️"
    )
except Exception as e:
    logger.error(f"页面定义失败: {str(e)}")
    st.error(f"❌ 无法加载页面: {get_user_friendly_message(e)}")
    st.stop()

# 定义页面列表
pages = [generator_page, about_page]

# 定义主页内容
def main_page():
    """主页内容"""
    st.set_page_config(page_title="源代码文档生成器", page_icon="📝")

    st.markdown("""
    <style>
    .hero-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 40px;
        border-radius: 20px;
        margin-bottom: 30px;
        text-align: center;
    }
    .hero-title {
        font-size: 48px;
        font-weight: bold;
        color: white;
        margin-bottom: 10px;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    .hero-subtitle {
        font-size: 20px;
        color: rgba(255,255,255,0.9);
        margin-bottom: 20px;
    }
    .feature-card {
        background: white;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        border-left: 5px solid;
    }
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    }
    .feature-icon {
        font-size: 48px;
        margin-bottom: 15px;
    }
    .stat-number {
        font-size: 36px;
        font-weight: bold;
        color: #667eea;
    }
    .step-card {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 30px;
        border-radius: 15px;
        text-align: center;
        height: 100%;
    }
    .step-number {
        background: #667eea;
        color: white;
        width: 50px;
        height: 50px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        font-weight: bold;
        margin: 0 auto 20px;
    }
    .tech-badge {
        display: inline-block;
        background: #e9ecef;
        padding: 8px 16px;
        border-radius: 20px;
        margin: 5px;
        font-size: 14px;
        font-weight: 500;
    }
    .tech-badge-python { background: #3776ab; color: white; }
    .tech-badge-streamlit { background: #ff4b4b; color: white; }
    .tech-badge-doxygen { background: #6c5ce7; color: white; }
    .tech-badge-jinja { background: #a62925; color: white; }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="hero-section">
        <div class="hero-title">🚀 源代码文档生成器</div>
        <div class="hero-subtitle">智能解析 Doxygen 注释，自动生成专业文档</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("支持语言", "2 种", "C / Java")
    with col2:
        st.metric("文档模板", "2 套", "Markdown 格式")
    with col3:
        st.metric("测试用例", "20+", "单元 & 集成")
    with col4:
        st.metric("文档覆盖", "100%", "核心模块")

    st.markdown("<br>", unsafe_allow_html=True)

    st.header("✨ 核心功能")

    f1, f2, f3 = st.columns(3)

    with f1:
        st.markdown("""
        <div class="feature-card" style="border-color: #667eea;">
            <div class="feature-icon">🔍</div>
            <h3 style="color: #667eea; margin-bottom: 10px;">智能代码解析</h3>
            <p style="color: #666;">自动识别 C 和 Java 源代码中的 Doxygen 注释，提取函数、类、变量等结构信息。</p>
        </div>
        """, unsafe_allow_html=True)

    with f2:
        st.markdown("""
        <div class="feature-card" style="border-color: #00b894;">
            <div class="feature-icon">📄</div>
            <h3 style="color: #00b894; margin-bottom: 10px;">Markdown 输出</h3>
            <p style="color: #666;">生成格式规范、易于阅读的 Markdown 文档，支持多种场景的文档需求。</p>
        </div>
        """, unsafe_allow_html=True)

    with f3:
        st.markdown("""
        <div class="feature-card" style="border-color: #fd79a8;">
            <div class="feature-icon">🎨</div>
            <h3 style="color: #fd79a8; margin-bottom: 10px;">美观的模板</h3>
            <p style="color: #666;">精心设计的文档模板，包含代码结构、参数说明、返回值等详细信息。</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    st.header("📚 使用步骤")

    s1, s2, s3 = st.columns(3)

    with s1:
        st.markdown("""
        <div class="step-card">
            <div class="step-number">1</div>
            <h4 style="color: #333; margin-bottom: 15px;">选择文档生成器</h4>
            <p style="color: #666; font-size: 14px;">在左侧导航栏中点击「文档生成器」进入功能页面。</p>
        </div>
        """, unsafe_allow_html=True)

    with s2:
        st.markdown("""
        <div class="step-card">
            <div class="step-number">2</div>
            <h4 style="color: #333; margin-bottom: 15px;">上传源代码文件</h4>
            <p style="color: #666; font-size: 14px;">支持单个或批量上传 .c、.h、.java 文件。</p>
        </div>
        """, unsafe_allow_html=True)

    with s3:
        st.markdown("""
        <div class="step-card">
            <div class="step-number">3</div>
            <h4 style="color: #333; margin-bottom: 15px;">生成并下载文档</h4>
            <p style="color: #666; font-size: 14px;">点击生成按钮，查看文档并下载 Markdown 文件。</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    st.header("🛠️ 技术栈")

    st.markdown("""
    <div style="text-align: center; padding: 30px; background: #f8f9fa; border-radius: 15px;">
        <span class="tech-badge tech-badge-python">🐍 Python 3.13</span>
        <span class="tech-badge tech-badge-streamlit">📊 Streamlit</span>
        <span class="tech-badge tech-badge-doxygen">📝 Doxygen</span>
        <span class="tech-badge tech-badge-jinja">🎨 Jinja2</span>
        <br><br>
        <p style="color: #666; font-size: 14px;">
            基于 Python 的现代化 Web 应用，正则表达式解析引擎，Jinja2 模板渲染
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    st.header("💡 Doxygen 标签支持")

    st.markdown("""
    | 标签 | 用途 | 标签 | 用途 |
    |------|------|------|------|
    | `@file` | 文件说明 | `@brief` | 简要说明 |
    | `@author` | 作者信息 | `@version` | 版本号 |
    | `@param` | 参数说明 | `@return` | 返回值 |
    | `@note` | 附加说明 | `@warning` | 警告信息 |
    | `@see` | 参考链接 | `@deprecated` | 废弃说明 |
    | `@class` | 类说明 | `@interface` | 接口说明 |
    """)

# 添加主页到页面列表
main_page_item = st.Page(
    main_page,
    title="主页",
    icon="🏠"
)

# 重新排序页面列表，将主页放在首位
pages = [main_page_item] + pages

# 添加侧边栏内容
st.sidebar.markdown(
    '<div class="sidebar-header">📚 源代码文档生成器</div>',
    unsafe_allow_html=True
)

st.sidebar.info("""
**智能代码文档生成工具**

自动解析源代码中的 Doxygen 注释，
生成专业的 Markdown 格式文档。
""")

st.sidebar.markdown("---")

st.sidebar.markdown("### 📖 使用步骤")

st.sidebar.markdown("""
1. 选择 **文档生成器** 页面
2. 上传源代码文件
3. 点击生成文档按钮
4. 查看并下载结果
""")

st.sidebar.markdown("### ✨ 核心特性")

st.sidebar.markdown("""
- 🔍 **智能解析** - 支持 C 和 Java
- 📄 **Markdown 输出** - 格式规范美观
- ⚡ **批量处理** - 一次上传多个文件
- 🎨 **精美模板** - 专业的文档格式
""")

st.sidebar.markdown("---")
st.sidebar.caption("🚀 Powered by Streamlit | v1.0.0")

# 添加导航
try:
    app = st.navigation(pages)
    app.run()
except Exception as e:
    logger.error(f"应用运行失败: {str(e)}", exc_info=True)
    st.error(f"❌ 应用启动失败: {get_user_friendly_message(e)}")
    st.markdown("""
    ### 故障排除建议:
    1. 确保所有依赖已正确安装: `uv pip install -e .`
    2. 检查 Python 版本是否符合要求 (3.9+)
    3. 查看日志文件获取详细错误信息
    4. 尝试重新启动应用
    """)
    st.stop()

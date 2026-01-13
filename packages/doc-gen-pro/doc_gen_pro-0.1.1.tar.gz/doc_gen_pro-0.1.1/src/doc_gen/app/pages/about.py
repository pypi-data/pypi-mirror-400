import streamlit as st

st.set_page_config(
    page_title="关于",
    page_icon="ℹ️",
)

st.title("ℹ️ 关于项目")

st.markdown("""
这是一个基于 Streamlit 和 AST（抽象语法树）构建的、支持多语言的源代码文档生成工具。
它能够自动分析源代码文件，提取其中的类、函数、变量等结构信息，并生成美观易读的 Markdown 文档。
""")

st.markdown("---")

# 功能特性
st.header("✨ 功能特性")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    **核心功能**
    - 🔍 多语言支持（Python、C、Java）
    - 📊 自动 AST 分析
    - 🎨 美观的 Markdown 报告
    - 📁 本地文件系统浏览器
    - 🌲 文件树可视化展示
    """)

with col2:
    st.markdown("""
    **用户体验**
    - 💻 现代化 UI 设计
    - 📱 响应式布局
    - ⚡ 实时进度显示
    - 🔄 智能缓存机制
    - 🛡️ 完善的错误处理
    """)

st.markdown("---")

# 技术栈
st.header("🛠️ 技术栈")

tech_col1, tech_col2 = st.columns(2)

with tech_col1:
    st.markdown("""
    **前端框架**
    - **Streamlit**: Web 应用框架
    - **自定义 CSS**: 现代化样式系统
    """)
    
    st.markdown("""
    **后端技术**
    - **Python AST**: 源码解析
    - **Jinja2**: 模板引擎
    - **uv**: 包管理器
    """)

with tech_col2:
    st.markdown("""
    **测试框架**
    - **pytest**: 单元测试
    - **Hypothesis**: 属性测试（PBT）
    """)
    
    st.markdown("""
    **开发工具**
    - **src 布局**: 项目结构
    - **绝对导入**: 模块管理
    - **日志系统**: 错误追踪
    """)

st.markdown("---")

# 架构设计
st.header("🏗️ 架构设计")

st.markdown("""
项目采用 **src 布局**，实现了核心业务逻辑与 UI 界面的完全分离：
""")

arch_col1, arch_col2 = st.columns(2)

with arch_col1:
    st.markdown("""
    **核心模块** (`src/doc_gen/core`)
    - 📦 **orchestrator.py**: 解析器调度器
    - 🎨 **renderer.py**: Markdown 渲染器
    - 🛡️ **error_handler.py**: 错误处理和日志
    - 🔧 **parsers/**: 多语言解析器
        - C 语言解析器
        - Java 解析器
    """)

with arch_col2:
    st.markdown("""
    **应用模块** (`src/doc_gen/app`)
    - 🏠 **main.py**: 应用主入口
    - 📄 **pages/generator.py**: 文档生成页面
    - ℹ️ **pages/about.py**: 关于页面
    - 🎨 **自定义 CSS**: 样式注入
    """)

st.info("""
**设计原则**:
- ✅ 所有导入使用绝对路径 (`from doc_gen.core...`)
- ✅ 核心逻辑与 UI 完全分离
- ✅ 统一的错误处理机制
- ✅ 完整的测试覆盖（单元测试 + 属性测试）
""")

st.markdown("---")

# UI 设计
st.header("🎨 UI 设计规范")

st.markdown("""
采用现代化的设计系统，确保界面美观且易于使用：
""")

ui_col1, ui_col2, ui_col3 = st.columns(3)

with ui_col1:
    st.markdown("""
    **色彩系统**
    - 🔵 主色调: `#3498db`
    - 🟢 成功色: `#2ecc71`
    - 🟠 警告色: `#f39c12`
    - 🔴 错误色: `#e74c3c`
    """)

with ui_col2:
    st.markdown("""
    **组件样式**
    - 圆角设计 (8px)
    - 悬停效果
    - 阴影增强
    - 平滑过渡 (0.3s)
    """)

with ui_col3:
    st.markdown("""
    **响应式设计**
    - 桌面端 (> 1024px)
    - 平板端 (768-1024px)
    - 移动端 (< 768px)
    """)

st.markdown("---")

# 测试与质量保证
st.header("🧪 测试与质量保证")

st.markdown("""
项目采用双重测试策略，确保代码质量和正确性：
""")

test_col1, test_col2 = st.columns(2)

with test_col1:
    st.markdown("""
    **单元测试**
    - ✅ 路径处理测试
    - ✅ 文件树构建测试
    - ✅ 解析器功能测试
    - ✅ 渲染器输出测试
    - ✅ 错误处理测试
    """)

with test_col2:
    st.markdown("""
    **属性测试 (PBT)**
    - ✅ 导入一致性属性
    - ✅ 无循环依赖属性
    - ✅ 树形结构完整性
    - ✅ 目录切换一致性
    - 🔄 每个属性 100+ 次迭代
    """)

st.success("""
**Property-Based Testing (PBT)** 使用 Hypothesis 库，通过生成大量随机测试用例，
验证代码在各种输入下都能保持正确性，提供比传统单元测试更强的质量保证。
""")

st.markdown("---")

# 版本信息
st.header("📦 版本信息")

st.markdown("""
**当前版本**: v1.0.0 (2025-12-27)

**主要更新**:
- ✨ 支持 C 语言 Doxygen 注释解析
- ✨ 支持 Java 语言 Doxygen 注释解析
- ✨ 实现批量文件上传和处理
- ✨ 提供美观的 Markdown 文档模板
- ✨ 完整的单元测试和集成测试覆盖
- ✨ 详细的开发文档和技术文档
""")

st.markdown("---")

# 团队信息
st.header("👥 团队信息")

st.markdown("""
请填写团队成员信息：
""")

team_data = [
    {"角色": "开发成员", "姓名": "马云贤", "学号": "120231080118", "班级": "软件2301"}
]

st.table(team_data)

st.info("💡 **提示**: 请在 `src/doc_gen/app/pages/about.py` 文件中修改团队成员信息。")

st.markdown("---")


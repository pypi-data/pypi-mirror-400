"""
页面管理模块，用于定义所有 Streamlit 页面。
"""
import streamlit as st

# 定义页面
generator_page = st.Page(
    r"pages/generator.py",
    title="文档生成器",
    icon="📄"
)

about_page = st.Page(
    r"pages/about.py",
    title="关于",
    icon="ℹ️"
)

# 定义页面列表
pages = [generator_page, about_page]

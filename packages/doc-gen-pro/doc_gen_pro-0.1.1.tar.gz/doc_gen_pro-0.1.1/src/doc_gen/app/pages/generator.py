# src/doc_gen/app/pages/generator.py (最终用户体验优化版)

import streamlit as st
import os
from doc_gen.core.orchestrator import get_parser
from doc_gen.core.renderer import render_markdown
from doc_gen.core.error_handler import (
    get_user_friendly_message,
    logger,
    ModuleImportError
)


# --- 页面配置 ---
st.set_page_config(
    page_title="文档生成器",
    page_icon="📄",
    layout="wide",
)

# --- 会话状态管理 ---
def init_session_state():
    """初始化会话状态"""
    if 'selected_files' not in st.session_state:
        st.session_state.selected_files = []




def format_doxygen_docstring(docstring: str) -> str:
    """格式化 Doxygen 注释为 Markdown 格式"""
    import re
    
    if not docstring:
        return ""
    
    # 简单的格式化，将Doxygen命令转换为Markdown
    formatted = docstring
    # 替换@brief
    formatted = re.sub(r'@brief\s+(.*?)(?:@|$)', r'**简介**: \1\n', formatted, flags=re.DOTALL)
    # 替换@author
    formatted = re.sub(r'@author\s+(.*?)(?:@|$)', r'**作者**: \1\n', formatted, flags=re.DOTALL)
    # 替换@version
    formatted = re.sub(r'@version\s+(.*?)(?:@|$)', r'**版本**: \1\n', formatted, flags=re.DOTALL)
    # 替换@date
    formatted = re.sub(r'@date\s+(.*?)(?:@|$)', r'**日期**: \1\n', formatted, flags=re.DOTALL)
    # 替换@copyright
    formatted = re.sub(r'@copyright\s+(.*?)(?:@|$)', r'**版权**: \1\n', formatted, flags=re.DOTALL)
    # 替换@note
    formatted = re.sub(r'@note\s+(.*?)(?:@|$)', r'**注意**: \1\n', formatted, flags=re.DOTALL)
    # 替换@section
    formatted = re.sub(r'@section\s+\w+\s+([^\n]+)\n', r'## \1\n', formatted)
    # 替换@subsection
    formatted = re.sub(r'@subsection\s+\w+\s+([^\n]+)\n', r'### \1\n', formatted)
    # 替换@param
    formatted = re.sub(r'@param\s+(\w+)\s+(.*?)(?:@|$)', r'**参数** `\1`: \2\n', formatted, flags=re.DOTALL)
    # 替换@return
    formatted = re.sub(r'@return\s+(.*?)(?:@|$)', r'**返回值**: \1\n', formatted, flags=re.DOTALL)
    # 替换@see
    formatted = re.sub(r'@see\s+(.*?)(?:@|$)', r'**参见**: \1\n', formatted, flags=re.DOTALL)
    # 替换@todo
    formatted = re.sub(r'@todo\s+(.*?)(?:@|$)', r'**待办**: \1\n', formatted, flags=re.DOTALL)
    # 替换@warning
    formatted = re.sub(r'@warning\s+(.*?)(?:@|$)', r'**警告**: \1\n', formatted, flags=re.DOTALL)
    # 替换@deprecated
    formatted = re.sub(r'@deprecated\s+(.*?)(?:@|$)', r'**已弃用**: \1\n', formatted, flags=re.DOTALL)
    
    # 清理多余的空行
    formatted = re.sub(r'\n{3,}', '\n\n', formatted)
    return formatted.strip()



# --- 文件上传区域 ---
st.markdown('<div class="card-header">📁 文件上传</div>', unsafe_allow_html=True)

# 显示支持的文件类型
st.info("📋 **支持的文件类型**: C源文件(.c) | C头文件(.h) | Java文件(.java)")


# 文件上传组件 - 支持多文件上传
uploaded_files = st.file_uploader(
    "选择要解析的代码文件（支持多选）",
    type=['c', 'h', 'java'],
    accept_multiple_files=True,
    help="支持的文件类型：C源文件(.c)、C头文件(.h)、Java文件(.java)"
)


# 显示上传文件信息
if uploaded_files:
    total_files = len(uploaded_files)
    st.success(f"📁 已上传 {total_files} 个文件")
    
    # 显示文件列表
    with st.expander("📋 文件详情", expanded=True):
        for i, file in enumerate(uploaded_files, 1):
            file_name = file.name
            file_size = file.size
            file_ext = os.path.splitext(file_name)[1].lower()
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write(f"**{i}.** 📄 {file_name}")
            with col2:
                st.info(f"📏 {file_size} 字节")
            with col3:
                if file_ext in ['.c', '.h', '.java']:
                    st.success(f"✅ {file_ext}")
                else:
                    st.error(f"❌ {file_ext}")
else:
    st.info("请上传代码文件进行分析")

# 生成按钮
st.markdown("---")  # 分隔线
if st.button("🚀 生成文档报告", type="primary", use_container_width=True):
    if not uploaded_files:
        st.error("❌ 请先上传代码文件！")
        st.stop()
    
    # 验证所有文件类型
    invalid_files = []
    for file in uploaded_files:
        file_name = file.name
        file_ext = os.path.splitext(file_name)[1].lower()
        if file_ext not in ['.c', '.h', '.java']:
            invalid_files.append(file_name)
    
    if invalid_files:
        st.error(f"❌ 以下文件类型不支持: {', '.join(invalid_files)}。请上传 .c、.h 或 .java 文件。")
        st.stop()
    
    # 创建加载状态容器
    loading_container = st.container()
    
    with loading_container:
        all_docs_data = []
        
        # 处理所有上传的文件
        total_files = len(uploaded_files)
        progress_bar = st.progress(0)
        progress_text = st.empty()
        
        for i, uploaded_file in enumerate(uploaded_files):
            # 更新进度
            progress = (i + 1) / total_files
            progress_bar.progress(progress)
            progress_text.text(f"📄 正在处理文件 {i + 1}/{total_files}: {uploaded_file.name}")
            
            file_name = uploaded_file.name
            
            # 获取解析器
            try:
                parser = get_parser(file_name)
            except ModuleImportError as e:
                st.error(get_user_friendly_message(e))
                logger.error(f"模块导入错误: {str(e)}")
                st.stop()
            except Exception as e:
                st.error(f"⚠️ 获取解析器时出错: {get_user_friendly_message(e)}")
                logger.error(f"获取解析器失败 {file_name}: {str(e)}")
                st.stop()
            
            if parser:
                try:
                    # 读取上传文件的内容
                    file_content = uploaded_file.getvalue().decode('utf-8')
                    if not file_content:
                        st.error(f"❌ 文件内容为空: {file_name}")
                        logger.error(f"文件内容为空: {file_name}")
                        st.stop()
                    
                    parsed_data = parser.parse(file_content)
                    
                    # 检查解析状态
                    if parsed_data.get("status") == "error":
                        st.error(f"❌ 解析文件失败: {parsed_data.get('message', '未知错误')}")
                        logger.error(f"解析失败 {file_name}: {parsed_data.get('message', '未知错误')}")
                        st.stop()
                    
                    # 格式化 Doxygen 注释（如果存在）
                    if "file_docstring" in parsed_data and parsed_data["file_docstring"]:
                        parsed_data["formatted_file_docstring"] = format_doxygen_docstring(parsed_data["file_docstring"])
                    
                    # 格式化函数中的 Doxygen 注释
                    for func in parsed_data.get("functions", []):
                        if "docstring" in func and func["docstring"]:
                            func["formatted_docstring"] = format_doxygen_docstring(func["docstring"])
                    
                    # 格式化类/结构体中的 Doxygen 注释
                    for cls in parsed_data.get("classes", []):
                        if "docstring" in cls and cls["docstring"]:
                            cls["formatted_docstring"] = format_doxygen_docstring(cls["docstring"])
                    
                    # 格式化变量中的 Doxygen 注释
                    for var in parsed_data.get("variables", []):
                        if "docstring" in var and var["docstring"]:
                            var["formatted_docstring"] = format_doxygen_docstring(var["docstring"])
                    
                    parsed_data['file_name'] = file_name
                    all_docs_data.append(parsed_data)
                    
                except UnicodeDecodeError as e:
                    st.error(f"❌ 文件编码错误: 无法解码为UTF-8")
                    logger.error(f"文件编码错误 {file_name}: {str(e)}")
                    st.stop()
                except Exception as e:
                    st.error(f"❌ 解析文件时出错: {get_user_friendly_message(e)}")
                    logger.error(f"解析文件失败 {file_name}: {str(e)}")
                    st.stop()
        
        # 隐藏进度条
        progress_bar.empty()
        progress_text.empty()
        
        if not all_docs_data:
            st.error("❌ 分析失败，未能从文件中提取到有效信息。请检查文件内容。")
            st.stop()
        
            # 显示生成报告的加载状态
        try:
            with st.spinner("📝 正在生成 Markdown 报告..."):
                final_report = render_markdown(all_docs_data)
        except Exception as e:
            st.error(f"❌ 生成报告时发生错误: {get_user_friendly_message(e)}")
            logger.error(f"报告生成失败: {str(e)}", exc_info=True)
            st.stop()
        
        # 显示成功消息（带动画效果）
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%);
            color: white;
            padding: 1.5rem;
            border-radius: 8px;
            text-align: center;
            margin: 1rem 0;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            animation: slideIn 0.5s ease-out;
        ">
            <h5 style="margin: 0 0 0.5rem 0;">🎉 文档生成成功！</h5>
            <p style="margin: 0; font-size: 1.1rem;">
                成功解析了 <strong>{}</strong> 个文件
            </p>
        </div>
        <style>
        @keyframes slideIn {{
            from {{
                opacity: 0;
                transform: translateY(-20px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}
        </style>
        """.format(len(all_docs_data)), unsafe_allow_html=True)
        
        # 显示报告预览
        with st.expander("👁️ 报告预览", expanded=True):
            st.markdown(final_report)
        
        # 下载按钮
        st.download_button(
            "💾 下载Markdown报告", 
            final_report, 
            "documentation.md", 
            type="primary",
            use_container_width=True
        )

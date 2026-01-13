"""
渲染器模块

负责将解析器生成的结构化数据，通过 Jinja2 模板引擎渲染成最终的 Markdown 报告。
"""
import jinja2
import os
from .error_handler import (
    handle_file_access,
    logger,
    FileAccessError,
    get_user_friendly_message
)


@handle_file_access
def render_markdown(docs_data: list[dict]) -> str:
    """
    使用 Jinja2 模板渲染 Markdown 报告。

    Args:
        docs_data: 一个包含多个文件解析结果的列表。

    Returns:
        渲染完成的 Markdown 字符串。
    
    Raises:
        FileAccessError: 如果模板文件无法访问
        jinja2.TemplateError: 如果模板渲染失败
    """
    try:
        template_dir = os.path.join(os.path.dirname(__file__), '..', 'templates')
        
        # 验证模板目录是否存在
        if not os.path.exists(template_dir):
            error_msg = f"模板目录不存在: {template_dir}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        
        # 为每个文件单独渲染报告
        rendered_parts = []
        
        for file_data in docs_data:
            file_name = file_data['file_name']
            
            # 根据文件扩展名选择特定模板
            if file_name.endswith('.c') or file_name.endswith('.h'):
                template_name = 'report_c.md'
            elif file_name.endswith('.java'):
                template_name = 'report_java.md'
            else:
                # 对于其他类型文件，使用通用模板
                template_name = 'report.md'
            
            # 验证模板文件是否存在
            template_file = os.path.join(template_dir, template_name)
            if not os.path.exists(template_file):
                error_msg = f"模板文件不存在: {template_file}"
                logger.error(error_msg)
                raise FileNotFoundError(error_msg)
            
            # 创建 Jinja2 环境
            env = jinja2.Environment(
                loader=jinja2.FileSystemLoader(template_dir),
                autoescape=False
            )
            
            # 加载模板
            try:
                template = env.get_template(template_name)
            except jinja2.TemplateNotFound as e:
                error_msg = f"无法找到模板文件: {str(e)}"
                logger.error(error_msg)
                raise FileAccessError(
                    error_msg,
                    "❌ 模板文件缺失，请检查项目安装"
                ) from e
            
            # 渲染单个文件的报告
            try:
                # 将单个文件数据包装成列表以兼容模板
                single_file_data = [file_data]
                rendered_part = template.render(files_data=single_file_data)
                rendered_parts.append(rendered_part)
            except jinja2.TemplateError as e:
                error_msg = f"模板渲染失败: {str(e)}"
                logger.error(error_msg)
                raise FileAccessError(
                    error_msg,
                    f"⚠️ 报告生成失败: {str(e)}"
                ) from e
        
        # 合并所有部分的报告
        final_report = "\n\n---\n\n".join(rendered_parts)
        logger.info(f"成功渲染 {len(docs_data)} 个文件的报告")
        return final_report
    
    except (FileNotFoundError, PermissionError, OSError) as e:
        # 这些错误会被 @handle_file_access 装饰器捕获并处理
        raise
    except Exception as e:
        error_msg = f"渲染过程中发生未预期的错误: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise FileAccessError(
            error_msg,
            get_user_friendly_message(e)
        ) from e
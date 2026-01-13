"""
调度器模块

根据文件类型动态选择并返回合适的解析器实例。
这是实现语言可扩展性的核心。
"""
from .parsers.base import BaseParser
from .error_handler import handle_module_import, logger, ModuleImportError

# 使用延迟导入和错误处理来导入解析器
@handle_module_import
def _import_parsers():
    """导入所有解析器模块，处理可能的导入错误"""
    try:
        from .parsers.c import CParser
        from .parsers.java import JavaParser  
                
        return {
            ".c": CParser(),
            ".h": CParser(),
            ".java": JavaParser(),
        }
    except ImportError as e:
        logger.error(f"无法导入解析器模块: {str(e)}")
        raise ModuleImportError(
            f"解析器模块导入失败: {str(e)}",
            "❌ 无法加载解析器。请确保所有依赖已正确安装。"
        ) from e

# 解析器映射表
try:
    PARSER_MAPPING = _import_parsers()
except ModuleImportError as e:
    logger.error(f"初始化解析器失败: {str(e)}")
    PARSER_MAPPING = {}


def get_parser(file_name: str) -> BaseParser | None:
    """
    根据文件名后缀获取对应的解析器。

    Args:
        file_name: 包含后缀的文件名。

    Returns:
        返回一个解析器实例；如果找不到支持的类型，则返回 None。
    
    Raises:
        ModuleImportError: 如果解析器模块导入失败
    """
    if not PARSER_MAPPING:
        logger.error("解析器映射表为空，可能是模块导入失败")
        return None
    
    try:
        extension = "." + file_name.rsplit('.', 1)[-1] if '.' in file_name else ''
        parser = PARSER_MAPPING.get(extension)
        
        if parser is None:
            logger.debug(f"未找到文件类型 {extension} 的解析器")
        
        return parser
    except Exception as e:
        logger.error(f"获取解析器时发生错误: {str(e)}")
        return None
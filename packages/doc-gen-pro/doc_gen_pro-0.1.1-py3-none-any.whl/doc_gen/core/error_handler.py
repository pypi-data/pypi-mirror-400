"""
错误处理模块

提供统一的错误处理、日志记录和用户友好的错误消息。
"""
import logging
import os
from typing import Optional, Callable, Any
from functools import wraps

# 配置日志记录器
logger = logging.getLogger("doc_gen")
logger.setLevel(logging.INFO)

# 创建日志处理器（如果还没有）
if not logger.handlers:
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # 文件处理器（可选）
    try:
        log_dir = os.path.join(os.path.expanduser("~"), ".doc_gen", "logs")
        os.makedirs(log_dir, exist_ok=True)
        file_handler = logging.FileHandler(
            os.path.join(log_dir, "doc_gen.log"),
            encoding="utf-8"
        )
        file_handler.setLevel(logging.DEBUG)
        
        # 设置日志格式
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
    except (PermissionError, OSError):
        # 如果无法创建日志文件，只使用控制台处理器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)


class DocGenError(Exception):
    """文档生成器基础异常类"""
    def __init__(self, message: str, user_message: Optional[str] = None):
        super().__init__(message)
        self.user_message = user_message or message


class FileAccessError(DocGenError):
    """文件访问错误"""
    pass


class PathValidationError(DocGenError):
    """路径验证错误"""
    pass


class ModuleImportError(DocGenError):
    """模块导入错误"""
    pass


class ParsingError(DocGenError):
    """解析错误"""
    pass


def handle_file_access(func: Callable) -> Callable:
    """
    装饰器：处理文件访问相关的错误
    
    捕获 PermissionError, FileNotFoundError, OSError 等文件系统错误，
    并转换为用户友好的错误消息。
    """
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        try:
            return func(*args, **kwargs)
        except PermissionError as e:
            file_path = str(args[0]) if args else "未知文件"
            error_msg = f"权限不足，无法访问文件或目录: {file_path}"
            user_msg = f"⚠️ 权限不足，无法访问: {os.path.basename(file_path)}"
            logger.error(f"{error_msg} - {str(e)}")
            raise FileAccessError(error_msg, user_msg) from e
        except FileNotFoundError as e:
            file_path = str(args[0]) if args else "未知文件"
            error_msg = f"文件或目录不存在: {file_path}"
            user_msg = f"❌ 文件不存在: {os.path.basename(file_path)}"
            logger.error(f"{error_msg} - {str(e)}")
            raise PathValidationError(error_msg, user_msg) from e
        except OSError as e:
            file_path = str(args[0]) if args else "未知文件"
            error_msg = f"文件系统错误: {file_path} - {str(e)}"
            user_msg = f"⚠️ 无法访问文件: {os.path.basename(file_path)}"
            logger.error(error_msg)
            raise FileAccessError(error_msg, user_msg) from e
        except Exception as e:
            logger.error(f"未预期的错误: {str(e)}", exc_info=True)
            raise
    return wrapper


def handle_module_import(func: Callable) -> Callable:
    """
    装饰器：处理模块导入相关的错误
    
    捕获 ImportError, ModuleNotFoundError 等导入错误，
    并转换为用户友好的错误消息。
    """
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        try:
            return func(*args, **kwargs)
        except ImportError as e:
            module_name = str(e).split("'")[1] if "'" in str(e) else "未知模块"
            error_msg = f"无法导入模块: {module_name}"
            user_msg = f"❌ 缺少必需的模块: {module_name}。请检查依赖安装。"
            logger.error(f"{error_msg} - {str(e)}")
            raise ModuleImportError(error_msg, user_msg) from e
        except ModuleNotFoundError as e:
            module_name = str(e).split("'")[1] if "'" in str(e) else "未知模块"
            error_msg = f"找不到模块: {module_name}"
            user_msg = f"❌ 找不到模块: {module_name}。请运行 'uv pip install -e .' 安装项目。"
            logger.error(f"{error_msg} - {str(e)}")
            raise ModuleImportError(error_msg, user_msg) from e
        except Exception as e:
            logger.error(f"未预期的错误: {str(e)}", exc_info=True)
            raise
    return wrapper


def safe_file_read(file_path: str, encoding: str = "utf-8") -> Optional[str]:
    """
    安全地读取文件内容，处理各种可能的错误
    
    Args:
        file_path: 文件路径
        encoding: 文件编码，默认为 utf-8
    
    Returns:
        文件内容字符串，如果读取失败则返回 None
    """
    try:
        with open(file_path, "r", encoding=encoding) as f:
            return f.read()
    except PermissionError:
        logger.warning(f"权限不足，无法读取文件: {file_path}")
        return None
    except FileNotFoundError:
        logger.warning(f"文件不存在: {file_path}")
        return None
    except UnicodeDecodeError:
        # 尝试使用其他编码
        try:
            with open(file_path, "r", encoding="latin-1") as f:
                logger.info(f"使用 latin-1 编码读取文件: {file_path}")
                return f.read()
        except Exception as e:
            logger.error(f"无法读取文件 {file_path}: {str(e)}")
            return None
    except OSError as e:
        logger.error(f"文件系统错误，无法读取 {file_path}: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"读取文件时发生未预期的错误 {file_path}: {str(e)}")
        return None


def safe_path_validation(path: str) -> bool:
    """
    安全地验证路径是否存在且可访问
    
    Args:
        path: 要验证的路径
    
    Returns:
        如果路径有效且可访问返回 True，否则返回 False
    """
    try:
        # 规范化路径
        normalized_path = os.path.normpath(os.path.abspath(path))
        
        # 检查路径是否存在
        if not os.path.exists(normalized_path):
            logger.debug(f"路径不存在: {normalized_path}")
            return False
        
        # 检查是否可访问（尝试列出目录或读取文件信息）
        if os.path.isdir(normalized_path):
            os.listdir(normalized_path)
        else:
            os.stat(normalized_path)
        
        return True
    except PermissionError:
        logger.warning(f"权限不足，无法访问路径: {path}")
        return False
    except FileNotFoundError:
        logger.debug(f"路径不存在: {path}")
        return False
    except OSError as e:
        logger.warning(f"路径验证失败 {path}: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"路径验证时发生未预期的错误 {path}: {str(e)}")
        return False


def safe_directory_walk(root_path: str, max_depth: int = 3):
    """
    安全地遍历目录，处理权限错误和其他异常
    
    Args:
        root_path: 根目录路径
        max_depth: 最大递归深度
    
    Yields:
        (dirpath, dirnames, filenames) 元组
    """
    def _walk_with_depth(path: str, current_depth: int = 0):
        if current_depth >= max_depth:
            return
        
        try:
            entries = os.listdir(path)
        except PermissionError:
            logger.warning(f"权限不足，跳过目录: {path}")
            return
        except OSError as e:
            logger.warning(f"无法访问目录 {path}: {str(e)}")
            return
        
        dirs = []
        files = []
        
        for entry in entries:
            # 跳过隐藏文件和系统目录
            if entry.startswith('.') or entry in ['$RECYCLE.BIN', 'System Volume Information']:
                continue
            
            entry_path = os.path.join(path, entry)
            
            try:
                if os.path.isdir(entry_path):
                    dirs.append(entry)
                elif os.path.isfile(entry_path):
                    files.append(entry)
            except (PermissionError, OSError):
                # 跳过无法访问的条目
                continue
        
        yield path, dirs, files
        
        # 递归遍历子目录
        for dir_name in dirs:
            dir_path = os.path.join(path, dir_name)
            yield from _walk_with_depth(dir_path, current_depth + 1)
    
    yield from _walk_with_depth(root_path)


def log_error(error: Exception, context: str = "") -> None:
    """
    记录错误日志
    
    Args:
        error: 异常对象
        context: 错误上下文信息
    """
    if context:
        logger.error(f"{context}: {str(error)}", exc_info=True)
    else:
        logger.error(str(error), exc_info=True)


def get_user_friendly_message(error: Exception) -> str:
    """
    将异常转换为用户友好的错误消息
    
    Args:
        error: 异常对象
    
    Returns:
        用户友好的错误消息字符串
    """
    if isinstance(error, DocGenError) and error.user_message:
        return error.user_message
    elif isinstance(error, PermissionError):
        return "⚠️ 权限不足，无法访问该文件或目录"
    elif isinstance(error, FileNotFoundError):
        return "❌ 文件或目录不存在"
    elif isinstance(error, ImportError):
        return "❌ 缺少必需的模块，请检查依赖安装"
    elif isinstance(error, SyntaxError):
        return f"⚠️ 代码语法错误: {str(error)}"
    elif isinstance(error, OSError):
        return "⚠️ 文件系统错误，请检查文件路径和权限"
    else:
        return f"❌ 发生错误: {str(error)}"

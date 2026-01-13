#!/usr/bin/env python3
"""
Java 语言解析器模块

使用正则表达式解析Java源代码，提取类、方法和变量信息。
"""
import re
from .base import BaseParser

class JavaParser(BaseParser):
    """Java语言解析器，用于提取类、方法和变量信息。"""
    
    def parse(self, file_content: str) -> dict:
        """
        解析Java源代码，提取类、方法和变量信息。
        
        Args:
            file_content: 要解析的Java源代码字符串。
            
        Returns:
            一个包含解析结果的字典，包含status、classes、functions和variables字段。
        """
        # 导入错误处理模块
        try:
            from ..error_handler import logger
        except ImportError:
            # 如果无法导入错误处理模块，使用基本的日志记录
            import logging
            logger = logging.getLogger(__name__)
        
        try:
            # 验证输入
            if not file_content:
                logger.warning("Java 解析器收到空内容")
                return {
                    "status": "warning",
                    "message": "文件内容为空",
                    "functions": [],
                    "classes": [],
                    "variables": [],
                    "imports": []
                }
            
            # 辅助函数：清理Javadoc注释
            def clean_javadoc_comment(comment):
                """清理Javadoc注释，移除星号和多余空白。"""
                if not comment:
                    return ""
                
                lines = comment.split("\n")
                cleaned_lines = []
                for line in lines:
                    # 移除前导和尾随空白
                    stripped = line.strip()
                    # 移除星号和前导空格
                    if stripped.startswith("*"):
                        stripped = stripped[1:].lstrip()
                    # 只添加非空行
                    if stripped:
                        cleaned_lines.append(stripped)
                return "\n".join(cleaned_lines).strip()
            
            # 辅助函数：提取Doxygen标签
            def extract_doxygen_tags(comment):
                """提取Doxygen标签并返回结构化数据。"""
                tags = {}
                
                if not comment:
                    return tags
                
                # 提取@brief
                brief_match = re.search(r'@brief\s+(.*?)(?:@|$)', comment, re.DOTALL)
                if brief_match:
                    tags['brief'] = brief_match.group(1).strip()
                
                # 提取@param
                param_matches = re.finditer(r'@param\s+(?:\[(in|out|in,out)\]\s+)?([a-zA-Z_][a-zA-Z0-9_]*)\s+(.*?)(?=@|$)', 
                                          comment, re.DOTALL)
                params = []
                for match in param_matches:
                    direction = match.group(1) or 'in'
                    name = match.group(2)
                    description = match.group(3).strip()
                    params.append({
                        'name': name,
                        'direction': direction,
                        'description': description
                    })
                if params:
                    tags['params'] = params
                
                # 提取@return
                return_match = re.search(r'@return\s+(.*?)(?:@|$)', comment, re.DOTALL)
                if return_match:
                    tags['return'] = return_match.group(1).strip()
                
                # 提取@throws或@exception
                throws_match = re.search(r'@(?:throws|exception)\s+(.*?)(?:@|$)', comment, re.DOTALL)
                if throws_match:
                    tags['throws'] = throws_match.group(1).strip()
                
                # 提取@note
                note_match = re.search(r'@note\s+(.*?)(?:@|$)', comment, re.DOTALL)
                if note_match:
                    tags['note'] = note_match.group(1).strip()
                
                # 提取@warning
                warning_match = re.search(r'@warning\s+(.*?)(?:@|$)', comment, re.DOTALL)
                if warning_match:
                    tags['warning'] = warning_match.group(1).strip()
                
                # 提取@deprecated
                if '@deprecated' in comment:
                    tags['deprecated'] = True
                
                # 提取@see
                see_matches = re.finditer(r'@see\s+(.*?)(?:@|$)', comment, re.DOTALL)
                sees = []
                for match in see_matches:
                    sees.append(match.group(1).strip())
                if sees:
                    tags['see'] = sees
                
                # 提取@author
                author_match = re.search(r'@author\s+(.*?)(?:@|$)', comment, re.DOTALL)
                if author_match:
                    tags['author'] = author_match.group(1).strip()
                
                # 提取@version
                version_match = re.search(r'@version\s+(.*?)(?:@|$)', comment, re.DOTALL)
                if version_match:
                    tags['version'] = version_match.group(1).strip()
                
                # 提取@since
                since_match = re.search(r'@since\s+(.*?)(?:@|$)', comment, re.DOTALL)
                if since_match:
                    tags['since'] = since_match.group(1).strip()
                
                return tags
            
            # 按行分割内容
            lines = file_content.split('\n')
            
            # 提取文件级Doxygen标签（文件开头的注释）
            file_doxygen_tags = {}
            file_docstring = ""
            
            # 检查文件开头是否有Doxygen注释
            if file_content.strip().startswith('/**'):
                # 找到第一个 */ 结束符
                end_pos = file_content.find('*/')
                if end_pos != -1:
                    file_comment = file_content[3:end_pos].strip()  # 移除 /** 和 */
                    file_docstring = clean_javadoc_comment(file_comment)
                    file_doxygen_tags = extract_doxygen_tags(file_docstring)
            
            # 解析导入语句
            imports = []
            import_pattern = r'^\s*(import\s+(static\s+)?([a-zA-Z0-9_.]+(?:\.[a-zA-Z0-9_]+)*));'
            for i, line in enumerate(lines):
                match = re.match(import_pattern, line)
                if match:
                    import_stmt, is_static, module = match.groups()
                    imports.append({
                        "type": "import",
                        "module": module,
                        "asname": None,
                        "line": i + 1
                    })
            
            # 解析类、接口和方法
            classes = []
            methods = []
            variables = []
            
            current_comment = ""
            in_comment = False
            
            for i, line in enumerate(lines):
                line_stripped = line.strip()
                
                # 处理Javadoc注释开始
                if line_stripped.startswith('/**'):
                    current_comment = line_stripped[3:].strip()  # 移除 /**
                    in_comment = True
                    continue
                
                # 处理注释中间行
                if in_comment:
                    if line_stripped.startswith('*/'):
                        # 注释结束
                        in_comment = False
                        continue
                    elif line_stripped.startswith('*'):
                        # 移除前导的 * 和空格
                        current_comment += '\n' + line_stripped[1:].strip()
                    else:
                        current_comment += '\n' + line_stripped
                    continue
                
                # 如果不在注释中，尝试匹配类定义
                if not in_comment and current_comment:
                    # 类定义模式
                    class_pattern = r'^\s*(?:public|protected|private)?\s*(?:abstract|final)?\s*(class|interface)\s+([a-zA-Z_][a-zA-Z0-9_]*)'
                    class_match = re.match(class_pattern, line)
                    
                    if class_match:
                        class_type, class_name = class_match.groups()
                        
                        # 清理注释
                        cleaned_comment = clean_javadoc_comment(current_comment)
                        doxygen_tags = extract_doxygen_tags(cleaned_comment)
                        
                        class_info = {
                            "name": class_name,
                            "bases": [],  # 简化处理，不解析继承关系
                            "docstring": cleaned_comment,
                            "doxygen_tags": doxygen_tags,
                            "methods": [],
                            "line": i + 1
                        }
                        classes.append(class_info)
                        
                        current_comment = ""
                        continue
                        
                    # 方法定义模式
                    method_pattern = r'^\s*(?:public|protected|private)?\s*(?:static)?\s*(?:final)?\s*([a-zA-Z_][a-zA-Z0-9_<>,\[\].]*)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(([^)]*)\)'
                    method_match = re.match(method_pattern, line)
                    
                    if method_match:
                        return_type, method_name, params = method_match.groups()
                        
                        # 检查是否是构造函数（方法名与当前类名相同）
                        is_constructor = False
                        if classes and method_name == classes[-1]["name"]:
                            is_constructor = True
                            return_type = ""  # 构造函数没有返回类型
                        
                        # 清理注释
                        cleaned_comment = clean_javadoc_comment(current_comment)
                        doxygen_tags = extract_doxygen_tags(cleaned_comment)
                        
                        method_info = {
                            "name": method_name,
                            "args": params.strip(),
                            "return_type": return_type.strip(),
                            "docstring": cleaned_comment,
                            "doxygen_tags": doxygen_tags,
                            "line": i + 1
                        }
                        methods.append(method_info)
                        
                        current_comment = ""
                        continue
                        
                    # 变量定义模式
                    var_pattern = r'^\s*(?:public|protected|private)?\s*(?:static)?\s*(?:final)?\s*([a-zA-Z_][a-zA-Z0-9_<>,\[\].]*)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*;'
                    var_match = re.match(var_pattern, line)
                    
                    if var_match:
                        var_type, var_name = var_match.groups()
                        
                        # 清理注释
                        cleaned_comment = clean_javadoc_comment(current_comment)
                        doxygen_tags = extract_doxygen_tags(cleaned_comment)
                        
                        var_info = {
                            "name": var_name,
                            "type": var_type.strip(),
                            "docstring": cleaned_comment,
                            "doxygen_tags": doxygen_tags,
                            "line": i + 1
                        }
                        variables.append(var_info)
                        
                        current_comment = ""
                        continue
                
                # 如果没有匹配到任何定义，清空当前注释
                if current_comment and not in_comment:
                    current_comment = ""
            
            # 返回最终结果
            logger.debug(f"成功解析 Java 文件: {len(classes)} 个类/接口, {len(methods)} 个方法, {len(variables)} 个变量, {len(imports)} 个导入")
            
            result = {
                "status": "success",
                "message": "Java文件解析成功",
                "functions": methods,
                "classes": classes,
                "variables": variables,
                "imports": imports
            }
            
            # 添加文件级Doxygen信息
            if file_docstring:
                result["file_docstring"] = file_docstring
            if file_doxygen_tags:
                result["file_doxygen_tags"] = file_doxygen_tags
                
            return result
        
        except re.error as e:
            # 正则表达式错误
            error_msg = f"Java 解析器正则表达式错误: {str(e)}"
            logger.error(error_msg)
            return {
                "status": "error",
                "message": error_msg,
                "functions": [],
                "classes": [],
                "variables": [],
                "imports": []
            }
        
        except Exception as e:
            # 捕获所有未预期的错误
            error_msg = f"Java 解析器发生未预期的错误: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {
                "status": "error",
                "message": error_msg,
                "functions": [],
                "classes": [],
                "variables": [],
                "imports": []
            }
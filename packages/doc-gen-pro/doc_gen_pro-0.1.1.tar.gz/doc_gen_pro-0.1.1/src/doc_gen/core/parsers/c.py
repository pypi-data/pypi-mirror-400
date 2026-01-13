"""
C语言解析器模块

使用正则表达式解析C语言源代码，提取函数、结构体和Doxygen注释信息。
"""
import re
from .base import BaseParser

class CParser(BaseParser):
    """C语言解析器，用于提取函数、结构体和Doxygen注释信息。"""
    
    def parse(self, file_content: str) -> dict:
        """
        解析C语言源代码，提取函数、结构体和Doxygen注释信息。
        
        Args:
            file_content: 要解析的C语言源代码字符串。
            
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
                logger.warning("C 解析器收到空内容")
                return {
                    "status": "success",
                    "message": "文件内容为空",
                    "functions": [],
                    "classes": [],
                    "variables": [],
                    "imports": [],
                    "file_docstring": ""
                }
            
            # 提取文件级注释
            file_docstring = ""
            file_doxygen_tags = {}
            file_doc_match = re.match(r"^(\/\*\*.*?\*\/)\s*", file_content, re.DOTALL)
            if file_doc_match:
                raw_file_doc = file_doc_match.group(1)
                # 解析文件级Doxygen注释
                file_doxygen_tags = self._parse_doxygen_comment(raw_file_doc)
                # 清理文件注释
                lines = []
                cleaned = raw_file_doc[3:-2].strip()
                for line in cleaned.split('\n'):
                    stripped = line.lstrip()
                    if stripped.startswith('*'):
                        stripped = stripped[1:].lstrip()
                    if stripped:
                        lines.append(stripped)
                file_docstring = '\n'.join(lines)
            
            # 定义匹配Doxygen注释块和代码签名的通用正则表达式
            DOC_BLOCK_AND_SIGNATURE_REGEX = r"""\s*               # 可选的前导空格
            (\/\*\*.*?\*\/)\s*                            # Group 1: Doxygen注释块
            (.*?)(?:;|\{)                                  # Group 2: 代码签名，直到分号或左花括号
            """
            functions = []
            classes = []
            variables = []
            macros = []
            
            # 查找所有匹配项
            for match in re.finditer(DOC_BLOCK_AND_SIGNATURE_REGEX, file_content, re.DOTALL | re.VERBOSE | re.MULTILINE):
                raw_comment = match.group(1)
                code_signature = match.group(2).strip()
                
                # 获取行号
                line_number = file_content[:match.start()].count('\n') + 1
                
                # 解析Doxygen注释
                doxygen_info = self._parse_doxygen_comment(raw_comment)
                
                # 解析代码签名
                signature_info = self._parse_c_signature(code_signature)
                
                # 合并两个字典
                combined_info = {
                    **doxygen_info,
                    **signature_info,
                    "line": line_number
                }
                
                # 检查是否是宏定义
                if code_signature.startswith('#define'):
                    # 解析宏定义
                    macro_name_match = re.search(r'#define\s+(\w+)', code_signature)
                    if macro_name_match:
                        macro_info = {
                            "name": macro_name_match.group(1),
                            "brief": doxygen_info.get("brief", ""),
                            "line": line_number
                        }
                        # 将宏定义添加到类型列表中（暂时）
                        classes.append(macro_info)
                else:
                    # 根据类型添加到不同的列表
                    if signature_info["type"] == "function":
                        functions.append(combined_info)
                    elif signature_info["type"] in ["struct", "enum", "typedef"]:
                        classes.append(combined_info)
                    elif signature_info["type"] == "variable":
                        variables.append(combined_info)
            
            # 返回最终结果
            logger.debug(f"成功解析 C 文件: {len(functions)} 个函数, {len(classes)} 个类型, {len(variables)} 个变量")
            
            result = {
                "status": "success",
                "message": "C语言文件解析成功",
                "functions": functions,
                "classes": classes,
                "variables": variables,
                "imports": [],
                "file_docstring": file_docstring
            }
            
            # 添加文件级Doxygen标签信息
            if file_doxygen_tags:
                result["file_doxygen_tags"] = file_doxygen_tags
                
            return result
        
        except re.error as e:
            # 正则表达式错误
            error_msg = f"C 解析器正则表达式错误: {str(e)}"
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
            error_msg = f"C 解析器发生未预期的错误: {str(e)}"
            logger.error(error_msg, exc_info=True)
            return {
                "status": "error",
                "message": error_msg,
                "functions": [],
                "classes": [],
                "variables": [],
                "imports": []
            }
    
    def _parse_doxygen_comment(self, raw_comment: str) -> dict:
        """
        解析Doxygen注释，提取结构化信息。
        
        Args:
            raw_comment: 原始的Doxygen注释字符串。
            
        Returns:
            包含结构化Doxygen信息的字典。
        """
        # 清理注释
        # 1. 移除开头的/**和结尾的*/
        cleaned_comment = raw_comment[3:-2].strip()
        # 2. 移除每行开头的*和空格
        lines = []
        for line in cleaned_comment.split('\n'):
            stripped = line.lstrip()
            if stripped.startswith('*'):
                stripped = stripped[1:].lstrip()
            if stripped:
                lines.append(stripped)
        cleaned_comment = '\n'.join(lines)
        
        # 初始化结果字典
        result = {
            "brief": "",
            "full_doc": "",
            "params": [],
            "returns": {},
            "note": "",
            "warning": "",
            "deprecated": "",
            "see": [],
            "todo": "",
            "author": "",
            "version": "",
            "date": "",
            "copyright": "",
            "docstring": cleaned_comment,
            "formatted_docstring": ""  # 用于存储格式化后的文档
        }
        
        # 提取@brief
        brief_match = re.search(r'@brief\s+(.*?)(?:@|$)', cleaned_comment, re.DOTALL)
        if brief_match:
            result["brief"] = brief_match.group(1).strip()
        
        # 提取@return
        return_match = re.search(r'@return\s+(.*?)(?:@|$)', cleaned_comment, re.DOTALL)
        if return_match:
            result["returns"] = {
                "doc": return_match.group(1).strip()
            }
        
        # 提取@param
        # 使用新的正则表达式，能够正确匹配多行@param标签
        param_pattern = r'@param\s+(?:\[(in|out|in,out)\]\s+)?([a-zA-Z_][a-zA-Z0-9_]*)\s+([^@]*)'
        param_matches = re.finditer(param_pattern, cleaned_comment, re.MULTILINE)
        for match in param_matches:
            direction = match.group(1) or "in"
            # 映射方向为中文
            direction_map = {
                "in": "输入",
                "out": "输出",
                "in,out": "输入输出"
            }
            direction_zh = direction_map.get(direction, direction)
            name = match.group(2)
            description = match.group(3).strip()
            result["params"].append({
                "direction": direction_zh,
                "name": name,
                "doc": description
            })
        
        # 如果仍然没有匹配到参数，尝试分割字符串的方式提取
        if not result["params"] and "@param" in cleaned_comment:
            # 按@分割字符串，然后逐个处理
            comment_parts = cleaned_comment.split('@')
            for part in comment_parts:
                if part.startswith('param'):
                    # 提取param部分
                    param_line = part[5:].strip()
                    if param_line:
                        # 尝试解析方向和名称
                        if '[' in param_line and ']' in param_line:
                            # 有方向指示符
                            dir_end = param_line.find(']')
                            direction = param_line[1:dir_end]
                            # 映射方向为中文
                            direction_map = {
                                "in": "输入",
                                "out": "输出",
                                "in,out": "输入输出"
                            }
                            direction_zh = direction_map.get(direction, direction)
                            # 提取名称和描述
                            name_desc = param_line[dir_end+1:].strip()
                            if name_desc:
                                name_end = name_desc.find(' ')
                                if name_end != -1:
                                    name = name_desc[:name_end]
                                    description = name_desc[name_end+1:].strip()
                                else:
                                    name = name_desc
                                    description = ""
                            # 使用中文方向
                            direction = direction_zh
                        else:
                            # 没有方向指示符
                            direction = "in"
                            # 提取名称和描述
                            name_end = param_line.find(' ')
                            if name_end != -1:
                                name = param_line[:name_end]
                                description = param_line[name_end+1:].strip()
                            else:
                                name = param_line
                                description = ""
                        
                        result["params"].append({
                            "direction": direction,
                            "name": name,
                            "doc": description
                        })
        
        # 提取@note
        note_match = re.search(r'@note\s+(.*?)(?:@|$)', cleaned_comment, re.DOTALL)
        if note_match:
            result["note"] = note_match.group(1).strip()
        
        # 提取@warning
        warning_match = re.search(r'@warning\s+(.*?)(?:@|$)', cleaned_comment, re.DOTALL)
        if warning_match:
            result["warning"] = warning_match.group(1).strip()
        
        # 提取@deprecated
        deprecated_match = re.search(r'@deprecated\s*(.*?)(?:@|$)', cleaned_comment, re.DOTALL)
        if deprecated_match:
            result["deprecated"] = deprecated_match.group(1).strip()
        
        # 提取@see
        see_match = re.search(r'@see\s+(.*?)(?:@|$)', cleaned_comment, re.DOTALL)
        if see_match:
            see_content = see_match.group(1).strip()
            # 如果有多个参考项，用逗号分隔
            result["see"] = [item.strip() for item in see_content.split(',')]
        
        # 提取@todo
        todo_match = re.search(r'@todo\s+(.*?)(?:@|$)', cleaned_comment, re.DOTALL)
        if todo_match:
            result["todo"] = todo_match.group(1).strip()
        
        # 提取@author
        author_match = re.search(r'@author\s+(.*?)(?:@|$)', cleaned_comment, re.DOTALL)
        if author_match:
            result["author"] = author_match.group(1).strip()
        
        # 提取@version
        version_match = re.search(r'@version\s+(.*?)(?:@|$)', cleaned_comment, re.DOTALL)
        if version_match:
            result["version"] = version_match.group(1).strip()
        
        # 提取@date
        date_match = re.search(r'@date\s+(.*?)(?:@|$)', cleaned_comment, re.DOTALL)
        if date_match:
            result["date"] = date_match.group(1).strip()
        
        # 提取@copyright
        copyright_match = re.search(r'@copyright\s+(.*?)(?:@|$)', cleaned_comment, re.DOTALL)
        if copyright_match:
            result["copyright"] = copyright_match.group(1).strip()
        
        # 提取full_doc（所有非命令行的文本）
        # 先移除所有命令行
        full_doc = re.sub(r'@[a-zA-Z]+\s+.*?(?=@|$)', '', cleaned_comment, flags=re.DOTALL)
        full_doc = full_doc.strip()
        result["full_doc"] = full_doc
        
        # 格式化docstring，将Doxygen命令转换为Markdown格式
        formatted = cleaned_comment
        
        # 替换@brief
        if brief_match:
            formatted = re.sub(r'@brief\s+(.*?)(?:@|$)', r'\1\n', formatted, flags=re.DOTALL)
        
        # 替换@author
        author_match = re.search(r'@author\s+(.*?)(?:@|$)', formatted, re.DOTALL)
        if author_match:
            formatted = re.sub(r'@author\s+(.*?)(?:@|$)', r'**作者**: \1\n', formatted, flags=re.DOTALL)
        
        # 替换@version
        version_match = re.search(r'@version\s+(.*?)(?:@|$)', formatted, re.DOTALL)
        if version_match:
            formatted = re.sub(r'@version\s+(.*?)(?:@|$)', r'**版本**: \1\n', formatted, flags=re.DOTALL)
        
        # 替换@date
        date_match = re.search(r'@date\s+(.*?)(?:@|$)', formatted, re.DOTALL)
        if date_match:
            formatted = re.sub(r'@date\s+(.*?)(?:@|$)', r'**日期**: \1\n', formatted, flags=re.DOTALL)
        
        # 替换@copyright
        copyright_match = re.search(r'@copyright\s+(.*?)(?:@|$)', formatted, re.DOTALL)
        if copyright_match:
            formatted = re.sub(r'@copyright\s+(.*?)(?:@|$)', r'**版权**: \1\n', formatted, flags=re.DOTALL)
        
        # 替换@note
        note_match = re.search(r'@note\s+(.*?)(?:@|$)', formatted, re.DOTALL)
        if note_match:
            formatted = re.sub(r'@note\s+(.*?)(?:@|$)', r'**注意**: \1\n', formatted, flags=re.DOTALL)
        
        # 替换@section
        formatted = re.sub(r'@section\s+\w+\s+([^\n]+)\n', r'## \1\n', formatted)
        
        # 清理多余的空行
        formatted = re.sub(r'\n{3,}', '\n\n', formatted)
        
        result["formatted_docstring"] = formatted.strip()
        
        return result
    
    def _parse_c_signature(self, signature: str) -> dict:
        """
        解析C代码签名，判断类型并提取信息。
        
        Args:
            signature: C代码签名字符串。
            
        Returns:
            包含签名信息的字典。
        """
        # 初始化结果字典
        result = {
            "type": "",
            "name": "",
            "return_type": "",
            "signature_args": "",
            "doxygen_tags": {}
        }
        
        # 检查是否是typedef
        typedef_match = re.match(r'typedef\s+(.*)', signature)
        if typedef_match:
            typedef_content = typedef_match.group(1).strip()
            
            # 检查是否是typedef函数指针
            func_ptr_match = re.match(r'(.*?)\s*\(\*([a-zA-Z_][a-zA-Z0-9_]*)\)\s*\((.*?)\)', typedef_content)
            if func_ptr_match:
                result["type"] = "function"
                result["return_type"] = f"typedef {func_ptr_match.group(1).strip()}"
                result["name"] = func_ptr_match.group(2).strip()
                result["signature_args"] = func_ptr_match.group(3).strip()
                return result
            
            # 检查是否是typedef enum
            enum_match = re.match(r'enum\s+(?:\w+\s+)?\{', typedef_content)
            if enum_match:
                # 提取typedef后的enum名称
                enum_name_match = re.search(r'\}\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*$', typedef_content)
                if enum_name_match:
                    result["type"] = "enum"
                    result["name"] = enum_name_match.group(1).strip()
                else:
                    # 匿名enum
                    result["type"] = "enum"
                    result["name"] = "anonymous_enum"
                return result
            
            # 检查是否是typedef struct
            struct_match = re.match(r'struct\s+(?:\w+\s+)?\{', typedef_content)
            if struct_match:
                # 提取typedef后的struct名称
                struct_name_match = re.search(r'\}\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*$', typedef_content)
                if struct_name_match:
                    result["type"] = "struct"
                    result["name"] = struct_name_match.group(1).strip()
                else:
                    # 匿名struct
                    result["type"] = "struct"
                    result["name"] = "anonymous_struct"
                return result
            
            # 其他typedef
            result["type"] = "typedef"
            # 尝试提取名称
            name_match = re.search(r'([a-zA-Z_][a-zA-Z0-9_]*)$', typedef_content)
            if name_match:
                result["name"] = name_match.group(1).strip()
            return result
        
        # 检查是否是函数
        function_pattern = r'([a-zA-Z_][a-zA-Z0-9_\s*\[\]]+)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\((.*?)\)'
        function_match = re.match(function_pattern, signature)
        if function_match:
            result["type"] = "function"
            result["return_type"] = function_match.group(1).strip()
            result["name"] = function_match.group(2).strip()
            result["signature_args"] = function_match.group(3).strip()
            return result
        
        # 检查是否是struct
        struct_match = re.match(r'struct\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\{', signature)
        if struct_match:
            result["type"] = "struct"
            result["name"] = struct_match.group(1).strip()
            return result
        
        # 检查是否是enum
        enum_match = re.match(r'enum\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\{', signature)
        if enum_match:
            result["type"] = "enum"
            result["name"] = enum_match.group(1).strip()
            return result
        
        # 检查是否是变量声明
        variable_pattern = r'([a-zA-Z_][a-zA-Z0-9_\s*\[\]]+)\s+([a-zA-Z_][a-zA-Z0-9_]*)'
        variable_match = re.match(variable_pattern, signature)
        if variable_match:
            result["type"] = "variable"
            result["return_type"] = variable_match.group(1).strip()
            result["name"] = variable_match.group(2).strip()
            return result
        
        # 默认情况
        result["type"] = "unknown"
        return result

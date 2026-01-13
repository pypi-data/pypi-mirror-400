"""
定义所有解析器必须遵守的抽象基类（ABC）。
这确保了所有解析器都有一致的接口。
"""
from abc import ABC, abstractmethod

class BaseParser(ABC):
    """解析器抽象基类。"""

    @abstractmethod
    def parse(self, file_content: str) -> dict:
        """
        解析给定的文件内容字符串。

        Args:
            file_content: 要解析的源代码字符串。

        Returns:
            一个包含解析后结构化数据的字典。
        """
        pass
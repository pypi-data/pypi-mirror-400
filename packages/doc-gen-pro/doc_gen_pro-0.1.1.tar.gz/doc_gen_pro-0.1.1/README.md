# 源代码文档生成器 (Doc-Gen Pro)

## 项目概述

这是一个基于 Streamlit 构建的、支持多语言的源代码文档生成工具。它能够自动分析源代码文件，提取其中的类、函数、变量等结构信息，并生成美观易读的 Markdown 文档。

本项目专注于 **C 语言** 和 **Java 语言** 的 Doxygen 文档注释解析，能够从源代码中提取 Doxygen 格式的注释信息，生成专业的 API 文档。

## 功能特性

- **多语言支持**: 专注于 C 和 Java 语言的 Doxygen 文档解析
- **Doxygen 注释提取**: 智能识别 `@file`、`@author`、`@version`、`@brief`、`@param`、`@return` 等常用 Doxygen 标签
- **美观报告**: 生成简洁美观的 Markdown 格式文档
- **批量处理**: 支持同时上传多个源文件进行批量文档生成
- **文件信息展示**: 自动提取文件级别的 Doxygen 信息（作者、版本、日期等）
- **用户友好**: 基于 Streamlit 的直观 Web 界面
- **模块化设计**: 清晰的项目架构，便于维护和扩展

## 技术栈

| 技术 | 用途 |
|------|------|
| **Streamlit** | Web 应用框架 |
| **Jinja2** | Markdown 模板引擎 |
| **正则表达式** | 源代码解析和注释提取 |
| **uv** | Python 包管理器 |
| **pytest** | 测试框架 |

## 项目结构

```
doc-generator/
├── start.py                    # 项目唯一启动入口
├── pyproject.toml              # 项目配置文件
├── README.md                   # 项目说明文档
├── .gitignore                  # Git 忽略文件配置
├── .streamlit/                 # Streamlit 配置
│   └── config.toml             # 主题和服务器配置
├── src/
│   └── doc_gen/                # 主包
│       ├── core/               # 核心业务逻辑
│       │   ├── __init__.py
│       │   ├── orchestrator.py # 解析器调度器
│       │   ├── renderer.py     # Markdown 渲染器
│       │   ├── error_handler.py# 错误处理和日志
│       │   └── parsers/        # 语言解析器
│       │       ├── __init__.py
│       │       ├── base.py     # 解析器抽象基类
│       │       ├── c.py        # C 语言解析器
│       │       └── java.py     # Java 解析器
│       ├── templates/          # Markdown 模板
│       │   ├── report_c.md     # C 语言文档模板
│       │   └── report_java.md  # Java 文档模板
│       └── app/                # Streamlit 应用
│           ├── __init__.py
│           ├── main.py         # 应用主入口
│           └── pages/
│               ├── __init__.py
│               ├── generator.py# 文档生成页面
│               └── about.py    # 关于页面
├── docs/                       # 文档目录
│   ├── development.md          # 开发文档
│   ├── technical.md            # 技术文档
│   └── example/                # 示例文件目录
│       ├── test_doxygen.h      # C 语言测试文件
│       ├── test_comprehensive_doxygen.java # Java 测试文件
│       └── ...
├── tests/                      # 测试目录
│   ├── unit/                   # 单元测试
│   │   ├── test_c_parser.py
│   │   └── test_java_parser.py
│   └── integration/            # 集成测试
│       └── test_workflow.py
```

## 安装与运行

### 从 PyPI 安装

```bash
# 使用 pip 安装
pip install doc-gen-pro

# 或使用 uv
uv add doc-gen-pro
```

### 从源码安装

```bash
# 克隆项目
git clone <repository-url>
cd doc-generator

# 安装依赖
uv pip install -e .
```

### 运行应用

#### Web 界面模式

```bash
# 使用启动脚本
uv run python start.py

# 或直接使用 Streamlit
uv run streamlit run src/doc_gen/app/main.py
```

应用启动后，访问 `http://localhost:8501`

#### 命令行模式

```bash
# 基本用法
doc-gen --source ./src --language c --output ./docs

# 详细输出
doc-gen --source ./src --language java --output ./docs --verbose

# 指定模板
doc-gen --source ./test.c --language c --output ./docs --template custom

# 查看帮助
doc-gen --help
```

## 使用指南

### 基本流程

1. 访问应用首页
2. 进入"文档生成器"页面
3. 点击"选择文件"按钮，选择一个或多个源文件（`.c`、`.h`、`.java`）
4. 点击"生成文档"按钮
5. 预览或下载生成的 Markdown 文档

### Doxygen 注释规范

#### C 语言示例

```c
/**
 * @file example.h
 * @brief 示例头文件
 * @author 张三
 * @version 1.0
 * @date 2025-12-27
 */

/**
 * @brief 计算两个整数的和
 * @param a 第一个加数
 * @param b 第二个加数
 * @return 两个整数的和
 */
int add(int a, int b);

/**
 * @brief 数据结构体
 */
typedef struct {
    int id;           /**< 成员 ID */
    char* name;       /**< 成员名称 */
} Data;
```

#### Java 语言示例

```java
/**
 * @file Example.java
 * @brief 示例类
 * @author 李四
 * @version 2.0
 * @date 2025-12-27
 */

public class Example {
    /**
     * @brief 默认构造函数
     */
    public Example() {
    }

    /**
     * @brief 带参数的构造函数
     * @param id 标识符
     * @param name 名称
     */
    public Example(int id, String name) {
    }

    /**
     * @brief 计算两个数的乘积
     * @param a 第一个乘数
     * @param b 第二个乘数
     * @return 两个数的乘积
     */
    public int multiply(int a, int b) {
        return a * b;
    }
}
```

### 支持的 Doxygen 标签

| 标签 | 说明 | 支持语言 |
|------|------|----------|
| `@file` | 文件名说明 | C, Java |
| `@brief` | 简要说明 | C, Java |
| `@author` | 作者信息 | C, Java |
| `@version` | 版本号 | C, Java |
| `@date` | 日期 | C, Java |
| `@param` | 参数说明 | C, Java |
| `@return` | 返回值说明 | C, Java |
| `@retval` | 返回值说明 | C, Java |
| `@note` | 备注 | C, Java |
| `@warning` | 警告信息 | C, Java |
| `@see` | 参见 | C, Java |
| `@deprecated` | 废弃说明 | C, Java |

## 测试说明

### 运行测试

```bash
# 运行所有测试
uv run python tests/run_tests.py

# 运行快速测试
uv run python tests/quick_test.py

# 运行集成测试
uv run python tests/integration/test_workflow.py

# 运行单元测试
uv run python tests/unit/test_c_parser.py
uv run python tests/unit/test_java_parser.py
```

### 测试覆盖

- C 语言解析器单元测试
- Java 解析器单元测试
- 完整工作流程集成测试
- 模板渲染测试

## 项目架构

### 核心模块

```
src/doc_gen/core/
├── orchestrator.py     # 根据文件扩展名选择解析器
├── renderer.py         # 使用 Jinja2 渲染 Markdown
├── error_handler.py    # 统一错误处理
└── parsers/
    ├── base.py         # 解析器抽象基类
    ├── c.py            # C 语言解析器
    └── java.py         # Java 解析器
```

### 解析器设计

所有解析器继承自 `BaseParser`，实现 `parse` 方法：

```python
class BaseParser:
    def parse(self, file_content: str, file_path: str = "") -> dict:
        """解析源代码，返回结构化数据"""
        pass

class CParser(BaseParser):
    def parse(self, file_content: str, file_path: str = "") -> dict:
        # 实现 C 语言解析逻辑
        pass

class JavaParser(BaseParser):
    def parse(self, file_content: str, file_path: str = "") -> dict:
        # 实现 Java 解析逻辑
        pass
```

### 模板系统

使用 Jinja2 模板引擎，支持条件渲染和循环：

```markdown
# {{ file_name }}

{% if file_docstring %}
## 📄 文件信息
{{ file_docstring }}
{% endif %}

{% if functions %}
## 📌 函数
{% for func in functions %}
### {{ func.name }}
...
{% endfor %}
{% endif %}
```

## 版本历史

### v1.0.0 (2025-12-27)

- 初始版本发布
- 支持 C 和 Java 语言的 Doxygen 注释解析
- 实现批量文件上传和处理
- 提供美观的 Markdown 文档模板
- 完整的单元测试和集成测试覆盖



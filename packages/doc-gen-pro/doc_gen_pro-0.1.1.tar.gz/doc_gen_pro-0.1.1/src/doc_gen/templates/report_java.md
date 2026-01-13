# API 参考文档

{% for file_data in files_data %}
## {{ file_data.file_name }}

**状态**: {{ file_data.message }}

{% if file_data.file_doxygen_tags %}
### 📄 文件信息

{% if file_data.file_doxygen_tags.author %}
**👤 作者**: {{ file_data.file_doxygen_tags.author }}
{% endif %}

{% if file_data.file_doxygen_tags.version %}
**🔗 版本**: {{ file_data.file_doxygen_tags.version }}
{% endif %}

{% if file_data.file_doxygen_tags.since %}
**📅 引入版本**: {{ file_data.file_doxygen_tags.since }}
{% endif %}

{% if file_data.file_doxygen_tags.deprecated %}
**🚫 已废弃**: 此文件已废弃，不再建议使用
{% endif %}

{% if file_data.file_doxygen_tags.warning %}
**⚠️ 警告**: {{ file_data.file_doxygen_tags.warning }}
{% endif %}

{% if file_data.file_doxygen_tags.note %}
**📌 注意**: {{ file_data.file_doxygen_tags.note }}
{% endif %}

{% if file_data.file_doxygen_tags.see %}
**📋 参考**: 
{% for see_item in file_data.file_doxygen_tags.see %}
- {{ see_item }}
{% endfor %}
{% endif %}

{% if file_data.file_docstring %}
**📖 文件描述**:
{{ file_data.file_docstring }}
{% endif %}

---

{% endif %}

{% if file_data.imports %}
### 📥 导入语句 ({{ file_data.imports|length }})
```
{% for import_item in file_data.imports %}
{{ import_item.module }}
{% endfor %}
```
{% endif %}

{% if file_data.classes %}
### 🏷️ 类与接口 ({{ file_data.classes|length }})

{% for class_item in file_data.classes %}
#### 🏷️ 类 `{{ class_item.name }}{% if class_item.bases %} ({{ ', '.join(class_item.bases) }}){% endif %}`

*第 {{ class_item.line }} 行*

{% if class_item.docstring %}
{{ class_item.docstring }}
{% endif %}

{% if (class_item.doxygen_tags | default({}, true)).brief %}
**📋 简要说明**: {{ (class_item.doxygen_tags | default({}, true)).brief }}
{% endif %}

{% if (class_item.doxygen_tags | default({}, true)).author %}
**👤 作者**: {{ (class_item.doxygen_tags | default({}, true)).author }}
{% endif %}

{% if (class_item.doxygen_tags | default({}, true)).version %}
**🔗 版本**: {{ (class_item.doxygen_tags | default({}, true)).version }}
{% endif %}

{% if (class_item.doxygen_tags | default({}, true)).since %}
**📅 引入版本**: {{ (class_item.doxygen_tags | default({}, true)).since }}
{% endif %}

{% if (class_item.doxygen_tags | default({}, true)).deprecated %}
**🚫 已废弃**: 此类已废弃，不再建议使用
{% endif %}

{% if (class_item.doxygen_tags | default({}, true)).warning %}
**⚠️ 警告**: {{ (class_item.doxygen_tags | default({}, true)).warning }}
{% endif %}

{% if (class_item.doxygen_tags | default({}, true)).note %}
**📌 注意**: {{ (class_item.doxygen_tags | default({}, true)).note }}
{% endif %}

{% if (class_item.doxygen_tags | default({}, true)).see %}
**🔗 参考**: 
{% for see_item in (class_item.doxygen_tags | default({}, true)).see %}
- {{ see_item }}
{% endfor %}
{% endif %}

{% endfor %}
{% endif %}

{% if file_data.functions %}
### 🔧 函数与方法 ({{ file_data.functions|length }})

{% for function in file_data.functions %}
#### `{% if file_data.file_name.endswith('.java') %}{{ function.return_type }} {% endif %}{{ function.name }}({{ function.args }})`

*第 {{ function.line }} 行*

{% if function.docstring %}
{{ function.docstring }}
{% endif %}

{% if (function.doxygen_tags | default({}, true)).params %}
**📥 参数列表**
| 参数名 | 方向 | 描述 |
|-------|------|------|
{% for param in (function.doxygen_tags | default({}, true)).params %}
| {{ param.name }} | {{ param.direction }} | {{ param.description }} |
{% endfor %}
{% endif %}

{% if (function.doxygen_tags | default({}, true)).return %}
**📤 返回值**: {{ (function.doxygen_tags | default({}, true)).return }}
{% endif %}

{% if (function.doxygen_tags | default({}, true)).throws %}
**⚠️ 异常抛出**: {{ (function.doxygen_tags | default({}, true)).throws }}
{% endif %}

{% if (function.doxygen_tags | default({}, true)).deprecated %}
**🚫 已废弃**: 此函数已废弃，不再建议使用
{% endif %}

{% if (function.doxygen_tags | default({}, true)).since %}
**📅 引入版本**: {{ (function.doxygen_tags | default({}, true)).since }}
{% endif %}

{% if (function.doxygen_tags | default({}, true)).warning %}
**⚠️ 警告**: {{ (function.doxygen_tags | default({}, true)).warning }}
{% endif %}

{% if (function.doxygen_tags | default({}, true)).note %}
**📌 注意**: {{ (function.doxygen_tags | default({}, true)).note }}
{% endif %}

{% if (function.doxygen_tags | default({}, true)).todo %}
**📝 待办事项**: {{ (function.doxygen_tags | default({}, true)).todo }}
{% endif %}

{% if (function.doxygen_tags | default({}, true)).see %}
**🔗 参考**: 
{% for see_item in (function.doxygen_tags | default({}, true)).see %}
- {{ see_item }}
{% endfor %}
{% endif %}

{% endfor %}
{% endif %}

{% if file_data.variables %}
### 📦 成员变量 ({{ file_data.variables|length }})

{% for variable in file_data.variables %}
#### 📊 变量 `{{ variable.type }} {{ variable.name }}`

*第 {{ variable.line }} 行*

{% if variable.docstring %}
{{ variable.docstring }}
{% endif %}

{% if (variable.doxygen_tags | default({}, true)).note %}
**📌 注意**: {{ (variable.doxygen_tags | default({}, true)).note }}
{% endif %}

{% if (variable.doxygen_tags | default({}, true)).warning %}
**⚠️ 警告**: {{ (variable.doxygen_tags | default({}, true)).warning }}
{% endif %}

{% endfor %}
{% endif %}

---

{% endfor %}
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

{% if file_data.file_doxygen_tags.date %}
**📅 日期**: {{ file_data.file_doxygen_tags.date }}
{% endif %}

{% if file_data.file_doxygen_tags.deprecated %}
**🚫 已废弃**: {{ file_data.file_doxygen_tags.deprecated }}
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

{% if file_data.file_doxygen_tags.copyright %}
**© 版权**: {{ file_data.file_doxygen_tags.copyright }}
{% endif %}

{% if file_data.file_doxygen_tags.full_doc %}
**📖 文件描述**:
{{ file_data.file_doxygen_tags.full_doc }}
{% endif %}

---

{% endif %}

{% if file_data.variables %}
### 🔤 全局变量 ({{ file_data.variables|length }})

{% for variable in file_data.variables %}
#### `{{ variable.return_type }} {{ variable.name }}`

*第 {{ variable.line }} 行*

{% if variable.brief %}
**📋 简述**: {{ variable.brief }}
{% endif %}

{% if variable.author %}
**👤 作者**: {{ variable.author }}
{% endif %}

{% if variable.version %}
**🔢 版本**: {{ variable.version }}
{% endif %}

{% if variable.date %}
**📅 日期**: {{ variable.date }}
{% endif %}

{% if variable.note %}
**📌 注意**: {{ variable.note }}
{% endif %}

{% if variable.warning %}
**⚠️ 警告**: {{ variable.warning }}
{% endif %}

{% if variable.copyright %}
** © 版权**: {{ variable.copyright }}
{% endif %}

{% if variable.deprecated %}
**🚫 已弃用**: {{ variable.deprecated }}
{% endif %}

{% if variable.todo %}
**📝 待办**: {{ variable.todo }}
{% endif %}

{% if variable.see %}
**🔗 参考**: 
{% for see_item in variable.see %}
- {{ see_item }}
{% endfor %}
{% endif %}

{% endfor %}
{% endif %}

{% if file_data.classes %}
### 🏷️ 类型定义 ({{ file_data.classes|length }})

{% for class_item in file_data.classes %}
#### {% if class_item.type == 'enum' %}🔢 {% else %}📊 {% endif %}{% if class_item.type == 'enum' %}枚举{% else %}类型{% endif %} `{{ class_item.name }}`

*第 {{ class_item.line }} 行*

{% if class_item.brief %}
**📋 简述**: {{ class_item.brief }}
{% endif %}

{% if class_item.author %}
**👤 作者**: {{ class_item.author }}
{% endif %}

{% if class_item.version %}
**🔢 版本**: {{ class_item.version }}
{% endif %}

{% if class_item.date %}
**📅 日期**: {{ class_item.date }}
{% endif %}

{% if class_item.see %}
**🔗 参考**: 
{% for see_item in class_item.see %}
- {{ see_item }}
{% endfor %}
{% endif %}

{% if class_item.note %}
**📌 注意**: {{ class_item.note }}
{% endif %}

{% if class_item.warning %}
**⚠️ 警告**: {{ class_item.warning }}
{% endif %}

{% if class_item.copyright %}
** © 版权**: {{ class_item.copyright }}
{% endif %}

{% if class_item.deprecated %}
**🚫 已弃用**: {{ class_item.deprecated }}
{% endif %}

{% if class_item.todo %}
**📝 待办**: {{ class_item.todo }}
{% endif %}

{% if class_item.full_doc %}
{{ class_item.full_doc }}
{% endif %}

{% endfor %}
{% endif %}

{% if file_data.functions %}
### 🔧 函数 ({{ file_data.functions|length }})

{% for function in file_data.functions %}
#### `{{ function.return_type }} {{ function.name }}({{ function.signature_args }})`

*第 {{ function.line }} 行*

{% if function.brief %}
**📋 简述**: {{ function.brief }}
{% endif %}

{% if function.author %}
**👤 作者**: {{ function.author }}
{% endif %}

{% if function.version %}
**🔢 版本**: {{ function.version }}
{% endif %}

{% if function.date %}
**📅 日期**: {{ function.date }}
{% endif %}

{% if function.params %}
**📥 参数列表**
| 参数名 | 方向 | 描述 |
|-------|------|------|
{% for param in function.params %}
| {{ param.name }} | {{ param.direction }} | {{ param.doc }} |
{% endfor %}
{% endif %}

{% if function.returns and function.returns.doc %}
**📤 返回值**: {{ function.returns.doc }}
{% endif %}

{% if function.pre %}
**🔍 前置条件**: {{ function.pre }}
{% endif %}

{% if function.post %}
**✅ 后置条件**: {{ function.post }}
{% endif %}

{% if function.deprecated %}
**🚫 已弃用**: {{ function.deprecated }}
{% endif %}

{% if function.todo %}
**📝 待办事项**: {{ function.todo }}
{% endif %}

{% if function.copyright %}
** © 版权**: {{ function.copyright }}
{% endif %}

{% if function.note %}
**📌 注意**: {{ function.note }}
{% endif %}

{% if function.warning %}
**⚠️ 警告**: {{ function.warning }}
{% endif %}

{% if function.see %}
**🔗 参考**: 
{% for see_item in function.see %}
- {{ see_item }}
{% endfor %}
{% endif %}

{% if function.note %}
**📌 注意**: {{ function.note }}
{% endif %}

{% if function.warning %}
**⚠️ 警告**: {{ function.warning }}
{% endif %}

{% endfor %}
{% endif %}

---

{% endfor %}
# workgroupgui

# 脚本管理工具 (main_gui.py) 使用说明

## 📖 项目简介

这是一个基于 Streamlit 的可视化脚本管理工具，可以方便地管理和运行多个 Python 脚本，支持自定义排序、批量运行等功能。

## 🚀 快速启动

### 方法一：双击启动（推荐）
直接双击 `start_gui.bat` 文件即可启动

### 方法二：命令行启动
```powershell
streamlit run main_gui.py
```

## ✨ 主要功能

### 1. 按钮式脚本执行
- **单part表格操作工具**：不含"sum"的脚本
- **汇总表格操作工具**：包含"sum"的脚本
- 点击按钮即可运行相应脚本，自动显示执行结果

### 2. 编辑模式（侧边栏）
打开左侧边栏的"🔧 编辑模式"可以：
- ⬆️ ⬇️ 调整按钮顺序
- 🗑️ 删除不需要的按钮
- 🔄 恢复默认顺序

### 3. 批量运行窗口
位于页面下方，支持：
- 从下拉菜单选择脚本并添加到队列
- ⬆️ ⬇️ 调整队列中脚本的执行顺序
- 🗑️ 从队列中删除脚本
- 🚀 一键批量运行所有队列中的脚本
- 🧹 清空整个队列

### 4. 顶部工具栏
- **❌ 关闭**：关闭应用
- **🔄 重启**：刷新页面
- **🔄 重置排序**：恢复默认按钮顺序

## 📝 自定义配置

### 修改默认按钮顺序
编辑 `main_gui.py` 中的 `DEFAULT_SCRIPTS` 列表（第17-35行）：
```python
DEFAULT_SCRIPTS = [
    {"file": "脚本文件名.py", "name": "显示名称", "icon": "📝", "type": "script"},
    # 调整这些行的顺序即可改变默认显示顺序
]
```

### 添加新按钮
在 `DEFAULT_SCRIPTS` 列表中添加新项：
```python
{"file": "your_script.py", "name": "按钮显示名称", "icon": "🎯", "type": "script"},
```

### 删除按钮
- 方法1：打开编辑模式，点击 🗑️ 按钮
- 方法2：从 `DEFAULT_SCRIPTS` 列表中删除对应行

## 🛠️ 依赖安装

```powershell
pip install streamlit pandas openpyxl Pillow PyMuPDF
```

## 🧩 脚本功能说明

### 单part表格操作工具

| 脚本名 | 功能描述 |
|--------|--------|
| **add_excel_title.py** | 添加Excel标题(属) - 为Excel表格添加属性标题 |
| **set_excel_title.py** | 设置Excel标题 - 设置或更新Excel表头信息 |
| **delete_excel_col_种.py** | 删除Excel列（种） - 删除"种"相关列 |
| **delete_excel_col_taxid.py** | 删除Excel列（TaxID） - 删除TaxID相关列 |
| **mark_excel_cell.py** | 标记Excel单元格 - 为特定单元格添加标记/颜色 |
| **rename_excel_cell.py** | 重命名Excel单元格 - 批量重命名单元格内容 |
| **sort_excel_color.py** | 按颜色排序Excel - 根据单元格颜色排序数据 |
| **check_excel_null.py** | 检查Excel空值 - 检测并处理空值单元格 |
| **attract_pdf_good.py** | 提取PDF（优质） - 从PDF中提取高质量内容 |
| **recognition_pdf_excellent.py** | PDF分类工具（旧版） - 使用tkinter的PDF分类工具 |

### 汇总表格操作工具

| 脚本名 | 功能描述 |
|--------|--------|
| **create_excel_sum.py** | 创建Excel汇总 - 生成汇总统计表格 |
| **process_excel_part.py** | reads求和(part) - 处理单个部分的数据求和 |
| **process_sum_excel_sum.py** | reads求和(summary) - 处理汇总数据求和 |
| **mark_excel_ff7f00.py** | 为极好的种标橙 - 使用橙色(#ff7f00)标记优质数据 |
| **sort_sum_excel_color.py** | 按颜色排序汇总Excel - 对汇总表格按颜色排序 |
| **recognition_pdf_excellent_streamlit.py** | PDF分类工具（Streamlit） - 基于Streamlit的可视化PDF分类工具 |

## 💡 使用技巧

1. **配置持久化**：按钮顺序会自动保存到 `scripts_config.json`，下次启动时保持
2. **脚本分类**：文件名包含"sum"的脚本会自动归类到"汇总表格操作工具"
3. **输出查看**：执行完成后可展开"查看输出"查看详细信息，点击 ❌ 关闭
4. **Streamlit应用**：标记为 `type: streamlit` 的脚本会在新标签页打开
5. **预设队列**：使用"预处理"和"汇总表格处理"快速加载常用脚本组合

## 📋 完整工作流程

6. **预处理阶段**
   - 找到页面下方的"🧩 批量运行窗口"
   - 点击"🔧 预处理"按钮加载预设队列
   - 点击"🚀 一键批量运行"开始执行
   - 等待程序完成所有预处理脚本

7. **PDF分类阶段**
   - 点击"PDF分类工具"按钮（有两个版本可选）
     - **PDF分类工具（旧版）**：使用传统 tkinter 界面
     - **PDF分类工具（Streamlit）**：使用现代化 Streamlit 界面
   - 手动完成分类工作

8. **汇总表格生成阶段**
   - 分类完成后，再次找到"🧩 批量运行窗口"
   - 点击"📊 汇总表格处理"按钮加载汇总队列
   - 点击"🚀 一键批量运行"开始执行
   - 程序会自动生成汇总表格

## 🎯 预设队列

**预处理队列**（按顺序执行）：
1. add_excel_title.py
2. set_excel_title.py
3. delete_excel_col_种.py
4. delete_excel_col_taxid.py
5. process_excel_part.py
6. rename_excel_cell.py
7. mark_excel_cell.py
8. sort_excel_color.py
9. check_excel_null.py
10. attract_pdf_good.py

**汇总表格处理队列**（按顺序执行）：
1. mark_excel_ff7f00.py
2. create_excel_sum.py
3. process_sum_excel_sum.py
4. sort_sum_excel_color.py

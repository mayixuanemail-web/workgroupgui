# ⚠️# 运行前务必更新代码
# ⚠️# 运行前务必更新代码
# ⚠️# 运行前务必更新代码
> **务必先下载最新代码：**  
> https://github.com/mayixuanemail-web/workgroupgui/archive/refs/heads/main.zip

# workgroupgui

# 脚本管理工具 (main_gui.py) 使用说明

## ✅ 快速上手（完整流程）

1. 解压 workgroupgui_main 文件。
2. 在解压后的文件夹中新建一个名为 files_debug 的文件夹。
3. 将 ***原始文件*** 解压缩到 files_debug 文件夹内。
4. 统一使用 Python 3.12 版本，如果不是请重新安装。
5. 运行 install_request.py 以安装依赖（安装一次即可，后续无需安装）。
6. 运行 start_gui 启动程序。
7. 直接点击全自动处理——一键批量运行，等待程序自动完成。
8. 程序可自动完成识别工作和80%左右的翻译，仅剩余少量的翻译工作手动完成。
9. 在手动完成所有的翻译工作后,可将翻译完的文档发给我,使程序更加完善。

## 📖 项目简介

这是一个基于 Streamlit 的可视化脚本管理工具，可以方便地管理和运行多个 Python 脚本，支持批量运行等功能。

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

### 2. 批量运行窗口
位于页面下方，支持：
- 从下拉菜单选择脚本并添加到队列
- ⬆️ ⬇️ 调整队列中脚本的执行顺序
- 🗑️ 从队列中删除脚本
- 🚀 一键批量运行所有队列中的脚本
- 🧹 清空整个队列

### 3. 顶部工具栏
- **❌ 关闭**：关闭应用
- **🔄 重启**：刷新页面
- **🔄 重置排序**：恢复默认按钮顺序

## 🛠️ 依赖安装

优先使用项目内安装脚本：

```powershell
python install_request.py
```

如需手动安装，可执行：

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

1. **脚本分类**：文件名包含"sum"的脚本会自动归类到"汇总表格操作工具"
2. **输出查看**：执行完成后可展开"查看输出"查看详细信息，点击 ❌ 关闭
3. **Streamlit应用**：标记为 `type: streamlit` 的脚本会在新标签页打开
4. **预设队列**：使用"预处理"和"汇总表格处理"快速加载常用脚本组合

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

import streamlit as st
import subprocess
import os
import json
from pathlib import Path


# 页面配置
st.set_page_config(page_title="脚本管理工具", page_icon="🚀", layout="wide")

# 标题与重要提示
st.markdown('<span style="color:red;font-weight:bold;font-size:22px;">运行前务必更新最新代码</span>', unsafe_allow_html=True)
st.markdown('<span style="color:red;font-weight:bold;font-size:22px;">滑动到最底部查看使用说明</span>', unsafe_allow_html=True)

# 使用 python 命令运行（自动从 PATH 查找）
PYTHON_PATH = "python"

# 配置文件路径
CONFIG_FILE = "scripts_config.json"

# 默认脚本列表
DEFAULT_SCRIPTS = [
    {"file": "add_excel_title.py", "name": "添加Excel标题(属)", "icon": "📝", "type": "script"},
    {"file": "attract_pdf_good.py", "name": "提取PDF（优质）", "icon": "📄", "type": "script"},
    {"file": "check_excel_null.py", "name": "检查Excel空值", "icon": "🔍", "type": "script"},
    {"file": "create_excel_sum.py", "name": "创建Excel汇总", "icon": "📊", "type": "script"},
    {"file": "delete_excel_col_种.py", "name": "删除Excel列（种）", "icon": "🗑️", "type": "script"},
    {"file": "delete_excel_col_taxid.py", "name": "删除Excel列（TaxID）", "icon": "🗑️", "type": "script"},
    {"file": "mark_excel_cell.py", "name": "标记Excel单元格", "icon": "🖍️", "type": "script"},
    {"file": "mark_excel_ff7f00.py", "name": "为极好的种标橙", "icon": "🟠", "type": "script"},
    {"file": "process_excel_part.py", "name": "reads求和(part)", "icon": "⚙️", "type": "script"},
    {"file": "process_sum_excel_sum.py", "name": "reads求和(summary)", "icon": "⚙️", "type": "script"},  
    {"file": "rename_excel_cell.py", "name": "重命名Excel单元格", "icon": "✏️", "type": "script"},
    {"file": "set_excel_title.py", "name": "设置Excel标题", "icon": "📋", "type": "script"},
    {"file": "sort_excel_color.py", "name": "按颜色排序Excel", "icon": "🎨", "type": "script"},
    {"file": "sort_sum_excel_color.py", "name": "按颜色排序汇总Excel", "icon": "🎨", "type": "script"},
    {"file": "translate_sum_genus_from_mapping.py", "name": "属名翻译（汇总）", "icon": "🈶", "type": "script"},
    {"file": "pdf_first_page_to_png.py", "name": "PDF首页转PNG", "icon": "🖼️", "type": "script"},
    {"file": "Recognition_PDF_automatically.py", "name": "PDF自动识别", "icon": "🤖", "type": "script"},
    {"file": "clean_temp_images.py", "name": "清理临时图片", "icon": "🧹", "type": "script"},
    {"file": "recognition_pdf_excellent.py", "name": "PDF分类工具（旧版）", "icon": "🎯", "type": "script"},
    {"file": "recognition_pdf_excellent_streamlit.py", "name": "PDF分类工具（Streamlit）", "icon": "🎯", "type": "streamlit"},
]

def load_scripts_config():
    """加载配置文件或返回默认配置"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            st.warning(f"⚠️ 加载配置失败: {e}，使用默认配置")
            return DEFAULT_SCRIPTS
    return DEFAULT_SCRIPTS

def save_scripts_config(scripts):
    """保存配置到文件"""
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(scripts, f, ensure_ascii=False, indent=2)
        st.success("✅ 配置已保存")
    except Exception as e:
        st.error(f"❌ 保存配置失败: {e}")

def run_script(script):
    """运行脚本或启动Streamlit应用"""
    script_path = script['file']
    
    if not os.path.exists(script_path):
        st.error(f"❌ 找不到文件: {script['file']}")
        return
    
    if script['type'] == 'streamlit':
        with st.spinner(f"正在启动 {script['name']}..."):
            try:
                subprocess.Popen(
                    [PYTHON_PATH, "-m", "streamlit", "run", script_path]
                )
                st.success(f"✅ {script['name']} 已启动！")
                st.info("💡 新应用将在浏览器新标签页中打开（通常在几秒后）")
            except Exception as e:
                st.error(f"❌ 启动出错: {str(e)}")
    else:
        st.info(f"🚀 正在运行 {script['name']}，输出将显示在终端中...")
        try:
            # 直接运行，输出到终端
            result = subprocess.run(
                [PYTHON_PATH, script_path],
                timeout=300
            )
            
            if result.returncode == 0:
                st.success(f"✅ {script['name']} 执行成功！")
            else:
                st.error(f"❌ {script['name']} 执行失败，请查看终端输出")
        except subprocess.TimeoutExpired:
            st.error(f"⏱️ {script['name']} 执行超时（超过5分钟）")
        except Exception as e:
            st.error(f"❌ 运行出错: {str(e)}")

# 加载脚本配置

scripts = load_scripts_config()

# 标题与操作按钮同一行
col_title, col_update, col_close, col_restart, col_reset = st.columns([4, 1, 1, 1, 1])
with col_title:
    st.markdown("## 🚀 脚本管理工具")
with col_update:
    if st.button("⬆️ 更新", use_container_width=True):
        try:
            result = subprocess.run(
                ["git", "pull"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                st.success("✅ 代码已更新！请刷新页面")
                st.info(result.stdout if result.stdout else "已是最新版本")
            else:
                st.error(f"❌ 更新失败: {result.stderr}")
        except Exception as e:
            st.error(f"❌ 更新出错: {str(e)}")
with col_close:
    if st.button("❌ 关闭", use_container_width=True):
        st.warning("正在关闭应用...")
        raise SystemExit(0)
with col_restart:
    if st.button("🔄 重启", use_container_width=True):
        st.rerun()
with col_reset:
    if st.button("🔄 重置", use_container_width=True):
        save_scripts_config(DEFAULT_SCRIPTS)
        st.success("✅ 已恢复默认顺序")
        st.rerun()

st.markdown("---")

def is_sum_script(script):
    return "sum" in script["file"].lower()

# 默认批量运行队列
DEFAULT_BATCH_QUEUE_1 = [
    "add_excel_title.py",
    "set_excel_title.py",
    "delete_excel_col_种.py",
    "delete_excel_col_taxid.py",
    "process_excel_part.py",
    "rename_excel_cell.py",
    "mark_excel_cell.py",
    "sort_excel_color.py",
    "check_excel_null.py",
    "attract_pdf_good.py",
]

DEFAULT_BATCH_QUEUE_2 = [
    "mark_excel_ff7f00.py",
    "create_excel_sum.py",
    "process_sum_excel_sum.py",
    "sort_sum_excel_color.py",
]

DEFAULT_BATCH_QUEUE_3 = [
    "add_excel_title.py",
    "set_excel_title.py",
    "delete_excel_col_种.py",
    "delete_excel_col_taxid.py",
    "process_excel_part.py",
    "rename_excel_cell.py",
    "mark_excel_cell.py",
    "attract_pdf_good.py",
    "pdf_first_page_to_png.py",
    "Recognition_PDF_automatically.py",
    "mark_excel_ff7f00.py",
    "create_excel_sum.py",
    "process_sum_excel_sum.py",
    "sort_sum_excel_color.py",
    "translate_sum_genus_from_mapping.py",
    "clean_temp_images.py",
]

# 初始化批量运行队列
if "batch_queue" not in st.session_state:
    st.session_state.batch_queue = list(DEFAULT_BATCH_QUEUE_3)
if "queue_preset" not in st.session_state:
    st.session_state.queue_preset = "队列3"

def get_script_by_file(file_name):
    for item in scripts:
        if item["file"] == file_name:
            return item
    return None

# ============= 批量运行窗口 =============
st.subheader("🧩 批量运行窗口")

# 预设队列选择
preset_col1, preset_col2, preset_col3, preset_col4 = st.columns([2, 2, 2, 4])
with preset_col1:
    if st.button("🔧 预处理", use_container_width=True, key="load_preset_1"):
        st.session_state.batch_queue = list(DEFAULT_BATCH_QUEUE_1)
        st.session_state.queue_preset = "预处理"
        st.rerun()
with preset_col2:
    if st.button("📊 汇总表格处理", use_container_width=True, key="load_preset_2"):
        st.session_state.batch_queue = list(DEFAULT_BATCH_QUEUE_2)
        st.session_state.queue_preset = "汇总表格处理"
        st.rerun()
with preset_col3:
    if st.button("🤖 全自动处理", use_container_width=True, key="load_preset_3"):
        st.session_state.batch_queue = list(DEFAULT_BATCH_QUEUE_3)
        st.session_state.queue_preset = "全自动处理"
        st.rerun()
with preset_col4:
    st.markdown(f"**当前队列：** {st.session_state.queue_preset}")

st.markdown("---")

with st.container():
    col_left, col_right = st.columns([2, 3])

    with col_left:
        st.markdown("**添加到队列**")
        script_options = [f"{s['icon']} {s['name']} ({s['file']})" for s in scripts]
        script_map = {f"{s['icon']} {s['name']} ({s['file']})": s["file"] for s in scripts}
        selected = st.selectbox("选择脚本", script_options, key="batch_select")
        if st.button("➕ 添加到队列", use_container_width=True):
            selected_file = script_map.get(selected)
            if selected_file:
                st.session_state.batch_queue.append(selected_file)
                st.success("✅ 已加入队列")

    with col_right:
        st.markdown("**运行队列（可排序）**")
        if not st.session_state.batch_queue:
            st.info("队列为空，请从左侧添加脚本")
        else:
            for idx, file_name in enumerate(st.session_state.batch_queue):
                script = get_script_by_file(file_name)
                if not script:
                    continue
                c1, c2, c3, c4 = st.columns([6, 1, 1, 1])
                with c1:
                    st.write(f"{idx + 1}. {script['icon']} {script['name']}")
                with c2:
                    if st.button("⬆️", key=f"batch_up_{idx}") and idx > 0:
                        st.session_state.batch_queue[idx - 1], st.session_state.batch_queue[idx] = (
                            st.session_state.batch_queue[idx],
                            st.session_state.batch_queue[idx - 1]
                        )
                        st.rerun()
                with c3:
                    if st.button("⬇️", key=f"batch_down_{idx}") and idx < len(st.session_state.batch_queue) - 1:
                        st.session_state.batch_queue[idx + 1], st.session_state.batch_queue[idx] = (
                            st.session_state.batch_queue[idx],
                            st.session_state.batch_queue[idx + 1]
                        )
                        st.rerun()
                with c4:
                    if st.button("🗑️", key=f"batch_del_{idx}"):
                        st.session_state.batch_queue.pop(idx)
                        st.rerun()

        col_run1, col_run2 = st.columns(2)
        with col_run1:
            if st.button("🚀 一键批量运行", use_container_width=True):
                # 显示进度条
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                total_scripts = len(st.session_state.batch_queue)
                for idx, file_name in enumerate(st.session_state.batch_queue):
                    script = get_script_by_file(file_name)
                    if script:
                        # 更新进度条
                        progress = (idx + 1) / total_scripts
                        progress_bar.progress(progress)
                        status_text.markdown(f"**进度：** {idx + 1}/{total_scripts} - 正在运行 {script['name']}...")
                        run_script(script)
                
                progress_bar.progress(1.0)
                status_text.markdown("✅ **所有脚本运行完成！**")
        with col_run2:
            if st.button("🧹 清空队列", use_container_width=True):
                st.session_state.batch_queue = []
                st.rerun()

st.markdown("---")

# ============= 脚本按钮窗口 =============
# 创建多列布局
cols_per_row = 3

# 第一部分：非 SUM 脚本
st.subheader("📊 单part表格操作工具")
non_sum_scripts = [s for s in scripts if not is_sum_script(s)]
for i in range(0, len(non_sum_scripts), cols_per_row):
    cols = st.columns(cols_per_row)
    for j, col in enumerate(cols):
        if i + j < len(non_sum_scripts):
            script = non_sum_scripts[i + j]
            with col:
                if st.button(f"{script['icon']} {script['name']}", key=f"btn_{i+j}_{script['file']}", use_container_width=True):
                    run_script(script)

# 分界线
st.markdown("---")

# 第二部分：SUM 脚本
st.subheader("📑 汇总表格操作工具")
sum_scripts = [s for s in scripts if is_sum_script(s)]
for i in range(0, len(sum_scripts), cols_per_row):
    cols = st.columns(cols_per_row)
    for j, col in enumerate(cols):
        if i + j < len(sum_scripts):
            script = sum_scripts[i + j]
            with col:
                if st.button(f"{script['icon']} {script['name']}", key=f"btn_{i+j}_sum_{script['file']}", use_container_width=True):
                    run_script(script)
st.markdown("---")
st.info("💡 点击对应按钮即可运行相应的Python脚本。Streamlit应用会在新进程中启动。")

st.markdown("---")

# 显示 README
st.subheader("📖 项目说明")

readme_path = "README.md"
if os.path.exists(readme_path):
    with open(readme_path, "r", encoding="utf-8") as f:
        readme_content = f.read()
    st.markdown(readme_content)
else:
    st.warning("⚠️ 未找到 README.md 文件")

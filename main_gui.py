import streamlit as st
import subprocess
import os
import json
from pathlib import Path

# 页面配置
st.set_page_config(page_title="脚本管理工具", page_icon="🚀", layout="wide")

# Python解释器路径
PYTHON_PATH = "C:/Users/ma/AppData/Local/Programs/Python/Python312/python.exe"

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
    script_path = os.path.join(os.path.dirname(__file__), script['file'])
    
    if not os.path.exists(script_path):
        st.error(f"❌ 找不到文件: {script['file']}")
        return
    
    if script['type'] == 'streamlit':
        with st.spinner(f"正在启动 {script['name']}..."):
            try:
                subprocess.Popen(
                    [PYTHON_PATH, "-m", "streamlit", "run", script_path],
                    cwd=os.path.dirname(__file__)
                )
                st.success(f"✅ {script['name']} 已启动！")
                st.info("💡 新应用将在浏览器新标签页中打开（通常在几秒后）")
            except Exception as e:
                st.error(f"❌ 启动出错: {str(e)}")
    else:
        with st.spinner(f"正在运行 {script['name']}..."):
            try:
                result = subprocess.run(
                    [PYTHON_PATH, script_path],
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                
                if result.returncode == 0:
                    st.success(f"✅ {script['name']} 执行成功！")
                    if result.stdout:
                        with st.expander("查看输出", expanded=True):
                            col_output, col_close_btn = st.columns([10, 1])
                            with col_output:
                                st.code(result.stdout)
                            with col_close_btn:
                                if st.button("❌", key=f"close_output_{script['file']}", help="关闭"):
                                    st.rerun()
                else:
                    st.error(f"❌ {script['name']} 执行失败！")
                    if result.stderr:
                        with st.expander("查看错误信息", expanded=True):
                            col_error, col_close_btn2 = st.columns([10, 1])
                            with col_error:
                                st.code(result.stderr)
                            with col_close_btn2:
                                if st.button("❌", key=f"close_error_{script['file']}", help="关闭"):
                                    st.rerun()
            except subprocess.TimeoutExpired:
                st.error(f"⏱️ {script['name']} 执行超时（超过5分钟）")
            except Exception as e:
                st.error(f"❌ 运行出错: {str(e)}")

# 侧边栏：编辑模式
with st.sidebar:
    st.header("⚙️ 工具配置")
    
    if st.checkbox("🔧 编辑模式", value=False):
        st.subheader("按钮排序编辑")
        
        scripts_list = load_scripts_config()
        
        # 显示可拖动的按钮列表
        for idx, script in enumerate(scripts_list):
            col1, col2, col3, col4, col5 = st.columns([0.5, 3, 0.5, 0.5, 0.5])
            
            with col1:
                st.write(f"{idx + 1}")
            
            with col2:
                st.write(f"{script['icon']} {script['name']}")
            
            with col3:
                if st.button("⬆️", key=f"up_{idx}"):
                    if idx > 0:
                        scripts_list[idx], scripts_list[idx - 1] = scripts_list[idx - 1], scripts_list[idx]
                        save_scripts_config(scripts_list)
                        st.rerun()
            
            with col4:
                if st.button("⬇️", key=f"down_{idx}"):
                    if idx < len(scripts_list) - 1:
                        scripts_list[idx], scripts_list[idx + 1] = scripts_list[idx + 1], scripts_list[idx]
                        save_scripts_config(scripts_list)
                        st.rerun()
            
            with col5:
                if st.button("🗑️", key=f"del_{idx}"):
                    scripts_list.pop(idx)
                    save_scripts_config(scripts_list)
                    st.rerun()
        
        # 重置按钮
        if st.button("🔄 恢复默认顺序"):
            save_scripts_config(DEFAULT_SCRIPTS)
            st.rerun()
    else:
        st.info("💡 打开'编辑模式'可拖动按钮进行分类")

# 加载脚本配置

scripts = load_scripts_config()

# 标题与操作按钮同一行
col_title, col_close, col_restart, col_reset = st.columns([5, 1, 1, 1])
with col_title:
    st.markdown("## 🚀 脚本管理工具")
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

# 初始化批量运行队列
if "batch_queue" not in st.session_state:
    st.session_state.batch_queue = list(DEFAULT_BATCH_QUEUE_1)
if "queue_preset" not in st.session_state:
    st.session_state.queue_preset = "队列1"

def get_script_by_file(file_name):
    for item in scripts:
        if item["file"] == file_name:
            return item
    return None

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

# 批量运行窗口
st.subheader("🧩 批量运行窗口")

# 预设队列选择
preset_col1, preset_col2, preset_col3 = st.columns([2, 2, 4])
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
                for file_name in st.session_state.batch_queue:
                    script = get_script_by_file(file_name)
                    if script:
                        run_script(script)
        with col_run2:
            if st.button("🧹 清空队列", use_container_width=True):
                st.session_state.batch_queue = []
                st.rerun()

st.markdown("---")

# 显示 README
st.subheader("📖 项目说明")

readme_path = os.path.join(os.path.dirname(__file__), "README.md")
if os.path.exists(readme_path):
    with open(readme_path, "r", encoding="utf-8") as f:
        readme_content = f.read()
    st.markdown(readme_content)
else:
    st.warning("⚠️ 未找到 README.md 文件")

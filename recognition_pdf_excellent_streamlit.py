import streamlit as st
import os
import shutil
import datetime
from pathlib import Path
from PIL import Image
import io
import json
import streamlit.components.v1 as components

# 可选依赖：PyMuPDF（预览）
try:
    import fitz  # PyMuPDF
    HAVE_RENDER = True
except Exception:
    fitz = None
    HAVE_RENDER = False

# 页面配置
st.set_page_config(page_title="PDF批量分类工具", page_icon="📄", layout="wide")

# 历史记录文件路径
HISTORY_FILE = Path(".history.json")

# 全局快捷键 JavaScript 组件
def keyboard_listener():
    """JavaScript 全局快捷键监听器"""
    components.html("""
    <script>
    const doc = window.parent.document;
    doc.addEventListener('keydown', function(e) {
        // 避免在输入框中触发
        if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
        
        const keyMap = {
            '1': 'btn_copy',
            '2': 'btn_skip'
        };
        
        if (keyMap[e.key]) {
            const buttons = doc.querySelectorAll('button');
            buttons.forEach(btn => {
                if (btn.getAttribute('data-testid') === keyMap[e.key] || 
                    btn.id === keyMap[e.key] ||
                    btn.innerText.includes(e.key === '1' ? '归类' : '跳过')) {
                    btn.click();
                }
            });
        }
    });
    </script>
    """, height=0)

def add_log(message):
    """添加日志消息"""
    timestamp = datetime.datetime.now().strftime("[%H:%M:%S]")
    st.session_state.log_messages.append(f"{timestamp} {message}")

def save_history():
    """保存历史记录到文件"""
    try:
        history_data = {
            "timestamp": datetime.datetime.now().isoformat(),
            "global_history": st.session_state.global_history,
            "directory_stack": st.session_state.directory_stack,
            "processed_pdfs": st.session_state.processed_pdfs,
            "total_pdfs": st.session_state.total_pdfs,
            "log_messages": st.session_state.log_messages,
            "all_tasks": st.session_state.all_tasks,
            "task_queue": st.session_state.task_queue,
            "source_dir": st.session_state.source_dir,
            "target_dir": st.session_state.target_dir,
            "current_index": st.session_state.current_index,
            "pdf_list": st.session_state.pdf_list
        }
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(history_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        add_log(f"❌ 保存历史记录失败: {e}")

def load_history():
    """从文件加载历史记录"""
    if not HISTORY_FILE.exists():
        return False
    
    try:
        with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
            history_data = json.load(f)
        
        st.session_state.global_history = [tuple(h) for h in history_data.get("global_history", [])]
        st.session_state.directory_stack = [tuple(d) for d in history_data.get("directory_stack", [])]
        st.session_state.processed_pdfs = history_data.get("processed_pdfs", 0)
        st.session_state.total_pdfs = history_data.get("total_pdfs", 0)
        st.session_state.log_messages = history_data.get("log_messages", ["程序就绪，等待任务加载"])
        st.session_state.all_tasks = [tuple(t) for t in history_data.get("all_tasks", [])]
        st.session_state.task_queue = [tuple(t) for t in history_data.get("task_queue", [])]
        st.session_state.source_dir = history_data.get("source_dir", None)
        st.session_state.target_dir = history_data.get("target_dir", None)
        st.session_state.current_index = history_data.get("current_index", 0)
        st.session_state.pdf_list = history_data.get("pdf_list", [])
        
        add_log("✅ 已恢复之前的历史记录")
        return True
    except Exception as e:
        add_log(f"❌ 加载历史记录失败: {e}")
        return False

def clear_history():
    """清空历史记录文件"""
    try:
        if HISTORY_FILE.exists():
            HISTORY_FILE.unlink()
        st.session_state.global_history = []
        st.session_state.directory_stack = []
        st.session_state.processed_pdfs = 0
        st.session_state.log_messages = ["程序就绪，等待任务加载"]
        add_log("🗑️ 已清空历史记录")
    except Exception as e:
        add_log(f"❌ 清空历史记录失败: {e}")

def restore_from_record(record_index):
    """从指定记录点恢复状态"""
    if record_index < 0 or record_index >= len(st.session_state.global_history):
        st.error("❌ 无效的记录索引")
        return
    
    # 获取要恢复的记录之后的所有操作并删除对应文件
    records_to_remove = st.session_state.global_history[record_index + 1:]
    for record in records_to_remove:
        action, filename, src_path, tar_path, source_dir, target_dir = record
        if action == "copy" and tar_path and os.path.exists(tar_path):
            try:
                os.remove(tar_path)
                add_log(f"🗑️ 删除文件 → {filename}")
            except Exception as e:
                add_log(f"❌ 删除失败 {filename}: {e}")
    
    # 截断历史记录到指定位置
    st.session_state.global_history = st.session_state.global_history[:record_index + 1]
    
    # 重新计算已处理数量
    st.session_state.processed_pdfs = len([h for h in st.session_state.global_history if h[0] in ["copy", "skip"]])
    
    # 更新目录栈并去重
    seen = set()
    unique_stack = []
    for item in reversed([tuple(h[4:6]) for h in st.session_state.global_history if h[0] in ["copy", "skip"]]):
        if item not in seen:
            seen.add(item)
            unique_stack.append(item)
    st.session_state.directory_stack = list(reversed(unique_stack))
    
    # 以选中记录的目录作为当前目录
    selected_record = st.session_state.global_history[record_index]
    _, _, _, _, selected_source, selected_target = selected_record
    st.session_state.source_dir = selected_source
    st.session_state.target_dir = selected_target

    # 重新加载当前目录的PDF列表
    if st.session_state.source_dir and os.path.exists(st.session_state.source_dir):
        st.session_state.pdf_list = [
            f for f in os.listdir(st.session_state.source_dir)
            if f.lower().endswith(".pdf")
        ]
        # 根据已处理的PDF数量调整current_index
        current_dir_history = [
            h for h in st.session_state.global_history
            if h[4] == st.session_state.source_dir and h[5] == st.session_state.target_dir
        ]
        st.session_state.current_index = min(len(current_dir_history), len(st.session_state.pdf_list))
    else:
        st.session_state.pdf_list = []
        st.session_state.current_index = 0
    
    add_log(f"⏮️ 已从第 {record_index + 1} 条记录恢复状态")
    save_history()

# 初始化会话状态
if "source_dir" not in st.session_state:
    st.session_state.source_dir = None
    st.session_state.target_dir = None
    st.session_state.pdf_list = []
    st.session_state.current_index = 0
    st.session_state.global_history = []
    st.session_state.directory_stack = []
    st.session_state.task_queue = []
    st.session_state.all_tasks = []
    st.session_state.log_messages = ["程序就绪，等待任务加载"]
    st.session_state.total_pdfs = 0
    st.session_state.processed_pdfs = 0
    
    # 尝试加载历史记录
    load_history()

def move_to_target(filename):
    """复制到目标并返回目标路径"""
    source_path = os.path.join(st.session_state.source_dir, filename)
    target_path = os.path.join(st.session_state.target_dir, filename)
    shutil.copy2(source_path, target_path)
    return target_path

def render_sidebar():
    """实时渲染侧边栏历史记录"""
    with st.sidebar:
        st.title("📊 历史记录")
        
        st.metric("总操作数", len(st.session_state.global_history))
        st.metric("已处理PDF", st.session_state.processed_pdfs)
        
        st.divider()
        
        # 历史记录展示（按时间倒序）
        if st.session_state.global_history:
            st.write("**最近操作 (最新优先)**")
            
            # 倒序显示历史记录
            for idx in range(len(st.session_state.global_history) - 1, -1, -1):
                record = st.session_state.global_history[idx]
                action, filename, src_path, tar_path, source_dir, target_dir = record
                action_icon = "✅" if action == "copy" else "➡️"
                
                # 显示记录信息
                dir_name = source_dir.split(os.sep)[-1] if os.sep in source_dir else source_dir
                
                # 简化显示文本
                display_text = f"{action_icon} {filename[:18]}"
                if len(filename) > 18:
                    display_text += "..."
                display_text += f" | {dir_name}"
                
                # 使用按钮组合文本展示
                if st.button(display_text, key=f"restore_{idx}", use_container_width=True):
                    restore_from_record(idx)
                    st.rerun()
            
            st.divider()
            
            # 导出按钮
            if st.button("📥 导出历史", use_container_width=True, key="export_history_btn"):
                history_json = json.dumps({
                    "export_time": datetime.datetime.now().isoformat(),
                    "total_processed": st.session_state.processed_pdfs,
                    "records": st.session_state.global_history
                }, ensure_ascii=False, indent=2)
                st.download_button(
                    label="⬇️ 下载JSON",
                    data=history_json,
                    file_name=f"history_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json",
                    key="download_history",
                    use_container_width=True
                )
            
            # 清空按钮
            if st.button("🗑️ 清空历史", use_container_width=True, key="clear_history_btn"):
                clear_history()
                st.rerun()
        else:
            st.info("📭 无记录")

# 立即渲染侧边栏
render_sidebar()

@st.cache_data(show_spinner=False)
def render_pdf_preview_cached(pdf_path, max_width=500, max_height=300):
    """缓存版本的PDF预览渲染（返回bytes以提高缓存效率）"""
    if not HAVE_RENDER or not os.path.exists(pdf_path):
        return None

    try:
        doc = fitz.open(pdf_path)
        if doc.page_count < 1:
            doc.close()
            return None
        page = doc.load_page(0)
        # 1.5x缩放：优先速度，兼顾清晰度（本地运行）
        mat = fitz.Matrix(2, 2)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        doc.close()
        
        # 等比缩放
        w, h = img.size
        scale = min(max_width / w, max_height / h, 1.0)
        if scale < 1.0:
            img = img.resize((int(w * scale), int(h * scale)), Image.BILINEAR)
        
        # 转换为bytes返回（缓存bytes比Image对象更高效）
        buf = io.BytesIO()
        img.save(buf, format='JPEG', quality=95)  # 质量95（本地运行优先清晰度）
        return buf.getvalue()
    except Exception as e:
        return None

@st.fragment
def pdf_viewer_fragment():
    """PDF查看和操作的fragment（局部刷新，不影响整页）"""
    if st.session_state.current_index >= len(st.session_state.pdf_list):
        st.success("✅ 当前目录完成！")
        if st.button("下一个目录", use_container_width=True, key="next_dir"):
            if st.session_state.task_queue:
                next_source, next_target = st.session_state.task_queue.pop(0)
                load_directory(next_source, next_target)
        return
    
    current_pdf = st.session_state.pdf_list[st.session_state.current_index]
    
    # 进度信息
    progress_info = f"{st.session_state.current_index + 1}/{len(st.session_state.pdf_list)}"
    st.markdown(f"<h3 style='white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin: 0;'>📄 {current_pdf} [{progress_info}]</h3>", unsafe_allow_html=True)
    
    # 两列布局：左边PDF预览，右边操作
    col_preview, col_actions = st.columns([2, 1])
    
    with col_preview:
        pdf_path = os.path.join(st.session_state.source_dir, current_pdf)
        img_bytes = render_pdf_preview_cached(pdf_path, max_width=450, max_height=400)
        if img_bytes:
            st.image(img_bytes, use_container_width=True)
        else:
            st.info("📄 无法预览或文件不存在")
    
    with col_actions:
        st.write("**操作面板**")
        
        if st.button("✅ 归类到好 (1)", use_container_width=True, key="btn_copy", type="primary"):
            current_pdf = st.session_state.pdf_list[st.session_state.current_index]
            tar_path = move_to_target(current_pdf)
            src_full_path = os.path.join(st.session_state.source_dir, current_pdf)
            st.session_state.global_history.append(("copy", current_pdf, src_full_path, tar_path, st.session_state.source_dir, st.session_state.target_dir))
            st.session_state.processed_pdfs += 1
            add_log(f"✅ 复制完成 → {current_pdf}")
            save_history()
            st.session_state.current_index += 1
            if st.session_state.current_index >= len(st.session_state.pdf_list):
                handle_directory_finished()
            st.rerun()
            
        if st.button("➡️ 跳过 (2)", use_container_width=True, key="btn_skip"):
            current_pdf = st.session_state.pdf_list[st.session_state.current_index]
            st.session_state.global_history.append(("skip", current_pdf, "", "", st.session_state.source_dir, st.session_state.target_dir))
            st.session_state.processed_pdfs += 1
            add_log(f"➡️ 已跳过 → {current_pdf}")
            save_history()
            st.session_state.current_index += 1
            if st.session_state.current_index >= len(st.session_state.pdf_list):
                handle_directory_finished()
            st.rerun()
        
        if st.button("🔄 重开当前目录", use_container_width=True, key="btn_restart_cur"):
            restart_current_directory()
            st.rerun()
        
        if st.button("⬅️ 重开上一目录", use_container_width=True, key="btn_restart_prev"):
            restart_previous_directory()
        
        st.divider()
        st.write("**统计**")
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            st.metric("当前目录", f"{st.session_state.current_index}/{len(st.session_state.pdf_list)}")
        with col_s2:
            st.metric("全局进度", f"{st.session_state.processed_pdfs}/{st.session_state.total_pdfs}")
    
    # 全局快捷键监听
    keyboard_listener()

def _delete_pdfs_in_directory(directory):
    """删除指定目录中的所有PDF文件"""
    if os.path.exists(directory):
        for fname in os.listdir(directory):
            if fname.lower().endswith('.pdf'):
                try:
                    os.remove(os.path.join(directory, fname))
                except Exception as e:
                    add_log(f"❌ 删除文件失败: {e}")

def restart_previous_directory():
    """重新开始上一个目录"""
    if not st.session_state.directory_stack:
        st.toast("⚠️ 没有上一个目录", icon="⚠️")
        return
    
    # 获取上一个已完成的目录
    prev_source, prev_target = st.session_state.directory_stack.pop()
    
    # 将当前目录放回任务队列最前面
    if st.session_state.source_dir:
        st.session_state.task_queue.insert(0, (st.session_state.source_dir, st.session_state.target_dir))
    
    # 删除上一目录的PDF文件
    _delete_pdfs_in_directory(prev_target)
    
    # 计算上一目录处理的PDF数量（用于减少全局统计）
    prev_dir_count = sum(1 for h in st.session_state.global_history if h[4] == prev_source)
    st.session_state.processed_pdfs = max(0, st.session_state.processed_pdfs - prev_dir_count)
    
    # 移除全局历史中上一目录的操作
    st.session_state.global_history = [
        h for h in st.session_state.global_history if h[4] != prev_source
    ]
    
    # 切换到上一个目录并重新开始
    st.session_state.source_dir = prev_source
    st.session_state.target_dir = prev_target
    st.session_state.pdf_list = sorted([f for f in os.listdir(prev_source) if f.lower().endswith(".pdf")])
    st.session_state.current_index = 0
    
    add_log(f"⬅️ 重新开始上一目录: {os.path.basename(prev_source)}")
    save_history()

def restart_current_directory():
    """重新开始当前目录"""
    if not st.session_state.source_dir:
        st.warning("⚠️ 当前没有加载目录")
        return
    
    # 计算当前目录处理的PDF数量（用于减少全局统计）
    current_dir_count = sum(
        1 for h in st.session_state.global_history 
        if h[4] == st.session_state.source_dir and h[5] == st.session_state.target_dir
    )
    st.session_state.processed_pdfs = max(0, st.session_state.processed_pdfs - current_dir_count)
    
    # 删除目标目录中的PDF文件
    _delete_pdfs_in_directory(st.session_state.target_dir)
    
    # 移除全局历史中当前目录的操作
    st.session_state.global_history = [
        h for h in st.session_state.global_history 
        if not (h[4] == st.session_state.source_dir and h[5] == st.session_state.target_dir)
    ]
    
    # 重置状态
    st.session_state.pdf_list = [
        f for f in os.listdir(st.session_state.source_dir) 
        if f.lower().endswith(".pdf")
    ]
    st.session_state.current_index = 0
    add_log(f"🔄 已重新开始当前目录：{st.session_state.source_dir}")
    save_history()

def restart_all_tasks():
    """重新开始全部任务"""
    if not st.session_state.all_tasks:
        st.warning("⚠️ 无初始任务清单")
        return
    
    # 恢复所有目标目录
    for src, targ in st.session_state.all_tasks:
        _delete_pdfs_in_directory(targ)
    
    # 清空历史
    st.session_state.global_history = []
    st.session_state.directory_stack = []
    st.session_state.processed_pdfs = 0  # 重置已处理数
    
    # 重新开始第一个任务
    if st.session_state.all_tasks:
        first_source, first_target = st.session_state.all_tasks[0]
        st.session_state.task_queue = st.session_state.all_tasks[1:]
        load_directory(first_source, first_target)
        add_log("🔁 已重新开始全部任务，从第一项重新处理")
        save_history()

def load_directory(source_dir, target_dir):
    """加载一个目录"""
    st.session_state.source_dir = source_dir
    st.session_state.target_dir = target_dir
    
    if not os.path.exists(st.session_state.target_dir):
        os.makedirs(st.session_state.target_dir)
    
    st.session_state.pdf_list = [
        f for f in os.listdir(st.session_state.source_dir) 
        if f.lower().endswith(".pdf")
    ]
    st.session_state.current_index = 0
    
    # 检查目录是否为空，如果为空则自动跳过
    if len(st.session_state.pdf_list) == 0:
        add_log(f"⏭️ 目录为空，自动跳过: {source_dir}")
        st.session_state.directory_stack.append((source_dir, target_dir))
        
        # 加载下一个任务
        if st.session_state.task_queue:
            next_source, next_target = st.session_state.task_queue.pop(0)
            load_directory(next_source, next_target)
        else:
            add_log("🎉 所有任务处理完成！")
        return
    
    add_log("--- 开始新目录处理 ---")
    add_log(f"源文件夹: {st.session_state.source_dir}")
    add_log(f"目标文件夹: {st.session_state.target_dir}")
    add_log(f"待处理PDF总数: {len(st.session_state.pdf_list)}\n")

def handle_directory_finished():
    """目录处理完成"""
    st.session_state.directory_stack.append((st.session_state.source_dir, st.session_state.target_dir))
    add_log(f"✅ 目录处理完成：{st.session_state.source_dir}\n")
    save_history()
    
    if st.session_state.task_queue:
        next_source, next_target = st.session_state.task_queue.pop(0)
        load_directory(next_source, next_target)
    else:
        add_log("🎉 所有任务处理完成！")
        save_history()

def _count_pdfs_in_tasks(tasks):
    """计算任务列表中的总PDF数"""
    total = 0
    for source, target in tasks:
        if os.path.exists(source):
            pdfs = [f for f in os.listdir(source) if f.lower().endswith('.pdf')]
            total += len(pdfs)
    return total

def _setup_tasks(tasks):
    """初始化任务列表"""
    st.session_state.all_tasks = list(tasks)
    st.session_state.task_queue = list(tasks[1:])
    st.session_state.total_pdfs = _count_pdfs_in_tasks(tasks)
    st.session_state.processed_pdfs = 0
    load_directory(tasks[0][0], tasks[0][1])
    save_history()

# 主页面
st.header("📄 PDF分类工具")

# 顶部工具栏
col_load, col_restart_all = st.columns(2)
with col_load:
    if st.button("🔄 加载任务", use_container_width=True, key="load_tasks"):
        base_path = Path("files_debug")
        tasks = []
        for number_dir in sorted(base_path.iterdir()):
            if not number_dir.is_dir():
                continue
            for category_dir in sorted(number_dir.iterdir()):
                if not category_dir.is_dir():
                    continue
                for part_dir in sorted(category_dir.iterdir()):
                    if not part_dir.is_dir() or not part_dir.name.startswith("part"):
                        continue
                    source = str(part_dir)
                    target = str(part_dir / "非常好")
                    if os.path.exists(source):
                        tasks.append((source, target))
        
        if tasks:
            _setup_tasks(tasks)
            st.toast(f"✅ 已加载 {len(tasks)} 个任务，共 {st.session_state.total_pdfs} 个PDF")
            st.rerun()
        else:
            st.toast("❌ 未找到有效的源文件夹", icon="❌")

with col_restart_all:
    if st.button("🔁 重新开始全部", use_container_width=True):
        restart_all_tasks()
        st.rerun()

# 主要内容区域 - 使用 fragment 实现局部刷新
pdf_viewer_fragment()

# 底部显示 README
st.divider()
with st.expander("📖 使用说明", expanded=False):
    readme_path = Path(__file__).parent / "README_PDF_TOOL.md"
    if readme_path.exists():
        st.markdown(readme_path.read_text(encoding="utf-8"))
    else:
        st.info("使用说明文件不存在")



import streamlit as st
import os
import shutil
import datetime
from pathlib import Path
from PIL import Image
import io
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

def calculate_global_stats():
    """计算全局统计信息"""
    total_tasks = len(st.session_state.all_tasks)
    completed_tasks = len(st.session_state.directory_stack)
    
    return total_tasks, completed_tasks, st.session_state.total_pdfs, st.session_state.processed_pdfs

def sidebar_stats_fragment():
    """侧边栏统计信息"""
    st.subheader("📊 全局统计")
    total_tasks, completed_tasks, total_pdfs, processed_pdfs = calculate_global_stats()
    
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.metric("任务完成", f"{completed_tasks}/{total_tasks}")
    with col_g2:
        st.metric("PDF处理", f"{processed_pdfs}/{total_pdfs}")

# 初始化会话状态
if "source_dir" not in st.session_state:
    st.session_state.source_dir = None
    st.session_state.target_dir = None
    st.session_state.pdf_list = []
    st.session_state.current_index = 0
    st.session_state.history = []
    st.session_state.global_history = []
    st.session_state.directory_stack = []
    st.session_state.task_queue = []
    st.session_state.all_tasks = []
    st.session_state.log_messages = ["程序就绪，等待任务加载"]
    st.session_state.last_key = None
    st.session_state.total_pdfs = 0  # 总PDF数
    st.session_state.processed_pdfs = 0  # 已处理PDF数
    st.session_state.buttons_disabled = False  # 按钮禁用状态

def add_log(message):
    """添加日志消息"""
    timestamp = datetime.datetime.now().strftime("[%H:%M:%S]")
    st.session_state.log_messages.append(f"{timestamp} {message}")

def move_to_target(filename):
    """复制到目标并返回目标路径"""
    source_path = os.path.join(st.session_state.source_dir, filename)
    target_path = os.path.join(st.session_state.target_dir, filename)
    shutil.copy2(source_path, target_path)
    return target_path

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

def render_pdf_preview(pdf_path, max_width=500, max_height=300):
    """渲染 PDF 首页（使用缓存）"""
    return render_pdf_preview_cached(pdf_path, max_width, max_height)

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
        img_bytes = render_pdf_preview(pdf_path, max_width=450, max_height=400)
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
            st.session_state.history.append(("copy", current_pdf, src_full_path, tar_path))
            st.session_state.global_history.append(("copy", current_pdf, src_full_path, tar_path, st.session_state.source_dir, st.session_state.target_dir))
            st.session_state.processed_pdfs += 1
            add_log(f"✅ 复制完成 → {current_pdf}")
            st.session_state.current_index += 1
            if st.session_state.current_index >= len(st.session_state.pdf_list):
                handle_directory_finished()
            
        if st.button("➡️ 跳过 (2)", use_container_width=True, key="btn_skip"):
            current_pdf = st.session_state.pdf_list[st.session_state.current_index]
            st.session_state.history.append(("skip", current_pdf, "", ""))
            st.session_state.global_history.append(("skip", current_pdf, "", "", st.session_state.source_dir, st.session_state.target_dir))
            st.session_state.processed_pdfs += 1
            add_log(f"➡️ 已跳过 → {current_pdf}")
            st.session_state.current_index += 1
            if st.session_state.current_index >= len(st.session_state.pdf_list):
                handle_directory_finished()
        
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
    
    # 删除上一目录的目标文件夹中的PDF
    if os.path.exists(prev_target):
        for fname in os.listdir(prev_target):
            if fname.lower().endswith('.pdf'):
                try:
                    os.remove(os.path.join(prev_target, fname))
                except Exception as e:
                    pass
    
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
    st.session_state.history = []
    
    add_log(f"⬅️ 重新开始上一目录: {os.path.basename(prev_source)}")

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
    
    # 删除目标目录中的 PDF 文件
    if os.path.exists(st.session_state.target_dir):
        for fname in os.listdir(st.session_state.target_dir):
            if fname.lower().endswith('.pdf'):
                try:
                    os.remove(os.path.join(st.session_state.target_dir, fname))
                except Exception as e:
                    add_log(f"❌ 删除文件失败: {e}")
    
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
    st.session_state.history = []
    add_log(f"🔄 已重新开始当前目录：{st.session_state.source_dir}")

def restart_all_tasks():
    """重新开始全部任务"""
    if not st.session_state.all_tasks:
        st.warning("⚠️ 无初始任务清单")
        return
    
    # 恢复所有目标目录
    for src, targ in st.session_state.all_tasks:
        if os.path.exists(targ):
            for fname in os.listdir(targ):
                if fname.lower().endswith('.pdf'):
                    try:
                        os.remove(os.path.join(targ, fname))
                    except Exception as e:
                        add_log(f"❌ 删除文件失败: {e}")
    
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
    st.session_state.history = []
    
    add_log("--- 开始新目录处理 ---")
    add_log(f"源文件夹: {st.session_state.source_dir}")
    add_log(f"目标文件夹: {st.session_state.target_dir}")
    add_log(f"待处理PDF总数: {len(st.session_state.pdf_list)}\n")

def handle_copy():
    """归类到好"""
    if st.session_state.current_index < len(st.session_state.pdf_list):
        current_pdf = st.session_state.pdf_list[st.session_state.current_index]
        tar_path = move_to_target(current_pdf)
        src_full_path = os.path.join(st.session_state.source_dir, current_pdf)
        st.session_state.history.append(("copy", current_pdf, src_full_path, tar_path))
        st.session_state.global_history.append(("copy", current_pdf, src_full_path, tar_path, st.session_state.source_dir, st.session_state.target_dir))
        st.session_state.processed_pdfs += 1  # 更新已处理数
        add_log(f"✅ 复制完成 → {current_pdf}")
        st.session_state.current_index += 1
        
        if st.session_state.current_index >= len(st.session_state.pdf_list):
            handle_directory_finished()
        st.rerun()

def handle_skip():
    """跳过"""
    if st.session_state.current_index < len(st.session_state.pdf_list):
        current_pdf = st.session_state.pdf_list[st.session_state.current_index]
        st.session_state.history.append(("skip", current_pdf, "", ""))
        st.session_state.global_history.append(("skip", current_pdf, "", "", st.session_state.source_dir, st.session_state.target_dir))
        add_log(f"➡️ 已跳过 → {current_pdf}")
        st.session_state.current_index += 1
        
        if st.session_state.current_index >= len(st.session_state.pdf_list):
            handle_directory_finished()
        st.rerun()

def handle_directory_finished():
    """目录处理完成"""
    st.session_state.directory_stack.append((st.session_state.source_dir, st.session_state.target_dir))
    add_log(f"✅ 目录处理完成：{st.session_state.source_dir}\n")
    
    if st.session_state.task_queue:
        next_source, next_target = st.session_state.task_queue.pop(0)
        load_directory(next_source, next_target)
    else:
        add_log("🎉 所有任务处理完成！")

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
            st.session_state.all_tasks = list(tasks)
            st.session_state.task_queue = list(tasks[1:])
            
            # 计算总PDF数
            total_pdfs = 0
            for source, target in st.session_state.all_tasks:
                if os.path.exists(source):
                    pdfs = [f for f in os.listdir(source) if f.lower().endswith('.pdf')]
                    total_pdfs += len(pdfs)
            st.session_state.total_pdfs = total_pdfs
            st.session_state.processed_pdfs = 0
            
            load_directory(tasks[0][0], tasks[0][1])
            st.toast(f"✅ 已加载 {len(tasks)} 个任务，共 {total_pdfs} 个PDF")
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

# -*- coding: utf-8 -*-
"""PDF 批量分类工具 V3 — GUI 辅助分类（复制、撤销、重启、日志）。

简要：加载目录后用数字键分类，支持预览与撤销。
依赖：tkinter、shutil、datetime、pathlib；可选：pymupdf + pillow（预览）。
使用：修改路径并运行脚本，按界面提示操作。
"""
import tkinter as tk
from tkinter import messagebox, scrolledtext
import os
import shutil
import datetime
from pathlib import Path

# 可选依赖：PyMuPDF + Pillow（预览）
try:
    import fitz  # PyMuPDF
    from PIL import Image, ImageTk
    HAVE_RENDER = True
except Exception:
    fitz = None
    Image = None
    ImageTk = None
    HAVE_RENDER = False

class PDFClassifier:
    def __init__(self, root):
        self.root = root
        self.source_dir = None
        self.target_dir = None
        self.pdf_list = []
        self.current_index = 0
        self.history = []  # 操作历史: (操作类型, 文件名, 源路径, 目标路径)
        self.global_history = []  # 全局历史: 记录所有操作包括跨目录 (操作类型, 文件名, 源路径, 目标路径, 当前source_dir, 当前target_dir)
        self.directory_stack = []  # 已完成目录栈: [(source_dir, target_dir), ...]
        self.task_queue = []  # 队列: [(source, target), ...]

        # 窗口
        self.root.title("PDF批量分类工具（支持撤销+日志）")
        self.root.geometry("600x380")
        self.root.resizable(False, False)

        # 快捷提示
        self.shortcut_label = tk.Label(
            root,
            text="【快捷键】 1=归类到好  |  2=跳过  |  8=撤销上一步",
            font=("Arial", 10, "bold"),
            fg="darkblue",
            bg="#f0f0f0"
        )
        self.shortcut_label.pack(fill=tk.X, pady=5)

        # 工具栏
        self.toolbar = tk.Frame(root)
        self.btn_restart_dir = tk.Button(self.toolbar, text="重新开始当前目录", command=self.restart_current_directory)
        self.btn_restart_all = tk.Button(self.toolbar, text="重新开始全部任务", command=self.restart_all_tasks)
        self.btn_restart_dir.pack(side=tk.LEFT, padx=5)
        self.btn_restart_all.pack(side=tk.LEFT, padx=5)
        self.toolbar.pack(pady=4)

        # 日志区域
        self.log_text = scrolledtext.ScrolledText(
            root,
            height=8,
            width=75,
            font=("Consolas", 9),
            state=tk.DISABLED  # 设为只读
        )
        self.log_text.pack(pady=5, padx=10)

        # 预览区（第一页）
        self.image_label = tk.Label(root)
        self.image_label.pack(pady=5)

        # 当前文件标签
        self.current_label = tk.Label(
            root,
            text=self.get_current_pdf_text(),
            font=("Arial", 11),
            wraplength=580,
            justify=tk.CENTER
        )
        self.current_label.pack(pady=20)

        # 绑定键
        self.root.bind("<Key>", self.on_key_press)

        # 初始化日志
        self.update_log("程序就绪，等待任务加载")

    def get_current_pdf_text(self):
        """返回当前文件提示文本"""
        if self.current_index < len(self.pdf_list):
            return f"当前待处理 → {self.pdf_list[self.current_index]}"
        else:
            return "✅ 所有PDF文件处理完成！"

    def update_log(self, content):
        """写日志并滚动到末尾"""
        timestamp = datetime.datetime.now().strftime("[%H:%M:%S]")
        self.log_text.config(state=tk.NORMAL)  # 临时解除只读
        self.log_text.insert(tk.END, f"{timestamp} {content}\n")
        self.log_text.see(tk.END)  # 滚动到末尾
        self.log_text.config(state=tk.DISABLED)  # 恢复只读

    def move_to_target(self, filename):
        """复制到目标并返回目标路径（同名覆盖）。"""
        source_path = os.path.join(self.source_dir, filename)
        target_path = os.path.join(self.target_dir, filename)
        # 直接复制，若存在则覆盖
        shutil.copy2(source_path, target_path)
        return target_path

    def render_pdf_preview(self, pdf_path, max_width=560, max_height=240):
        """渲染并显示 PDF 首页（可选依赖）。"""
        if not HAVE_RENDER:
            self.update_log("⚠️ 无法渲染预览：未安装 pymupdf 或 Pillow")
            return

        if not os.path.exists(pdf_path):
            self.image_label.config(image="")
            return

        try:
            doc = fitz.open(pdf_path)
            if doc.page_count < 1:
                self.image_label.config(image="")
                return
            page = doc.load_page(0)
            mat = fitz.Matrix(2, 2)
            pix = page.get_pixmap(matrix=mat, alpha=False)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            # 等比缩放
            w, h = img.size
            scale = min(max_width / w, max_height / h, 1.0)
            if scale < 1.0:
                img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)
            self.image_tk = ImageTk.PhotoImage(img)
            self.image_label.config(image=self.image_tk)
        except Exception as e:
            self.update_log(f"❌ 预览渲染失败: {e}")
            self.image_label.config(image="")

    def undo_last_operation(self):
        """撤销上一步（支持跨目录）"""
        if not self.global_history:
            self.update_log("⚠️ 无历史操作可撤销")
            messagebox.showinfo("提示", "没有可撤销的操作！")
            return

        last_op = self.global_history.pop()
        op_type, filename, src_path, tar_path, ctx_source, ctx_target = last_op

        # 如果撤销操作来自另一个目录，需要先恢复那个目录的状态
        if ctx_source != self.source_dir or ctx_target != self.target_dir:
            # 撤销涉及跨目录，需要回退当前目录并进入前一个目录
            if not self.directory_stack:
                messagebox.showerror("错误", "无法恢复前一个目录的状态")
                self.global_history.append(last_op)  # 恢复操作
                return
            
            # 保存当前目录状态
            prev_source, prev_target = self.directory_stack.pop()
            
            # 恢复到前一个目录
            self.source_dir = ctx_source
            self.target_dir = ctx_target
            
            # 重新加载该目录的PDF列表并恢复到完成时的状态
            self.pdf_list = [f for f in os.listdir(self.source_dir) if f.lower().endswith(".pdf")]
            self.current_index = len(self.pdf_list)  # 设为完成状态
            self.history = []  # 清空本地历史，因为现在从全局历史恢复
            
            # 重建本地历史（从全局历史中提取当前目录的操作）
            for h_op in self.global_history:
                h_op_type, h_filename, h_src, h_tar, h_ctx_src, h_ctx_tar = h_op
                if h_ctx_src == self.source_dir:
                    self.history.append((h_op_type, h_filename, h_src, h_tar))
                    if h_op_type == "copy":
                        self.current_index -= 1
                    elif h_op_type == "skip":
                        self.current_index -= 1
            
            self.update_log(f"⬅️ 已回退至前一个目录: {self.source_dir}")
        else:
            # 撤销操作在当前目录内
            if op_type == "copy":
                # 撤销复制：删除目标副本
                try:
                    if tar_path and os.path.exists(tar_path):
                        os.remove(tar_path)
                except Exception as e:
                    messagebox.showerror("错误", f"撤销失败：{str(e)}")
            elif op_type == "skip":
                # 仅回溯索引以重新处理该文件
                pass
            
            self.current_index -= 1
        
        # 同时从本地历史中移除（如果存在）
        if self.history:
            self.history.pop()
        
        self.current_label.config(text=self.get_current_pdf_text())
        # 更新预览
        self.show_current_pdf_preview()

    def on_key_press(self, event):
        """处理按键"""
        if self.current_index >= len(self.pdf_list) and not self.history:
            return

        key = event.char.lower()
        current_pdf = self.pdf_list[self.current_index] if self.current_index < len(self.pdf_list) else ""

        if key == "1" and self.current_index < len(self.pdf_list):
            # 归类
            tar_path = self.move_to_target(current_pdf)
            src_full_path = os.path.join(self.source_dir, current_pdf)
            self.history.append(("copy", current_pdf, src_full_path, tar_path))
            self.global_history.append(("copy", current_pdf, src_full_path, tar_path, self.source_dir, self.target_dir))
            self.update_log(f"✅ 复制完成 → {current_pdf} → {self.target_dir}")
            self.current_index += 1
            self.current_label.config(text=self.get_current_pdf_text())
            if self.current_index >= len(self.pdf_list):
                self.on_directory_finished()
            else:
                self.show_current_pdf_preview()

        elif key == "2" and self.current_index < len(self.pdf_list):
            # 跳过
            self.history.append(("skip", current_pdf, "", ""))
            self.global_history.append(("skip", current_pdf, "", "", self.source_dir, self.target_dir))
            self.update_log(f"➡️ 已跳过 → {current_pdf}")
            self.current_index += 1
            self.current_label.config(text=self.get_current_pdf_text())
            if self.current_index >= len(self.pdf_list):
                self.on_directory_finished()
            else:
                self.show_current_pdf_preview()

        elif key == "8":
            # 撤销
            self.undo_last_operation()

        elif key == "9":
            # 重新开始当前目录
            self.restart_current_directory()

        elif key == "0":
            # 重新开始全部任务
            self.restart_all_tasks()

        # 其他按键不响应

    def load_directory(self, source_dir, target_dir):
        """加载一个目录进行处理"""
        self.source_dir = source_dir
        self.target_dir = target_dir
        # 创建目标文件夹
        if not os.path.exists(self.target_dir):
            os.makedirs(self.target_dir)

        # 列出PDF文件
        self.pdf_list = [f for f in os.listdir(self.source_dir) if f.lower().endswith(".pdf")]
        self.current_index = 0
        self.history = []

        # 更新界面和日志
        self.current_label.config(text=self.get_current_pdf_text())
        # 渲染当前 PDF 的第一页预览
        self.show_current_pdf_preview()
        self.update_log("--- 开始新目录处理 ---")
        self.update_log(f"源文件夹: {self.source_dir}")
        self.update_log(f"目标文件夹: {self.target_dir}")
        self.update_log(f"待处理PDF总数: {len(self.pdf_list)}\n")
        
        # 如果当前目录没有 PDF 文件，自动切换到下一个任务
        if len(self.pdf_list) == 0:
            self.update_log("⚠️ 当前目录无 PDF 文件，自动跳过")
            self.on_directory_finished()

    def restart_current_directory(self):
        """将当前目录重新开始处理：从文件系统重新读取文件列表并从头开始（不撤销已移动的文件）。"""
        if not self.source_dir:
            self.update_log("⚠️ 当前没有加载目录，无法重新开始")
            return
        # 恢复目标文件夹中的文件到源目录（覆盖之前的处理）
        try:
            self.restore_directory_files(self.source_dir, self.target_dir)
        except Exception as e:
            self.update_log(f"❌ 恢复文件时出错: {e}")

        # 移除全局历史中与当前目录相关的操作
        self.global_history = [h for h in self.global_history if not (h[4] == self.source_dir and h[5] == self.target_dir)]
        
        # 重新读取当前源目录下的 PDF 列表并从头开始
        self.pdf_list = [f for f in os.listdir(self.source_dir) if f.lower().endswith(".pdf")]
        self.current_index = 0
        self.history = []
        self.current_label.config(text=self.get_current_pdf_text())
        self.show_current_pdf_preview()
        self.update_log(f"🔄 已重新开始当前目录并覆盖之前的处理：{self.source_dir}")

    def restart_all_tasks(self):
        """将所有任务重置为初始任务清单并从第一个任务开始处理。"""
        if not hasattr(self, 'all_tasks') or not self.all_tasks:
            self.update_log("⚠️ 无初始任务清单，无法重新开始全部任务")
            return
        # 对每个任务先恢复目标文件到源目录
        for src, targ in list(self.all_tasks):
            try:
                self.restore_directory_files(src, targ)
            except Exception as e:
                self.update_log(f"❌ 恢复 {targ} 到 {src} 时出错: {e}")

        # 清空全局历史和目录栈
        self.global_history = []
        self.directory_stack = []
        
        # 重新构建任务队列并开始第一个任务
        tasks_copy = list(self.all_tasks)
        first_source, first_target = tasks_copy.pop(0)
        self.task_queue = tasks_copy
        self.load_directory(first_source, first_target)
        self.update_log("🔁 已重新开始全部任务并覆盖之前的处理，从第一项重新处理")

    def restore_directory_files(self, source_dir, target_dir):
        """
        将目标目录中的 PDF 文件删除（因为现在使用复制）。
        """
        if not os.path.exists(target_dir):
            return

        for fname in os.listdir(target_dir):
            if not fname.lower().endswith('.pdf'):
                continue
            fpath = os.path.join(target_dir, fname)
            try:
                os.remove(fpath)
                self.update_log(f"🗑️ 删除目标文件 {fname} 从 {target_dir}")
            except Exception as e:
                self.update_log(f"❌ 删除文件 {fname} 时出错: {e}")

    def on_directory_finished(self):
        """当前目录处理完成，切换到下一个任务或结束程序"""
        # 保存当前目录到栈（用于撤销时恢复）
        self.directory_stack.append((self.source_dir, self.target_dir))
        
        self.update_log(f"✅ 目录处理完成：{self.source_dir}\n")
        if self.task_queue:
            next_source, next_target = self.task_queue.pop(0)
            self.load_directory(next_source, next_target)
        else:
            self.update_log("所有任务处理完成！")
            messagebox.showinfo("完成", "所有目录已处理完成！")

    def show_current_pdf_preview(self):
        """显示当前待处理 PDF 的第一页预览（若有）。"""
        if not self.source_dir or self.current_index >= len(self.pdf_list):
            # 清空
            self.image_label.config(image="")
            return
        current_pdf = self.pdf_list[self.current_index]
        pdf_path = os.path.join(self.source_dir, current_pdf)
        self.render_pdf_preview(pdf_path)

if __name__ == "__main__":
    base_path = Path("files_debug")
    tasks = []
    for number_dir in sorted(base_path.iterdir()):
        if not number_dir.is_dir():
            continue
        for category_dir in sorted(number_dir.iterdir()):
            if not category_dir.is_dir():
                continue
            # 遍历所有 partxx 目录
            for part_dir in sorted(category_dir.iterdir()):
                if not part_dir.is_dir() or not part_dir.name.startswith("part"):
                    continue
                SOURCE_DIRECTORY = str(part_dir)
                TARGET_DIRECTORY = str(part_dir / "非常好")
                # 仅加入存在的源目录
                if os.path.exists(SOURCE_DIRECTORY):
                    tasks.append((SOURCE_DIRECTORY, TARGET_DIRECTORY))

    if not tasks:
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("错误", "未找到任何有效的源文件夹，请检查路径")
        root.destroy()
    else:
        root = tk.Tk()
        app = PDFClassifier(root)
        # 将任务保存为初始清单，并加载第一个任务
        first_source, first_target = tasks.pop(0)
        app.all_tasks = [(first_source, first_target)] + list(tasks)
        app.task_queue = list(tasks)
        app.load_directory(first_source, first_target)
        root.mainloop()
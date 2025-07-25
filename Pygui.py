import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import threading
import logging
from typing import Optional, Callable, Any
import pandas as pd
import weakref
import gc
import subprocess
import json
from concurrent.futures import ThreadPoolExecutor

# 从项目其他模块导入函数
from extract_ui import extract_system_tree
from transition_ui import preprocess_to_excel
from parmeter_ui import handle_param_file
from matcher_ui import run_and_display_matching
from load_ui import apply_real_id_to_fam
from save_excel_ui import generate_json_and_excel
from compress_ui import GIMExtractor
from device_display_ui import display_device_data, display_param_data

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("工程建设数据与三维模型自动挂接工具")
        self.root.geometry("1200x700")
        self.gim_extract_dir: Optional[str] = None
        self.gim_path: Optional[str] = None
        self.df: Optional[pd.DataFrame] = None

        # 线程池用于后台任务
        self.executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="AppWorker")

        # 使用弱引用缓存，防止内存泄漏
        self._file_tree_cache = weakref.WeakValueDictionary()

        # 当前任务状态
        self._current_task: Optional[threading.Thread] = None
        self._task_cancelled = False

        self._setup_window()
        self._create_ui()

        # 绑定窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

    def _setup_window(self) -> None:
        """设置窗口属性"""
        if os.name == 'nt':
            try:
                import ctypes
                ctypes.windll.shcore.SetProcessDpiAwareness(1)
            except (ImportError, AttributeError, OSError):
                pass
        try:
            self.root.state('zoomed')
        except tk.TclError:
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            self.root.geometry(f"{screen_width}x{screen_height - 60}+0+0")
        try:
            icon_path = "app.ico"
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except tk.TclError:
            self.log("ℹ️ 未找到或无法设置窗口图标 (app.ico)。")
        self.root.configure(bg='#f0f0f0')
        self.root.minsize(800, 600)

    def _create_ui(self) -> None:
        """创建用户界面"""
        button_frame = tk.Frame(self.root, bg='#f0f0f0')
        button_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        button_configs = [
            ("导入", self._import_action, "选择并解压.gim文件"),
            ("导出设备清单", self._export_action, "从模型数据生成设备Excel清单"),
            ("参数文件", self._param_action, "选择实物ID清单并自动处理"),
            ("挂接", self._mount_action, "自动匹配模型与实物ID"),
            ("载入", self._load_action, "将挂接结果写回模型文件"),
            ("保存", self._save_action, "将修改后的文件重新打包为.gim")
        ]

        self.buttons = {}
        for name, command, tooltip in button_configs:
            btn = tk.Button(button_frame, text=name, width=12, command=command, relief=tk.RAISED, bd=2)
            btn.pack(side=tk.LEFT, padx=5, pady=5)
            self.buttons[name] = btn
            self._create_tooltip(btn, tooltip)

        main_pane = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, sashrelief=tk.RAISED)
        main_pane.pack(fill="both", expand=True, padx=10)

        self.file_tree_frame = ttk.LabelFrame(main_pane, text="项目文件结构")
        self._create_file_tree()
        main_pane.add(self.file_tree_frame, width=300, stretch="never")

        right_pane = tk.PanedWindow(main_pane, orient=tk.VERTICAL, sashrelief=tk.RAISED)
        main_pane.add(right_pane, stretch="always")

        mount_frame_wrapper = ttk.LabelFrame(right_pane, text="可视化数据与操作")
        self.mount_frame = ttk.Frame(mount_frame_wrapper)
        self.mount_frame.pack(fill="both", expand=True, padx=5, pady=5)
        right_pane.add(mount_frame_wrapper, height=500, stretch="always")

        self._create_log_area()

        self.progress = ttk.Progressbar(self.root, orient="horizontal", mode="determinate")
        self.progress.pack(side="bottom", fill="x", padx=10, pady=(5, 10))

    def _create_file_tree(self) -> None:
        """创建文件树控件"""
        tree_scroll_y = ttk.Scrollbar(self.file_tree_frame, orient="vertical")
        tree_scroll_y.pack(side="right", fill="y")
        tree_scroll_x = ttk.Scrollbar(self.file_tree_frame, orient="horizontal")
        tree_scroll_x.pack(side="bottom", fill="x")

        self.file_tree = ttk.Treeview(
            self.file_tree_frame,
            yscrollcommand=tree_scroll_y.set,
            xscrollcommand=tree_scroll_x.set,
            selectmode="extended"
        )
        self.file_tree.pack(fill="both", expand=True)
        tree_scroll_y.config(command=self.file_tree.yview)
        tree_scroll_x.config(command=self.file_tree.xview)

        self.file_tree.bind("<Double-1>", self._on_tree_double_click)

    def _create_log_area(self) -> None:
        """创建日志区域"""
        log_frame = ttk.LabelFrame(self.root, text="运行日志")
        log_frame.pack(side="bottom", fill="x", padx=10, pady=(0, 5))

        log_scroll = ttk.Scrollbar(log_frame)
        log_scroll.pack(side="right", fill="y")

        self.log_text = tk.Text(log_frame, height=6, bg="#F8F9FA", fg="#2C3E50", font=("Consolas", 9),
                                yscrollcommand=log_scroll.set, wrap=tk.WORD, state=tk.DISABLED,
                                insertbackground="#2C3E50", selectbackground="#E3F2FD", relief="flat", bd=1)
        self.log_text.pack(fill="both", expand=True, padx=5, pady=5)
        log_scroll.config(command=self.log_text.yview)

        clear_btn = tk.Button(log_frame, text="清除日志", command=self._clear_log, width=10)
        clear_btn.pack(side="right", padx=5, pady=2)

    def _create_tooltip(self, widget: tk.Widget, text: str) -> None:
        """创建工具提示"""
        tooltip = None

        def show_tooltip(event):
            nonlocal tooltip
            if tooltip:
                tooltip.destroy()
            tooltip = tk.Toplevel(widget)
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root + 15}+{event.y_root + 10}")
            label = tk.Label(tooltip, text=text, background="lightyellow", relief="solid", borderwidth=1,
                             font=("Arial", 9))
            label.pack()

        def hide_tooltip(event):
            nonlocal tooltip
            if tooltip:
                tooltip.destroy()
                tooltip = None

        widget.bind("<Enter>", show_tooltip)
        widget.bind("<Leave>", hide_tooltip)

    def log(self, msg: str) -> None:
        """线程安全的日志记录"""

        def _log():
            self.log_text.config(state=tk.NORMAL)
            self.log_text.insert(tk.END, f"{msg}\n")
            self.log_text.see(tk.END)
            self.log_text.config(state=tk.DISABLED)

        if threading.current_thread() != threading.main_thread():
            self.root.after(0, _log)
        else:
            _log()

    def _clear_log(self) -> None:
        """清除日志内容"""
        self.log_text.config(state=tk.NORMAL)
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state=tk.DISABLED)

    def set_progress(self, val: float) -> None:
        """线程安全的进度更新"""

        def _update():
            self.progress['value'] = val
            self.root.update_idletasks()

        if threading.current_thread() != threading.main_thread():
            self.root.after(0, _update)
        else:
            _update()

    def _set_buttons_state(self, state: str) -> None:
        """设置所有按钮的状态"""
        for btn in self.buttons.values():
            btn.config(state=state)

    def populate_file_tree(self, root_path: str) -> None:
        """填充文件树，只显示文件名，不显示类型和大小"""
        if not os.path.exists(root_path):
            self.log(f"❌ 路径不存在: {root_path}")
            return

        self.file_tree.delete(*self.file_tree.get_children())

        # 简化：不设置额外列，只使用默认的文件名列
        self.file_tree["columns"] = ()
        self.file_tree.column("#0", width=300, stretch=tk.YES)
        self.file_tree.heading("#0", text="文件名", anchor="w")

        def should_show_file(name: str, full_path: str) -> bool:
            """判断是否应该显示该文件"""
            # 过滤掉JSON文件
            if name.lower().endswith('.json'):
                return False
            # 可以添加更多过滤规则
            return True

        def insert_items_async(parent: str, path: str) -> None:
            """异步插入文件项，只显示文件名"""
            try:
                self.log(f"🔄 正在加载文件树: {os.path.basename(path)}")
                all_items = os.listdir(path)
                # 过滤文件
                items = [name for name in all_items
                         if should_show_file(name, os.path.join(path, name))]
                # 排序：文件夹在前，然后按名称排序
                items = sorted(items, key=lambda x: (not os.path.isdir(os.path.join(path, x)), x.lower()))

                batch_size = 100  # 增加批处理大小
                total_batches = (len(items) + batch_size - 1) // batch_size

                for batch_idx in range(total_batches):
                    start_idx = batch_idx * batch_size
                    end_idx = min(start_idx + batch_size, len(items))
                    batch_items = items[start_idx:end_idx]

                    for name in batch_items:
                        try:
                            full_path = os.path.join(path, name)
                            is_dir = os.path.isdir(full_path)

                            # 只插入文件名，不需要额外的值
                            node = self.file_tree.insert(parent, 'end', text=name, open=False)

                            # 只有文件夹且非空时才添加占位符
                            if is_dir:
                                try:
                                    # 检查文件夹是否有可显示的内容
                                    has_visible_content = any(
                                        should_show_file(item, os.path.join(full_path, item))
                                        for item in os.listdir(full_path)
                                    )
                                    if has_visible_content:
                                        self.file_tree.insert(node, 'end', text="...")
                                except (OSError, PermissionError):
                                    pass
                        except Exception as e:
                            self.log(f"⚠️ 跳过文件: {name}, {e}")

                    # 批次间短暂休息，让UI响应
                    if batch_idx < total_batches - 1:
                        self.root.update_idletasks()

                filtered_count = len(all_items) - len(items)
                if filtered_count > 0:
                    self.log(f"📂 文件树加载完成: {len(items)} 个项目 (已过滤 {filtered_count} 个文件)")
                else:
                    self.log(f"📂 文件树加载完成: {len(items)} 个项目")

            except Exception as e:
                self.log(f"❌ 无法访问: {path}, {e}")

        # 在后台线程中执行文件加载
        def load_in_background():
            try:
                insert_items_async('', root_path)
            finally:
                self.root.after(0, lambda: self.file_tree.bind("<<TreeviewOpen>>", self._on_tree_expand))

        # 使用线程池执行异步任务
        self.executor.submit(load_in_background)

    def _on_tree_expand(self, event) -> None:
        """处理树节点展开事件，实现懒加载"""
        item = self.file_tree.focus()
        if not item: return

        children = self.file_tree.get_children(item)
        if len(children) == 1 and self.file_tree.item(children[0], 'text') == "...":
            self.file_tree.delete(children[0])

            path_parts = [self.file_tree.item(item, 'text')]
            parent_item = self.file_tree.parent(item)
            while parent_item:
                path_parts.insert(0, self.file_tree.item(parent_item, 'text'))
                parent_item = self.file_tree.parent(parent_item)

            path = os.path.join(self.gim_extract_dir, *path_parts)

            def should_show_file(name: str, full_path: str) -> bool:
                """判断是否应该显示该文件"""
                if name.lower().endswith('.json'):
                    return False
                return True

            def insert_items(parent_node, current_path):
                try:
                    all_items = os.listdir(current_path)
                    items = [name for name in all_items
                             if should_show_file(name, os.path.join(current_path, name))]
                    items = sorted(items, key=lambda x: (not os.path.isdir(os.path.join(current_path, x)), x.lower()))

                    for name in items:
                        full_path = os.path.join(current_path, name)
                        is_dir = os.path.isdir(full_path)

                        # 只插入文件名
                        node = self.file_tree.insert(parent_node, 'end', text=name, open=False)

                        if is_dir:
                            try:
                                dir_items = os.listdir(full_path)
                                has_visible_content = any(
                                    should_show_file(item, os.path.join(full_path, item))
                                    for item in dir_items
                                )
                                if has_visible_content:
                                    self.file_tree.insert(node, 'end', text="...")
                            except (OSError, PermissionError):
                                pass
                except Exception as e:
                    self.log(f"❌ 无法访问: {current_path}, {e}")

            insert_items(item, path)

    def _on_tree_double_click(self, event) -> None:
        """处理文件树双击事件 - 显示文件内容窗口"""
        item = self.file_tree.focus()
        if not item: return

        path_parts = [self.file_tree.item(item, 'text')]
        parent_item = self.file_tree.parent(item)
        while parent_item:
            path_parts.insert(0, self.file_tree.item(parent_item, 'text'))
            parent_item = self.file_tree.parent(parent_item)
        file_path = os.path.join(self.gim_extract_dir, *path_parts)

        if os.path.isfile(file_path):
            self._show_file_content_window(file_path)

    def _show_file_content_window(self, file_path: str) -> None:
        """显示文件内容的独立窗口 - 居中显示"""
        try:
            file_name = os.path.basename(file_path)
            content_window = tk.Toplevel(self.root)
            content_window.title(f"文件内容 - {file_name}")

            # 设置窗口大小
            window_width = 1000
            window_height = 700

            # 获取屏幕尺寸
            screen_width = content_window.winfo_screenwidth()
            screen_height = content_window.winfo_screenheight()

            # 计算居中位置
            center_x = int((screen_width - window_width) / 2)
            center_y = int((screen_height - window_height) / 2)

            # 设置窗口大小和位置（居中）
            content_window.geometry(f"{window_width}x{window_height}+{center_x}+{center_y}")
            content_window.transient(self.root)
            content_window.grab_set()  # 设置为模态窗口

            # 设置窗口图标（如果有的话）
            try:
                if hasattr(self.root, 'iconbitmap'):
                    content_window.iconbitmap(default="app.ico")
            except:
                pass

            # 创建顶部信息栏
            info_frame = tk.Frame(content_window, bg="#f0f0f0", height=40)
            info_frame.pack(fill="x", padx=0, pady=0)
            info_frame.pack_propagate(False)

            # 文件信息
            try:
                file_size = os.path.getsize(file_path)
                size_text = self._format_size(file_size)
                file_info = f"📄 文件: {file_name}  |  📏 大小: {size_text}  |  📍 路径: {file_path}"
            except:
                file_info = f"📄 文件: {file_name}  |  📍 路径: {file_path}"

            info_label = tk.Label(info_frame, text=file_info,
                                  font=("微软雅黑", 9), bg="#f0f0f0", fg="#333",
                                  anchor="w")
            info_label.pack(side="left", fill="both", expand=True, padx=10, pady=8)

            # 添加关闭按钮
            close_btn = tk.Button(info_frame, text="✕ 关闭",
                                  command=content_window.destroy,
                                  font=("微软雅黑", 9), bg="#ff4444", fg="white",
                                  relief="flat", padx=15, cursor="hand2")
            close_btn.pack(side="right", padx=10, pady=5)

            # 创建主内容框架
            text_frame = tk.Frame(content_window)
            text_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))

            # 垂直滚动条
            scrollbar_y = ttk.Scrollbar(text_frame, orient="vertical")
            scrollbar_y.pack(side="right", fill="y")

            # 水平滚动条
            scrollbar_x = ttk.Scrollbar(text_frame, orient="horizontal")
            scrollbar_x.pack(side="bottom", fill="x")

            # 文本显示区域
            text_widget = tk.Text(text_frame, wrap=tk.NONE,
                                  yscrollcommand=scrollbar_y.set,
                                  xscrollcommand=scrollbar_x.set,
                                  font=("Consolas", 11),
                                  bg="#fafafa", fg="#333",
                                  insertbackground="#333",
                                  selectbackground="#CCE5FF",
                                  relief="flat", bd=0,
                                  padx=10, pady=10)
            text_widget.pack(side="left", fill="both", expand=True)

            scrollbar_y.config(command=text_widget.yview)
            scrollbar_x.config(command=text_widget.xview)

            # 读取并显示文件内容
            try:
                # 检查文件大小，避免加载过大文件
                file_size = os.path.getsize(file_path)
                if file_size > 10 * 1024 * 1024:  # 10MB限制
                    content = f"⚠️ 文件过大 ({self._format_size(file_size)})，无法预览。\n\n文件路径: {file_path}"
                else:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()

                    # 如果内容为空
                    if not content.strip():
                        content = "📝 文件为空"

            except UnicodeDecodeError:
                # 尝试其他编码
                try:
                    with open(file_path, 'r', encoding='gbk', errors='ignore') as f:
                        content = f.read()
                except:
                    content = f"❌ 无法读取文件内容（可能是二进制文件）\n\n文件路径: {file_path}"
            except Exception as e:
                content = f"❌ 读取文件时发生错误: {str(e)}\n\n文件路径: {file_path}"

            text_widget.insert(tk.END, content)
            text_widget.config(state=tk.DISABLED)  # 设置为只读

            # 创建底部状态栏
            status_frame = tk.Frame(content_window, bg="#e0e0e0", height=30)
            status_frame.pack(fill="x", side="bottom")
            status_frame.pack_propagate(False)

            # 显示行数统计
            line_count = content.count('\n') + 1 if content else 0
            char_count = len(content) if content else 0
            status_text = f"📊 共 {line_count} 行  |  🔤 {char_count} 个字符"

            status_label = tk.Label(status_frame, text=status_text,
                                    font=("微软雅黑", 8), bg="#e0e0e0", fg="#666",
                                    anchor="w")
            status_label.pack(side="left", fill="y", padx=10, pady=5)

            # 键盘快捷键
            def on_key_press(event):
                if event.state & 0x4:  # Ctrl键
                    if event.keysym.lower() == 'f':  # Ctrl+F 查找
                        self._show_search_dialog(text_widget)
                        return "break"
                    elif event.keysym.lower() == 'w':  # Ctrl+W 关闭
                        content_window.destroy()
                        return "break"
                elif event.keysym == 'Escape':  # ESC 关闭
                    content_window.destroy()
                    return "break"

            content_window.bind('<Key>', on_key_press)
            content_window.focus_set()

            # 添加右键菜单
            def show_context_menu(event):
                context_menu = tk.Menu(content_window, tearoff=0)
                context_menu.add_command(label="📋 复制全部",
                                         command=lambda: self._copy_to_clipboard(content))
                context_menu.add_command(label="🔍 查找文本",
                                         command=lambda: self._show_search_dialog(text_widget))
                context_menu.add_separator()
                context_menu.add_command(label="📁 打开文件位置",
                                         command=lambda: self._open_file_location(os.path.dirname(file_path)))
                context_menu.add_separator()
                context_menu.add_command(label="✕ 关闭窗口",
                                         command=content_window.destroy)
                try:
                    context_menu.post(event.x_root, event.y_root)
                except:
                    pass

            text_widget.bind("<Button-3>", show_context_menu)

            # 窗口关闭时的清理
            def on_closing():
                try:
                    content_window.grab_release()
                    content_window.destroy()
                except:
                    pass

            content_window.protocol("WM_DELETE_WINDOW", on_closing)

        except Exception as e:
            self.log(f"❌ 打开文件内容失败: {e}")
            messagebox.showerror("打开失败", f"无法预览文件内容:\n{e}")

    def _copy_to_clipboard(self, text: str):
        """复制文本到剪贴板"""
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            self.log("✅ 内容已复制到剪贴板")
        except Exception as e:
            self.log(f"❌ 复制失败: {e}")

    def _show_search_dialog(self, text_widget):
        """显示搜索对话框"""
        try:
            search_window = tk.Toplevel(self.root)
            search_window.title("查找文本")
            search_window.geometry("400x100")
            search_window.transient(self.root)
            search_window.grab_set()

            # 居中显示搜索窗口
            search_window.update_idletasks()
            x = (search_window.winfo_screenwidth() // 2) - (search_window.winfo_width() // 2)
            y = (search_window.winfo_screenheight() // 2) - (search_window.winfo_height() // 2)
            search_window.geometry(f"+{x}+{y}")

            tk.Label(search_window, text="查找内容:", font=("微软雅黑", 10)).pack(pady=10)

            search_entry = tk.Entry(search_window, font=("微软雅黑", 10), width=40)
            search_entry.pack(pady=5)
            search_entry.focus_set()

            def do_search():
                search_text = search_entry.get()
                if search_text:
                    # 清除之前的高亮
                    text_widget.tag_remove("search", "1.0", tk.END)

                    # 搜索并高亮
                    start = "1.0"
                    while True:
                        pos = text_widget.search(search_text, start, tk.END)
                        if not pos:
                            break
                        end = f"{pos}+{len(search_text)}c"
                        text_widget.tag_add("search", pos, end)
                        start = end

                    # 设置高亮样式
                    text_widget.tag_config("search", background="yellow", foreground="black")

                    # 跳转到第一个匹配项
                    first_match = text_widget.search(search_text, "1.0", tk.END)
                    if first_match:
                        text_widget.see(first_match)

                    search_window.destroy()

            search_entry.bind('<Return>', lambda e: do_search())

            btn_frame = tk.Frame(search_window)
            btn_frame.pack(pady=10)

            tk.Button(btn_frame, text="查找", command=do_search,
                      font=("微软雅黑", 9)).pack(side=tk.LEFT, padx=5)
            tk.Button(btn_frame, text="取消", command=search_window.destroy,
                      font=("微软雅黑", 9)).pack(side=tk.LEFT, padx=5)

        except Exception as e:
            self.log(f"❌ 搜索功能错误: {e}")

    def _import_action(self) -> None:
        """导入GIM文件"""
        file_path = filedialog.askopenfilename(title="选择 GIM 文件", filetypes=[("GIM 文件", "*.gim")])
        if not file_path: return

        def task():
            try:
                self.log(f"📥 正在导入: {os.path.basename(file_path)}")
                extractor = GIMExtractor(file_path)
                out_dir = extractor.extract_embedded_7z()
                self.gim_extract_dir = out_dir
                self.gim_path = file_path
                self.root.after(0, self.populate_file_tree, out_dir)
                return f"导入成功, 解压至: {out_dir}"
            except Exception as e:
                raise Exception(f"导入GIM文件时发生错误: {e}")

        self._run_async_task(task, "导入GIM文件")

    def _export_action(self) -> None:
        """导出设备清单"""
        if not self._check_gim_imported(): return

        def task():
            try:
                self.log("🔄 正在提取系统树...")
                json_path = extract_system_tree(self.gim_extract_dir)
                self.log("📝 正在从JSON生成Excel文件...")
                excel_path = preprocess_to_excel(json_path)
                self.log(f"📊 设备清单已生成: {excel_path}")
                
                # 在可视化数据框中显示设备清单
                self.root.after(0, lambda: display_device_data(self.mount_frame, excel_path))
                
                return f"设备清单已生成并显示: {excel_path}"
            except Exception as e:
                raise Exception(f"导出设备清单时发生错误: {e}")

        self._run_async_task(task, "导出设备清单")

    def _param_action(self) -> None:
        """选择参数文件并自动处理"""
        file_path = filedialog.askopenfilename(
            title="选择参数文件 (实物ID清单)",
            filetypes=[("Excel/CSV 文件", "*.xlsx;*.xls;*.csv"), ("所有文件", "*.*")],
            initialdir=self.gim_extract_dir if self.gim_extract_dir else os.getcwd()
        )
        if not file_path:
            self.log("ℹ️ 用户取消了文件选择。")
            return

        def task():
            """在后台线程中处理文件的任务"""
            try:
                self.log(f"🚀 正在自动处理参数文件: {os.path.basename(file_path)}")
                # 处理参数文件，不显示弹窗预览
                result_path = handle_param_file(file_path, show_preview=False)
                
                # 在可视化数据框中显示参数数据
                self.root.after(0, lambda: display_param_data(self.mount_frame, result_path))
                
                success_msg = f"参数文件已成功处理！\n标准参考文件已生成: {result_path}"
                self.log(f"✅ {success_msg.replace(chr(10), ' ')}")
                
                return f"参数文件处理完成并显示: {result_path}"

            except Exception as e:
                error_msg = f"处理参数文件时发生错误:\n{e}"
                self.log(f"❌ {error_msg.replace(chr(10), ' ')}")
                raise

        self._run_async_task(task, "参数文件自动处理")

    def _mount_action(self) -> None:
        """执行挂接操作"""
        if not self._check_gim_imported(): return
        if not os.path.exists("device_data.xlsx") or not os.path.exists("test_work.xlsx"):
            messagebox.showwarning("文件缺失", "请先执行“导出设备清单”和“参数文件”步骤。")
            return

        def task():
            try:
                self.log("🔗 正在执行挂接操作...")
                # run_and_display_matching现在直接在主线程中创建UI组件，所以使用after
                self.root.after(0, run_and_display_matching, self.mount_frame)
                return "挂接与匹配完成，请在界面上校对结果。"
            except Exception as e:
                raise Exception(f"挂接操作时发生错误: {e}")

        self._run_async_task(task, "挂接操作")

    def _load_action(self) -> None:
        """载入数据"""
        if not self._check_gim_imported(): return
        if not os.path.exists("最终修正结果.xlsx"):
            messagebox.showwarning("文件缺失", "未找到“最终修正结果.xlsx”。\n请先执行“挂接”并在表格中导出结果。")
            return

        def task():
            try:
                self.log("📂 正在将实物ID载入模型文件...")
                result = apply_real_id_to_fam(base_path=self.gim_extract_dir, strict=True)
                return result
            except Exception as e:
                raise Exception(f"载入数据时发生错误: {e}")

        self._run_async_task(task, "数据载入")

    def _save_action(self) -> None:
        """保存结果"""
        if not self._check_gim_imported(): return

        def task():
            try:
                self.log("💾 正在封装GIM文件...")
                output_gim_path = self.gim_path.replace(".gim", "_已挂接.gim")
                extractor = GIMExtractor(self.gim_path)

                with open(self.gim_path, 'rb') as f:
                    extractor.gim_header = f.read(776)

                extractor.build_custom_file(self.gim_extract_dir, output_gim_path)

                self.root.after(0, self._open_file_location, os.path.dirname(output_gim_path))
                return f"封装完成: {output_gim_path}"
            except Exception as e:
                raise Exception(f"保存结果时发生错误: {e}")

        self._run_async_task(task, "保存结果")

    def _run_async_task(self, task_func: Callable, task_name: str) -> None:
        """异步运行任务"""
        if self._current_task and self._current_task.is_alive():
            messagebox.showwarning("警告", "已有任务正在执行，请等待完成。")
            return

        def wrapped_task():
            try:
                self._task_cancelled = False
                self.root.after(0, self._set_buttons_state, tk.DISABLED)
                self.root.after(0, self.set_progress, 10)
                self.log(f"🚀 开始执行: {task_name}")

                result = task_func()

                if not self._task_cancelled:
                    self.root.after(0, self.set_progress, 100)
                    if result:
                        self.log(f"✅ {task_name} 完成: {result}")
                    else:
                        self.log(f"✅ {task_name} 完成")

            except Exception as e:
                if not self._task_cancelled:
                    self.log(f"❌ {task_name} 失败: {e}")
                    logger.error(f"{task_name} 错误: {e}", exc_info=True)

            finally:
                if not self._task_cancelled:
                    self.root.after(0, self.set_progress, 0)
                self.root.after(0, self._set_buttons_state, tk.NORMAL)
                self._current_task = None
                gc.collect()

        self._current_task = threading.Thread(target=wrapped_task, name=f"Task-{task_name}")
        self._current_task.daemon = True
        self._current_task.start()

    def _check_gim_imported(self) -> bool:
        """检查是否已导入GIM文件"""
        if not self.gim_extract_dir or not os.path.exists(self.gim_extract_dir):
            messagebox.showwarning("操作无效", "请先通过“导入”按钮解压一个 .gim 文件。")
            return False
        return True

    def _format_size(self, size_bytes: int) -> str:
        """格式化文件大小"""
        if size_bytes == 0: return ""
        size_names = ("B", "KB", "MB", "GB", "TB")
        i = 0
        s = float(size_bytes)
        while s >= 1024 and i < len(size_names) - 1:
            s /= 1024
            i += 1
        return f"{s:.1f} {size_names[i]}"

    def _open_file_location(self, path: str, open_file=False):
        """打开文件或其所在目录"""
        try:
            if os.name == 'nt':
                if open_file:
                    os.startfile(path)
                else:
                    subprocess.run(['explorer', '/select,', path])
            else:
                opener = "open" if open_file else "open -R"
                subprocess.run([opener, path], shell=True)
        except Exception as e:
            self.log(f"⚠️ 无法打开: {e}")

    def _on_closing(self) -> None:
        """处理窗口关闭事件"""
        if messagebox.askokcancel("退出", "您确定要退出程序吗?"):
            self._task_cancelled = True
            if self._current_task and self._current_task.is_alive():
                self.log("🛑 正在等待当前任务结束...")
                self._current_task.join(timeout=2.0)
            self.executor.shutdown(wait=False)
            self.root.destroy()


if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = App(root)
        root.mainloop()
    except Exception as e:
        logging.error(f"应用程序启动失败: {e}", exc_info=True)
        messagebox.showerror("启动错误", f"应用程序启动失败: {e}")

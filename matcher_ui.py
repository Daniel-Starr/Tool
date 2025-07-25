import pandas as pd
from tkinter import ttk, messagebox
import tkinter as tk
from matching01 import DataProcessor, generate_initial_report


def run_and_display_matching(parent_frame: ttk.Frame, filter_nan=True):
    """
    运行匹配逻辑，生成报告，并在UI上显示过滤后的、已成功匹配的结果。
    """
    processor = DataProcessor("device_data.xlsx", "test_work.xlsx")
    results = processor.match_devices()
    report_path = "智能设备匹配报告-专业版.xlsx"

    # 生成的Excel报告仍将包含所有条目，包括未匹配的
    generate_initial_report(results, processor.model_df, report_path)

    # 加载并显示表格，此函数内部已增加了过滤逻辑
    load_mount_table(parent_frame, report_path, filter_nan=filter_nan)


def load_mount_table(parent_frame: ttk.Frame, excel_path="智能设备匹配报告-专业版.xlsx", filter_nan=True):
    """
    加载匹配报告并在UI上创建可交互的表格。
    改进版本：优化下拉框体验，支持搜索和筛选。
    """
    df_original = pd.read_excel(excel_path).fillna("")
    df = df_original.copy()

    # 添加匹配状态分类
    df['匹配分类'] = df.apply(lambda row:
                              '✅ 已匹配' if row['实物ID'] != '需手动输入'
                              else '⚠️ 需手动匹配', axis=1)

    try:
        # 读取可用的实物ID列表
        ref_df = pd.read_excel("test_work.xlsx").fillna("")
        candidate_aliases = ["实物ID", "ID", "PhysicalID"]
        actual_col = next((col for col in ref_df.columns
                           if any(alias in str(col) for alias in candidate_aliases)), None)

        if actual_col is None:
            raise Exception(f"未找到实物ID相关列，列名包括：{ref_df.columns.tolist()}")

        raw_ids = ref_df[actual_col].dropna().astype(str)
        clean_ids = [i.strip() for i in raw_ids if i.strip() and i.strip().lower() != 'nan']
        available_ids = sorted(set(clean_ids))

        # 限制ID数量，提升性能
        if len(available_ids) > 500:
            available_ids = available_ids[:500]
            search_hint = True
        else:
            search_hint = False

    except Exception as e:
        messagebox.showerror("读取ID失败", f"无法从 test_work.xlsx 读取实物ID列表：\n{e}")
        available_ids = []
        search_hint = False

    # 清空旧的UI组件
    for widget in parent_frame.winfo_children():
        widget.destroy()

    # 创建控制面板
    control_frame = ttk.Frame(parent_frame)
    control_frame.pack(fill="x", padx=5, pady=5)

    # 统计信息
    total_count = len(df)
    matched_count = len(df[df['实物ID'] != '需手动输入'])
    unmatched_count = total_count - matched_count

    stats_label = ttk.Label(control_frame,
                            text=f"总计: {total_count} | ✅ 已匹配: {matched_count} | ⚠️ 需手动匹配: {unmatched_count}",
                            font=("微软雅黑", 10, "bold"))
    stats_label.pack(side="left", padx=5)

    # 筛选选项
    filter_var = tk.StringVar(value="全部")
    filter_combo = ttk.Combobox(control_frame, textvariable=filter_var,
                                values=["全部", "✅ 已匹配", "⚠️ 需手动匹配"],
                                state="readonly", width=15)
    filter_combo.pack(side="right", padx=5)

    # 搜索提示
    if search_hint:
        hint_label = ttk.Label(control_frame,
                               text=f"💡 实物ID选项已限制为500个，支持搜索过滤功能",
                               font=("微软雅黑", 8), foreground="blue")
        hint_label.pack(side="right", padx=10)

    current_df = df.copy()

    # 创建表格框架
    tree_frame = ttk.Frame(parent_frame)
    tree_frame.pack(fill="both", expand=True)

    v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical")
    v_scrollbar.pack(side="right", fill="y")

    h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal")
    h_scrollbar.pack(side="bottom", fill="x")

    tree = ttk.Treeview(
        tree_frame,
        columns=list(current_df.columns),
        show="headings",
        height=20,
        yscrollcommand=v_scrollbar.set,
        xscrollcommand=h_scrollbar.set
    )
    tree.pack(side="left", fill="both", expand=True)
    v_scrollbar.config(command=tree.yview)
    h_scrollbar.config(command=tree.xview)

    def refresh_table():
        """根据筛选条件刷新表格"""
        nonlocal current_df

        filter_value = filter_var.get()
        if filter_value == "全部":
            current_df = df.copy()
        else:
            current_df = df[df['匹配分类'] == filter_value].copy()

        # 清空树视图
        for item in tree.get_children():
            tree.delete(item)

        tree["columns"] = list(current_df.columns)

        # 设置列标题和宽度
        for col in current_df.columns:
            content_len = current_df[col].astype(str).apply(len).max() if len(current_df) > 0 else 0
            header_len = len(str(col))
            max_len = max(content_len, header_len)
            col_width = min(max(max_len * 8 + 20, 100), 300)
            tree.heading(col, text=col, anchor="center")
            tree.column(col, width=col_width, anchor="center", stretch=True)

        # 填充表格数据
        for idx, row in current_df.iterrows():
            tags = ()
            if row.get('匹配分类', '') == '⚠️ 需手动匹配':
                tags = ('unmatched',)
            elif row.get('匹配分类', '') == '✅ 已匹配':
                tags = ('matched',)
            tree.insert("", "end", iid=str(idx), values=list(row), tags=tags)

    # 初始设置列
    for col in current_df.columns:
        content_len = current_df[col].astype(str).apply(len).max() if len(current_df) > 0 else 0
        header_len = len(str(col))
        max_len = max(content_len, header_len)
        col_width = min(max(max_len * 8 + 20, 100), 300)
        tree.heading(col, text=col, anchor="center")
        tree.column(col, width=col_width, anchor="center", stretch=True)

    refresh_table()
    filter_combo.bind("<<ComboboxSelected>>", lambda e: refresh_table())

    # 配置样式
    tree.tag_configure("highlight", background="#CCE5FF")
    tree.tag_configure("matched", background="#E8F5E8")
    tree.tag_configure("unmatched", background="#FFF2E8")

    def save_and_highlight(row_id, new_value):
        """保存修改并高亮显示"""
        original_idx = int(row_id)
        df.loc[original_idx, "实物ID"] = new_value
        df.loc[original_idx, "匹配分类"] = '✅ 已匹配' if new_value != '需手动输入' else '⚠️ 需手动匹配'

        tree.set(row_id, "实物ID", new_value)
        tree.set(row_id, "匹配分类", df.loc[original_idx, "匹配分类"])
        tree.item(row_id, tags=("highlight",))

        # 更新统计
        matched_count = len(df[df['实物ID'] != '需手动输入'])
        unmatched_count = len(df) - matched_count
        stats_label.config(text=f"总计: {len(df)} | ✅ 已匹配: {matched_count} | ⚠️ 需手动匹配: {unmatched_count}")

    # 用于跟踪当前编辑状态
    current_edit_frame = None
    current_edit_row = None
    current_edit_col = None

    def cleanup_edit():
        """清理编辑状态"""
        nonlocal current_edit_frame, current_edit_row, current_edit_col
        if current_edit_frame and current_edit_frame.winfo_exists():
            try:
                current_edit_frame.destroy()
            except:
                pass
        current_edit_frame = None
        current_edit_row = None
        current_edit_col = None

    def update_edit_position():
        """更新编辑框位置"""
        if not current_edit_frame or not current_edit_frame.winfo_exists():
            return
        if not current_edit_row or not current_edit_col:
            return

        try:
            # 检查行是否仍然可见
            if current_edit_row not in tree.get_children():
                cleanup_edit()
                return

            # 获取新的位置
            x, y, width, height = tree.bbox(current_edit_row, current_edit_col)
            current_edit_frame.place(x=x, y=y, width=max(width, 200), height=height + 5)
        except tk.TclError:
            # 如果单元格不可见，关闭编辑框
            cleanup_edit()
        except Exception:
            cleanup_edit()

    def on_tree_scroll(*args):
        """处理表格滚动事件"""
        if current_edit_frame:
            # 延迟更新位置，避免滚动时频繁调用
            tree.after_idle(update_edit_position)

    # 绑定滚动事件
    def bind_scroll_events():
        tree.bind('<MouseWheel>', lambda e: tree.after_idle(on_tree_scroll))
        tree.bind('<Button-4>', lambda e: tree.after_idle(on_tree_scroll))
        tree.bind('<Button-5>', lambda e: tree.after_idle(on_tree_scroll))
        v_scrollbar.config(command=lambda *args: (tree.yview(*args), on_tree_scroll()))
        h_scrollbar.config(command=lambda *args: (tree.xview(*args), on_tree_scroll()))

    def on_double_click(event):
        """双击编辑事件处理"""
        nonlocal current_edit_frame, current_edit_row, current_edit_col

        # 先清理之前的编辑框
        cleanup_edit()

        region = tree.identify("region", event.x, event.y)
        if region != "cell":
            return

        row_id = tree.identify_row(event.y)
        col_id = tree.identify_column(event.x)
        if not row_id or not col_id:
            return

        col_index = int(col_id.replace("#", "")) - 1
        if col_index >= len(tree["columns"]):
            return

        col_name = tree["columns"][col_index]
        if "实物ID" not in col_name:
            return

        try:
            x, y, width, height = tree.bbox(row_id, col_id)
        except:
            return

        current_value = tree.set(row_id, col_name)

        # 记录当前编辑的行和列
        current_edit_row = row_id
        current_edit_col = col_id

        # 创建编辑框架
        current_edit_frame = tk.Frame(tree, relief="solid", bd=1, bg="white")
        current_edit_frame.place(x=x, y=y, width=max(width, 200), height=height + 5)

        # 创建可搜索的下拉框
        search_var = tk.StringVar(value=current_value)
        combo = ttk.Combobox(current_edit_frame, textvariable=search_var,
                             font=("微软雅黑", 9), height=8)
        combo.pack(fill="both", expand=True, padx=1, pady=1)

        # 设置初始值
        initial_values = available_ids[:50] if available_ids else ["需手动输入"]
        combo['values'] = initial_values
        combo.set(current_value)

        # 设置焦点和选择文本
        combo.focus_set()
        combo.selection_range(0, tk.END)

        # 搜索过滤功能
        def filter_options(*args):
            if not current_edit_frame or not current_edit_frame.winfo_exists():
                return

            try:
                search_text = search_var.get().lower().strip()
                if len(search_text) >= 2:
                    filtered_ids = [id_val for id_val in available_ids
                                    if search_text in id_val.lower()][:30]
                    if filtered_ids:
                        combo['values'] = filtered_ids
                    else:
                        combo['values'] = ["无匹配结果"]
                elif search_text == "":
                    combo['values'] = initial_values
            except:
                pass

        # 延迟绑定搜索
        def delayed_search():
            if current_edit_frame and current_edit_frame.winfo_exists():
                search_var.trace('w', filter_options)

        current_edit_frame.after(100, delayed_search)

        def save():
            if not current_edit_frame or not current_edit_frame.winfo_exists():
                return
            try:
                val = combo.get().strip()
                if val and val != "无匹配结果":
                    save_and_highlight(row_id, val)
            except:
                pass
            finally:
                cleanup_edit()

        def cancel():
            cleanup_edit()

        # 简化的事件绑定 - 修复下拉框展开问题
        def safe_bind():
            if current_edit_frame and current_edit_frame.winfo_exists():
                try:
                    combo.bind("<<ComboboxSelected>>", lambda e: save())
                    combo.bind("<Return>", lambda e: save())
                    combo.bind("<Escape>", lambda e: cancel())

                    # 使用更简单的焦点处理，避免阻止下拉框展开
                    def on_focus_out(event):
                        # 只在真正失去焦点时关闭（不是点击下拉箭头）
                        def delayed_cancel():
                            try:
                                # 检查当前焦点
                                current_focus = combo.focus_get()
                                # 如果焦点完全离开了编辑区域，才关闭
                                if (not current_focus or
                                        (current_focus != combo and
                                         not str(current_focus).startswith(str(combo)))):
                                    cancel()
                            except:
                                cancel()

                        # 给下拉框足够时间展开
                        current_edit_frame.after(300, delayed_cancel)

                    combo.bind("<FocusOut>", on_focus_out)

                except Exception as e:
                    pass

        current_edit_frame.after(50, safe_bind)

    # 绑定滚动事件（在tree创建后调用）
    bind_scroll_events()

    tree.bind("<Double-1>", on_double_click)

    # 导出功能
    def export_file():
        try:
            export_df = df.drop(columns=['匹配分类'])
            export_df.to_excel("最终修正结果.xlsx", index=False)

            total_exported = len(export_df)
            matched_exported = len(export_df[export_df['实物ID'] != '需手动输入'])

            messagebox.showinfo("导出成功",
                                f"文件已保存为：最终修正结果.xlsx\n"
                                f"共导出 {total_exported} 条记录\n"
                                f"其中已匹配 {matched_exported} 条，待手动匹配 {total_exported - matched_exported} 条")
        except Exception as e:
            messagebox.showerror("保存失败", str(e))

    def preview_current():
        try:
            preview_df = current_df.drop(columns=['匹配分类'])
            preview_df.to_excel("当前筛选结果.xlsx", index=False)
            messagebox.showinfo("预览导出成功",
                                f"当前筛选的 {len(preview_df)} 条记录已保存为：当前筛选结果.xlsx")
        except Exception as e:
            messagebox.showerror("预览导出失败", str(e))

    def show_help():
        help_text = """🔧 实物ID编辑帮助：

1. 双击"实物ID"列的单元格开始编辑
2. 在下拉框中输入2个以上字符可自动过滤选项
3. 使用上下箭头键选择，回车确认
4. 右键点击下拉框可查看更多选项
5. ESC键或点击其他区域取消编辑

💡 小贴士：
• 绿色行表示已成功匹配
• 橙色行表示需要手动匹配
• 可以通过顶部筛选器查看不同状态的记录"""

        messagebox.showinfo("操作帮助", help_text)

    # 按钮框架
    export_frame = ttk.Frame(parent_frame)
    export_frame.pack(pady=10)

    ttk.Button(export_frame, text="保存修改结果 (完整数据)",
               command=export_file).pack(side="left", padx=5)
    ttk.Button(export_frame, text="导出当前筛选结果",
               command=preview_current).pack(side="left", padx=5)
    ttk.Button(export_frame, text="❓ 操作帮助",
               command=show_help).pack(side="right", padx=5)
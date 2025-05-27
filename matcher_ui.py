import pandas as pd
from tkinter import ttk, messagebox
import tkinter as tk
from matching01 import DataProcessor, generate_initial_report


def run_and_display_matching(parent_frame: ttk.Frame, filter_nan=True):
    processor = DataProcessor("device_data.xlsx", "test_work.xlsx")
    results = processor.match_devices()
    report_path = "智能设备匹配报告-专业版.xlsx"
    generate_initial_report(results, processor.model_df, report_path)
    return load_mount_table(parent_frame, report_path, filter_nan=filter_nan)
    return df



def load_mount_table(parent_frame: ttk.Frame, excel_path="智能设备匹配报告-专业版.xlsx", filter_nan=True):
    df = pd.read_excel(excel_path).fillna("")

    try:
        ref_df = pd.read_excel("test_work.xlsx").fillna("")
        candidate_aliases = ["实物ID", "ID", "PhysicalID"]
        actual_col = next((col for col in ref_df.columns if any(alias in str(col) for alias in candidate_aliases)), None)
        if actual_col is None:
            raise Exception(f"未找到“实物ID”相关列，列名包括：{ref_df.columns.tolist()}")
        raw_ids = ref_df[actual_col].dropna().astype(str)
        clean_ids = [i.strip() for i in raw_ids if i.strip()]
        available_ids = sorted(set(clean_ids))[:300]
    except Exception as e:
        messagebox.showerror("读取失败", f"无法读取 test_work.xlsx 中的实物ID列：\n{e}")
        available_ids = []

    for widget in parent_frame.winfo_children():
        widget.destroy()

    tree_frame = ttk.Frame(parent_frame)
    tree_frame.pack(fill="both", expand=True)

    v_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical")
    v_scrollbar.pack(side="right", fill="y")

    h_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal")
    h_scrollbar.pack(side="bottom", fill="x")

    tree = ttk.Treeview(
        tree_frame,
        columns=list(df.columns),
        show="headings",
        height=20,
        yscrollcommand=v_scrollbar.set,
        xscrollcommand=h_scrollbar.set
    )
    tree.pack(side="left", fill="both", expand=True)
    v_scrollbar.config(command=tree.yview)
    h_scrollbar.config(command=tree.xview)

    for col in df.columns:
        max_len = max([len(str(val)) for val in df[col]] + [len(col)])
        col_width = min(max_len * 12, 300)
        tree.heading(col, text=col, anchor="center")
        tree.column(col, width=col_width, anchor="center")

    for idx, row in df.iterrows():
        device_id = row.get("Device_ID", "")
        if filter_nan and (pd.isna(device_id) or str(device_id).strip().lower() in ["", "nan"]):
            continue
        tree.insert("", "end", iid=str(idx), values=list(row))

    tree.tag_configure("highlight", background="#CCE5FF")

    def save_and_highlight(row_id, new_value):
        df.at[int(row_id), "实物ID"] = new_value
        tree.set(row_id, "实物ID", new_value)
        tree.item(row_id, tags=("highlight",))  # ✅ 修复了多余的括号

    def on_double_click(event):
        region = tree.identify("region", event.x, event.y)
        if region != "cell":
            return

        row_id = tree.identify_row(event.y)
        col_id = tree.identify_column(event.x)
        col_index = int(col_id.replace("#", "")) - 1
        col_name = tree["columns"][col_index]

        if "实物ID" not in col_name:
            return

        x, y, width, height = tree.bbox(row_id, col_id)
        abs_x = tree.winfo_rootx() + x
        abs_y = tree.winfo_rooty() + y

        current_value = tree.set(row_id, col_name)

        combo = ttk.Combobox(tree, values=available_ids, font=("微软雅黑", 10), height=10)
        combo.place(x=x, y=y, width=width, height=height)
        combo.set(current_value)
        combo.focus()

        def filter_list(event=None):
            val = combo.get().strip().lower()
            filtered = [item for item in available_ids if val in item.lower()]
            combo["values"] = filtered if filtered else available_ids

        def on_typing(event):
            combo.delete(0, tk.END)

        def save():
            val = combo.get().strip()
            if val:
                save_and_highlight(row_id, val)
            combo.destroy()

        combo.bind("<KeyRelease>", filter_list)
        combo.bind("<FocusIn>", on_typing)
        combo.bind("<<ComboboxSelected>>", lambda e: save())
        combo.bind("<Return>", lambda e: save())
        combo.bind("<FocusOut>", lambda e: combo.destroy())
        combo.after_idle(lambda: combo.event_generate("<Button-1>"))

    tree.bind("<Double-1>", on_double_click)

    id_count_text = f"共识别出 {len(available_ids)} 个可选实物ID" if available_ids else "未识别到任何可用实物ID"
    if hasattr(parent_frame, 'log_text'):
        parent_frame.log_text.insert(tk.END, id_count_text + "\\n")
        parent_frame.log_text.see(tk.END)

    def export_file():
        try:
            df.to_excel("最终修正结果.xlsx", index=False)
            messagebox.showinfo("导出成功", "文件已保存为：最终修正结果.xlsx")
        except Exception as e:
            messagebox.showerror("保存失败", str(e))

    export_btn = ttk.Button(parent_frame, text="保存修改结果", command=export_file)
    export_btn.pack(pady=10)

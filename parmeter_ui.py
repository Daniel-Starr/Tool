import pandas as pd
from pathlib import Path
import os


def handle_param_file(file_path: str, show_preview: bool = True):
    """
    参数文件功能：根据指定的路径提取四列并导出新Excel。
    此函数现在接收一个文件路径作为参数，并可选择是否显示数据预览。

    参数:
        file_path (str): 要处理的Excel文件的完整路径。
        show_preview (bool): 是否显示数据预览窗口，默认为True。

    返回:
        str: 成功生成的输出文件的路径。

    异常:
        ValueError: 如果文件路径无效或文件中缺少必要的列。
        FileNotFoundError: 如果提供的文件路径不存在。
    """
    if not file_path or not os.path.exists(file_path):
        raise FileNotFoundError(f"错误：文件未找到或路径无效: {file_path}")

    try:
        df = pd.read_excel(file_path)
    except Exception as e:
        raise Exception(f"读取Excel文件 '{os.path.basename(file_path)}' 时出错: {e}")

    # 定义必要列
    required_columns = ['设备名称', '设备类型', '电压等级', '实物ID']

    # 检查是否有缺失的列
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise ValueError(f"错误：文件缺失以下必要列：{', '.join(missing)}")

    # 提取数据并保存
    df_selected = df[required_columns]

    # 将结果保存到固定的输出文件 test_work.xlsx
    output_path = Path("test_work.xlsx")
    df_selected.to_excel(output_path, index=False)

    # 显示数据预览（如果需要）
    if show_preview:
        show_param_data_preview(df_selected, file_path)

    return str(output_path)


def show_param_data_preview(df: pd.DataFrame, original_file_path: str):
    """
    显示参数数据预览窗口
    
    参数:
        df: 处理后的DataFrame
        original_file_path: 原始文件路径
    """
    import tkinter as tk
    from tkinter import ttk, messagebox
    
    # 创建预览窗口
    preview_window = tk.Toplevel()
    preview_window.title(f"参数数据预览 - {os.path.basename(original_file_path)}")
    preview_window.geometry("800x600")
    preview_window.grab_set()  # 设置为模态窗口
    
    # 信息框架
    info_frame = ttk.Frame(preview_window)
    info_frame.pack(fill="x", padx=10, pady=5)
    
    # 显示统计信息
    stats_text = f"原文件: {os.path.basename(original_file_path)} | 提取记录数: {len(df)} | 输出文件: test_work.xlsx"
    stats_label = ttk.Label(info_frame, text=stats_text, font=("微软雅黑", 10))
    stats_label.pack(anchor="w")
    
    # 数据类型统计
    if '设备类型' in df.columns:
        device_types = df['设备类型'].value_counts()
        type_info = " | ".join([f"{t}: {c}个" for t, c in device_types.head(5).items()])
        type_label = ttk.Label(info_frame, text=f"主要设备类型: {type_info}", 
                              font=("微软雅黑", 9), foreground="gray")
        type_label.pack(anchor="w")
    
    # 创建表格框架
    table_frame = ttk.Frame(preview_window)
    table_frame.pack(fill="both", expand=True, padx=10, pady=5)
    
    # 滚动条
    v_scrollbar = ttk.Scrollbar(table_frame, orient="vertical")
    v_scrollbar.pack(side="right", fill="y")
    
    h_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal")
    h_scrollbar.pack(side="bottom", fill="x")
    
    # 创建表格
    tree = ttk.Treeview(
        table_frame,
        columns=list(df.columns),
        show="headings",
        yscrollcommand=v_scrollbar.set,
        xscrollcommand=h_scrollbar.set
    )
    tree.pack(side="left", fill="both", expand=True)
    
    v_scrollbar.config(command=tree.yview)
    h_scrollbar.config(command=tree.xview)
    
    # 设置列标题和宽度
    for col in df.columns:
        tree.heading(col, text=col, anchor="center")
        # 根据列内容计算合适的宽度
        max_len = max(
            df[col].astype(str).apply(len).max() if len(df) > 0 else 0,
            len(col)
        )
        col_width = min(max(max_len * 8 + 20, 100), 200)
        tree.column(col, width=col_width, anchor="w")
    
    # 填充数据（只显示前500行避免性能问题）
    display_rows = min(len(df), 500)
    for idx, row in df.head(display_rows).iterrows():
        tree.insert("", "end", values=list(row))
    
    # 如果数据行数超过显示限制，显示提示
    if len(df) > display_rows:
        warning_label = ttk.Label(info_frame, 
                                text=f"注意: 仅显示前 {display_rows} 行数据，完整数据已保存到 test_work.xlsx",
                                font=("微软雅黑", 9), foreground="orange")
        warning_label.pack(anchor="w")
    
    # 按钮框架
    button_frame = ttk.Frame(preview_window)
    button_frame.pack(fill="x", padx=10, pady=10)
    
    def open_excel_file():
        """打开生成的Excel文件"""
        try:
            import subprocess
            import sys
            
            if sys.platform.startswith('win'):
                os.startfile("test_work.xlsx")
            elif sys.platform.startswith('darwin'):  # macOS
                subprocess.run(['open', "test_work.xlsx"])
            else:  # Linux
                subprocess.run(['xdg-open', "test_work.xlsx"])
        except Exception as e:
            messagebox.showerror("打开失败", f"无法打开Excel文件：{e}")
    
    # 按钮
    ttk.Button(button_frame, text="打开Excel文件", command=open_excel_file).pack(side="left", padx=5)
    ttk.Button(button_frame, text="关闭预览", command=preview_window.destroy).pack(side="right", padx=5)
    
    # 居中显示窗口
    preview_window.update_idletasks()
    x = (preview_window.winfo_screenwidth() // 2) - (preview_window.winfo_width() // 2)
    y = (preview_window.winfo_screenheight() // 2) - (preview_window.winfo_height() // 2)
    preview_window.geometry(f"+{x}+{y}")

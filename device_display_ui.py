import pandas as pd
from tkinter import ttk, messagebox
import tkinter as tk
import os


def display_device_data(parent_frame: ttk.Frame, excel_path: str = "device_data.xlsx"):
    """
    在可视化数据框中显示设备清单数据

    参数:
        parent_frame: 父容器框架
        excel_path: Excel文件路径
    """
    try:
        # 读取设备数据
        if not os.path.exists(excel_path):
            show_message(parent_frame, "文件不存在", f"未找到文件: {excel_path}")
            return

        df = pd.read_excel(excel_path).fillna("")

        if df.empty:
            show_message(parent_frame, "数据为空", "设备清单文件中没有数据")
            return

        # 清空旧的UI组件
        for widget in parent_frame.winfo_children():
            widget.destroy()

        # 创建标题框架
        title_frame = ttk.Frame(parent_frame)
        title_frame.pack(fill="x", padx=5, pady=5)

        title_label = ttk.Label(title_frame, text="📋 设备清单数据",
                                font=("微软雅黑", 12, "bold"))
        title_label.pack(side="left")

        # 统计信息
        stats_text = f"总计: {len(df)} 条设备记录"
        if '电压等级' in df.columns:
            try:
                voltage_counts = df['电压等级'].value_counts()
                voltage_info = " | ".join([f"{v}: {c}个" for v, c in voltage_counts.head(3).items()])
                stats_text += f" | 主要电压等级: {voltage_info}"
            except:
                pass

        stats_label = ttk.Label(title_frame, text=stats_text,
                                font=("微软雅黑", 9), foreground="gray")
        stats_label.pack(side="left", padx=(20, 0))

        # 创建表格框架
        table_frame = ttk.Frame(parent_frame)
        table_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # 滚动条
        v_scrollbar = ttk.Scrollbar(table_frame, orient="vertical")
        v_scrollbar.pack(side="right", fill="y")

        h_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal")
        h_scrollbar.pack(side="bottom", fill="x")

        # 创建表格
        columns = [str(col) for col in df.columns]  # 确保列名是字符串
        tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            yscrollcommand=v_scrollbar.set,
            xscrollcommand=h_scrollbar.set
        )
        tree.pack(side="left", fill="both", expand=True)

        v_scrollbar.config(command=tree.yview)
        h_scrollbar.config(command=tree.xview)

        # 设置列标题和宽度 - 与参数数据样式完全一致：居中+自适应
        for col in columns:
            tree.heading(col, text=col, anchor="center")
            # 根据列内容计算合适的宽度（与参数数据计算方式一致）
            try:
                content_len = df[col].astype(str).apply(len).max() if len(df) > 0 else 0
                header_len = len(str(col))
                max_len = max(content_len, header_len)
                # 使用与参数数据相同的计算方式，支持自适应宽度
                col_width = min(max(max_len * 8 + 20, 100), 300)
            except:
                col_width = 150  # 默认宽度
            # 设置列为居中显示，并允许拉伸以支持自适应宽度
            tree.column(col, width=col_width, anchor="center", stretch=True)

        # 填充数据（限制显示行数以避免性能问题）
        display_rows = min(len(df), 1000)
        for idx, row in df.head(display_rows).iterrows():
            try:
                values = [str(val) for val in row.values]  # 确保所有值都是字符串
                tree.insert("", "end", values=values)
            except Exception as e:
                print(f"插入行 {idx} 时出错: {e}")
                continue

        # 设置交替行背景色（与参数数据保持一致）
        tree.tag_configure("evenrow", background="#f0f0f0")
        for i, child in enumerate(tree.get_children()):
            if i % 2 == 0:
                tree.item(child, tags=("evenrow",))

        # 如果数据被截断，显示提示（与参数数据保持一致）
        if len(df) > display_rows:
            warning_frame = ttk.Frame(parent_frame)
            warning_frame.pack(fill="x", padx=5)
            warning_label = ttk.Label(warning_frame,
                                      text=f"⚠️ 仅显示前 {display_rows} 行数据，完整数据请查看Excel文件",
                                      font=("微软雅黑", 9), foreground="orange")
            warning_label.pack(anchor="w")

        # 按钮框架
        button_frame = ttk.Frame(parent_frame)
        button_frame.pack(fill="x", padx=5, pady=10)

        def open_excel():
            """打开Excel文件"""
            try:
                import subprocess
                if os.name == 'nt':
                    os.startfile(excel_path)
                else:
                    subprocess.run(['open' if os.name == 'posix' else 'xdg-open', excel_path])
            except Exception as e:
                messagebox.showerror("打开失败", f"无法打开Excel文件：{e}")

        def refresh_data():
            """刷新数据"""
            display_device_data(parent_frame, excel_path)

        # 按钮
        ttk.Button(button_frame, text="打开Excel文件", command=open_excel).pack(side="left", padx=5)
        ttk.Button(button_frame, text="刷新数据", command=refresh_data).pack(side="left", padx=5)

        # 显示成功消息
        success_label = ttk.Label(button_frame, text="✅ 设备清单加载成功",
                                  foreground="green", font=("微软雅黑", 9))
        success_label.pack(side="right", padx=5)

    except Exception as e:
        show_error(parent_frame, "显示设备数据失败", str(e))


def display_param_data(parent_frame: ttk.Frame, excel_path: str = "test_work.xlsx"):
    """
    在可视化数据框中显示参数文件数据

    参数:
        parent_frame: 父容器框架
        excel_path: Excel文件路径
    """
    try:
        # 读取参数数据
        if not os.path.exists(excel_path):
            show_message(parent_frame, "文件不存在", f"未找到文件: {excel_path}")
            return

        df = pd.read_excel(excel_path).fillna("")

        if df.empty:
            show_message(parent_frame, "数据为空", "参数文件中没有数据")
            return

        # 清空旧的UI组件
        for widget in parent_frame.winfo_children():
            widget.destroy()

        # 创建标题框架
        title_frame = ttk.Frame(parent_frame)
        title_frame.pack(fill="x", padx=5, pady=5)

        title_label = ttk.Label(title_frame, text="🔧 参数文件数据",
                                font=("微软雅黑", 12, "bold"))
        title_label.pack(side="left")

        # 统计信息
        stats_text = f"总计: {len(df)} 条参数记录"
        if '设备类型' in df.columns:
            device_types = df['设备类型'].value_counts()
            type_info = " | ".join([f"{t}: {c}个" for t, c in device_types.head(3).items()])
            stats_text += f" | 主要设备类型: {type_info}"

        stats_label = ttk.Label(title_frame, text=stats_text,
                                font=("微软雅黑", 9), foreground="gray")
        stats_label.pack(side="left", padx=(20, 0))

        # 创建表格框架
        table_frame = ttk.Frame(parent_frame)
        table_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # 滚动条
        v_scrollbar = ttk.Scrollbar(table_frame, orient="vertical")
        v_scrollbar.pack(side="right", fill="y")

        h_scrollbar = ttk.Scrollbar(table_frame, orient="horizontal")
        h_scrollbar.pack(side="bottom", fill="x")

        # 创建表格
        columns = [str(col) for col in df.columns]  # 确保列名是字符串
        tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            yscrollcommand=v_scrollbar.set,
            xscrollcommand=h_scrollbar.set
        )
        tree.pack(side="left", fill="both", expand=True)

        v_scrollbar.config(command=tree.yview)
        h_scrollbar.config(command=tree.xview)

        # 设置列标题和宽度 - 居中对齐+自适应宽度
        for col in columns:
            tree.heading(col, text=col, anchor="center")  # 标题居中
            # 根据列内容计算合适的宽度
            try:
                content_len = df[col].astype(str).apply(len).max() if len(df) > 0 else 0
                header_len = len(str(col))
                max_len = max(content_len, header_len)
                # 计算自适应宽度
                col_width = min(max(max_len * 8 + 20, 100), 300)
            except:
                col_width = 150  # 默认宽度
            # 设置列为居中显示，并允许拉伸以支持自适应宽度
            tree.column(col, width=col_width, anchor="center", stretch=True)

        # 填充数据（限制显示行数以避免性能问题）
        display_rows = min(len(df), 1000)
        for idx, row in df.head(display_rows).iterrows():
            try:
                values = [str(val) for val in row.values]  # 确保所有值都是字符串
                tree.insert("", "end", values=values)
            except Exception as e:
                print(f"插入行 {idx} 时出错: {e}")
                continue

        # 设置交替行背景色
        tree.tag_configure("evenrow", background="#f0f0f0")
        for i, child in enumerate(tree.get_children()):
            if i % 2 == 0:
                tree.item(child, tags=("evenrow",))

        # 如果数据被截断，显示提示
        if len(df) > display_rows:
            warning_frame = ttk.Frame(parent_frame)
            warning_frame.pack(fill="x", padx=5)
            warning_label = ttk.Label(warning_frame,
                                      text=f"⚠️ 仅显示前 {display_rows} 行数据，完整数据请查看Excel文件",
                                      font=("微软雅黑", 9), foreground="orange")
            warning_label.pack(anchor="w")

        # 按钮框架
        button_frame = ttk.Frame(parent_frame)
        button_frame.pack(fill="x", padx=5, pady=10)

        def open_excel():
            """打开Excel文件"""
            try:
                import subprocess
                if os.name == 'nt':
                    os.startfile(excel_path)
                else:
                    subprocess.run(['open' if os.name == 'posix' else 'xdg-open', excel_path])
            except Exception as e:
                messagebox.showerror("打开失败", f"无法打开Excel文件：{e}")

        def refresh_data():
            """刷新数据"""
            display_param_data(parent_frame, excel_path)

        # 按钮
        ttk.Button(button_frame, text="打开Excel文件", command=open_excel).pack(side="left", padx=5)
        ttk.Button(button_frame, text="刷新数据", command=refresh_data).pack(side="left", padx=5)

        # 显示成功消息
        success_label = ttk.Label(button_frame, text="✅ 参数数据加载成功",
                                  foreground="green", font=("微软雅黑", 9))
        success_label.pack(side="right", padx=5)

    except Exception as e:
        show_error(parent_frame, "显示参数数据失败", str(e))


def show_message(parent_frame: ttk.Frame, title: str, message: str):
    """显示信息消息"""
    # 清空旧的UI组件
    for widget in parent_frame.winfo_children():
        widget.destroy()
        
    # 创建消息显示框架
    message_frame = ttk.Frame(parent_frame)
    message_frame.pack(expand=True, fill="both")
    
    # 居中显示消息
    center_frame = ttk.Frame(message_frame)
    center_frame.pack(expand=True)
    
    title_label = ttk.Label(center_frame, text=title, 
                           font=("微软雅黑", 14, "bold"))
    title_label.pack(pady=(50, 10))
    
    message_label = ttk.Label(center_frame, text=message, 
                             font=("微软雅黑", 11), foreground="gray")
    message_label.pack(pady=10)


def show_error(parent_frame: ttk.Frame, title: str, error_msg: str):
    """显示错误消息"""
    # 清空旧的UI组件
    for widget in parent_frame.winfo_children():
        widget.destroy()
        
    # 创建错误显示框架
    error_frame = ttk.Frame(parent_frame)
    error_frame.pack(expand=True, fill="both")
    
    # 居中显示错误
    center_frame = ttk.Frame(error_frame)
    center_frame.pack(expand=True)
    
    title_label = ttk.Label(center_frame, text=f"❌ {title}", 
                           font=("微软雅黑", 14, "bold"), foreground="red")
    title_label.pack(pady=(50, 10))
    
    error_label = ttk.Label(center_frame, text=error_msg, 
                           font=("微软雅黑", 10), foreground="darkred", 
                           wraplength=400, justify="center")
    error_label.pack(pady=10)
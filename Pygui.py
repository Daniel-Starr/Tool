import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from extract_ui import extract_system_tree
from transition_ui import preprocess_to_excel
from parmeter_ui import handle_param_file
from matcher_ui import run_and_display_matching
from load_ui import apply_real_id_to_fam

from save_excel_ui import generate_json_and_excel  # 新增导入模块
import os
import threading

from compress_ui import GIMExtractor

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("工程建设数据与三维模型自动挂接工具")
        self.root.geometry("1200x700")
        self.gim_extract_dir = None
        self.gim_path = None

        try:
            self.root.state('zoomed')
        except:
            screen_width = self.root.winfo_screenwidth()
            screen_height = self.root.winfo_screenheight()
            self.root.geometry(f"{screen_width}x{screen_height}")

        button_frame = tk.Frame(self.root)
        button_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        btn_names = ["导入", "导出设备清单" , "参数文件", "挂接", "载入", "保存"]
        for name in btn_names:
            btn = tk.Button(button_frame, text=name, width=12, command=lambda n=name: self.button_action(n))
            btn.pack(side=tk.LEFT, padx=5)


        main_pane = tk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_pane.pack(fill="both", expand=True)

        self.file_tree_frame = ttk.LabelFrame(main_pane, text="项目文件")
        self.file_tree = ttk.Treeview(self.file_tree_frame)
        self.file_tree.pack(fill="both", expand=True)
        main_pane.add(self.file_tree_frame, stretch="never")


        right_pane = tk.PanedWindow(main_pane, orient=tk.VERTICAL)
        main_pane.add(right_pane, stretch="always")

        mount_frame_wrapper = ttk.LabelFrame(right_pane, text="可视化数据")
        self.mount_frame = ttk.Frame(mount_frame_wrapper)
        self.mount_frame.pack(fill="both", expand=True, padx=5, pady=5)
        right_pane.add(mount_frame_wrapper, stretch="always")

        log_frame = ttk.LabelFrame(self.root, text="运行日志")
        log_frame.pack(side="bottom", fill="x", padx=10, pady=(0, 5))

        self.log_text = tk.Text(log_frame, height=6, bg="#f8f8f8", font=("Consolas", 9))
        self.log_text.pack(fill="both", expand=True, padx=5, pady=5)

        self.progress = ttk.Progressbar(self.root, orient="horizontal", mode="determinate")
        self.progress.pack(side="bottom", fill="x", padx=10, pady=(0, 10))

    def log(self, msg):
        self.log_text.insert(tk.END, msg + "\n")
        self.log_text.see(tk.END)

    def set_progress(self, val):
        self.progress['value'] = val
        self.root.update_idletasks()

    def populate_file_tree(self, root_path):
        self.file_tree.delete(*self.file_tree.get_children())
        def insert_items(parent, path):
            try:
                for name in os.listdir(path):
                    full_path = os.path.join(path, name)
                    is_dir = os.path.isdir(full_path)
                    node = self.file_tree.insert(parent, 'end', text=name, open=False)
                    if is_dir:
                        insert_items(node, full_path)
            except Exception as e:
                self.log(f"❌ 目录加载失败: {e}")
        insert_items('', root_path)
        self.log(f"📂 工程结构已加载：{root_path}")

    def button_action(self, name):
        if name == "导入":
            file_path = filedialog.askopenfilename(title="选择 GIM 文件", filetypes=[("GIM 文件", "*.gim")])
            if file_path:
                def task():
                    try:
                        self.set_progress(10)
                        extractor = GIMExtractor(file_path)
                        out_dir = extractor.extract_embedded_7z()
                        self.gim_extract_dir = out_dir
                        self.gim_path = file_path
                        self.set_progress(70)
                        self.populate_file_tree(out_dir)
                        self.set_progress(100)
                        self.log(f"✅ 解压完成: {out_dir}")
                        messagebox.showinfo("导入成功", f"GIM 解压至: {out_dir}")
                    except Exception as e:
                        self.log(f"❌ 解压失败: {str(e)}")
                        messagebox.showerror("导入失败", str(e))
                    finally:
                        self.set_progress(0)
                threading.Thread(target=task).start()

        elif name == "提取":
            if not self.gim_extract_dir:
                messagebox.showwarning("未导入", "请先通过“导入”按钮解压 .gim 文件")
                return
            def task():
                try:
                    self.set_progress(20)
                    output_file = extract_system_tree(base_path=self.gim_extract_dir)
                    self.set_progress(100)
                    self.log(f"✅ 提取完成: {output_file}")
                    messagebox.showinfo("提取成功", f"系统树保存为：{output_file}")
                except Exception as e:
                    self.log(f"❌ 提取失败: {str(e)}")
                    messagebox.showerror("提取失败", str(e))
                finally:
                    self.set_progress(0)
            threading.Thread(target=task).start()

        elif name == "预处理":
            def task():
                try:
                    self.set_progress(30)
                    excel_file = preprocess_to_excel()
                    self.set_progress(100)
                    self.log(f"✅ 预处理输出: {excel_file}")
                    messagebox.showinfo("预处理完成", f"数据已输出为：{excel_file}")
                except Exception as e:
                    self.log(f"❌ 预处理失败: {str(e)}")
                    messagebox.showerror("预处理失败", str(e))
                finally:
                    self.set_progress(0)
            threading.Thread(target=task).start()

        elif name == "参数文件":
            def task():
                try:
                    self.set_progress(40)
                    output_file = handle_param_file()
                    self.set_progress(100)
                    self.log(f"✅ 生成参数文件: {output_file}")
                    messagebox.showinfo("成功", f"生成文件：{output_file}")
                except Exception as e:
                    self.log(f"❌ 参数处理失败: {str(e)}")
                    messagebox.showerror("参数文件处理失败", str(e))
                finally:
                    self.set_progress(0)
            threading.Thread(target=task).start()

        elif name == "挂接":
            def task():
                try:
                    self.set_progress(30)
                    self.df = run_and_display_matching(self.mount_frame)
                    self.set_progress(100)
                    self.log("✅ 挂接展示完成")
                except Exception as e:
                    self.log(f"❌ 挂接失败: {str(e)}")
                    messagebox.showerror("挂接失败", str(e))
                finally:
                    self.set_progress(0)
            threading.Thread(target=task).start()

        elif name == "载入":
            def task():
                try:
                    if not self.gim_extract_dir:
                        messagebox.showwarning("未导入", "请先通过“导入”按钮解压 .gim 文件")
                        return
                    self.set_progress(20)
                    result = apply_real_id_to_fam(base_path=self.gim_extract_dir, strict=True)
                    self.set_progress(100)
                    self.log(f"✅ 载入完成\n{result}")
                    messagebox.showinfo("载入完成", result)
                except Exception as e:
                    self.log(f"❌ 载入失败: {str(e)}")
                    messagebox.showerror("载入失败", str(e))
                finally:
                    self.set_progress(0)
            threading.Thread(target=task).start()

        elif name == "导出设备清单":
            def task():
                try:
                    if not self.gim_extract_dir:
                        messagebox.showwarning("未导入", "请先通过“导入”按钮解压 .gim 文件")
                        return
                    self.set_progress(30)
                    excel_path = generate_json_and_excel(self.gim_extract_dir)  # ✅ 输入输出同路径
                    self.set_progress(100)
                    self.log(f"✅ 导出完成: {excel_path}")
                    messagebox.showinfo("导出完成", f"Excel 文件已生成：{excel_path}")
                except Exception as e:
                    self.log(f"❌ 导出失败: {str(e)}")
                    messagebox.showerror("导出失败", str(e))
                finally:
                    self.set_progress(0)

            threading.Thread(target=task).start()




        elif name == "保存":
            def task():
                try:
                    if not self.gim_path or not self.gim_extract_dir:
                        messagebox.showwarning("未导入", "请先导入并解压 .gim 文件")
                        return
                    self.set_progress(30)
                    from compress_ui import GIMExtractor
                    output_gim_path = self.gim_path.replace(".gim", "_已封装.gim")
                    extractor = GIMExtractor(self.gim_path)
                    extractor.extract_embedded_7z()
                    extractor.build_custom_file(self.gim_extract_dir, output_gim_path)
                    self.set_progress(100)
                    self.log(f"✅ 保存成功: {output_gim_path}")
                    messagebox.showinfo("保存完成", f"GIM 文件已封装：{output_gim_path}")
                    try:
                        os.startfile(os.path.dirname(output_gim_path))  # 自动打开目录（仅限 Windows）
                    except:
                        pass
                except Exception as e:
                    self.set_progress(0)
                    self.log(f"❌ 保存失败: {str(e)}")
                    messagebox.showerror("保存失败", str(e))
                finally:
                    self.set_progress(0)
            threading.Thread(target=task).start()

        else:
            self.log(f"ℹ️ 你点击了按钮：{name}")

    def save(self):
        if hasattr(self, 'df'):
            self.df.to_excel("最终修正结果.xlsx", index=False)
            self.log("✅ 文件已保存为：最终修正结果.xlsx")
        else:
            self.log("⚠️ 当前无可保存的数据，请先执行挂接。")



if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()

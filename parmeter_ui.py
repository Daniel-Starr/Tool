import pandas as pd
from tkinter import filedialog
from pathlib import Path

def handle_param_file():
    """参数文件功能：提取四列并导出新Excel"""
    file_path = filedialog.askopenfilename(
        title="选择参数Excel文件",
        filetypes=[("Excel files", "*.xlsx *.xls")]
    )

    if not file_path:
        raise Exception("未选择文件")

    df = pd.read_excel(file_path)

    required_columns = ['设备名称', '设备类型', '电压等级', '实物ID']
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        raise Exception(f"缺失必要列：{', '.join(missing)}")

    df_selected = df[required_columns]
    output_path = Path("test_work.xlsx")
    df_selected.to_excel(output_path, index=False)

    return str(output_path)

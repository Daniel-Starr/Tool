import json
import pandas as pd
from openpyxl.utils import get_column_letter


def preprocess_to_excel(json_file_path="system_tree.json", excel_file_path="device_data.xlsx"):
    """
    从 system_tree.json 中提取以下字段并生成 Excel 文件：
    - 电网工程标识系统编码
    - 工程中名称
    - 电压等级
    - Device_ID

    参数:
        json_file_path (str): 输入 JSON 文件路径
        excel_file_path (str): 输出 Excel 文件路径

    返回:
        str: 生成的 Excel 文件路径
    """
    with open(json_file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)

    results = []

    def traverse(node):
        description = node.get('DESCRIPTION', {})
        row = {
            "电网工程标识系统编码": description.get("电网工程标识系统编码", "").split("=")[-1].strip(),
            "工程中名称": description.get("工程中名称", "").split("=")[-1].strip(),
            "电压等级": description.get("电压等级", "").split("=")[-1].strip(),
            "Device_ID": ""  # 默认空
        }

        if 'DEVICES' in node:
            devices = node['DEVICES']
            if isinstance(devices, dict):
                row["Device_ID"] = devices.get("ID", "")
                results.append(row)
            elif isinstance(devices, list):
                for device in devices:
                    new_row = row.copy()
                    new_row["Device_ID"] = device.get("ID", "")
                    results.append(new_row)

        if 'SUBSYSTEMS' in node:
            for sub in node['SUBSYSTEMS'].values():
                traverse(sub)

    for root_node in data.values():
        traverse(root_node)

    df = pd.DataFrame(results)

    with pd.ExcelWriter(excel_file_path, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
        worksheet = writer.sheets['Sheet1']
        for idx, column in enumerate(df.columns, 1):
            column_letter = get_column_letter(idx)
            max_len = df[column].fillna('').astype(str).apply(len).max()
            max_len = max(max_len, len(column))
            worksheet.column_dimensions[column_letter].width = max_len * 1.5 + 2

    print(f"✅ Excel文件已生成: {excel_file_path}")
    return excel_file_path

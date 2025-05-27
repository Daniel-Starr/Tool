from test import json
import pandas as pd

# 读取 JSON 文件（请确保 fam_and_extra_cbm_data.json 在当前目录）
with open("fam_and_extra_cbm_data.json", "r", encoding="utf-8") as f:
    all_data = json.load(f)

# 提取与清洗函数
def clean(value):
    return value.split("=", 1)[-1].strip() if isinstance(value, str) and "=" in value else value

# 提取目标字段
extracted_rows = []
for item in all_data.get("fam_files", []) + all_data.get("cbm_diff_files", []):
    file_name = item.get("file_name", "")
    sections = item.get("sections", {})
    design = sections.get("设计参数", {})

    extracted_rows.append({
        "电网工程标识系统编码": clean(design.get("电网工程标识系统编码", "")),
        "工程中名称": clean(design.get("工程中名称", "")),
        "电压等级": clean(design.get("电压等级", "")),
        "file_name": file_name
    })

# 写入 Excel
df = pd.DataFrame(extracted_rows)
df.to_excel("仅字段提取设备信息.xlsx", index=False)

print("✅ 提取完成，结果保存在：仅字段提取设备信息.xlsx")

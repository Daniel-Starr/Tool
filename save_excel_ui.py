# 封装为函数供 Pygui 调用：只处理 .fam 文件并导出设备信息 Excel
def generate_json_and_excel(cbm_dir):
    return generate_excel_from_fam(cbm_dir, ".")

import json
import pandas as pd
from collections import defaultdict
from pathlib import Path
import os

def parse_structured_file(file_path):
    result = {
        "file_name": file_path.name,
        "sections": defaultdict(dict)
    }
    current_section = "GLOBAL"
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.startswith("[") and line.endswith("]"):
                current_section = line[1:-1].strip()
                continue
            if "=" in line:
                key, value = line.split("=", 1)
                result["sections"][current_section][key.strip()] = value.strip()
    return result

def extract_key_fields(all_sections):
    result = {"电网工程标识系统编码": "", "工程中名称": "", "电压等级": ""}
    for section in all_sections.values():
        for key, value in section.items():
            if key.strip() in result:
                result[key.strip()] = value
    return result

def clean(value):
    return value.split("=", 1)[-1].strip() if isinstance(value, str) and "=" in value else value


def generate_excel_from_fam(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)

    fam_files = list(Path(input_dir).rglob("*.fam"))
    parsed_fam_data = [parse_structured_file(f) for f in fam_files]

    extracted_rows = []
    for item in parsed_fam_data:
        file_name = item.get("file_name", "")
        sections = item.get("sections", {})
        extracted = extract_key_fields(sections)

        extracted_rows.append({
            "电网工程标识系统编码": clean(extracted["电网工程标识系统编码"]),
            "工程中名称": clean(extracted["工程中名称"]),
            "电压等级": clean(extracted["电压等级"]),
            "Device_ID": file_name
        })

    df = pd.DataFrame(extracted_rows)
    df = df[(df["电网工程标识系统编码"] != "") | (df["工程中名称"] != "") | (df["电压等级"] != "")]

    excel_path = os.path.join(output_dir, "device_data.xlsx")
    df.to_excel(excel_path, index=False)
    return excel_path

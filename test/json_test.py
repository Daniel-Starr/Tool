import json
from collections import defaultdict
from pathlib import Path

# 设置扫描路径（你可以修改为你自己的 CBM 文件夹路径）
data_dir = "G:\Project\Tool\output\郴州东500KV变电站竣工图设计\CBM"

# 通用解析函数：将 .cbm 和 .fam 文件解析为节块和键值对结构
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

# 扫描所有 .fam 和 .cbm 文件
cbm_files = list(Path(data_dir).rglob("*.cbm"))
fam_files = list(Path(data_dir).rglob("*.fam"))

# 分别解析
parsed_cbm_data = [parse_structured_file(f) for f in cbm_files]
parsed_fam_data = [parse_structured_file(f) for f in fam_files]

# 合并保存为 JSON
combined_data = {
    "cbm_diff_files": parsed_cbm_data,
    "fam_files": parsed_fam_data
}

with open("fam_and_extra_cbm_data.json", "w", encoding="utf-8") as f:
    json.dump(combined_data, f, indent=2, ensure_ascii=False)

print("✅ 已生成 fam_and_extra_cbm_data.json 文件")

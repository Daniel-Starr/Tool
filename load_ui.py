import os
import pandas as pd

def apply_real_id_to_fam(base_path=None, strict=False):
    """
    将最终修正结果中的“实物ID”写入解压目录下的 .fam 文件中。

    参数:
        base_path (str): GIM 解压的主目录，代码将自动在其下查找 CBM 子目录。
        strict (bool): 若为 True，则会跳过“需手动输入”或 NaN 的实物ID值。

    返回:
        str: 包含更新成功与跳过的数量的摘要信息。
    """
    try:
        df = pd.read_excel("最终修正结果.xlsx")

        if not base_path:
            return "❌ 未指定载入路径 base_path"

        target_dir = os.path.join(base_path, "CBM")
        if not os.path.exists(target_dir):
            return f"❌ CBM 目录不存在：{target_dir}"

        updated_count = 0
        skipped = 0

        for _, row in df.iterrows():
            device_id = str(row.get("Device_ID", "")).strip()
            if device_id.endswith(".fam"):
                device_id = device_id[:-4]
            real_id = str(row.get("实物ID", "")).strip()

            if not device_id or not real_id:
                skipped += 1
                continue

            if strict and (real_id == "需手动输入" or real_id.lower() == "nan"):
                skipped += 1
                continue

            fam_path = os.path.join(target_dir, f"{device_id}.fam")
            if not os.path.exists(fam_path):
                skipped += 1
                continue

            with open(fam_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            found = False
            for i, line in enumerate(lines):
                if line.startswith("实物ID=实物ID="):
                    lines[i] = f"实物ID=实物ID={real_id}\n"
                    found = True
                    break

            if found:
                with open(fam_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
                updated_count += 1
            else:
                skipped += 1

        return f"✅ 共更新 {updated_count} 个 .fam 文件，跳过 {skipped} 个条目。"

    except Exception as e:
        return f"❌ 处理失败：{str(e)}"



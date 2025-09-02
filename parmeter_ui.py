import pandas as pd
from pathlib import Path
import os
import shutil
import re
from typing import Optional, Dict, List
from fuzzywuzzy import fuzz, process


def merge_compound_files() -> str:
    """
    整合compound文件夹下的四个xlsx文件
    
    返回:
        str: 整合后的文件路径
    """
    compound_dir = Path('compound')
    
    if not compound_dir.exists():
        raise FileNotFoundError("compound文件夹不存在")
    
    # 定义要读取的文件
    files = {
        '设备实物ID': compound_dir / '设备实物ID (3).xls',
        '物资技术参数': compound_dir / '物资技术参数.xls',
        '设备交接实验': compound_dir / '设备交接实验.xls',
        '设备安装调试': compound_dir / '设备安装调试.xls'
    }
    
    # 检查文件是否存在
    missing_files = [str(path) for name, path in files.items() if not path.exists()]
    if missing_files:
        raise FileNotFoundError(f"以下文件不存在: {', '.join(missing_files)}")
    
    print("开始整合compound文件...")
    
    # 读取所有文件
    dataframes = {}
    for name, file_path in files.items():
        try:
            print(f"正在读取文件: {file_path}")
            df = pd.read_excel(file_path)
            dataframes[name] = df
            print(f"  - 成功读取 {len(df)} 行数据")
        except Exception as e:
            raise Exception(f"读取文件 {file_path} 时出错: {e}")
    
    # 以设备实物ID文件为基础进行整合
    base_df = dataframes['设备实物ID'].copy()
    
    # 查找实物ID列的可能名称
    id_column = None
    possible_id_names = ['实物ID', '实物id', '设备ID', '设备id', 'ID', 'id']
    
    for col in base_df.columns:
        if any(name in str(col) for name in possible_id_names):
            id_column = col
            break
    
    if id_column is None:
        print("警告：未找到明确的实物ID列，使用第一列作为ID列")
        id_column = base_df.columns[0]
    
    print(f"使用 '{id_column}' 作为主键进行整合")
    
    # 去除基础数据中的重复项
    print(f"去除重复数据...")
    print(f"  - 设备实物ID 原始行数: {len(base_df)}")
    base_df = base_df.drop_duplicates(subset=[id_column], keep='first')
    print(f"  - 设备实物ID 去重后行数: {len(base_df)}")
    
    # 整合其他文件的数据
    merged_df = base_df.copy()
    
    for name, df in dataframes.items():
        if name == '设备实物ID':
            continue
            
        # 在当前数据框中查找ID列
        df_id_column = None
        for col in df.columns:
            if any(id_name in str(col) for id_name in possible_id_names):
                df_id_column = col
                break
        
        if df_id_column is None:
            print(f"警告：在 {name} 中未找到ID列，尝试使用第一列")
            df_id_column = df.columns[0]
        
        # 去除当前文件中的重复项
        print(f"  - {name} 原始行数: {len(df)}")
        df = df.drop_duplicates(subset=[df_id_column], keep='first')
        print(f"  - {name} 去重后行数: {len(df)}")
        
        # 重命名ID列以避免冲突
        if df_id_column != id_column:
            df = df.rename(columns={df_id_column: id_column})
        
        # 为其他列添加前缀以避免列名冲突
        columns_to_rename = {}
        for col in df.columns:
            if col != id_column:
                columns_to_rename[col] = f"{name}_{col}"
        df = df.rename(columns=columns_to_rename)
        
        # 合并数据
        merged_df = pd.merge(merged_df, df, on=id_column, how='left')
    
    # 保存结果
    output_file = compound_dir / '整合数据结果.xlsx'
    merged_df.to_excel(output_file, index=False)
    
    print(f"整合完成! 结果已保存到: {output_file}")
    print(f"总行数: {len(merged_df)}")
    print(f"总列数: {len(merged_df.columns)}")
    
    return str(output_file)


def extract_core_fields_from_merged_data(merged_file_path: str) -> pd.DataFrame:
    """
    从整合后的数据中智能提取核心字段
    
    参数:
        merged_file_path: 整合数据文件路径
        
    返回:
        包含四个核心字段的DataFrame
    """
    # 智能读取Excel文件
    try:
        if merged_file_path.lower().endswith('.xls'):
            df = pd.read_excel(merged_file_path, engine='xlrd')
        else:
            df = pd.read_excel(merged_file_path)
    except Exception as e:
        try:
            df = pd.read_excel(merged_file_path, engine='openpyxl')
        except Exception as e2:
            raise Exception(f"无法读取合并文件: xlrd错误={e}, openpyxl错误={e2}")
    print(f"\n开始智能字段提取，数据形状: {df.shape}")
    
    # 定义更灵活的字段匹配规则
    field_patterns = {
        '实物ID': {
            'exact': ['实物ID', '设备ID', 'ID', '物资编码', '设备编号'],
            'partial': ['id', 'ID', '编码', '编号']
        },
        '物资描述': {
            'exact': ['物资描述', '设备名称', '物料描述', '设备描述', '名称', '描述'],
            'partial': ['描述', '名称', '物资', '物料']
        },
        '设备类型描述': {
            'exact': ['设备类型描述', '设备类型', '物料类型', '类型描述', '设备型号'],
            'partial': ['类型', '型号', 'type']
        },
        '电压等级': {
            'exact': ['电压等级', '电压', '额定电压', '工作电压', '电压级别'],
            'partial': ['电压', 'voltage', 'kv', 'KV']
        }
    }
    
    # 智能查找列
    found_columns = {}
    
    for target_field, patterns in field_patterns.items():
        found_column = None
        best_score = 0
        
        # 精确匹配 - 同时检查数据完整性
        best_exact_match = None
        best_exact_score = 0
        
        for col in df.columns:
            col_str = str(col).strip()
            for exact_name in patterns['exact']:
                if col_str == exact_name:
                    # 检查这个列的数据完整性
                    non_null_count = df[col].notna().sum()
                    if non_null_count > best_exact_score:
                        best_exact_score = non_null_count
                        best_exact_match = col
        
        if best_exact_match and best_exact_score > 0:
            found_column = best_exact_match
            print(f"精确匹配: {target_field} <- {found_column} (数据完整性: {best_exact_score})")
        
        # 如果没有精确匹配，进行模糊匹配
        if not found_column:
            for col in df.columns:
                col_str = str(col).strip().lower()
                for partial_name in patterns['partial']:
                    if partial_name.lower() in col_str:
                        score = fuzz.ratio(col_str, partial_name.lower())
                        if score > best_score:
                            best_score = score
                            found_column = col
            
            if found_column and best_score > 60:
                print(f"模糊匹配: {target_field} <- {found_column} (相似度: {best_score})")
            else:
                found_column = None
        
        found_columns[target_field] = found_column
    
    # 如果没有找到某些关键字段，尝试从所有列中推测
    if not found_columns['物资描述']:
        # 寻找包含最多非空值的文本列
        text_columns = []
        for col in df.columns:
            if df[col].dtype == 'object':  # 文本列
                non_null_count = df[col].notna().sum()
                avg_length = df[col].dropna().astype(str).str.len().mean()
                if non_null_count > len(df) * 0.3 and avg_length > 5:  # 至少30%非空且平均长度>5
                    text_columns.append((col, non_null_count, avg_length))
        
        if text_columns:
            # 选择非空值最多的文本列作为物资描述
            best_text_col = max(text_columns, key=lambda x: x[1])
            found_columns['物资描述'] = best_text_col[0]
            print(f"推测物资描述列: {best_text_col[0]} (非空: {best_text_col[1]}, 平均长度: {best_text_col[2]:.1f})")
    
    # 构建核心数据
    core_data = {}
    
    # 处理实物ID
    id_col = found_columns['实物ID']
    if id_col:
        core_data['实物ID'] = df[id_col]
        print(f"使用实物ID列: {id_col}")
    else:
        # 如果没有精确匹配，查找任何包含ID的列
        potential_id_cols = [col for col in df.columns if 'id' in str(col).lower() or 'ID' in str(col)]
        if potential_id_cols:
            # 选择非空值最多的ID列
            best_id_col = None
            max_non_null = 0
            for col in potential_id_cols:
                non_null_count = df[col].notna().sum()
                if non_null_count > max_non_null:
                    max_non_null = non_null_count
                    best_id_col = col
            
            if best_id_col and max_non_null > 0:
                core_data['实物ID'] = df[best_id_col]
                print(f"使用候选实物ID列: {best_id_col} (非空值: {max_non_null})")
            else:
                # 使用行索引作为临时ID
                core_data['实物ID'] = [f'AUTO_ID_{i:06d}' for i in range(len(df))]
                print("警告: 未找到有效实物ID列，使用自动生成的ID")
        else:
            # 使用行索引作为临时ID
            core_data['实物ID'] = [f'AUTO_ID_{i:06d}' for i in range(len(df))]
            print("警告: 未找到任何ID列，使用自动生成的ID")
    
    # 处理物资描述 -> 设备名称
    desc_col = found_columns['物资描述']
    if desc_col:
        print(f"从 '{desc_col}' 列提取设备名称...")
        core_data['设备名称'] = df[desc_col].apply(extract_device_name)
        
        # 同时从物资描述中提取电压等级（如果没有专门的电压等级列）
        if not found_columns['电压等级']:
            print(f"从物资描述中提取电压等级...")
            core_data['电压等级'] = df[desc_col].apply(extract_voltage_level)
        else:
            voltage_col = found_columns['电压等级']
            print(f"从 '{voltage_col}' 列提取电压等级...")
            # 先尝试直接使用电压等级列，如果为空则从物资描述中提取
            voltage_from_col = df[voltage_col].apply(extract_voltage_level)
            voltage_from_desc = df[desc_col].apply(extract_voltage_level)
            core_data['电压等级'] = voltage_from_col.fillna(voltage_from_desc)
    else:
        core_data['设备名称'] = [None] * len(df)
        core_data['电压等级'] = [None] * len(df)
        print("警告: 未找到物资描述列")
    
    # 处理设备类型描述 -> 设备类型
    type_col = found_columns['设备类型描述']
    if type_col:
        print(f"从 '{type_col}' 列提取设备类型...")
        core_data['设备类型'] = df[type_col].apply(extract_device_type)
    elif desc_col:
        print(f"从物资描述中提取设备类型...")
        # 如果没有专门的设备类型列，从物资描述中提取
        core_data['设备类型'] = df[desc_col].apply(extract_device_type)
    else:
        core_data['设备类型'] = [None] * len(df)
        print("警告: 未找到设备类型列")
    
    # 创建核心数据DataFrame
    core_df = pd.DataFrame(core_data)
    
    # 数据清理和去重
    print(f"\n数据清理前: {len(core_df)} 行")
    
    # 移除实物ID为空的行
    core_df = core_df.dropna(subset=['实物ID'])
    print(f"去除空ID后: {len(core_df)} 行")
    
    # 根据实物ID去重
    core_df = core_df.drop_duplicates(subset=['实物ID'], keep='first')
    print(f"去重后: {len(core_df)} 行")
    
    # 数据质量报告
    print(f"\n数据质量报告:")
    for col in core_df.columns:
        non_null_count = core_df[col].notna().sum()
        total_count = len(core_df)
        percentage = (non_null_count / total_count) * 100
        print(f"  {col}: {non_null_count}/{total_count} ({percentage:.1f}% 完整)")
    
    return core_df


def handle_compound_files() -> str:
    """
    处理compound文件夹：整合四个文件并提取核心字段
    
    返回:
        str: 成功生成的输出文件路径
    """
    try:
        # 1. 整合compound文件
        merged_file_path = merge_compound_files()
        
        # 2. 从整合数据中提取核心字段
        core_df = extract_core_fields_from_merged_data(merged_file_path)
        
        # 3. 保存核心字段到test_work.xlsx
        output_path = Path("test_work.xlsx")
        core_df.to_excel(output_path, index=False)
        
        print(f"compound文件处理完成!")
        print(f"提取核心字段数据: {len(core_df)} 行")
        print(f"输出文件: {output_path}")
        
        return str(output_path)
        
    except Exception as e:
        raise Exception(f"处理compound文件时出错: {e}")


def extract_voltage_level(text: str) -> str:
    """
    从文本中提取电压等级
    """
    if pd.isna(text) or not isinstance(text, str):
        return None
    
    text = str(text).strip()
    
    # 电压等级模式匹配
    voltage_patterns = [
        r'(\d+(?:\.\d+)?)\s*[kK][Vv]',  # 如 "110kV", "35KV"
        r'(\d+(?:\.\d+)?)\s*千伏',      # 如 "110千伏"
        r'(\d+(?:\.\d+)?)\s*[kK]',     # 如 "110K"
        r'([0-9]+(?:\.[0-9]+)?)(?=.*(?:电压|伏特|volt))', # 包含电压关键字的数字
    ]
    
    for pattern in voltage_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            voltage = float(matches[0])
            # 标准化电压等级
            if voltage >= 1000:
                return f"{int(voltage/1000)}kV"
            elif voltage >= 100:
                return f"{int(voltage)}kV"
            elif voltage >= 10:
                return f"{int(voltage)}kV"
            else:
                return f"{voltage}kV"
    
    # 尝试从常见电压等级词汇中匹配
    standard_voltages = ['750kV', '500kV', '330kV', '220kV', '110kV', '66kV', '35kV', '20kV', '10kV', '6kV', '0.4kV']
    best_match = process.extractOne(text, standard_voltages, scorer=fuzz.partial_ratio)
    if best_match and best_match[1] > 60:  # 相似度阈值
        return best_match[0]
    
    return None


def extract_device_type(text: str) -> str:
    """
    从设备类型描述中提取设备类型
    """
    if pd.isna(text) or not isinstance(text, str):
        return None
    
    text = str(text).strip()
    
    # 常见设备类型关键字
    device_types = {
        '变压器': ['变压器', '主变', '变压', '电力变压器', '配电变压器'],
        '开关柜': ['开关柜', '开关设备', '配电柜', '高压开关柜', '中压开关柜'],
        '断路器': ['断路器', '开关', '真空断路器', '六氟化硫断路器', 'SF6断路器'],
        '隔离开关': ['隔离开关', '刀闸', '隔离刀闸'],
        '电缆': ['电缆', '电力电缆', '高压电缆', '架空线'],
        '母线': ['母线', '汇流排', '导线', '母排'],
        '避雷器': ['避雷器', '避雷针', '浪涌保护器'],
        '电容器': ['电容器', '并联电容器', '补偿电容器'],
        '电抗器': ['电抗器', '限流电抗器'],
        '互感器': ['互感器', '电流互感器', '电压互感器', 'CT', 'PT'],
        '绝缘子': ['绝缘子', '瓷绝缘子', '复合绝缘子'],
        '接地装置': ['接地', '接地装置', '接地网'],
    }
    
    # 精确匹配
    for device_type, keywords in device_types.items():
        for keyword in keywords:
            if keyword in text:
                return device_type
    
    # 模糊匹配
    all_types = list(device_types.keys())
    best_match = process.extractOne(text, all_types, scorer=fuzz.partial_ratio)
    if best_match and best_match[1] > 70:  # 相似度阈值
        return best_match[0]
    
    return text  # 如果无法识别，返回原文


def extract_device_name(text: str) -> str:
    """
    从物资描述中提取设备名称
    """
    if pd.isna(text) or not isinstance(text, str):
        return None
    
    text = str(text).strip()
    
    # 清理常见的前后缀
    clean_patterns = [
        r'^[\d\-]+[\s]*',  # 去掉开头的编号
        r'[\s]*\([^\)]*\)$',  # 去掉结尾的括号内容
        r'[\s]*（[^）]*）$',  # 去掉结尾的中文括号内容
        r'[\s]*\[[^\]]*\]$',  # 去掉结尾的方括号内容
    ]
    
    cleaned_text = text
    for pattern in clean_patterns:
        cleaned_text = re.sub(pattern, '', cleaned_text).strip()
    
    # 如果清理后为空，返回原文的前30个字符
    if not cleaned_text:
        return text[:30] if len(text) > 30 else text
    
    return cleaned_text


def merge_custom_files(file_paths: List[str]) -> str:
    """
    整合自定义选择的多个Excel文件，先整合所有数据再去重
    
    参数:
        file_paths: 要整合的文件路径列表
        
    返回:
        str: 整合后的文件路径
    """
    if not file_paths:
        raise ValueError("文件路径列表为空")
    
    print(f"开始整合 {len(file_paths)} 个文件...")
    
    # 读取所有文件数据
    all_data = []
    total_rows = 0
    
    for i, file_path in enumerate(file_paths):
        try:
            print(f"正在读取文件 {i+1}/{len(file_paths)}: {os.path.basename(file_path)}")
            
            if not os.path.exists(file_path):
                print(f"  - 警告: 文件不存在，跳过: {file_path}")
                continue
                
            # 尝试读取Excel文件，支持xls和xlsx格式
            try:
                if file_path.lower().endswith('.xls'):
                    df = pd.read_excel(file_path, engine='xlrd')
                else:
                    df = pd.read_excel(file_path)
            except Exception as read_error:
                # 如果xlrd引擎失败，尝试openpyxl引擎
                try:
                    df = pd.read_excel(file_path, engine='openpyxl')
                    print(f"  - 使用openpyxl引擎成功读取")
                except Exception as e2:
                    raise Exception(f"无法读取文件，尝试了多种引擎: xlrd错误={read_error}, openpyxl错误={e2}")
                    
            print(f"  - 成功读取 {len(df)} 行数据, {len(df.columns)} 列")
            print(f"  - 列名: {list(df.columns)[:3]}{'...' if len(df.columns) > 3 else ''}")
            
            # 为每行数据添加来源文件标识
            df['_source_file'] = os.path.basename(file_path)
            all_data.append(df)
            total_rows += len(df)
            
        except Exception as e:
            print(f"  - 错误: 读取文件 {file_path} 时出错: {e}")
            continue
    
    if not all_data:
        raise Exception("没有成功读取任何文件")
    
    print(f"\n开始合并所有数据... 总计 {total_rows} 行")
    
    # 合并所有数据框
    combined_df = pd.concat(all_data, ignore_index=True, sort=False)
    print(f"合并完成，总计 {len(combined_df)} 行, {len(combined_df.columns)} 列")
    
    # 显示合并后的列名
    print(f"合并后的所有列名: {list(combined_df.columns)}")
    
    # 保存合并结果用于调试
    debug_file = '合并原始数据.xlsx'
    combined_df.to_excel(debug_file, index=False)
    print(f"原始合并数据已保存到: {debug_file}")
    
    # 查找ID列
    possible_id_names = ['实物ID', '设备ID', 'ID', '物资编码', '设备编号', '编号', 'id', 'Id']
    id_column = None
    
    for col in combined_df.columns:
        for id_name in possible_id_names:
            if id_name.lower() in str(col).lower():
                id_column = col
                print(f"找到ID列: '{id_column}'")
                break
        if id_column:
            break
    
    if not id_column:
        # 如果没找到明确的ID列，使用第一列
        id_column = combined_df.columns[0]
        print(f"未找到明确ID列，使用第一列: '{id_column}'")
    
    # 根据ID列去重（保留第一条记录）
    print(f"开始去重处理...")
    print(f"去重前: {len(combined_df)} 行")
    
    # 先去除ID为空的行
    combined_df = combined_df.dropna(subset=[id_column])
    print(f"去除空ID后: {len(combined_df)} 行")
    
    # 去重
    combined_df = combined_df.drop_duplicates(subset=[id_column], keep='first')
    print(f"去重后: {len(combined_df)} 行")
    
    # 保存整合结果
    output_file = '自定义整合结果.xlsx'
    combined_df.to_excel(output_file, index=False)
    
    print(f"\n整合完成!")
    print(f"结果已保存到: {output_file}")
    print(f"最终行数: {len(combined_df)}")
    print(f"最终列数: {len(combined_df.columns)}")
    
    return output_file


def handle_param_file(file_path, show_preview: bool = True):
    """
    参数文件功能：根据指定的路径或处理compound文件夹，提取四列并导出新Excel。
    
    参数:
        file_path (str): 要处理的Excel文件的完整路径，或者 "compound" 表示处理compound文件夹。
        show_preview (bool): 是否显示数据预览窗口，默认为True。

    返回:
        str: 成功生成的输出文件的路径。

    异常:
        ValueError: 如果文件路径无效或文件中缺少必要的列。
        FileNotFoundError: 如果提供的文件路径不存在。
    """
    # 检查处理类型
    if isinstance(file_path, dict) and file_path.get("type") == "custom_multiple":
        # 处理自定义多文件整合
        print("检测到自定义多文件整合请求")
        file_paths = file_path.get("files", [])
        
        # 整合文件
        merged_file_path = merge_custom_files(file_paths)
        
        # 提取核心字段
        core_df = extract_core_fields_from_merged_data(merged_file_path)
        
        # 保存核心字段
        output_path = Path("test_work.xlsx")
        core_df.to_excel(output_path, index=False)
        
        print(f"自定义多文件整合完成!")
        print(f"提取核心字段数据: {len(core_df)} 行")
        
        # 显示数据预览（如果需要）
        if show_preview:
            show_param_data_preview(core_df, f"自定义整合 ({len(file_paths)}个文件)")
        
        return str(output_path)
    
    elif file_path == "compound" or (isinstance(file_path, str) and "compound" in file_path.lower()):
        # 处理compound文件夹
        print("检测到compound文件夹处理请求")
        output_path = handle_compound_files()
        
        # 显示数据预览（如果需要）
        if show_preview:
            df_result = pd.read_excel(output_path)
            show_param_data_preview(df_result, "compound文件夹")
        
        return output_path
    
    # 原有的单文件处理逻辑
    if not file_path or not os.path.exists(file_path):
        raise FileNotFoundError(f"错误：文件未找到或路径无效: {file_path}")

    try:
        # 尝试读取Excel文件，支持xls和xlsx格式
        if isinstance(file_path, str) and file_path.lower().endswith('.xls'):
            df = pd.read_excel(file_path, engine='xlrd')
        else:
            df = pd.read_excel(file_path)
    except Exception as e:
        # 如果失败，尝试其他引擎
        try:
            if isinstance(file_path, str) and file_path.lower().endswith('.xls'):
                df = pd.read_excel(file_path, engine='openpyxl')
            else:
                df = pd.read_excel(file_path, engine='xlrd')
        except Exception as e2:
            raise Exception(f"读取Excel文件 '{os.path.basename(file_path)}' 时出错: 主要错误={e}, 备用引擎错误={e2}")

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

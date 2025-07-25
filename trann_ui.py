import json
import pandas as pd
from openpyxl.utils import get_column_letter
from typing import Dict, Any, List, Optional
import os
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def preprocess_to_excel(json_file_path: str = "system_tree.json", excel_file_path: str = "device_data.xlsx") -> Optional[str]:
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
        Optional[str]: 生成的 Excel 文件路径，失败时返回 None

    异常:
        FileNotFoundError: JSON 文件不存在
        json.JSONDecodeError: JSON 格式错误
        PermissionError: 无权限写入 Excel 文件
        Exception: 其他处理错误
    """
    try:
        # 验证输入文件路径
        if not os.path.exists(json_file_path):
            logger.error(f"JSON 文件不存在: {json_file_path}")
            raise FileNotFoundError(f"JSON 文件不存在: {json_file_path}")
        
        # 验证输出目录
        output_dir = os.path.dirname(excel_file_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
            logger.info(f"创建输出目录: {output_dir}")

        logger.info(f"开始处理 JSON 文件: {json_file_path}")
        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)

        if not isinstance(data, dict):
            raise ValueError("JSON 数据格式不正确，应为字典类型")

        results: List[Dict[str, str]] = []

        def traverse(node: Dict[str, Any]) -> None:
            """递归遍历节点提取数据"""
            if not isinstance(node, dict):
                return
                
            description = node.get('DESCRIPTION', {})
            if not isinstance(description, dict):
                description = {}
                
            row = {
                "电网工程标识系统编码": _safe_extract_value(description.get("电网工程标识系统编码", "")),
                "工程中名称": _safe_extract_value(description.get("工程中名称", "")),
                "电压等级": _safe_extract_value(description.get("电压等级", "")),
                "Device_ID": ""  # 默认空
            }

            if 'DEVICES' in node:
                devices = node['DEVICES']
                if isinstance(devices, dict):
                    row["Device_ID"] = devices.get("ID", "")
                    results.append(row.copy())
                elif isinstance(devices, list):
                    for device in devices:
                        if isinstance(device, dict):
                            new_row = row.copy()
                            new_row["Device_ID"] = device.get("ID", "")
                            results.append(new_row)

            if 'SUBSYSTEMS' in node and isinstance(node['SUBSYSTEMS'], dict):
                for sub in node['SUBSYSTEMS'].values():
                    traverse(sub)

        def _safe_extract_value(value: str) -> str:
            """安全提取等号后的值"""
            if not isinstance(value, str):
                return ""
            parts = value.split("=")
            return parts[-1].strip() if len(parts) > 1 else value.strip()

        # 处理数据
        for root_node in data.values():
            traverse(root_node)

        if not results:
            logger.warning("未找到任何设备数据")
            return None

        logger.info(f"提取到 {len(results)} 条设备记录")
        df = pd.DataFrame(results)
        
        # 过滤掉"标识系统编码"和"工程名称"为金具、金具+数字类型的数据
        df = _filter_hardware_data(df)

        # 写入 Excel 文件
        try:
            with pd.ExcelWriter(excel_file_path, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Sheet1')
                worksheet = writer.sheets['Sheet1']
                
                # 自动调整列宽
                for idx, column in enumerate(df.columns, 1):
                    column_letter = get_column_letter(idx)
                    max_len = max(
                        df[column].fillna('').astype(str).apply(len).max(),
                        len(column)
                    )
                    worksheet.column_dimensions[column_letter].width = min(max_len * 1.2 + 2, 50)  # 限制最大宽度

            logger.info(f"✅ Excel文件已生成: {excel_file_path}")
            return excel_file_path
            
        except PermissionError as e:
            logger.error(f"无权限写入文件 {excel_file_path}: {e}")
            raise PermissionError(f"无权限写入文件 {excel_file_path}")

    except FileNotFoundError:
        raise
    except json.JSONDecodeError as e:
        logger.error(f"JSON 解析错误: {e}")
        raise json.JSONDecodeError(f"JSON 解析错误: {e}", e.doc, e.pos)
    except PermissionError:
        raise
    except Exception as e:
        logger.error(f"处理过程中发生错误: {e}")
        raise Exception(f"处理过程中发生错误: {e}")

    return None


def _filter_hardware_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    过滤掉"标识系统编码"为空白和"工程名称"为金具、金具+数字类型的数据
    
    参数:
        df (pd.DataFrame): 输入的数据框
        
    返回:
        pd.DataFrame: 过滤后的数据框
    """
    import re
    
    if df.empty:
        return df
    
    original_count = len(df)
    
    # 检查列是否存在
    system_code_col = "电网工程标识系统编码"
    project_name_col = "工程中名称"
    
    # 定义过滤条件：金具、金具+数字的正则表达式
    hardware_pattern = re.compile(r'^金具\d*$', re.IGNORECASE)
    
    # 过滤条件1：过滤"标识系统编码"为空白的记录
    if system_code_col in df.columns:
        # 过滤空白、NaN、空字符串或只包含空格的记录
        mask1 = (
            df[system_code_col].notna() & 
            (df[system_code_col].astype(str).str.strip() != '') &
            (df[system_code_col].astype(str).str.strip() != 'nan')
        )
        df = df[mask1]
        logger.info(f"根据标识系统编码非空过滤，剩余记录: {len(df)}")
    
    # 过滤条件2：过滤"工程名称"为金具、金具+数字的记录
    if project_name_col in df.columns:
        mask2 = ~df[project_name_col].astype(str).str.match(hardware_pattern, na=False)
        df = df[mask2]
        logger.info(f"根据工程名称过滤金具类型，剩余记录: {len(df)}")
    
    filtered_count = original_count - len(df)
    if filtered_count > 0:
        logger.info(f"已过滤掉 {filtered_count} 条记录（空白标识系统编码 + 金具类型工程名称）")
    
    return df

import pandas as pd
import os
from pathlib import Path

def merge_compound_files():
    """
    将compound文件夹下的四个xlsx文件按照实物ID整合到一个新文件中
    """
    # 设置文件路径 - 当前脚本就在compound文件夹中
    compound_dir = Path('.')
    
    # 定义要读取的文件
    files = {
        '设备实物ID': compound_dir / '设备实物ID (3).xls',
        '物资技术参数': compound_dir / '物资技术参数.xls',
        '设备交接实验': compound_dir / '设备交接实验.xls',
        '设备安装调试': compound_dir / '设备安装调试.xls'
    }
    
    # 读取所有文件
    dataframes = {}
    for name, file_path in files.items():
        try:
            print(f"正在读取文件: {file_path}")
            df = pd.read_excel(file_path)
            dataframes[name] = df
            print(f"  - 成功读取 {len(df)} 行数据")
            print(f"  - 列名: {df.columns.tolist()}")
        except Exception as e:
            print(f"读取文件 {file_path} 时出错: {e}")
            return
    
    print("\n开始整合数据...")
    
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
    
    # 去除基础数据中的重复项（保留第一条）
    print(f"\n去除重复数据...")
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
        
        # 去除当前文件中的重复项（保留第一条）
        print(f"  - {name} 原始行数: {len(df)}")
        df = df.drop_duplicates(subset=[df_id_column], keep='first')
        print(f"  - {name} 去重后行数: {len(df)}")
        
        print(f"  - 整合 {name}，使用列 '{df_id_column}' 进行匹配")
        
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
    output_file = '整合数据结果.xlsx'
    merged_df.to_excel(output_file, index=False)
    
    print(f"\n整合完成!")
    print(f"结果已保存到: {output_file}")
    print(f"总行数: {len(merged_df)}")
    print(f"总列数: {len(merged_df.columns)}")
    
    # 显示前几行数据预览
    print("\n数据预览（前5行）:")
    print(merged_df.head())
    
    return merged_df

if __name__ == "__main__":
    merge_compound_files()
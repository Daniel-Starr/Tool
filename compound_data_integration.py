"""
Compound数据整合脚本
将四个XLS文件整合到一个文件中并去重
"""
import pandas as pd
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def integrate_compound_data():
    """整合compound文件夹中的四个XLS文件"""
    
    logger.info("=== 开始整合compound数据 ===")
    
    # 定义文件路径
    files = {
        '设备实物ID': Path('compound/设备实物ID (3).xls'),
        '物资技术参数': Path('compound/物资技术参数.xls'),
        '设备交接实验': Path('compound/设备交接实验.xls'),
        '设备安装调试': Path('compound/设备安装调试.xls')
    }
    
    # 检查文件是否存在
    missing_files = [str(path) for name, path in files.items() if not path.exists()]
    if missing_files:
        raise FileNotFoundError(f"以下文件不存在: {missing_files}")
    
    # 读取所有文件
    dataframes = {}
    total_rows_before = 0
    
    for name, file_path in files.items():
        logger.info(f"读取文件: {name}")
        try:
            df = pd.read_excel(file_path)
            dataframes[name] = df
            total_rows_before += len(df)
            logger.info(f"  - {name}: {len(df)} 行, {len(df.columns)} 列")
            
            # 显示实物ID列信息
            id_columns = [col for col in df.columns if '实物' in str(col) or 'ID' in str(col) or 'id' in str(col)]
            if id_columns:
                id_col = id_columns[0]
                unique_ids = df[id_col].dropna().nunique()
                logger.info(f"  - 实物ID列: {id_col}, 唯一ID数: {unique_ids}")
                
        except Exception as e:
            logger.error(f"读取文件 {file_path} 失败: {e}")
            raise
    
    logger.info(f"文件读取完成，总行数: {total_rows_before}")
    
    # 第一步：以设备实物ID文件为基础
    base_df = dataframes['设备实物ID'].copy()
    base_id_col = '实物ID'
    
    logger.info(f"\n=== 数据整合过程 ===")
    logger.info(f"基础数据: 设备实物ID文件 ({len(base_df)} 行)")
    
    # 标准化实物ID列名
    def standardize_id_column(df, source_name):
        """标准化实物ID列名为统一的'实物ID'"""
        id_columns = [col for col in df.columns if '实物' in str(col) or 'ID' in str(col) or 'id' in str(col)]
        
        if not id_columns:
            logger.warning(f"{source_name}: 未找到实物ID列")
            return df, None
            
        # 选择最可能的ID列
        primary_id_col = None
        for col in id_columns:
            if '实物ID' == col or '实物id' == col:
                primary_id_col = col
                break
        
        if not primary_id_col and id_columns:
            primary_id_col = id_columns[0]
            
        if primary_id_col and primary_id_col != '实物ID':
            df = df.rename(columns={primary_id_col: '实物ID'})
            logger.info(f"  - {source_name}: 列名 '{primary_id_col}' 标准化为 '实物ID'")
            
        return df, '实物ID'
    
    # 整合其他文件
    merged_df = base_df.copy()
    
    for name, df in dataframes.items():
        if name == '设备实物ID':
            continue
            
        logger.info(f"\n整合文件: {name}")
        
        # 标准化ID列名
        df_processed, id_col = standardize_id_column(df.copy(), name)
        
        if id_col is None:
            logger.warning(f"跳过 {name}: 没有找到有效的实物ID列")
            continue
        
        # 去重处理
        original_count = len(df_processed)
        df_processed = df_processed.drop_duplicates(subset=[id_col], keep='first')
        dedup_count = len(df_processed)
        logger.info(f"  - 去重: {original_count} → {dedup_count} 行")
        
        # 避免列名冲突，为其他列添加前缀
        columns_to_rename = {}
        for col in df_processed.columns:
            if col != '实物ID':  # 保持实物ID列名不变
                new_col_name = f"{name}_{col}"
                # 如果新列名已存在，添加序号
                counter = 1
                while new_col_name in merged_df.columns:
                    new_col_name = f"{name}_{col}_{counter}"
                    counter += 1
                columns_to_rename[col] = new_col_name
        
        df_processed = df_processed.rename(columns=columns_to_rename)
        
        # 执行左连接
        before_merge = len(merged_df)
        merged_df = pd.merge(merged_df, df_processed, on='实物ID', how='left')
        after_merge = len(merged_df)
        
        # 统计匹配情况
        matched_ids = merged_df['实物ID'].isin(df_processed['实物ID']).sum()
        logger.info(f"  - 合并结果: {before_merge} → {after_merge} 行")
        logger.info(f"  - 匹配的实物ID: {matched_ids}/{len(merged_df)}")
    
    # 最终去重（基于实物ID）
    logger.info(f"\n=== 最终去重处理 ===")
    before_final_dedup = len(merged_df)
    merged_df = merged_df.drop_duplicates(subset=['实物ID'], keep='first')
    after_final_dedup = len(merged_df)
    
    logger.info(f"最终去重: {before_final_dedup} → {after_final_dedup} 行")
    
    # 数据清洗
    logger.info(f"\n=== 数据清洗 ===")
    
    # 移除全空行
    before_clean = len(merged_df)
    merged_df = merged_df.dropna(how='all')
    after_clean = len(merged_df)
    logger.info(f"移除全空行: {before_clean} → {after_clean}")
    
    # 实物ID列的清洗
    if '实物ID' in merged_df.columns:
        id_before = len(merged_df)
        merged_df = merged_df[merged_df['实物ID'].notna()]  # 移除实物ID为空的行
        merged_df = merged_df[merged_df['实物ID'] != '']     # 移除实物ID为空字符串的行
        id_after = len(merged_df)
        logger.info(f"清理无效实物ID: {id_before} → {id_after}")
    
    # 保存整合结果到compound文件夹
    output_file = Path('compound/compound_整合数据_完整版.xlsx')
    merged_df.to_excel(output_file, index=False)
    
    # 生成摘要信息
    logger.info(f"\n=== 整合完成 ===")
    logger.info(f"输出文件: {output_file}")
    logger.info(f"总行数: {len(merged_df)}")
    logger.info(f"总列数: {len(merged_df.columns)}")
    logger.info(f"唯一实物ID: {merged_df['实物ID'].nunique()}")
    
    # 显示各文件的数据贡献
    logger.info(f"\n数据贡献统计:")
    for name in files.keys():
        if name == '设备实物ID':
            continue
        prefix_cols = [col for col in merged_df.columns if col.startswith(f"{name}_")]
        if prefix_cols:
            # 检查有数据的行数
            has_data = merged_df[prefix_cols].notna().any(axis=1).sum()
            logger.info(f"  - {name}: {len(prefix_cols)} 列, {has_data} 行有数据")
    
    # 保存数据质量报告
    quality_report = {
        '原始文件统计': {},
        '整合结果': {
            '总行数': len(merged_df),
            '总列数': len(merged_df.columns),
            '唯一实物ID数': merged_df['实物ID'].nunique(),
            '输出文件': output_file
        }
    }
    
    for name, df in dataframes.items():
        quality_report['原始文件统计'][name] = {
            '行数': len(df),
            '列数': len(df.columns)
        }
    
    # 保存简化版（只包含关键字段）
    key_columns = ['实物ID']
    
    # 添加一些重要的业务字段
    important_patterns = ['名称', '类型', '型号', '规格', '厂家', '状态', '电压', '容量']
    
    for col in merged_df.columns:
        if col == '实物ID':
            continue
        # 检查是否包含重要信息
        col_lower = col.lower()
        if any(pattern in col for pattern in important_patterns):
            key_columns.append(col)
        # 限制关键字段数量
        if len(key_columns) >= 15:
            break
    
    if len(key_columns) > 1:
        simplified_df = merged_df[key_columns].copy()
        simplified_output = Path('compound/compound_整合数据_简化版.xlsx')
        simplified_df.to_excel(simplified_output, index=False)
        logger.info(f"简化版文件: {simplified_output} ({len(simplified_df)} 行, {len(simplified_df.columns)} 列)")
    
    # 显示前几行数据预览
    logger.info(f"\n数据预览 (前3行):")
    preview_cols = merged_df.columns[:8] if len(merged_df.columns) > 8 else merged_df.columns
    print(merged_df[preview_cols].head(3).to_string(index=False))
    
    return merged_df, output_file

if __name__ == "__main__":
    try:
        result_df, output_path = integrate_compound_data()
        print(f"\n✅ 数据整合成功完成！")
        print(f"📁 输出文件: {output_path}")
        print(f"📊 最终数据: {len(result_df)} 行, {len(result_df.columns)} 列")
    except Exception as e:
        print(f"\n❌ 数据整合失败: {e}")
        raise
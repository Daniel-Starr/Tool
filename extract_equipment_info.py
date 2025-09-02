"""
从设备参数字段中提取结构化信息
根据用户指示：设备名称=第1元素，电压等级=第2元素，设备类型=第4元素
"""
import pandas as pd
import json
import re
from pathlib import Path

def parse_material_description(desc_string):
    """解析物资描述字符串 - 第1元素=设备名称，第2元素=电压等级"""
    if pd.isna(desc_string) or desc_string == '':
        return {
            '设备名称': None,
            '电压等级': None,
            '标准电压等级': None,
            '原始描述': desc_string
        }
    
    # 按逗号分割描述
    parts = str(desc_string).split(',')
    
    result = {
        '设备名称': parts[0].strip() if len(parts) > 0 else None,
        '电压等级': parts[1].strip() if len(parts) > 1 else None,
        '原始描述': desc_string,
        '参数数量': len(parts)
    }
    
    # 清理电压等级格式
    if result['电压等级']:
        voltage = result['电压等级']
        # 提取数字和单位，去掉AC前缀
        voltage_cleaned = voltage.replace('AC', '').strip()
        voltage_match = re.search(r'(\d+(?:\.\d+)?)([kK][Vv]?)', voltage_cleaned)
        if voltage_match:
            result['标准电压等级'] = f"{voltage_match.group(1)}kV"
        else:
            result['标准电压等级'] = voltage_cleaned
    
    return result

def parse_technical_parameters(tech_param_string):
    """解析物资技术参数JSON字符串"""
    if pd.isna(tech_param_string) or tech_param_string == '':
        return {}
    
    try:
        # 尝试解析JSON
        tech_data = json.loads(str(tech_param_string))
        
        # 提取关键技术参数
        extracted = {}
        
        # 电压等级相关
        if 'EDDY' in tech_data and tech_data['EDDY']:
            extracted['额定电压'] = f"{tech_data['EDDY']}kV"
        
        # 型号规格
        if 'XH' in tech_data and tech_data['XH']:
            extracted['型号'] = tech_data['XH']
            
        # 生产厂家
        if 'SCCJMC' in tech_data and tech_data['SCCJMC']:
            extracted['生产厂家'] = tech_data['SCCJMC']
        
        # 设备结构形式
        if 'JGXSMC' in tech_data and tech_data['JGXSMC']:
            extracted['结构形式'] = tech_data['JGXSMC']
            
        # 出厂编号
        if 'CCBH' in tech_data and tech_data['CCBH']:
            extracted['出厂编号'] = tech_data['CCBH']
        
        return extracted
        
    except json.JSONDecodeError:
        return {'解析错误': '无效JSON格式'}

def extract_equipment_info():
    """从compound数据中提取设备信息"""
    
    print("=== 设备信息提取工具 ===")
    
    # 读取整合数据
    input_file = Path('compound/compound_整合数据_完整版.xlsx')
    if not input_file.exists():
        raise FileNotFoundError("未找到整合数据文件")
    
    df = pd.read_excel(input_file)
    print(f"读取数据：{len(df)} 行, {len(df.columns)} 列")
    
    # 提取物资描述信息（设备名称和电压等级）
    enhanced_df = df
    if '物资描述' in df.columns:
        print("\n=== 解析物资描述字段 ===")
        
        # 应用解析函数
        desc_results = df['物资描述'].apply(parse_material_description)
        
        # 将解析结果转换为DataFrame
        desc_df = pd.json_normalize(desc_results)
        
        # 合并到原始数据
        enhanced_df = pd.concat([df, desc_df], axis=1)
        
        # 统计解析结果
        valid_equipment = desc_df['设备名称'].notna().sum()
        valid_voltage = desc_df['电压等级'].notna().sum()
        
        print(f"物资描述解析结果：")
        print(f"  - 有效设备名称: {valid_equipment}/{len(df)}")
        print(f"  - 有效电压等级: {valid_voltage}/{len(df)}")
        
        # 显示解析样例
        print(f"\n解析样例：")
        sample_data = desc_df.head(5)
        for i, (_, row) in enumerate(sample_data.iterrows()):
            print(f"  {i+1}. 设备名称: {row.get('设备名称', 'N/A')}")
            print(f"     电压等级: {row.get('电压等级', 'N/A')} -> {row.get('标准电压等级', 'N/A')}")
            print()
    else:
        print("警告：未找到'物资描述'字段")
    
    # 直接使用设备类型描述作为设备类型
    if '设备类型描述' in enhanced_df.columns:
        print("=== 使用设备类型描述 ===")
        enhanced_df['设备类型'] = enhanced_df['设备类型描述']
        valid_type = enhanced_df['设备类型'].notna().sum()
        print(f"有效设备类型: {valid_type}/{len(enhanced_df)}")
    else:
        print("警告：未找到'设备类型描述'字段")
    
    # 解析技术参数
    tech_param_col = '物资技术参数_物资技术参数'
    if tech_param_col in df.columns:
        print("=== 解析物资技术参数 ===")
        
        tech_results = df[tech_param_col].apply(parse_technical_parameters)
        tech_df = pd.json_normalize(tech_results)
        
        # 为技术参数列名添加前缀
        tech_df.columns = [f'技术参数_{col}' for col in tech_df.columns]
        
        # 合并技术参数
        enhanced_df = pd.concat([enhanced_df, tech_df], axis=1)
        
        print(f"技术参数解析完成，新增 {len(tech_df.columns)} 个字段")
    
    # 创建核心匹配字段文件
    key_columns = ['实物ID']
    
    # 添加解析出的关键信息
    extracted_columns = ['设备名称', '电压等级', '标准电压等级', '设备类型']
    for col in extracted_columns:
        if col in enhanced_df.columns:
            key_columns.append(col)
    
    # 添加原有的重要信息
    original_important = ['设备代码', '设备名称描述', '供应商名称', '状态描述', '状态名称']
    for col in original_important:
        if col in enhanced_df.columns and col not in key_columns:
            key_columns.append(col)
    
    # 添加技术参数中的关键信息
    tech_columns = ['技术参数_额定电压', '技术参数_型号', '技术参数_生产厂家', '技术参数_结构形式']
    for col in tech_columns:
        if col in enhanced_df.columns:
            key_columns.append(col)
    
    # 生成输出文件
    output_files = {
        'compound/设备信息_完整提取结果.xlsx': enhanced_df,
        'compound/设备信息_核心匹配字段.xlsx': enhanced_df[key_columns] if len(key_columns) > 1 else enhanced_df
    }
    
    for output_file, data in output_files.items():
        data.to_excel(output_file, index=False)
        print(f"保存文件: {output_file} ({len(data)} 行, {len(data.columns)} 列)")
    
    # 生成统计报告
    print(f"\n=== 提取结果统计 ===")
    
    if '设备名称' in enhanced_df.columns:
        device_name_stats = enhanced_df['设备名称'].value_counts()
        print(f"设备名称类型: {len(device_name_stats)} 种")
        print("前5种设备名称:")
        for name, count in device_name_stats.head().items():
            print(f"  - {name}: {count} 个")
    
    if '标准电压等级' in enhanced_df.columns:
        voltage_stats = enhanced_df['标准电压等级'].value_counts()
        print(f"\n电压等级分布:")
        for voltage, count in voltage_stats.items():
            print(f"  - {voltage}: {count} 个")
    
    if '设备类型' in enhanced_df.columns:
        type_stats = enhanced_df['设备类型'].value_counts()
        print(f"\n设备类型分布:")
        for dev_type, count in type_stats.items():
            print(f"  - {dev_type}: {count} 个")
    
    return enhanced_df

if __name__ == "__main__":
    try:
        result_df = extract_equipment_info()
        print(f"\n✅ 设备信息提取完成！")
        print(f"📊 最终数据: {len(result_df)} 行, {len(result_df.columns)} 列")
    except Exception as e:
        print(f"\n❌ 提取失败: {e}")
        raise
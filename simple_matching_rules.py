"""
简化版智能配对规则 - 基于device_data.xlsx的实用配对策略
"""
import pandas as pd
import random
from fuzzywuzzy import fuzz

def simple_smart_matching():
    """简单而实用的智能匹配算法"""
    
    print("=== 开始智能配对 ===")
    
    # 加载数据
    model_df = pd.read_excel('device_data.xlsx')
    physical_df = pd.read_excel('test_work.xlsx')
    
    print(f"模型数据: {len(model_df)} 条")
    print(f"实物数据: {len(physical_df)} 条")
    print(f"设备类型分布: {physical_df['设备类型'].value_counts().to_dict()}")
    
    # 按电压等级对模型数据排序（优先35kV设备）
    voltage_order = {'35(kV 中性)': 1, '500(kV 中性)': 2, '220(kV 中性)': 3, 
                    '10(kV 中性)': 4, '3(kV 中性)': 5}
    
    def get_voltage_priority(voltage):
        return voltage_order.get(str(voltage), 999)
    
    model_df['priority'] = model_df['电压等级'].apply(get_voltage_priority)
    model_df_sorted = model_df.sort_values(['priority', '工程中名称']).reset_index(drop=True)
    
    print("\n模型数据电压等级分布:")
    print(model_df['电压等级'].value_counts())
    
    # 设备名称关键词分析
    device_keywords = {
        '高价值设备': ['断路器', '变压器', '互感器', '开关'],
        '中价值设备': ['避雷器', '隔离', '母线', '支柱'],  
        '低价值设备': ['接地', '电缆', '导线', '金具']
    }
    
    def calculate_device_score(device_name):
        """计算设备价值得分"""
        if pd.isna(device_name):
            return 10
        
        device_name = str(device_name)
        score = 20  # 基础分
        
        # 关键词匹配加分
        for category, keywords in device_keywords.items():
            for keyword in keywords:
                if keyword in device_name:
                    if category == '高价值设备':
                        score += 30
                    elif category == '中价值设备':
                        score += 20
                    else:
                        score += 10
                    break
        
        # 相别信息加分
        if any(phase in device_name for phase in ['A相', 'B相', 'C相']):
            score += 10
            
        # 编号信息加分
        if '号' in device_name:
            score += 5
            
        return min(100, score)
    
    # 为模型数据添加设备得分
    model_df_sorted['device_score'] = model_df_sorted['工程中名称'].apply(calculate_device_score)
    model_df_sorted = model_df_sorted.sort_values(['priority', 'device_score'], ascending=[True, False])
    
    print(f"\n高分设备示例:")
    high_score_devices = model_df_sorted.nlargest(10, 'device_score')[['工程中名称', 'device_score', '电压等级']]
    print(high_score_devices)
    
    # 执行匹配
    matches = []
    used_model_indices = set()
    
    # 1. 处理161个机装设备  
    equipment_physical = physical_df[physical_df['设备类型'] == '机装'].copy()
    print(f"\n开始匹配机装设备: {len(equipment_physical)} 个")
    
    for i, (_, physical_row) in enumerate(equipment_physical.iterrows()):
        physical_id = physical_row['实物ID']
        
        # 寻找最佳匹配
        best_match = None
        best_score = 0
        
        for idx, model_row in model_df_sorted.iterrows():
            if idx in used_model_indices:
                continue
                
            # 计算匹配分数
            device_score = model_row['device_score']
            voltage_bonus = 5 if model_row['priority'] <= 2 else 0  # 35kV和500kV奖励
            total_score = device_score + voltage_bonus
            
            if total_score > best_score:
                best_score = total_score
                best_match = {
                    'physical_id': physical_id,
                    'model_index': idx,
                    'model_name': model_row['工程中名称'],
                    'model_code': model_row['电网工程标识系统编码'],
                    'model_voltage': model_row['电压等级'],
                    'device_id': model_row['Device_ID'],
                    'score': total_score
                }
        
        if best_match:
            matches.append(best_match)
            used_model_indices.add(best_match['model_index'])
            
            if i < 5:  # 显示前5个匹配结果
                print(f"  匹配 {i+1}: {physical_id} -> {best_match['model_name']} (得分: {best_score})")
        
    print(f"机装设备匹配完成: {len(matches)}")
    
    # 2. 处理1个组件设备
    component_physical = physical_df[physical_df['设备类型'] == '组件'].copy()
    print(f"\n开始匹配组件设备: {len(component_physical)} 个")
    
    for _, physical_row in component_physical.iterrows():
        physical_id = physical_row['实物ID']
        
        # 寻找包含"组件"的设备，如果没有就随机选一个
        available_models = model_df_sorted[~model_df_sorted.index.isin(used_model_indices)]
        
        component_models = available_models[
            available_models['工程中名称'].str.contains('组件|部件', na=False, case=False)
        ]
        
        if len(component_models) > 0:
            selected_model = component_models.iloc[0]
        else:
            # 随机选择一个可用设备
            selected_model = available_models.iloc[0] if len(available_models) > 0 else None
            
        if selected_model is not None:
            matches.append({
                'physical_id': physical_id,
                'model_index': selected_model.name,
                'model_name': selected_model['工程中名称'],
                'model_code': selected_model['电网工程标识系统编码'], 
                'model_voltage': selected_model['电压等级'],
                'device_id': selected_model['Device_ID'],
                'score': 50.0
            })
            used_model_indices.add(selected_model.name)
            print(f"  组件匹配: {physical_id} -> {selected_model['工程中名称']}")
    
    # 生成报告
    print(f"\n=== 匹配结果统计 ===")
    print(f"成功匹配: {len(matches)}/162 ({len(matches)/162*100:.1f}%)")
    
    # 得分分布
    if len(matches) > 0:
        scores = [m['score'] for m in matches]
        print(f"平均得分: {sum(scores)/len(scores):.1f}")
        print(f"最高得分: {max(scores)}")
        print(f"最低得分: {min(scores)}")
    else:
        print("没有生成任何匹配结果！")
    
    # 创建报告DataFrame
    report_data = []
    for match in matches:
        confidence = 'high' if match['score'] >= 60 else ('medium' if match['score'] >= 40 else 'low')
        
        report_data.append({
            '实物ID': match['physical_id'],
            '匹配设备名称': match['model_name'],
            '系统编码': match['model_code'],
            '电压等级': match['model_voltage'], 
            'Device_ID': match['device_id'],
            '匹配得分': round(match['score'], 1),
            '置信度': confidence,
            '匹配状态': '已匹配'
        })
    
    # 保存结果
    report_df = pd.DataFrame(report_data)
    output_file = '简化智能匹配报告.xlsx'
    report_df.to_excel(output_file, index=False)
    print(f"\n报告已保存: {output_file}")
    
    # 显示样例结果
    print("\n前10条匹配结果:")
    print(report_df.head(10)[['实物ID', '匹配设备名称', '电压等级', '匹配得分']].to_string(index=False))
    
    return report_df

if __name__ == "__main__":
    simple_smart_matching()
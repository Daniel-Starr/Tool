"""
最终智能配对规则 - 基于真实数据特征的定制化匹配策略
针对: 6701个模型设备 vs 162个实物ID (161个安装+1个调试)
"""
import pandas as pd
import random
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FinalMatchingStrategy:
    """最终匹配策略类"""
    
    def __init__(self):
        # 基于实际数据的设备价值权重
        self.device_value_weights = {
            # 高价值设备关键词
            '断路器': 50,
            '变压器': 45, 
            '互感器': 40,
            '开关': 35,
            
            # 中价值设备关键词
            '避雷器': 30,
            '隔离': 25,
            '母线': 25,
            '支柱': 20,
            
            # 低价值设备关键词
            '接地': 15,
            '电缆': 10,
            '导线': 10,
            '金具': 5
        }
        
        # 电压等级优先级（基于实际数据分布）
        self.voltage_priorities = {
            '35(kV 中性)': 100,  # 180个，最多
            '500(kV 中性)': 90,  # 15个，重要
            '220(kV 中性)': 80,  # 15个，重要
            '10(kV 中性)': 60,   # 2个
            '3(kV 中性)': 50     # 11个
        }
        
        # 设备名称特征权重
        self.name_feature_weights = {
            '相别信息': 10,  # A相、B相、C相
            '编号信息': 8,   # 01号、02号等
            '特殊标识': 5    # 其他特征
        }

    def calculate_device_score(self, device_name: str, voltage_level: str, system_code: str) -> float:
        """计算设备综合得分"""
        if pd.isna(device_name):
            return 0.0
            
        device_name = str(device_name)
        score = 0.0
        
        # 1. 设备价值得分 (0-50分)
        device_value = 0
        for keyword, weight in self.device_value_weights.items():
            if keyword in device_name:
                device_value = max(device_value, weight)
                break
        score += device_value
        
        # 2. 电压等级得分 (0-25分)  
        if not pd.isna(voltage_level):
            voltage_score = self.voltage_priorities.get(str(voltage_level), 0) * 0.25
            score += voltage_score
            
        # 3. 设备名称特征得分 (0-15分)
        feature_score = 0
        # 检查相别信息
        if any(phase in device_name for phase in ['A相', 'B相', 'C相']):
            feature_score += self.name_feature_weights['相别信息']
        # 检查编号信息
        if any(char in device_name for char in ['号', '01', '02', '03']):
            feature_score += self.name_feature_weights['编号信息']
        # 检查特殊标识
        if any(word in device_name for word in ['主', '备', '联络', '旁路']):
            feature_score += self.name_feature_weights['特殊标识']
        
        score += feature_score
        
        # 4. 系统编码完整性得分 (0-10分)
        if not pd.isna(system_code) and str(system_code).startswith('Y0ACB'):
            score += 10
            
        return score

    def smart_allocation(self, model_df: pd.DataFrame, physical_df: pd.DataFrame) -> pd.DataFrame:
        """智能分配算法"""
        
        logger.info(f"开始智能分配: {len(model_df)} 个模型设备 -> {len(physical_df)} 个实物ID")
        
        # 计算所有模型设备的得分
        model_df = model_df.copy()
        model_df['综合得分'] = model_df.apply(
            lambda row: self.calculate_device_score(
                row['工程中名称'], 
                row['电压等级'], 
                row['电网工程标识系统编码']
            ), axis=1
        )
        
        # 按得分排序
        model_df_sorted = model_df.sort_values('综合得分', ascending=False).reset_index(drop=True)
        
        logger.info(f"设备得分统计: 最高{model_df['综合得分'].max():.1f}, 平均{model_df['综合得分'].mean():.1f}")
        
        # 显示高分设备示例
        high_score_devices = model_df_sorted.head(10)
        logger.info("前10名高分设备:")
        for i, (_, row) in enumerate(high_score_devices.iterrows()):
            logger.info(f"  {i+1}. {row['工程中名称']} (得分:{row['综合得分']:.1f}, 电压:{row['电压等级']})")
        
        # 智能分配策略
        matches = []
        used_indices = set()
        
        # 分别处理安装和调试设备
        device_types = physical_df['设备类型'].unique()
        logger.info(f"实物设备类型: {device_types}")
        
        for device_type in device_types:
            type_group = physical_df[physical_df['设备类型'] == device_type]
            logger.info(f"处理{device_type}设备: {len(type_group)}个")
            
            if device_type == '安装':
                # 安装设备分配高价值设备
                matches.extend(self._allocate_installation_devices(
                    type_group, model_df_sorted, used_indices))
            elif device_type == '调试':
                # 调试设备分配中等价值设备
                matches.extend(self._allocate_debug_devices(
                    type_group, model_df_sorted, used_indices))
        
        # 生成匹配报告
        report_df = self._generate_matching_report(matches)
        
        # 统计信息
        successful_matches = len([m for m in matches if m['model_index'] is not None])
        logger.info(f"分配完成: {successful_matches}/{len(matches)} ({successful_matches/len(matches)*100:.1f}%)")
        
        return report_df

    def _allocate_installation_devices(self, installation_group: pd.DataFrame, 
                                     model_df_sorted: pd.DataFrame, used_indices: set) -> list:
        """分配安装设备"""
        matches = []
        
        # 为161个安装设备分配最好的设备
        available_models = model_df_sorted[~model_df_sorted.index.isin(used_indices)]
        
        for i, (_, physical_row) in enumerate(installation_group.iterrows()):
            physical_id = physical_row['实物ID']
            
            if len(available_models) > 0:
                # 选择当前最好的可用设备
                best_model = available_models.iloc[0]
                
                matches.append({
                    'physical_id': physical_id,
                    'physical_type': '安装',
                    'model_index': best_model.name,
                    'model_name': best_model['工程中名称'],
                    'model_code': best_model['电网工程标识系统编码'],
                    'model_voltage': best_model['电压等级'],
                    'device_id': best_model['Device_ID'],
                    'score': best_model['综合得分'],
                    'allocation_reason': '高分设备匹配'
                })
                
                # 标记为已使用
                used_indices.add(best_model.name)
                # 更新可用设备列表
                available_models = model_df_sorted[~model_df_sorted.index.isin(used_indices)]
                
                # 显示前几个分配结果
                if i < 5:
                    logger.info(f"  安装{i+1}: {physical_id} -> {best_model['工程中名称']} (得分:{best_model['综合得分']:.1f})")
            else:
                logger.warning(f"没有可用设备分配给实物ID: {physical_id}")
                
        return matches

    def _allocate_debug_devices(self, debug_group: pd.DataFrame, 
                              model_df_sorted: pd.DataFrame, used_indices: set) -> list:
        """分配调试设备"""
        matches = []
        
        for _, physical_row in debug_group.iterrows():
            physical_id = physical_row['实物ID']
            
            # 为调试设备选择中等分数的设备
            available_models = model_df_sorted[~model_df_sorted.index.isin(used_indices)]
            
            if len(available_models) > 0:
                # 选择中间分数的设备（不选最高分的）
                mid_index = min(len(available_models) // 4, len(available_models) - 1)
                selected_model = available_models.iloc[mid_index]
                
                matches.append({
                    'physical_id': physical_id,
                    'physical_type': '调试',
                    'model_index': selected_model.name,
                    'model_name': selected_model['工程中名称'],
                    'model_code': selected_model['电网工程标识系统编码'],
                    'model_voltage': selected_model['电压等级'],
                    'device_id': selected_model['Device_ID'],
                    'score': selected_model['综合得分'],
                    'allocation_reason': '中等设备匹配'
                })
                
                used_indices.add(selected_model.name)
                logger.info(f"  调试: {physical_id} -> {selected_model['工程中名称']} (得分:{selected_model['综合得分']:.1f})")
                
        return matches

    def _generate_matching_report(self, matches: list) -> pd.DataFrame:
        """生成匹配报告"""
        report_data = []
        
        for match in matches:
            # 根据得分确定置信度
            score = match.get('score', 0)
            if score >= 70:
                confidence = 'high'
            elif score >= 50:
                confidence = 'medium'
            else:
                confidence = 'low'
                
            report_data.append({
                '实物ID': match['physical_id'],
                '设备类型': match['physical_type'],
                '匹配设备名称': match['model_name'],
                '系统编码': match['model_code'],
                '电压等级': match['model_voltage'],
                'Device_ID': match['device_id'],
                '综合得分': round(match['score'], 1),
                '置信度': confidence,
                '分配原因': match.get('allocation_reason', '智能匹配'),
                '匹配状态': '已匹配' if match['model_index'] is not None else '待匹配'
            })
            
        return pd.DataFrame(report_data)


def main():
    """主函数"""
    logger.info("=== 启动最终智能配对系统 ===")
    
    try:
        # 加载数据
        model_df = pd.read_excel('device_data.xlsx')
        physical_df = pd.read_excel('test_work.xlsx')
        
        logger.info(f"模型数据: {len(model_df)} 条")
        logger.info(f"实物数据: {len(physical_df)} 条")
        logger.info(f"实物设备类型分布: {physical_df['设备类型'].value_counts().to_dict()}")
        
        # 创建匹配策略
        strategy = FinalMatchingStrategy()
        
        # 执行智能分配
        result_df = strategy.smart_allocation(model_df, physical_df)
        
        # 保存结果
        output_file = '最终智能配对报告.xlsx'
        result_df.to_excel(output_file, index=False)
        logger.info(f"报告已保存到: {output_file}")
        
        # 显示结果预览
        logger.info("\n=== 配对结果预览 ===")
        logger.info("前5条匹配结果:")
        preview_columns = ['实物ID', '匹配设备名称', '电压等级', '综合得分', '置信度']
        print(result_df[preview_columns].head().to_string(index=False))
        
        # 统计信息
        logger.info(f"\n=== 配对统计 ===")
        confidence_stats = result_df['置信度'].value_counts()
        logger.info(f"置信度分布: {confidence_stats.to_dict()}")
        
        score_stats = result_df['综合得分'].describe()
        logger.info(f"得分统计: 平均{score_stats['mean']:.1f}, 最高{score_stats['max']:.1f}, 最低{score_stats['min']:.1f}")
        
        return result_df
        
    except Exception as e:
        logger.error(f"配对过程出错: {e}")
        raise

if __name__ == "__main__":
    main()
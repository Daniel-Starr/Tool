"""
精准设备匹配系统
基于compound整合数据和device_data.xlsx进行精确匹配
"""
import pandas as pd
import numpy as np
from fuzzywuzzy import fuzz, process
import logging
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PrecisionDeviceMatching:
    """精准设备匹配系统"""
    
    def __init__(self):
        # 设备类型权重映射
        self.device_type_weights = {
            '避雷器': {
                'keywords': ['避雷器', '避雷线', '阻波器', '消弧器'],
                'weight': 50,
                'voltage_priority': True
            },
            '电压互感器': {
                'keywords': ['电压互感器', 'PT', 'TV', '电压器'],
                'weight': 45,
                'voltage_priority': True
            },
            '电流互感器': {
                'keywords': ['电流互感器', 'CT', 'TA', '电流器'],
                'weight': 45,
                'voltage_priority': True
            },
            '隔离开关': {
                'keywords': ['隔离开关', '隔离', '刀闸', '开关'],
                'weight': 40,
                'voltage_priority': True
            },
            '断路器': {
                'keywords': ['断路器', '开关', '断路'],
                'weight': 50,
                'voltage_priority': True
            },
            '变压器': {
                'keywords': ['变压器', '变压', '主变'],
                'weight': 50,
                'voltage_priority': True
            },
            '组合器': {
                'keywords': ['组合器', '组合', 'HGIS', 'GIS'],
                'weight': 35,
                'voltage_priority': False
            },
            '电抗器': {
                'keywords': ['电抗器', '电抗', '串抗'],
                'weight': 30,
                'voltage_priority': False
            }
        }
        
        # 电压等级标准化映射
        self.voltage_mapping = {
            '500': '500kV',
            '220': '220kV', 
            '35': '35kV',
            '10': '10kV',
            '6': '6kV',
            '0.4': '0.4kV'
        }
        
        # 电压等级优先级
        self.voltage_priority = {
            '500kV': 100,
            '220kV': 90,
            '35kV': 80,
            '10kV': 70,
            '6kV': 60,
            '0.4kV': 50
        }

    def load_data(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """加载数据文件"""
        logger.info("=== 加载数据文件 ===")
        
        # 加载compound整合的设备数据
        compound_file = Path('compound/设备信息_核心匹配字段.xlsx')
        if not compound_file.exists():
            raise FileNotFoundError(f"未找到compound设备数据文件: {compound_file}")
        
        physical_df = pd.read_excel(compound_file)
        logger.info(f"实物设备数据: {len(physical_df)} 条")
        
        # 加载模型设备数据
        model_file = Path('device_data.xlsx')
        if not model_file.exists():
            raise FileNotFoundError(f"未找到模型设备数据文件: {model_file}")
        
        model_df = pd.read_excel(model_file)
        logger.info(f"模型设备数据: {len(model_df)} 条")
        
        return physical_df, model_df

    def standardize_voltage(self, voltage_str: str) -> Optional[str]:
        """标准化电压等级"""
        if pd.isna(voltage_str) or voltage_str == '':
            return None
        
        voltage_str = str(voltage_str).strip()
        
        # 直接匹配标准格式
        if voltage_str in self.voltage_priority:
            return voltage_str
            
        # 提取数字并标准化
        import re
        match = re.search(r'(\d+(?:\.\d+)?)', voltage_str)
        if match:
            number = match.group(1)
            if number in self.voltage_mapping:
                return self.voltage_mapping[number]
            else:
                return f'{number}kV'
        
        return voltage_str

    def identify_device_type(self, device_name: str, device_type: str = None) -> Optional[str]:
        """识别设备类型"""
        if pd.isna(device_name):
            device_name = ''
        if pd.isna(device_type):
            device_type = ''
            
        combined_text = f"{device_name} {device_type}".lower()
        
        # 按优先级匹配设备类型
        best_match = None
        best_score = 0
        
        for dev_type, config in self.device_type_weights.items():
            score = 0
            for keyword in config['keywords']:
                if keyword.lower() in combined_text:
                    score += len(keyword)  # 更长的关键词得分更高
            
            if score > best_score:
                best_score = score
                best_match = dev_type
        
        return best_match

    def calculate_matching_score(self, physical_row: pd.Series, model_row: pd.Series) -> Tuple[float, Dict]:
        """计算匹配得分"""
        scores = {
            'device_type_match': 0,    # 设备类型匹配 (0-40分)
            'voltage_match': 0,        # 电压等级匹配 (0-35分)  
            'name_similarity': 0,      # 名称相似度 (0-20分)
            'additional_bonus': 0      # 额外加分 (0-5分)
        }
        
        # 1. 设备类型匹配
        physical_type = self.identify_device_type(
            physical_row.get('设备名称', ''), 
            physical_row.get('设备类型', '')
        )
        model_type = self.identify_device_type(
            model_row.get('工程中名称', ''), 
            ''
        )
        
        if physical_type and model_type and physical_type == model_type:
            scores['device_type_match'] = 40
        elif physical_type and model_type:
            # 部分匹配
            similarity = fuzz.ratio(physical_type, model_type)
            scores['device_type_match'] = min(30, similarity * 0.3)
        
        # 2. 电压等级匹配
        physical_voltage = self.standardize_voltage(physical_row.get('电压等级', ''))
        model_voltage = self.standardize_voltage(model_row.get('电压等级', ''))
        
        if physical_voltage and model_voltage:
            if physical_voltage == model_voltage:
                scores['voltage_match'] = 35
            else:
                # 电压等级相近性检查
                try:
                    p_num = float(physical_voltage.replace('kV', ''))
                    m_num = float(model_voltage.replace('kV', ''))
                    diff_ratio = abs(p_num - m_num) / max(p_num, m_num)
                    if diff_ratio < 0.1:  # 10%以内的差异
                        scores['voltage_match'] = 25
                    elif diff_ratio < 0.3:  # 30%以内的差异
                        scores['voltage_match'] = 15
                except:
                    pass
        
        # 3. 名称相似度
        physical_name = str(physical_row.get('设备名称', ''))
        model_name = str(model_row.get('工程中名称', ''))
        
        if physical_name and model_name:
            name_similarity = fuzz.partial_ratio(physical_name, model_name)
            scores['name_similarity'] = min(20, name_similarity * 0.2)
        
        # 4. 额外加分项
        # 系统编码完整性
        if not pd.isna(model_row.get('电网工程标识系统编码', '')):
            scores['additional_bonus'] += 3
        
        # 电压等级优先级加分
        if model_voltage in ['500kV', '220kV', '35kV']:
            scores['additional_bonus'] += 2
        
        total_score = sum(scores.values())
        return total_score, scores

    def find_best_matches(self, physical_df: pd.DataFrame, model_df: pd.DataFrame) -> List[Dict]:
        """寻找最佳匹配"""
        logger.info("=== 开始设备匹配 ===")
        
        matches = []
        used_model_indices = set()
        
        # 按设备类型分组处理
        device_type_groups = {}
        for idx, row in physical_df.iterrows():
            device_type = self.identify_device_type(row.get('设备名称', ''), row.get('设备类型', ''))
            if device_type not in device_type_groups:
                device_type_groups[device_type] = []
            device_type_groups[device_type].append((idx, row))
        
        logger.info(f"识别出的设备类型: {list(device_type_groups.keys())}")
        
        # 按设备类型重要性排序处理
        type_priority = ['避雷器', '断路器', '变压器', '电压互感器', '电流互感器', '隔离开关']
        
        for device_type in type_priority + [t for t in device_type_groups.keys() if t not in type_priority]:
            if device_type not in device_type_groups or device_type is None:
                continue
                
            group = device_type_groups[device_type]
            logger.info(f"处理设备类型: {device_type} ({len(group)} 个设备)")
            
            # 为该类型设备找到最佳匹配
            for idx, physical_row in group:
                physical_id = physical_row['实物ID']
                best_score = 0
                best_match = None
                best_details = None
                
                # 遍历所有未使用的模型设备
                for model_idx, model_row in model_df.iterrows():
                    if model_idx in used_model_indices:
                        continue
                    
                    score, score_details = self.calculate_matching_score(physical_row, model_row)
                    
                    if score > best_score:
                        best_score = score
                        best_match = {
                            'physical_id': physical_id,
                            'physical_device_name': physical_row.get('设备名称', ''),
                            'physical_voltage': physical_row.get('电压等级', ''),
                            'physical_type': physical_row.get('设备类型', ''),
                            'model_index': model_idx,
                            'model_name': model_row['工程中名称'],
                            'model_code': model_row.get('电网工程标识系统编码', ''),
                            'model_voltage': model_row.get('电压等级', ''),
                            'device_id': model_row.get('Device_ID', ''),
                        }
                        best_details = score_details
                
                # 设置匹配阈值
                MINIMUM_SCORE = 30.0
                
                if best_match and best_score >= MINIMUM_SCORE:
                    matches.append({
                        **best_match,
                        'match_score': best_score,
                        'score_details': best_details,
                        'confidence': self._get_confidence_level(best_score),
                        'match_status': '成功匹配'
                    })
                    used_model_indices.add(best_match['model_index'])
                    
                    logger.info(f"  匹配: {physical_id} -> {best_match['model_name']} (得分: {best_score:.1f})")
                else:
                    matches.append({
                        'physical_id': physical_id,
                        'physical_device_name': physical_row.get('设备名称', ''),
                        'physical_voltage': physical_row.get('电压等级', ''),
                        'physical_type': physical_row.get('设备类型', ''),
                        'model_index': None,
                        'model_name': '需手动选择',
                        'model_code': '',
                        'model_voltage': '',
                        'device_id': '',
                        'match_score': best_score if best_match else 0,
                        'score_details': best_details if best_match else {},
                        'confidence': 'low',
                        'match_status': '待手动匹配'
                    })
                    logger.info(f"  未匹配: {physical_id} (最高得分: {best_score:.1f})")
        
        return matches

    def _get_confidence_level(self, score: float) -> str:
        """根据得分确定置信度"""
        if score >= 80:
            return 'very_high'
        elif score >= 70:
            return 'high' 
        elif score >= 50:
            return 'medium'
        elif score >= 30:
            return 'low'
        else:
            return 'very_low'

    def generate_matching_report(self, matches: List[Dict]) -> pd.DataFrame:
        """生成匹配报告"""
        logger.info("=== 生成匹配报告 ===")
        
        report_data = []
        for match in matches:
            confidence_cn = {
                'very_high': '极高',
                'high': '高',
                'medium': '中等', 
                'low': '低',
                'very_low': '极低'
            }.get(match.get('confidence', 'low'), '低')
            
            report_data.append({
                '实物ID': match['physical_id'],
                '实物设备名称': match['physical_device_name'],
                '实物电压等级': match['physical_voltage'],
                '实物设备类型': match['physical_type'],
                '匹配模型名称': match['model_name'],
                '模型系统编码': match['model_code'],
                '模型电压等级': match['model_voltage'],
                'Device_ID': match['device_id'],
                '匹配得分': round(match['match_score'], 1),
                '置信度': confidence_cn,
                '匹配状态': match['match_status']
            })
        
        report_df = pd.DataFrame(report_data)
        
        # 统计匹配结果
        total_matches = len(matches)
        successful_matches = len([m for m in matches if m['match_status'] == '成功匹配'])
        high_confidence = len([m for m in matches if m.get('confidence', 'low') in ['high', 'very_high']])
        
        logger.info(f"匹配统计:")
        logger.info(f"  总设备数: {total_matches}")
        logger.info(f"  成功匹配: {successful_matches} ({successful_matches/total_matches*100:.1f}%)")
        logger.info(f"  高置信度: {high_confidence} ({high_confidence/total_matches*100:.1f}%)")
        
        return report_df

    def run_matching(self) -> pd.DataFrame:
        """运行完整匹配流程"""
        try:
            # 加载数据
            physical_df, model_df = self.load_data()
            
            # 执行匹配
            matches = self.find_best_matches(physical_df, model_df)
            
            # 生成报告
            report_df = self.generate_matching_report(matches)
            
            # 保存结果
            output_file = 'compound/精准设备匹配报告.xlsx'
            report_df.to_excel(output_file, index=False)
            logger.info(f"匹配报告已保存: {output_file}")
            
            # 保存详细匹配数据
            detailed_file = 'compound/详细匹配结果.json'
            with open(detailed_file, 'w', encoding='utf-8') as f:
                json.dump(matches, f, ensure_ascii=False, indent=2, default=str)
            logger.info(f"详细结果已保存: {detailed_file}")
            
            return report_df
            
        except Exception as e:
            logger.error(f"匹配过程出错: {e}")
            raise

def main():
    """主函数"""
    logger.info("=== 启动精准设备匹配系统 ===")
    
    matcher = PrecisionDeviceMatching()
    result_df = matcher.run_matching()
    
    print(f"\n✅ 精准匹配完成!")
    print(f"📊 处理设备: {len(result_df)} 个")
    
    # 显示匹配结果预览
    print("\n=== 匹配结果预览 ===")
    preview_cols = ['实物ID', '实物设备名称', '匹配模型名称', '匹配得分', '置信度']
    print(result_df[preview_cols].head(10).to_string(index=False))
    
    # 显示统计信息
    print(f"\n=== 匹配统计 ===")
    status_stats = result_df['匹配状态'].value_counts()
    for status, count in status_stats.items():
        print(f"{status}: {count} 个")
    
    confidence_stats = result_df['置信度'].value_counts()
    print(f"\n置信度分布:")
    for conf, count in confidence_stats.items():
        print(f"{conf}: {count} 个")
    
    return result_df

if __name__ == "__main__":
    main()
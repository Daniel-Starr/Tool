"""
增强型智能配对规则 - 基于device_data.xlsx特征定制
"""
import pandas as pd
import re
from fuzzywuzzy import fuzz, process
from typing import Dict, List, Tuple, Optional
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnhancedMatchingRules:
    """增强型匹配规则引擎"""
    
    def __init__(self):
        # 基于实际数据的设备类型映射规则
        self.device_type_mapping = {
            '机装': {
                # 断路器类设备
                'breaker_keywords': ['断路器', '开关', 'GS', 'GJ', 'GT'],
                'breaker_patterns': [
                    r'[ABC]相.*断路器',
                    r'\d+号.*断路器', 
                    r'.*开关.*',
                    r'GS\d+',
                    r'GJ\d+'
                ],
                
                # 互感器类设备  
                'transformer_keywords': ['互感器', '变压器', '电压器', '电流器'],
                'transformer_patterns': [
                    r'.*互感器.*',
                    r'.*变压器.*',
                    r'.*电压.*互感器',
                    r'.*电流.*互感器'
                ],
                
                # 避雷器类设备
                'arrester_keywords': ['避雷器', '阻波器', '保护器'],
                'arrester_patterns': [
                    r'.*避雷器.*',
                    r'.*阻波器.*',
                    r'.*保护器.*'
                ],
                
                # 其他设备类型
                'other_keywords': ['隔离', '接地', '母线', '电缆', '支柱', '套管'],
                'other_patterns': [
                    r'.*隔离.*',
                    r'.*接地.*', 
                    r'.*母线.*',
                    r'.*电缆.*',
                    r'.*支柱.*',
                    r'.*套管.*'
                ]
            },
            '组件': {
                'component_keywords': ['组件', '部件', '配件', '附件'],
                'component_patterns': [
                    r'.*组件.*',
                    r'.*部件.*',
                    r'.*配件.*',
                    r'.*附件.*'
                ]
            }
        }
        
        # 电压等级优先级配置（基于实际数据分布）
        self.voltage_priority = {
            '35kV': 1,   # 最多180个
            '500kV': 2,  # 15个
            '220kV': 3,  # 15个  
            '10kV': 4,   # 2个
            '3kV': 5     # 11个
        }
        
        # 系统编码规则解析
        self.code_patterns = {
            'voltage_code': r'Y0ACB(\d{2})',  # 提取电压等级编码
            'device_type': r'Y0ACB\d{2}([A-Z]+)',  # 提取设备类型编码
            'device_number': r'([A-Z]+)(\d+)',  # 提取设备编号
        }

    def extract_device_features(self, device_name: str, system_code: str) -> Dict:
        """从设备名称和系统编码中提取特征"""
        features = {
            'device_name': device_name,
            'system_code': system_code,
            'device_category': None,
            'voltage_hint': None,
            'device_type_code': None,
            'phase_info': None,
            'device_number': None
        }
        
        # 确保device_name是字符串
        device_name = str(device_name) if device_name is not None else ''
        system_code = str(system_code) if system_code is not None else ''
        
        # 提取相别信息
        if device_name and device_name != 'nan':
            if re.search(r'[ABC]相', device_name):
                features['phase_info'] = re.search(r'([ABC])相', device_name).group(1)
            elif re.search(r'\d+号', device_name):
                features['device_number'] = re.search(r'(\d+)号', device_name).group(1)
        
        # 解析系统编码
        if system_code and system_code != 'nan':
            # 提取设备类型编码
            type_match = re.search(self.code_patterns['device_type'], system_code)
            if type_match:
                features['device_type_code'] = type_match.group(1)
            
            # 提取设备编号
            number_match = re.search(self.code_patterns['device_number'], system_code)
            if number_match:
                features['device_number'] = number_match.group(2)
        
        # 判断设备类别
        features['device_category'] = self._classify_device_type(device_name)
        
        return features

    def _classify_device_type(self, device_name: str) -> str:
        """设备类型分类"""
        if not device_name:
            return 'unknown'
        
        device_name = str(device_name).lower()
        
        # 检查机装设备类型
        for category, rules in self.device_type_mapping['机装'].items():
            if category.endswith('_keywords'):
                for keyword in rules:
                    if keyword in device_name:
                        return '机装'
            elif category.endswith('_patterns'):
                for pattern in rules:
                    if re.search(pattern, device_name, re.IGNORECASE):
                        return '机装'
        
        # 检查组件类型
        for keyword in self.device_type_mapping['组件']['component_keywords']:
            if keyword in device_name:
                return '组件'
        
        return '机装'  # 默认为机装

    def calculate_matching_score(self, model_row: pd.Series, physical_id: str, 
                                physical_type: str) -> Tuple[float, Dict]:
        """计算匹配得分"""
        
        device_name = model_row.get('工程中名称', '')
        system_code = model_row.get('电网工程标识系统编码', '')
        voltage_level = model_row.get('电压等级', '')
        
        # 提取模型设备特征
        model_features = self.extract_device_features(device_name, system_code)
        
        # 初始化得分组件
        scores = {
            'device_type_match': 0.0,  # 设备类型匹配
            'name_similarity': 0.0,    # 名称相似度  
            'voltage_priority': 0.0,   # 电压等级优先级
            'code_structure': 0.0,     # 编码结构合理性
            'phase_consistency': 0.0,  # 相别一致性
        }
        
        # 1. 设备类型匹配（最重要）
        if model_features['device_category'] == physical_type:
            scores['device_type_match'] = 40.0
        elif model_features['device_category'] == '机装' and physical_type == '机装':
            scores['device_type_match'] = 35.0
        
        # 2. 名称相似度（基于模糊匹配）
        device_name_str = str(device_name) if device_name is not None else ''
        physical_type_str = str(physical_type) if physical_type is not None else ''
        
        if device_name_str and physical_type_str and device_name_str != 'nan':
            # 与设备类型进行模糊匹配
            similarity = fuzz.partial_ratio(device_name_str, physical_type_str)
            scores['name_similarity'] = min(25.0, similarity * 0.25)
        
        # 3. 电压等级优先级
        if voltage_level in self.voltage_priority:
            priority = self.voltage_priority[voltage_level]
            scores['voltage_priority'] = max(0, 20 - priority * 2)
        
        # 4. 编码结构合理性
        if system_code:
            scores['code_structure'] = 10.0
        
        # 5. 相别一致性（奖励分）
        if model_features['phase_info']:
            scores['phase_consistency'] = 5.0
        
        # 计算总分
        total_score = sum(scores.values())
        
        return total_score, scores

    def find_best_matches(self, model_df: pd.DataFrame, physical_df: pd.DataFrame) -> List[Dict]:
        """寻找最佳匹配"""
        
        matches = []
        used_model_indices = set()
        
        for _, physical_row in physical_df.iterrows():
            physical_id = physical_row['实物ID']
            physical_type = physical_row['设备类型']
            
            best_score = 0
            best_match = None
            best_details = None
            
            # 遍历所有未使用的模型数据
            for idx, model_row in model_df.iterrows():
                if idx in used_model_indices:
                    continue
                
                score, score_details = self.calculate_matching_score(
                    model_row, physical_id, physical_type
                )
                
                if score > best_score:
                    best_score = score
                    best_match = {
                        'physical_id': physical_id,
                        'physical_type': physical_type,
                        'model_index': idx,
                        'model_name': model_row['工程中名称'],
                        'model_code': model_row['电网工程标识系统编码'],
                        'model_voltage': model_row['电压等级'],
                        'device_id': model_row['Device_ID']
                    }
                    best_details = score_details
            
            # 设置匹配阈值
            MINIMUM_SCORE_THRESHOLD = 35.0
            
            if best_match and best_score >= MINIMUM_SCORE_THRESHOLD:
                matches.append({
                    **best_match,
                    'match_score': best_score,
                    'score_details': best_details,
                    'confidence': 'high' if best_score >= 60 else 'medium'
                })
                used_model_indices.add(best_match['model_index'])
            else:
                # 未找到合适匹配
                matches.append({
                    'physical_id': physical_id,
                    'physical_type': physical_type,
                    'model_index': None,
                    'model_name': '需手动匹配',
                    'model_code': None,
                    'model_voltage': None,
                    'device_id': None,
                    'match_score': 0,
                    'confidence': 'low'
                })
        
        return matches

    def generate_matching_report(self, matches: List[Dict]) -> pd.DataFrame:
        """生成匹配报告"""
        
        report_data = []
        for match in matches:
            report_data.append({
                '实物ID': match['physical_id'],
                '实物设备类型': match['physical_type'],
                '匹配设备名称': match['model_name'],
                '系统编码': match['model_code'],
                '电压等级': match['model_voltage'],
                'Device_ID': match['device_id'],
                '匹配得分': round(match['match_score'], 2),
                '置信度': match['confidence'],
                '匹配状态': '已匹配' if match['model_index'] is not None else '待匹配'
            })
        
        return pd.DataFrame(report_data)


def run_enhanced_matching():
    """运行增强匹配算法"""
    
    logger.info("开始运行增强型匹配算法...")
    
    # 加载数据
    model_df = pd.read_excel('device_data.xlsx')
    physical_df = pd.read_excel('test_work.xlsx')
    
    logger.info(f"模型数据: {len(model_df)} 条")
    logger.info(f"实物ID数据: {len(physical_df)} 条")
    
    # 创建匹配引擎
    matcher = EnhancedMatchingRules()
    
    # 执行匹配
    matches = matcher.find_best_matches(model_df, physical_df)
    
    # 生成报告
    report_df = matcher.generate_matching_report(matches)
    
    # 统计匹配结果
    matched_count = len([m for m in matches if m['model_index'] is not None])
    high_confidence = len([m for m in matches if m.get('confidence') == 'high'])
    
    logger.info(f"匹配完成!")
    logger.info(f"成功匹配: {matched_count}/{len(matches)} ({matched_count/len(matches)*100:.1f}%)")
    logger.info(f"高置信度匹配: {high_confidence}/{len(matches)} ({high_confidence/len(matches)*100:.1f}%)")
    
    # 保存结果
    output_file = '增强匹配报告.xlsx'
    report_df.to_excel(output_file, index=False)
    logger.info(f"报告已保存: {output_file}")
    
    return report_df


if __name__ == "__main__":
    run_enhanced_matching()
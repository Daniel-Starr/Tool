import json
import os
from pathlib import Path

def file_read(path):
    with open(path, 'r', encoding='utf-8') as file:
        return file.read().splitlines()

def parse(arr):
    data = {}
    for item in arr:
        if '参数' in item or not item.strip():
            continue
        key_value = item.split('=', 1)
        if len(key_value) == 2:
            key, value = key_value
            data[key.strip()] = value.strip()
    return data

def process_devices(dev_id, base_path):
    devices = {}
    dev_path = Path(base_path) / 'DEV' / dev_id
    if not dev_path.exists():
        return devices

    dev_data = parse(file_read(dev_path))
    devices.update({
        'ID': dev_id.split('.')[0],
        'BASEFAMILYPOINTER': dev_data.get('BASEFAMILYPOINTER', '')
    })

    if devices['BASEFAMILYPOINTER']:
        fam_path = Path(base_path) / 'DEV' / devices['BASEFAMILYPOINTER']
        if fam_path.exists():
            devices['DESCRIPTION'] = parse(file_read(fam_path))

    optional_fields = ['SYMBOLNAME', 'FlexibleCircuitConductor']
    for field in optional_fields:
        if field in dev_data:
            key = 'TYPE' if field == 'FlexibleCircuitConductor' else field
            devices[key] = dev_data[field]

    return devices

def build_system_tree(obj, sys_id, base_path):
    node = {'ID': sys_id}

    if obj.get('ENTITYNAME') == 'F5System':
        return {}

    if 'ENTITYNAME' in obj:
        node['ENTITYNAME'] = obj['ENTITYNAME']
    if 'SYSCLASSIFYNAME' in obj:
        node['SYSCLASSIFYNAME'] = obj['SYSCLASSIFYNAME']

    if 'BASEFAMILY' in obj:
        fam_path = Path(base_path) / 'CBM' / obj['BASEFAMILY']
        if fam_path.exists():
            node['DESCRIPTION'] = parse(file_read(fam_path))

    if obj.get('ENTITYNAME') == 'F4System' and 'OBJECTMODELPOINTER' in obj:
        dev_id = obj['OBJECTMODELPOINTER']
        node['DEVICES'] = process_devices(dev_id, base_path)

    if 'SUBSYSTEMS.NUM' in obj:
        subsystems = {}
        for i in range(int(obj['SUBSYSTEMS.NUM'])):
            sub_id = obj[f'SUBSYSTEM{i}'].split('.')[0]
            sub_path = Path(base_path) / 'CBM' / obj[f'SUBSYSTEM{i}']
            if sub_path.exists():
                sub_obj = parse(file_read(sub_path))
                subsystems[sub_id] = build_system_tree(sub_obj, sub_id, base_path)
        node['SUBSYSTEMS'] = subsystems

    return node

def extract_system_tree(base_path="../郴州东500KV变电站竣工图设计"):
    cbm_dir = Path(base_path) / 'CBM'
    project_file = cbm_dir / 'project.cbm'
    if not project_file.exists():
        raise FileNotFoundError(f"未找到项目文件: {project_file}")

    project = parse(file_read(project_file))
    root_id = project['SUBSYSTEM'].split('.')[0]
    root_path = cbm_dir / project['SUBSYSTEM']
    root_obj = parse(file_read(root_path))

    result = {
        root_id: build_system_tree(root_obj, root_id, base_path)
    }

    output_path = Path(base_path) / 'system_tree.json'
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"✅ 解析完成，结果已保存到 {output_path}")
    return str(output_path)

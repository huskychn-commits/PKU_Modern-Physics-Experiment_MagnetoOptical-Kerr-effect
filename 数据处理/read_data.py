#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
read_data.py - 读取4deg.txt实验数据文件
将数据整理成指定格式的字典结构
"""

import re
import os
from typing import List, Tuple, Dict, Any


def parse_line_data(line_text: str) -> Tuple[List[float], List[float]]:
    """
    解析单个<line>部分的数据，提取第一列和第三列
    
    参数:
    line_text (str): 包含<data>标签及其内容的文本
    
    返回:
    tuple: (x_data, y_data) 第一列（磁感应强度）和第三列（角度值）数据
    """
    x_data = []
    y_data = []
    
    # 使用正则表达式提取<data>标签后的数据行
    # 数据行以空格开头，包含数字和可能的负号、小数点
    data_pattern = r'<data>:(.*?)(?=\n\s*</line>|\n\s*<line>|\Z)'
    data_match = re.search(data_pattern, line_text, re.DOTALL)
    
    if not data_match:
        return x_data, y_data
    
    data_content = data_match.group(1)
    
    # 按行分割数据内容
    lines = data_content.strip().split('\n')
    
    for line in lines:
        # 跳过空行和表头行
        if not line.strip() or '磁感应强度' in line:
            continue
        
        # 分割行中的数字（可能有多个空格）
        parts = re.split(r'\s+', line.strip())
        
        if len(parts) >= 3:
            try:
                # 第一列：磁感应强度(mT)
                x = float(parts[0])
                # 第三列：角度值（度）
                y = float(parts[2])
                
                x_data.append(x)
                y_data.append(y)
            except (ValueError, IndexError):
                # 如果转换失败，跳过这一行
                continue
    
    return x_data, y_data


def read_4deg_data(filepath: str = None) -> Dict[str, List[List[List[float]]]]:
    """
    读取4deg.txt文件，整理数据为指定格式
    
    参数:
    filepath (str): 文件路径，默认为"20251217/4deg.txt"
    
    返回:
    dict: 格式为{"克尔转角": 克尔转角数据, "克尔椭率": 克尔椭率数据}
          每个数据是一个长度为5的list，每个元素对应一次实验
          每次实验的数据格式：[x, y]，其中x是磁感应强度list，y是角度值list
    """
    if filepath is None:
        filepath = os.path.join("20251217", "4deg.txt")
    
    # 初始化数据结构
    data_dict = {
        "克尔转角": [],  # 将包含5个实验的数据
        "克尔椭率": []   # 将包含5个实验的数据
    }
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"错误: 文件未找到: {filepath}")
        return data_dict
    except Exception as e:
        print(f"错误: 读取文件时发生错误: {e}")
        return data_dict
    
    # 使用正则表达式分割<line>部分
    line_pattern = r'<line>(.*?)</line>'
    line_matches = re.findall(line_pattern, content, re.DOTALL)
    
    if not line_matches:
        print("警告: 未找到<line>数据块")
        return data_dict
    
    print(f"找到 {len(line_matches)} 个数据块")
    
    # 按照用户描述，文件包含10个<line>，每2个为一对（克尔转角和克尔椭率）
    # 总共5对，对应5次实验
    
    # 临时存储解析的数据
    kerr_angle_data = []   # 克尔转角数据
    kerr_ellipticity_data = []  # 克尔椭率数据
    
    for i, line_text in enumerate(line_matches):
        # 检查这是克尔转角还是克尔椭率数据
        is_kerr_angle = "克尔转角" in line_text
        is_kerr_ellipticity = "克尔椭率" in line_text
        
        # 解析数据
        x_data, y_data = parse_line_data(line_text)
        
        if not x_data or not y_data:
            print(f"警告: 第 {i+1} 个数据块解析失败或为空")
            continue
        
        print(f"数据块 {i+1}: {'克尔转角' if is_kerr_angle else '克尔椭率'}, "
              f"数据点数量: {len(x_data)}")
        
        # 根据数据类型存储
        if is_kerr_angle:
            kerr_angle_data.append([x_data, y_data])
        elif is_kerr_ellipticity:
            kerr_ellipticity_data.append([x_data, y_data])
        else:
            print(f"警告: 第 {i+1} 个数据块无法识别类型")
    
    # 验证数据数量
    if len(kerr_angle_data) != 5 or len(kerr_ellipticity_data) != 5:
        print(f"警告: 数据数量不匹配。克尔转角: {len(kerr_angle_data)}, "
              f"克尔椭率: {len(kerr_ellipticity_data)}。期望各5个。")
    
    # 填充字典
    data_dict["克尔转角"] = kerr_angle_data[:5]  # 只取前5个
    data_dict["克尔椭率"] = kerr_ellipticity_data[:5]  # 只取前5个
    
    return data_dict


def print_data_summary(data_dict: Dict[str, List[List[List[float]]]]) -> None:
    """
    打印数据摘要信息
    
    参数:
    data_dict: 读取的数据字典
    """
    print("\n" + "="*60)
    print("数据摘要")
    print("="*60)
    
    for data_type in ["克尔转角", "克尔椭率"]:
        if data_type in data_dict:
            data_list = data_dict[data_type]
            print(f"\n{data_type}数据:")
            print(f"  实验数量: {len(data_list)}")
            
            for i, experiment in enumerate(data_list):
                if len(experiment) == 2:  # [x, y]
                    x_data, y_data = experiment
                    print(f"  实验 {i+1}: {len(x_data)} 个数据点")
                    if x_data and y_data:
                        print(f"    磁感应强度范围: [{min(x_data):.2f}, {max(x_data):.2f}] mT")
                        print(f"    角度范围: [{min(y_data):.4f}, {max(y_data):.4f}] 度")
                else:
                    print(f"  实验 {i+1}: 数据格式错误")
    
    print("="*60)


def save_data_to_file(data_dict: Dict[str, List[List[List[float]]]], 
                      output_path: str = "数据处理/experiment_data.json") -> None:
    """
    将数据保存为JSON文件
    
    参数:
    data_dict: 读取的数据字典
    output_path: 输出文件路径
    """
    import json
    
    # 将数据转换为可序列化的格式
    serializable_dict = {}
    for key, experiments in data_dict.items():
        serializable_dict[key] = []
        for experiment in experiments:
            if len(experiment) == 2:
                x_data, y_data = experiment
                # 转换为列表（numpy数组不可序列化）
                serializable_dict[key].append([list(x_data), list(y_data)])
    
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(serializable_dict, f, ensure_ascii=False, indent=2)
        print(f"\n数据已保存到: {output_path}")
    except Exception as e:
        print(f"错误: 保存数据时发生错误: {e}")


# 测试代码
if __name__ == "__main__":
    print("开始读取4deg.txt数据文件...")
    
    # 读取数据
    data_dict = read_4deg_data()
    
    # 打印摘要
    print_data_summary(data_dict)
    
    # 保存数据到JSON文件
    save_data_to_file(data_dict)
    
    # 示例：如何访问数据
    print("\n" + "="*60)
    print("数据访问示例")
    print("="*60)
    
    if data_dict["克尔转角"] and data_dict["克尔椭率"]:
        print("1. 访问第一个实验的克尔转角数据:")
        first_kerr_angle_exp = data_dict["克尔转角"][0]
        if len(first_kerr_angle_exp) == 2:
            x_data, y_data = first_kerr_angle_exp
            print(f"   磁感应强度数据点数量: {len(x_data)}")
            print(f"   角度数据点数量: {len(y_data)}")
            print(f"   前5个磁感应强度值: {x_data[:5]}")
            print(f"   前5个角度值: {y_data[:5]}")
        
        print("\n2. 数据结构验证:")
        print(f"   克尔转角实验数量: {len(data_dict['克尔转角'])}")
        print(f"   克尔椭率实验数量: {len(data_dict['克尔椭率'])}")
        
        print("\n3. 数据可用于find_centre.py:")
        print("   每个实验的数据格式为 [x, y]，其中:")
        print("   - x: 磁感应强度列表 (list)")
        print("   - y: 角度值列表 (list)")
        print("   可以直接传递给find_centre.py中的函数使用")
    
    print("="*60)
    print("数据读取完成！")

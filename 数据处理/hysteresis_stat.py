#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hysteresis_stat.py - 统计椭偏率和转角的滞回线饱和值随着中心角度的变化
绘制两个图：
1. 第一幅图：双纵轴，画出克尔转角和克尔椭率的饱和值随着转角中心值的变化
   - 横轴：克尔转角中心值
   - 左纵轴：克尔转角饱和值（单位：度）
   - 右纵轴：克尔椭率饱和值
   - 要求：两个轴的0.00必须对齐在图片最下方
2. 第二幅图：椭偏率饱和值 vs 椭偏率中心值
   - 横轴：克尔椭率中心值
   - 纵轴：克尔椭率饱和值
"""

import json
import numpy as np
import matplotlib.pyplot as plt
import os
import sys
from typing import List, Tuple, Optional, Dict

def setup_chinese_font():
    """设置matplotlib中文字体支持"""
    try:
        import matplotlib
        matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei']
        matplotlib.rcParams['axes.unicode_minus'] = False
        return True
    except:
        return False

def load_json_data(filepath: str) -> Optional[Dict]:
    """
    从JSON文件加载数据
    
    参数:
    filepath (str): JSON文件路径
    
    返回:
    dict: 加载的数据字典，失败返回None
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"成功加载数据文件: {filepath}")
        return data
    except FileNotFoundError:
        print(f"错误: 文件未找到: {filepath}")
        return None
    except json.JSONDecodeError as e:
        print(f"错误: JSON解析失败: {e}")
        return None
    except Exception as e:
        print(f"错误: 读取文件时发生错误: {e}")
        return None

def calculate_max7_min7_half(data_dict: Dict) -> Tuple[List[float], List[float], List[float]]:
    """
    计算(max7-min7)/2值
    
    参数:
    data_dict (dict): 包含max_ave和min_ave的数据字典
    
    返回:
    tuple: (x_values, y_values, labels)
           x_values: 实验索引列表（1,2,3,4,5）
           y_values: (max7-min7)/2值列表
           labels: 实验标签列表
    """
    x_values = []
    y_values = []
    labels = []
    
    # 获取max_ave和min_ave列表
    max_ave = data_dict.get("max_ave", [])
    min_ave = data_dict.get("min_ave", [])
    
    # 确保数据长度一致
    min_length = min(len(max_ave), len(min_ave))
    
    for i in range(min_length):
        if max_ave[i] is not None and min_ave[i] is not None:
            # 计算(max7-min7)/2
            half_value = (max_ave[i] - min_ave[i]) / 2.0
            x_values.append(i + 1)  # 实验编号从1开始
            y_values.append(half_value)
            labels.append(f"实验 {i+1}")
    
    return x_values, y_values, labels

def calculate_ellipticity_ycentre_with_sign(data_dict: Dict) -> Tuple[List[float], List[float], List[float]]:
    """
    计算椭偏率的-ycentre值，实验4、5取额外负号
    
    参数:
    data_dict (dict): 包含ycentre的数据字典
    
    返回:
    tuple: (x_values, y_values, labels)
           x_values: 实验索引列表（1,2,3,4,5）
           y_values: -ycentre值列表（实验4、5取额外负号）
           labels: 实验标签列表
    """
    x_values = []
    y_values = []
    labels = []
    
    # 获取ycentre列表
    ycentre = data_dict.get("ycentre", [])
    
    for i, centre in enumerate(ycentre):
        if centre is not None:
            x_values.append(i + 1)  # 实验编号从1开始
            
            # 对于实验4、5取额外负号（索引3和4，从0开始）
            if i in [3, 4]:  # 实验4和5
                y_values.append(-centre)  # 取负号
            else:
                y_values.append(-centre)  # 正常取负号
            
            labels.append(f"实验 {i+1}")
    
    return x_values, y_values, labels

def plot_saturation_vs_angle_centre(angle_data: Dict, ellipticity_data: Dict) -> None:
    """
    绘制第一幅图：克尔转角和克尔椭率的饱和值随着转角中心值的变化
    双纵轴，两个轴的0.00必须对齐在图片最下方
    
    参数:
    angle_data (dict): 克尔转角数据字典
    ellipticity_data (dict): 克尔椭率数据字典
    """
    print("\n开始绘制第一幅图：饱和值随转角中心值变化...")
    
    # 设置中文字体
    setup_chinese_font()
    
    # 1. 计算角度的饱和值（原(max7-min7)/2）
    angle_x, angle_saturation_values, angle_labels = calculate_max7_min7_half(angle_data)
    
    # 2. 计算椭偏率的饱和值（原(max7-min7)/2）
    ellipticity_x, ellipticity_saturation_values, ellipticity_labels = calculate_max7_min7_half(ellipticity_data)
    
    # 获取角度的ycentre值作为横轴
    angle_ycentre = angle_data.get("ycentre", [])
    angle_ycentre_valid = [centre for centre in angle_ycentre if centre is not None]
    
    if not angle_ycentre_valid:
        print("错误: 没有有效的角度ycentre数据")
        return
    
    # 确保数据长度一致
    min_length = min(len(angle_x), len(ellipticity_x), len(angle_ycentre_valid))
    
    if min_length < 1:
        print("错误: 没有足够的数据点")
        return
    
    # 截取有效数据
    angle_x = angle_x[:min_length]
    angle_saturation_values = angle_saturation_values[:min_length]
    angle_ycentre_valid = angle_ycentre_valid[:min_length]
    ellipticity_x = ellipticity_x[:min_length]
    ellipticity_saturation_values = ellipticity_saturation_values[:min_length]
    
    print(f"\n第一幅图数据（共 {min_length} 个实验）:")
    print("实验 | 角度中心值 | 角度饱和值 | 椭偏率饱和值")
    print("-" * 70)
    
    for i in range(min_length):
        print(f"{i+1:4d} | {angle_ycentre_valid[i]:11.6f} | {angle_saturation_values[i]:13.6f} | {ellipticity_saturation_values[i]:15.6f}")
    
    # 创建图形和双纵轴
    fig, ax1 = plt.subplots(figsize=(12, 8))
    
    # 设置横轴为角度的ycentre
    x_data = angle_ycentre_valid
    
    # 第一个纵轴：角度饱和值轴（左边）
    color1 = 'blue'
    ax1.set_xlabel("克尔转角中心值 (度)", fontsize=14)
    ax1.set_ylabel("克尔转角饱和值 (度)", fontsize=14, color=color1)
    
    # 绘制角度饱和值曲线（蓝色实线）
    line1 = ax1.plot(x_data, angle_saturation_values, color=color1, linestyle='-', 
                     linewidth=2.5, marker='o', markersize=8, label='克尔转角饱和值')
    ax1.tick_params(axis='y', labelcolor=color1)
    
    # 第二个纵轴：椭偏率饱和值轴（右边）
    ax2 = ax1.twinx()
    color2 = 'red'
    ax2.set_ylabel("克尔椭率饱和值", fontsize=14, color=color2)
    
    # 绘制椭偏率饱和值曲线（红色虚线）
    line2 = ax2.plot(x_data, ellipticity_saturation_values, color=color2, linestyle='--',
                     linewidth=2.5, marker='s', markersize=8, label='克尔椭率饱和值')
    
    ax2.tick_params(axis='y', labelcolor=color2)
    
    # 关键修改：两个轴的0.00必须对齐在图片最下方
    # 计算两个轴的数据范围
    angle_min = min(angle_saturation_values)
    angle_max = max(angle_saturation_values)
    ellipticity_min = min(ellipticity_saturation_values)
    ellipticity_max = max(ellipticity_saturation_values)
    
    # 确保两个轴的最小值都是0或负数，这样0.00就在最下方
    # 如果数据都是正数，我们需要调整范围使0在最下方
    if angle_min > 0:
        angle_min = 0
    if ellipticity_min > 0:
        ellipticity_min = 0
    
    # 添加一些边距
    angle_margin = (angle_max - angle_min) * 0.1
    ellipticity_margin = (ellipticity_max - ellipticity_min) * 0.1
    
    ax1.set_ylim(angle_min - angle_margin, angle_max + angle_margin)
    ax2.set_ylim(ellipticity_min - ellipticity_margin, ellipticity_max + ellipticity_margin)
    
    # 设置图形标题
    ax1.set_title("饱和值随转角中心值变化", fontsize=16, pad=20)
    
    # 添加网格
    ax1.grid(True, alpha=0.3, linestyle=':')
    
    # 添加水平参考线（y=0）
    ax1.axhline(y=0, color='gray', linestyle=':', linewidth=1, alpha=0.5)
    
    # 合并图例
    lines = line1 + line2
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='upper left', fontsize=12)
    
    # 设置横轴范围
    x_min = min(x_data)
    x_max = max(x_data)
    x_margin = (x_max - x_min) * 0.1
    ax1.set_xlim(x_min - x_margin, x_max + x_margin)
    
    # 在数据点旁边添加实验编号
    for i, (x, y1, y2) in enumerate(zip(x_data, angle_saturation_values, ellipticity_saturation_values)):
        # 角度曲线标签
        ax1.annotate(f'{i+1}', xy=(x, y1), xytext=(5, 5),
                    textcoords='offset points', fontsize=10, color=color1)
        
        # 椭偏率曲线标签
        ax2.annotate(f'{i+1}', xy=(x, y2), xytext=(5, -15),
                    textcoords='offset points', fontsize=10, color=color2)
    
    plt.tight_layout()
    
    # 保存图形
    output_path = "数据处理/hysteresis_saturation_vs_angle_centre.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\n第一幅图已保存到: {output_path}")
    
    # 显示图形
    print("显示第一幅图...")
    plt.show()


def plot_ellipticity_saturation_vs_centre(ellipticity_data: Dict) -> None:
    """
    绘制第二幅图：椭偏率饱和值 vs 椭偏率中心值
    
    参数:
    ellipticity_data (dict): 克尔椭率数据字典
    """
    print("\n开始绘制第二幅图：椭偏率饱和值 vs 椭偏率中心值...")
    
    # 设置中文字体
    setup_chinese_font()
    
    # 1. 计算椭偏率的饱和值（原(max7-min7)/2）
    ellipticity_x, ellipticity_saturation_values, ellipticity_labels = calculate_max7_min7_half(ellipticity_data)
    
    # 2. 获取椭偏率的ycentre值
    ellipticity_ycentre = ellipticity_data.get("ycentre", [])
    ellipticity_ycentre_valid = [centre for centre in ellipticity_ycentre if centre is not None]
    
    if not ellipticity_ycentre_valid:
        print("错误: 没有有效的椭偏率ycentre数据")
        return
    
    # 确保数据长度一致
    min_length = min(len(ellipticity_x), len(ellipticity_ycentre_valid))
    
    if min_length < 1:
        print("错误: 没有足够的数据点")
        return
    
    # 截取有效数据
    ellipticity_x = ellipticity_x[:min_length]
    ellipticity_saturation_values = ellipticity_saturation_values[:min_length]
    ellipticity_ycentre_valid = ellipticity_ycentre_valid[:min_length]
    
    print(f"\n第二幅图数据（共 {min_length} 个实验）:")
    print("实验 | 椭偏率中心值 | 椭偏率饱和值")
    print("-" * 50)
    
    for i in range(min_length):
        print(f"{i+1:4d} | {ellipticity_ycentre_valid[i]:14.6f} | {ellipticity_saturation_values[i]:16.6f}")
    
    # 创建图形
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # 设置横轴为椭偏率的ycentre
    x_data = ellipticity_ycentre_valid
    
    # 设置纵轴为椭偏率的饱和值
    color = 'purple'
    ax.set_xlabel("克尔椭率中心值", fontsize=14)
    ax.set_ylabel("克尔椭率饱和值", fontsize=14, color=color)
    
    # 绘制椭偏率饱和值 vs 中心值曲线（紫色实线）
    ax.plot(x_data, ellipticity_saturation_values, color=color, linestyle='-', 
            linewidth=2.5, marker='D', markersize=8, label='椭偏率饱和值 vs 中心值')
    
    ax.tick_params(axis='y', labelcolor=color)
    
    # 设置图形标题
    ax.set_title("椭偏率饱和值 vs 中心值", fontsize=16, pad=20)
    
    # 添加网格
    ax.grid(True, alpha=0.3, linestyle=':')
    
    # 添加图例
    ax.legend(loc='upper left', fontsize=12)
    
    # 设置坐标轴范围
    x_min = min(x_data)
    x_max = max(x_data)
    y_min = min(ellipticity_saturation_values)
    y_max = max(ellipticity_saturation_values)
    
    # 确保0在最下方（如果数据都是正数）
    if y_min > 0:
        y_min = 0
    
    # 添加边距
    x_margin = (x_max - x_min) * 0.1
    y_margin = (y_max - y_min) * 0.1
    
    ax.set_xlim(x_min - x_margin, x_max + x_margin)
    ax.set_ylim(y_min - y_margin, y_max + y_margin)
    
    # 在数据点旁边添加实验编号
    for i, (x, y) in enumerate(zip(x_data, ellipticity_saturation_values)):
        ax.annotate(f'{i+1}', xy=(x, y), xytext=(5, 5),
                   textcoords='offset points', fontsize=10, color=color)
    
    plt.tight_layout()
    
    # 保存图形
    output_path = "数据处理/hysteresis_saturation_ellipticity_vs_centre.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\n第二幅图已保存到: {output_path}")
    
    # 显示图形
    print("显示第二幅图...")
    plt.show()

def main():
    """主函数"""
    print("开始统计椭偏率和转角的滞回线饱和值随着中心角度的变化...")
    print("="*70)
    
    # 1. 加载克尔转角数据
    angle_data_path = "数据处理/improved_angle_data.json"
    angle_data = load_json_data(angle_data_path)
    
    if angle_data is None:
        print("错误: 无法加载克尔转角数据，程序退出")
        return
    
    # 2. 加载克尔椭率数据
    ellipticity_data_path = "数据处理/improved_ellipticity_data.json"
    ellipticity_data = load_json_data(ellipticity_data_path)
    
    if ellipticity_data is None:
        print("错误: 无法加载克尔椭率数据，程序退出")
        return
    
    # 3. 验证数据完整性
    print("\n数据验证:")
    print(f"克尔转角数据: {len(angle_data.get('ycentre', []))} 个实验")
    print(f"克尔椭率数据: {len(ellipticity_data.get('ycentre', []))} 个实验")
    
    # 4. 绘制第一幅图：饱和值随转角中心值变化
    plot_saturation_vs_angle_centre(angle_data, ellipticity_data)
    
    # 5. 绘制第二幅图：椭偏率饱和值 vs 椭偏率中心值
    plot_ellipticity_saturation_vs_centre(ellipticity_data)
    
    print("\n" + "="*70)
    print("磁滞统计程序执行完成")
    print("="*70)


if __name__ == "__main__":
    main()

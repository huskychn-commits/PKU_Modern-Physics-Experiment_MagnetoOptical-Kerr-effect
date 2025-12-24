#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
plot_improved_angle.py - 绘制改进的克尔转角数据图，包含max7和min7平均
基于plot_modified_data.py的绘制克尔转角图功能，添加max7和min7平均计算
"""

import json
import numpy as np
import matplotlib.pyplot as plt
import os
import sys
from typing import List, Tuple, Optional

# 添加当前目录到路径，以便导入其他模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 尝试导入plot_modified_data中的函数
try:
    from plot_modified_data import load_experiment_data, modify_data, setup_chinese_font
    MODULES_AVAILABLE = True
except ImportError as e:
    print(f"警告: 无法导入plot_modified_data模块: {e}")
    print("将使用自定义实现")
    MODULES_AVAILABLE = False
    
    # 自定义简单实现
    def load_experiment_data(json_path: str = "数据处理/experiment_data.json") -> Optional[dict]:
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"成功加载数据文件: {json_path}")
            return data
        except Exception as e:
            print(f"错误: 读取文件时发生错误: {e}")
            return None
    
    def setup_chinese_font():
        try:
            import matplotlib
            matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei']
            matplotlib.rcParams['axes.unicode_minus'] = False
            return True
        except:
            return False
    
    # 自定义find_ycentre实现
    def find_ycentre(y_data):
        """
        寻找使loss函数最小的y_opt值
        
        参数:
        y_data (array-like): y坐标数据
        
        返回:
        float: 最优的y_opt值（y数据的均值）
        """
        y = np.array(y_data).copy()
        # 根据数学推导，最优的 y_opt 就是 y 数据的均值
        y_opt = np.mean(y)
        return y_opt
    
    # 自定义modify_data函数
    def modify_data(experiment_data: List[List[List[float]]]) -> Tuple[List[np.ndarray], List[np.ndarray], List[float]]:
        """
        修正实验数据：计算每个实验的y中心值，然后将y值减去中心值，使中心平移到0
        
        参数:
        experiment_data (list): 实验数据列表，每个元素为[x_data, y_data]
        
        返回:
        tuple: (modified_x_list, modified_y_list, centres)
               modified_x_list: 修正后的x数据列表
               modified_y_list: 修正后的y数据列表（中心平移到0）
               centres: 每个实验的原始中心值列表
        """
        modified_x_list = []
        modified_y_list = []
        centres = []
        
        for i, experiment in enumerate(experiment_data):
            if len(experiment) != 2:
                print(f"警告: 实验 {i+1} 数据格式错误，跳过")
                continue
            
            x_data, y_data = experiment
            x_array = np.array(x_data)
            y_array = np.array(y_data)
            
            # 计算y中心值
            y_centre = find_ycentre(y_array)
            centres.append(y_centre)
            
            # 修正：y值减去中心值，使中心平移到0
            y_modified = y_array - y_centre
            
            modified_x_list.append(x_array)
            modified_y_list.append(y_modified)
            
            print(f"实验 {i+1}: 原始中心值 = {y_centre:.6f}, 修正后范围 = [{y_modified.min():.6f}, {y_modified.max():.6f}]")
        
        return modified_x_list, modified_y_list, centres


def calculate_max7_min7_means(modified_y_list: List[np.ndarray]) -> Tuple[List[float], List[float]]:
    """
    计算每个实验的max7和min7均值
    
    参数:
    modified_y_list (list): 修正后的y数据列表（中心平移到0）
    
    返回:
    tuple: (max7_means, min7_means) max7均值列表和min7均值列表
    """
    max7_means = []
    min7_means = []
    
    for i, y_data in enumerate(modified_y_list):
        # 计算max7和min7均值
        if len(y_data) >= 7:
            # 找出最大的7个y值
            max7_indices = np.argsort(y_data)[-7:]  # 最大的7个值的索引
            max7_values = y_data[max7_indices]
            max7_mean = np.mean(max7_values)
            
            # 找出最小的7个y值
            min7_indices = np.argsort(y_data)[:7]  # 最小的7个值的索引
            min7_values = y_data[min7_indices]
            min7_mean = np.mean(min7_values)
            
            # 存储均值
            max7_means.append(max7_mean)
            min7_means.append(min7_mean)
            
            # 在调试输出中print这些值
            print(f"实验 {i+1}:")
            print(f"  max7值: {max7_values}")
            print(f"  max7均值: {max7_mean:.6f} 度")
            print(f"  min7值: {min7_values}")
            print(f"  min7均值: {min7_mean:.6f} 度")
            print(f"  max7-min7差值: {max7_mean - min7_mean:.6f} 度")
        else:
            print(f"警告: 实验 {i+1} 数据点不足7个，无法计算max7和min7均值")
            max7_means.append(np.nan)
            min7_means.append(np.nan)
    
    return max7_means, min7_means


def save_improved_data_to_json(modified_x_list: List[np.ndarray],
                              modified_y_list: List[np.ndarray],
                              centres: List[float],
                              max7_means: List[float],
                              min7_means: List[float]) -> None:
    """
    保存改进数据到JSON文件
    
    参数:
    modified_x_list (list): 修正后的x数据列表
    modified_y_list (list): 修正后的y数据列表（中心平移到0）
    centres (list): 每个实验的原始中心值列表
    max7_means (list): 每个实验的max7均值列表
    min7_means (list): 每个实验的min7均值列表
    """
    output_path = "数据处理/improved_angle_data.json"
    
    try:
        # 准备数据字典
        data_dict = {
            "data": [],        # 5元素list，每个元素是[x,y]
            "ycentre": [],     # 5元素list，每个元素是ycentre值
            "max_ave": [],     # 5元素list，每个元素是max7均值
            "min_ave": []      # 5元素list，每个元素是min7均值
        }
        
        # 确保所有列表长度一致（取最小长度）
        min_length = min(len(modified_x_list), len(modified_y_list), 
                        len(centres), len(max7_means), len(min7_means))
        
        print(f"\n保存改进数据到JSON文件，共 {min_length} 个实验数据")
        
        for i in range(min_length):
            # 转换numpy数组为Python列表
            x_data = modified_x_list[i].tolist() if hasattr(modified_x_list[i], 'tolist') else list(modified_x_list[i])
            y_data = modified_y_list[i].tolist() if hasattr(modified_y_list[i], 'tolist') else list(modified_y_list[i])
            
            # 添加到data列表
            data_dict["data"].append([x_data, y_data])
            
            # 添加ycentre值
            data_dict["ycentre"].append(float(centres[i]))
            
            # 添加max7均值（如果是nan则存储None）
            if not np.isnan(max7_means[i]):
                data_dict["max_ave"].append(float(max7_means[i]))
            else:
                data_dict["max_ave"].append(None)
            
            # 添加min7均值（如果是nan则存储None）
            if not np.isnan(min7_means[i]):
                data_dict["min_ave"].append(float(min7_means[i]))
            else:
                data_dict["min_ave"].append(None)
            
            print(f"实验 {i+1}:")
            print(f"  数据点数量: {len(x_data)}")
            print(f"  ycentre值: {centres[i]:.6f}")
            if not np.isnan(max7_means[i]):
                print(f"  max7均值: {max7_means[i]:.6f}")
            if not np.isnan(min7_means[i]):
                print(f"  min7均值: {min7_means[i]:.6f}")
        
        # 保存到JSON文件
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data_dict, f, ensure_ascii=False, indent=2)
        
        print(f"改进数据已保存到JSON文件: {output_path}")
        
        # 打印JSON文件内容摘要
        print(f"\nJSON文件内容摘要:")
        print(f"  data: {len(data_dict['data'])} 个实验数据")
        print(f"  ycentre: {len(data_dict['ycentre'])} 个中心值")
        print(f"  max_ave: {len(data_dict['max_ave'])} 个max7均值")
        print(f"  min_ave: {len(data_dict['min_ave'])} 个min7均值")
        
        # 验证数据
        print(f"\n数据验证:")
        for i in range(min_length):
            print(f"  实验 {i+1}:")
            print(f"    data格式: list of [x, y], x长度={len(data_dict['data'][i][0])}, y长度={len(data_dict['data'][i][1])}")
            print(f"    ycentre: {data_dict['ycentre'][i]:.6f}")
            print(f"    max_ave: {data_dict['max_ave'][i]}")
            print(f"    min_ave: {data_dict['min_ave'][i]}")
    
    except Exception as e:
        print(f"错误: 保存改进数据到JSON文件时发生错误: {e}")


def plot_improved_angle(modified_x_list: List[np.ndarray],
                       modified_y_list: List[np.ndarray],
                       centres: List[float]) -> None:
    """
    绘制改进的克尔转角数据图，包含max7和min7平均
    
    参数:
    modified_x_list (list): 修正后的x数据列表
    modified_y_list (list): 修正后的y数据列表（中心平移到0）
    centres (list): 每个实验的原始中心值列表
    """
    if not modified_x_list or not modified_y_list:
        print("错误: 没有有效数据可绘制")
        return
    
    # 设置中文字体
    setup_chinese_font()
    
    # 计算max7和min7均值
    max7_means, min7_means = calculate_max7_min7_means(modified_y_list)
    
    # 创建图形
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # 定义颜色列表（5个实验用5种不同颜色）
    colors = ['blue', 'red', 'green', 'orange', 'purple']
    
    # 绘制每个实验的数据
    for i, (x_data, y_data) in enumerate(zip(modified_x_list, modified_y_list)):
        if i >= len(colors):
            color = colors[i % len(colors)]
        else:
            color = colors[i]
        
        # 绘制散点图（数据点）
        ax.scatter(x_data, y_data, color=color, s=40, alpha=0.7, 
                   label=f'实验 {i+1}', edgecolors='black', linewidth=0.5)
        
        # 绘制连线（细虚线）- 按原始顺序连接以形成磁滞回线
        # 创建闭合的数据：将第一个点添加到末尾以形成闭合曲线
        x_closed = np.append(x_data, x_data[0])
        y_closed = np.append(y_data, y_data[0])
        
        ax.plot(x_closed, y_closed, color=color, linestyle='--', linewidth=1, alpha=0.6)
        
        # 绘制max7均值横线（实线）
        if i < len(max7_means) and not np.isnan(max7_means[i]):
            ax.axhline(y=max7_means[i], color=color, linestyle='-', linewidth=1.5, alpha=0.8,
                      label=f'实验 {i+1} max7均值')
        
        # 绘制min7均值横线（实线）
        if i < len(min7_means) and not np.isnan(min7_means[i]):
            ax.axhline(y=min7_means[i], color=color, linestyle='-', linewidth=1.5, alpha=0.8,
                      label=f'实验 {i+1} min7均值')
    
    # 设置图形属性
    title = "改进的克尔转角数据对比"
    ax.set_title(title, fontsize=16, pad=20)
    ax.set_xlabel("磁感应强度 (mT)", fontsize=14)
    ax.set_ylabel("克尔转角 (度, 中心修正)", fontsize=14)
    ax.grid(True, alpha=0.3, linestyle=':')
    
    # 添加水平参考线（y=0）
    ax.axhline(y=0, color='black', linestyle='-', linewidth=0.8, alpha=0.5)
    
    # 添加图例（简化图例，避免重复）
    # 只显示实验标签，不显示max7/min7均值标签
    handles, labels = ax.get_legend_handles_labels()
    unique_labels = []
    unique_handles = []
    for handle, label in zip(handles, labels):
        if '实验' in label and 'max7' not in label and 'min7' not in label:
            if label not in unique_labels:
                unique_labels.append(label)
                unique_handles.append(handle)
    
    ax.legend(unique_handles, unique_labels, loc='best', fontsize=12)
    
    # 设置坐标轴范围
    all_x = np.concatenate(modified_x_list)
    all_y = np.concatenate(modified_y_list)
    
    x_min, x_max = all_x.min(), all_x.max()
    y_min, y_max = all_y.min(), all_y.max()
    
    # 考虑max7和min7均值线，调整y轴范围
    all_means = max7_means + min7_means
    valid_means = [m for m in all_means if not np.isnan(m)]
    if valid_means:
        means_min = min(valid_means)
        means_max = max(valid_means)
        y_min = min(y_min, means_min)
        y_max = max(y_max, means_max)
    
    # 增加一些边距
    x_margin = (x_max - x_min) * 0.05
    y_margin = (y_max - y_min) * 0.1
    
    ax.set_xlim(x_min - x_margin, x_max + x_margin)
    ax.set_ylim(y_min - y_margin, y_max + y_margin)
    
    # 添加网格和背景
    ax.set_axisbelow(True)
    
    plt.tight_layout()
    
    # 保存图形
    output_path = "数据处理/克尔转角_improved.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"改进的克尔转角图已保存到: {output_path}")
    
    # 打印处理信息
    print("\n处理摘要:")
    print("-" * 40)
    for i, centre in enumerate(centres):
        print(f"实验 {i+1}: 原始中心值 = {centre:.6f} 度")
    
    # 打印max7和min7均值统计
    print("\nmax7和min7均值统计:")
    print("-" * 40)
    for i in range(len(max7_means)):
        if not np.isnan(max7_means[i]) and not np.isnan(min7_means[i]):
            print(f"实验 {i+1}:")
            print(f"  max7均值: {max7_means[i]:.6f} 度")
            print(f"  min7均值: {min7_means[i]:.6f} 度")
            print(f"  差值 (max7-min7): {max7_means[i] - min7_means[i]:.6f} 度")
            print(f"  原始中心值: {centres[i]:.6f} 度")
    
    # 保存改进处理信息到文件
    save_improvement_info(centres, max7_means, min7_means, "克尔转角")
    
    # 保存改进数据到JSON文件
    save_improved_data_to_json(modified_x_list, modified_y_list, centres, max7_means, min7_means)
    
    # 显示图形
    plt.show()


def save_improvement_info(centres: List[float], 
                         max7_means: List[float], 
                         min7_means: List[float],
                         data_type: str = "克尔转角") -> None:
    """
    保存改进处理信息到文件
    
    参数:
    centres (list): 每个实验的原始中心值列表
    max7_means (list): 每个实验的max7均值列表
    min7_means (list): 每个实验的min7均值列表
    data_type (str): 数据类型，用于文件名和标题
    """
    output_path = f"数据处理/{data_type}_improved_info.txt"
    
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(f"{data_type}数据改进处理信息\n")
            f.write("=" * 50 + "\n\n")
            
            f.write("处理说明:\n")
            f.write(f"- 所有{data_type}实验: y中心值已平移到0\n")
            f.write("- 计算每个实验的max7均值（最大的7个值的平均值）\n")
            f.write("- 计算每个实验的min7均值（最小的7个值的平均值）\n\n")
            
            f.write(f"各实验原始中心值:\n")
            f.write("-" * 30 + "\n")
            for i, centre in enumerate(centres):
                f.write(f"实验 {i+1}: {centre:.6f} 度\n")
            
            if centres:
                f.write("\n中心值统计:\n")
                f.write(f"  范围: [{min(centres):.6f}, {max(centres):.6f}] 度\n")
                f.write(f"  均值: {np.mean(centres):.6f} 度\n")
                f.write(f"  标准差: {np.std(centres):.6f} 度\n")
            
            # 添加max7和min7均值表格
            f.write("\n" + "=" * 50 + "\n")
            f.write("max7和min7均值统计表格\n")
            f.write("=" * 50 + "\n\n")
            
            # 表头
            f.write("实验 | max7均值 (度) | min7均值 (度) | 差值 (max7-min7) | (max7均值+min7均值)/2\n")
            f.write("-" * 80 + "\n")
            
            # 表格数据
            valid_data_count = 0
            for i in range(len(centres)):
                if i < len(max7_means) and i < len(min7_means):
                    if not np.isnan(max7_means[i]) and not np.isnan(min7_means[i]):
                        max7_mean = max7_means[i]
                        min7_mean = min7_means[i]
                        diff = max7_mean - min7_mean
                        avg_of_means = (max7_mean + min7_mean) / 2
                        
                        f.write(f"{i+1:4d} | {max7_mean:14.6f} | {min7_mean:14.6f} | {diff:17.6f} | {avg_of_means:22.6f}\n")
                        valid_data_count += 1
            
            if valid_data_count > 0:
                # 计算统计信息
                valid_max7 = [m for m in max7_means if not np.isnan(m)]
                valid_min7 = [m for m in min7_means if not np.isnan(m)]
                
                if valid_max7 and valid_min7:
                    max7_stats = {
                        'min': min(valid_max7),
                        'max': max(valid_max7),
                        'mean': np.mean(valid_max7),
                        'std': np.std(valid_max7)
                    }
                    
                    min7_stats = {
                        'min': min(valid_min7),
                        'max': max(valid_min7),
                        'mean': np.mean(valid_min7),
                        'std': np.std(valid_min7)
                    }
                    
                    # 计算差值统计
                    diffs = [max7_means[i] - min7_means[i] for i in range(len(max7_means)) 
                            if not np.isnan(max7_means[i]) and not np.isnan(min7_means[i])]
                    
                    diff_stats = {
                        'min': min(diffs),
                        'max': max(diffs),
                        'mean': np.mean(diffs),
                        'std': np.std(diffs)
                    }
                    
                    # 计算(max7均值+min7均值)/2的统计
                    avg_means = [(max7_means[i] + min7_means[i]) / 2 for i in range(len(max7_means)) 
                                if not np.isnan(max7_means[i]) and not np.isnan(min7_means[i])]
                    
                    avg_stats = {
                        'min': min(avg_means),
                        'max': max(avg_means),
                        'mean': np.mean(avg_means),
                        'std': np.std(avg_means)
                    }
                    
                    f.write("\n" + "=" * 50 + "\n")
                    f.write("统计摘要\n")
                    f.write("=" * 50 + "\n\n")
                    
                    f.write("max7均值统计:\n")
                    f.write(f"  范围: [{max7_stats['min']:.6f}, {max7_stats['max']:.6f}] 度\n")
                    f.write(f"  均值: {max7_stats['mean']:.6f} 度\n")
                    f.write(f"  标准差: {max7_stats['std']:.6f} 度\n\n")
                    
                    f.write("min7均值统计:\n")
                    f.write(f"  范围: [{min7_stats['min']:.6f}, {min7_stats['max']:.6f}] 度\n")
                    f.write(f"  均值: {min7_stats['mean']:.6f} 度\n")
                    f.write(f"  标准差: {min7_stats['std']:.6f} 度\n\n")
                    
                    f.write("差值 (max7-min7) 统计:\n")
                    f.write(f"  范围: [{diff_stats['min']:.6f}, {diff_stats['max']:.6f}] 度\n")
                    f.write(f"  均值: {diff_stats['mean']:.6f} 度\n")
                    f.write(f"  标准差: {diff_stats['std']:.6f} 度\n\n")
                    
                    f.write("(max7均值+min7均值)/2 统计:\n")
                    f.write(f"  范围: [{avg_stats['min']:.6f}, {avg_stats['max']:.6f}] 度\n")
                    f.write(f"  均值: {avg_stats['mean']:.6f} 度\n")
                    f.write(f"  标准差: {avg_stats['std']:.6f} 度\n")
        
        print(f"改进处理信息已保存到: {output_path}")
    except Exception as e:
        print(f"错误: 保存改进处理信息时发生错误: {e}")


def main():
    """主函数"""
    print("开始绘制改进的克尔转角数据图（包含max7和min7平均）...")
    print("="*60)
    
    # 1. 加载实验数据
    data = load_experiment_data()
    if data is None:
        print("错误: 无法加载实验数据，程序退出")
        return
    
    # 2. 提取克尔转角数据
    kerr_angle_data = data.get("克尔转角", [])
    print(f"找到 {len(kerr_angle_data)} 个克尔转角实验数据")
    
    if len(kerr_angle_data) < 1:
        print("错误: 没有克尔转角数据可处理")
        return
    
    # 3. 修正数据（y中心平移到0）
    modified_x_list, modified_y_list, centres = modify_data(kerr_angle_data)
    
    if not modified_x_list or not modified_y_list:
        print("错误: 数据处理失败，程序退出")
        return
    
    print(f"\n成功修正 {len(modified_x_list)} 个克尔转角实验")
    
    # 4. 绘制改进的克尔转角数据图（包含max7和min7平均）
    plot_improved_angle(modified_x_list, modified_y_list, centres)
    
    print("\n" + "="*60)
    print("改进的克尔转角数据图绘制完成")
    print("="*60)


if __name__ == "__main__":
    main()

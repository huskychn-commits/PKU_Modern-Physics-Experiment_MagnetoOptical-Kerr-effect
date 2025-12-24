#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
plot_modified_data.py - 绘制修正数据图
将五个克尔转角或克尔椭率实验数据画在一起，y中心平移到0处。
用不同颜色标记不同的实验，数据点和连线用同一种颜色。
"""

import json
import numpy as np
import matplotlib.pyplot as plt
import os
import sys
from typing import List, Tuple, Optional

# 添加当前目录到路径，以便导入find_centre模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 尝试导入find_centre模块中的函数
try:
    from find_centre import find_ycentre, setup_chinese_font
    FIND_CENTRE_AVAILABLE = True
except ImportError as e:
    print(f"警告: 无法导入find_centre模块: {e}")
    print("将使用自定义的find_ycentre实现")
    FIND_CENTRE_AVAILABLE = False
    
    # 自定义find_ycentre实现（与find_centre.py中的相同）
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
    
    # 自定义中文字体设置
    def setup_chinese_font():
        """设置matplotlib中文字体支持"""
        try:
            import matplotlib
            font_names = ['Microsoft YaHei', 'SimHei', 'SimSun', 'FangSong', 'KaiTi']
            for font_name in font_names:
                try:
                    matplotlib.rcParams['font.sans-serif'] = [font_name]
                    matplotlib.rcParams['axes.unicode_minus'] = False
                    print(f"已设置中文字体: {font_name}")
                    return True
                except:
                    continue
            print("警告: 未找到合适的中文字体，使用默认字体")
            return False
        except ImportError:
            print("警告: matplotlib未安装，无法设置中文字体")
            return False


def load_experiment_data(json_path: str = "数据处理/experiment_data.json") -> Optional[dict]:
    """
    从JSON文件加载实验数据
    
    参数:
    json_path (str): JSON文件路径
    
    返回:
    dict: 包含克尔转角和克尔椭率数据的字典，失败返回None
    """
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        print(f"成功加载数据文件: {json_path}")
        return data
    except FileNotFoundError:
        print(f"错误: 文件未找到: {json_path}")
        return None
    except json.JSONDecodeError as e:
        print(f"错误: JSON解析失败: {e}")
        return None
    except Exception as e:
        print(f"错误: 读取文件时发生错误: {e}")
        return None


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


def plot_modified_experiments(modified_x_list: List[np.ndarray],
                               modified_y_list: List[np.ndarray],
                               data_type: str = "克尔转角",
                               title_suffix: str = "") -> None:
    """
    绘制修正后的实验数据图
    
    参数:
    modified_x_list (list): 修正后的x数据列表
    modified_y_list (list): 修正后的y数据列表（中心平移到0）
    data_type (str): 数据类型，用于标题和标签
    title_suffix (str): 标题后缀，可为空
    """
    if not modified_x_list or not modified_y_list:
        print(f"错误: 没有有效数据可绘制 ({data_type})")
        return
    
    # 设置中文字体
    setup_chinese_font()
    
    # 创建图形
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # 定义颜色列表（5个实验用5种不同颜色）
    colors = ['blue', 'red', 'green', 'orange', 'purple']
    
    # 绘制每个实验的数据
    for i, (x_data, y_data) in enumerate(zip(modified_x_list, modified_y_list)):
        if i >= len(colors):
            color = colors[i % len(colors)]  # 如果实验多于颜色数，循环使用颜色
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
    
    # 设置图形属性
    title = f"修正{data_type}数据对比 (y中心平移到0)"
    if title_suffix:
        title += f" - {title_suffix}"
    
    ax.set_title(title, fontsize=16, pad=20)
    ax.set_xlabel("磁感应强度 (mT)", fontsize=14)
    ax.set_ylabel(f"{data_type} (度, 中心修正)", fontsize=14)
    ax.grid(True, alpha=0.3, linestyle=':')
    
    # 添加水平参考线（y=0）
    ax.axhline(y=0, color='black', linestyle='-', linewidth=0.8, alpha=0.5)
    
    # 添加图例
    ax.legend(loc='best', fontsize=12)
    
    # 设置坐标轴范围
    all_x = np.concatenate(modified_x_list)
    all_y = np.concatenate(modified_y_list)
    
    x_min, x_max = all_x.min(), all_x.max()
    y_min, y_max = all_y.min(), all_y.max()
    
    # 增加一些边距
    x_margin = (x_max - x_min) * 0.05
    y_margin = (y_max - y_min) * 0.1
    
    ax.set_xlim(x_min - x_margin, x_max + x_margin)
    ax.set_ylim(y_min - y_margin, y_max + y_margin)
    
    # 添加网格和背景
    ax.set_axisbelow(True)
    
    plt.tight_layout()
    
    # 保存图形
    filename = data_type.replace(" ", "_")
    output_path = f"数据处理/{filename}_modified.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"{data_type}修正图已保存到: {output_path}")
    
    # 显示图形
    plt.show()


def plot_both_modified(kerr_angle_data: List[List[List[float]]],
                        kerr_ellipticity_data: List[List[List[float]]]) -> None:
    """
    绘制克尔转角和克尔椭率的修正数据图
    
    参数:
    kerr_angle_data (list): 克尔转角实验数据
    kerr_ellipticity_data (list): 克尔椭率实验数据
    """
    print("\n" + "="*60)
    print("开始绘制修正数据图")
    print("="*60)
    
    # 1. 处理克尔转角数据
    print("\n处理克尔转角数据...")
    angle_x_list, angle_y_list, angle_centres = modify_data(kerr_angle_data)
    
    if angle_x_list and angle_y_list:
        print(f"成功修正 {len(angle_x_list)} 个克尔转角实验")
        plot_modified_experiments(angle_x_list, angle_y_list, "克尔转角")
        
        # 打印中心值信息
        print("\n克尔转角原始中心值:")
        for i, centre in enumerate(angle_centres):
            print(f"  实验 {i+1}: {centre:.6f} 度")
    else:
        print("警告: 没有有效的克尔转角数据")
    
    # 2. 处理克尔椭率数据
    print("\n处理克尔椭率数据...")
    ellipticity_x_list, ellipticity_y_list, ellipticity_centres = modify_data(kerr_ellipticity_data)
    
    if ellipticity_x_list and ellipticity_y_list:
        print(f"成功修正 {len(ellipticity_x_list)} 个克尔椭率实验")
        plot_modified_experiments(ellipticity_x_list, ellipticity_y_list, "克尔椭率")
        
        # 打印中心值信息
        print("\n克尔椭率原始中心值:")
        for i, centre in enumerate(ellipticity_centres):
            print(f"  实验 {i+1}: {centre:.6f} 度")
    else:
        print("警告: 没有有效的克尔椭率数据")
    
    # 3. 保存中心值数据到文件
    save_centres_to_file(angle_centres, ellipticity_centres)
    
    print("\n" + "="*60)
    print("修正数据图绘制完成")
    print("="*60)


def save_centres_to_file(angle_centres: List[float], ellipticity_centres: List[float]) -> None:
    """
    保存中心值数据到文本文件
    
    参数:
    angle_centres (list): 克尔转角中心值列表
    ellipticity_centres (list): 克尔椭率中心值列表
    """
    output_path = "数据处理/modification_centres.txt"
    
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("实验数据修正中心值\n")
            f.write("=" * 50 + "\n\n")
            
            f.write("克尔转角原始中心值:\n")
            f.write("-" * 30 + "\n")
            for i, centre in enumerate(angle_centres):
                f.write(f"实验 {i+1}: {centre:.6f} 度\n")
            
            f.write("\n克尔椭率原始中心值:\n")
            f.write("-" * 30 + "\n")
            for i, centre in enumerate(ellipticity_centres):
                f.write(f"实验 {i+1}: {centre:.6f} 度\n")
            
            # 添加统计信息
            if angle_centres:
                f.write("\n克尔转角中心值统计:\n")
                f.write(f"  范围: [{min(angle_centres):.6f}, {max(angle_centres):.6f}] 度\n")
                f.write(f"  均值: {np.mean(angle_centres):.6f} 度\n")
                f.write(f"  标准差: {np.std(angle_centres):.6f} 度\n")
            
            if ellipticity_centres:
                f.write("\n克尔椭率中心值统计:\n")
                f.write(f"  范围: [{min(ellipticity_centres):.6f}, {max(ellipticity_centres):.6f}] 度\n")
                f.write(f"  均值: {np.mean(ellipticity_centres):.6f} 度\n")
                f.write(f"  标准差: {np.std(ellipticity_centres):.6f} 度\n")
        
        print(f"中心值数据已保存到: {output_path}")
    except Exception as e:
        print(f"错误: 保存中心值数据时发生错误: {e}")


def main():
    """主函数"""
    print("开始绘制修正实验数据图...")
    
    # 1. 加载实验数据
    data = load_experiment_data()
    if data is None:
        print("错误: 无法加载实验数据，程序退出")
        return
    
    # 2. 提取克尔转角和克尔椭率数据
    kerr_angle_data = data.get("克尔转角", [])
    kerr_ellipticity_data = data.get("克尔椭率", [])
    
    print(f"找到 {len(kerr_angle_data)} 个克尔转角实验数据")
    print(f"找到 {len(kerr_ellipticity_data)} 个克尔椭率实验数据")
    
    # 3. 绘制修正数据图
    plot_both_modified(kerr_angle_data, kerr_ellipticity_data)
    
    print("\n程序执行完成！")


if __name__ == "__main__":
    main()

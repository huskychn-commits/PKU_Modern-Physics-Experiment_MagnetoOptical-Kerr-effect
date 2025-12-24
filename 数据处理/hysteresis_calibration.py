#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hysteresis_calibration.py - 磁滞校准分析脚本
从experiment_data.json读取五个克尔转角数据，计算y中心角度，
分析其与起偏器额外转角的关系，并进行线性拟合。
"""

import json
import numpy as np
import matplotlib.pyplot as plt
import os
import sys

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


def load_experiment_data(json_path="数据处理/experiment_data.json"):
    """
    从JSON文件加载实验数据
    
    参数:
    json_path (str): JSON文件路径
    
    返回:
    dict: 包含克尔转角和克尔椭率数据的字典
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


def calculate_y_centres(kerr_angle_data):
    """
    计算每个实验的y中心角度
    
    参数:
    kerr_angle_data (list): 克尔转角实验数据列表
    
    返回:
    list: 每个实验的y中心角度列表
    """
    y_centres = []
    
    for i, experiment in enumerate(kerr_angle_data):
        if len(experiment) == 2:
            x_data, y_data = experiment
            # 计算y中心角度
            y_centre = find_ycentre(y_data)
            y_centres.append(y_centre)
            print(f"实验 {i+1}: y中心角度 = {y_centre:.6f} 度")
        else:
            print(f"警告: 实验 {i+1} 数据格式错误，跳过")
            y_centres.append(None)
    
    return y_centres


def linear_fit(x_data, y_data):
    """
    进行线性拟合
    
    参数:
    x_data (array-like): x坐标数据
    y_data (array-like): y坐标数据
    
    返回:
    tuple: (slope, intercept, r_squared) 斜率、截距、R²值
    """
    # 移除None值
    valid_indices = [i for i, y in enumerate(y_data) if y is not None]
    x_valid = np.array([x_data[i] for i in valid_indices])
    y_valid = np.array([y_data[i] for i in valid_indices])
    
    if len(x_valid) < 2:
        print("错误: 有效数据点不足，无法进行线性拟合")
        return None, None, None
    
    # 线性拟合
    slope, intercept = np.polyfit(x_valid, y_valid, 1)
    
    # 计算R²值
    y_pred = slope * x_valid + intercept
    ss_res = np.sum((y_valid - y_pred) ** 2)
    ss_tot = np.sum((y_valid - np.mean(y_valid)) ** 2)
    r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
    
    return slope, intercept, r_squared


def plot_calibration_curve(extra_angles, y_centres, slope, intercept, r_squared):
    """
    绘制校准曲线
    
    参数:
    extra_angles (list): 额外转角列表
    y_centres (list): y中心角度列表
    slope (float): 拟合直线斜率
    intercept (float): 拟合直线截距
    r_squared (float): R²值
    """
    # 设置中文字体
    setup_chinese_font()
    
    # 创建图形
    fig, ax = plt.subplots(figsize=(10, 7))
    
    # 绘制数据点
    valid_indices = [i for i, y in enumerate(y_centres) if y is not None]
    x_valid = [extra_angles[i] for i in valid_indices]
    y_valid = [y_centres[i] for i in valid_indices]
    
    ax.scatter(x_valid, y_valid, color='blue', s=100, label='实验数据点', zorder=5)
    
    # 添加数据点标签
    for i, (x, y) in enumerate(zip(x_valid, y_valid)):
        ax.annotate(f'{y:.4f}', xy=(x, y), xytext=(5, 5), 
                   textcoords='offset points', fontsize=10)
    
    # 绘制拟合直线
    if slope is not None and intercept is not None:
        x_fit = np.array([min(x_valid) - 0.5, max(x_valid) + 0.5])
        y_fit = slope * x_fit + intercept
        ax.plot(x_fit, y_fit, color='red', linewidth=2, 
                label=f'线性拟合: y = {slope:.4f}x + {intercept:.4f}\nR² = {r_squared:.6f}')
    
    # 设置图形属性
    ax.set_title("克尔转角中心值与起偏器额外转角的关系", fontsize=16, pad=20)
    ax.set_xlabel("起偏器额外转角 (度)", fontsize=14)
    ax.set_ylabel("克尔转角中心值 (度)", fontsize=14)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.legend(loc='best', fontsize=12)
    
    # 设置坐标轴范围
    ax.set_xlim(min(extra_angles) - 0.5, max(extra_angles) + 0.5)
    
    # 添加网格和背景
    ax.set_axisbelow(True)
    
    plt.tight_layout()
    
    # 保存图形
    output_path = "数据处理/calibration_curve.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"图形已保存到: {output_path}")
    
    # 显示图形
    plt.show()


def print_calibration_results(extra_angles, y_centres, slope, intercept, r_squared):
    """
    打印校准结果
    
    参数:
    extra_angles (list): 额外转角列表
    y_centres (list): y中心角度列表
    slope (float): 拟合直线斜率
    intercept (float): 拟合直线截距
    r_squared (float): R²值
    """
    print("\n" + "="*60)
    print("磁滞校准分析结果")
    print("="*60)
    
    print("\n实验数据:")
    print("起偏器额外转角 (度) | 克尔转角中心值 (度)")
    print("-" * 40)
    for i, (angle, y_centre) in enumerate(zip(extra_angles, y_centres)):
        if y_centre is not None:
            print(f"{angle:^20} | {y_centre:^20.6f}")
        else:
            print(f"{angle:^20} | {'无效数据':^20}")
    
    if slope is not None and intercept is not None:
        print("\n线性拟合结果:")
        print(f"拟合方程: y = {slope:.6f} * x + {intercept:.6f}")
        print(f"斜率: {slope:.6f} 度/度")
        print(f"截距: {intercept:.6f} 度")
        print(f"R²值: {r_squared:.6f}")
        
        # 解释斜率的意义
        print(f"\n斜率解释: 起偏器额外转角每增加1度，克尔转角中心值变化 {slope:.6f} 度")
        
        # 计算校准系数（如果需要）
        if abs(slope) > 1e-10:
            calibration_factor = 1.0 / slope
            print(f"校准系数: {calibration_factor:.6f} (1/斜率)")
    
    print("="*60)


def main():
    """主函数"""
    print("开始磁滞校准分析...")
    print("="*60)
    
    # 1. 加载实验数据
    data = load_experiment_data()
    if data is None:
        print("错误: 无法加载实验数据，程序退出")
        return
    
    # 2. 提取克尔转角数据（前5个实验）
    kerr_angle_data = data.get("克尔转角", [])
    if len(kerr_angle_data) < 5:
        print(f"警告: 克尔转角数据不足，期望5个，实际{len(kerr_angle_data)}个")
        # 只使用已有的数据
        kerr_angle_data = kerr_angle_data[:5]
    
    print(f"找到 {len(kerr_angle_data)} 个克尔转角实验数据")
    
    # 3. 计算每个实验的y中心角度
    y_centres = calculate_y_centres(kerr_angle_data)
    
    # 4. 定义起偏器额外转角（已知：0, 1, 2, 3, 4度）
    extra_angles = [0, 1, 2, 3, 4]
    
    # 确保数据长度匹配
    if len(y_centres) > len(extra_angles):
        y_centres = y_centres[:len(extra_angles)]
    elif len(y_centres) < len(extra_angles):
        extra_angles = extra_angles[:len(y_centres)]
    
    # 5. 线性拟合
    slope, intercept, r_squared = linear_fit(extra_angles, y_centres)
    
    # 6. 打印结果
    print_calibration_results(extra_angles, y_centres, slope, intercept, r_squared)
    
    # 7. 绘制校准曲线
    plot_calibration_curve(extra_angles, y_centres, slope, intercept, r_squared)
    
    print("\n磁滞校准分析完成！")


if __name__ == "__main__":
    main()

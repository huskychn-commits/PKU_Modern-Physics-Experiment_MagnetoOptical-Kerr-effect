#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
kerr_relation.py - 计算克尔椭率和克尔转角的变化关系图
从experiment_data.json读取数据，计算每个实验的克尔转角和克尔椭率中心值，
并绘制它们的关系图。
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


def calculate_centres(kerr_angle_data, kerr_ellipticity_data):
    """
    计算每个实验的克尔转角和克尔椭率中心值
    
    参数:
    kerr_angle_data (list): 克尔转角实验数据列表
    kerr_ellipticity_data (list): 克尔椭率实验数据列表
    
    返回:
    tuple: (angle_centres, ellipticity_centres) 克尔转角中心值和克尔椭率中心值列表
    """
    angle_centres = []
    ellipticity_centres = []
    
    # 确保数据长度一致
    min_length = min(len(kerr_angle_data), len(kerr_ellipticity_data))
    kerr_angle_data = kerr_angle_data[:min_length]
    kerr_ellipticity_data = kerr_ellipticity_data[:min_length]
    
    print(f"分析 {min_length} 个实验数据...")
    
    for i in range(min_length):
        # 计算克尔转角中心值
        angle_exp = kerr_angle_data[i]
        if len(angle_exp) == 2:
            _, y_angle_data = angle_exp
            angle_centre = find_ycentre(y_angle_data)
            angle_centres.append(angle_centre)
        else:
            print(f"警告: 实验 {i+1} 克尔转角数据格式错误，跳过")
            angle_centres.append(None)
        
        # 计算克尔椭率中心值
        ellipticity_exp = kerr_ellipticity_data[i]
        if len(ellipticity_exp) == 2:
            _, y_ellipticity_data = ellipticity_exp
            ellipticity_centre = find_ycentre(y_ellipticity_data)
            ellipticity_centres.append(ellipticity_centre)
        else:
            print(f"警告: 实验 {i+1} 克尔椭率数据格式错误，跳过")
            ellipticity_centres.append(None)
    
    return angle_centres, ellipticity_centres


def print_relation_results(angle_centres, ellipticity_centres):
    """
    打印克尔转角和克尔椭率关系结果
    
    参数:
    angle_centres (list): 克尔转角中心值列表
    ellipticity_centres (list): 克尔椭率中心值列表
    """
    print("\n" + "="*60)
    print("克尔转角与克尔椭率关系分析")
    print("="*60)
    
    print("\n实验数据:")
    print("实验编号 | 克尔转角中心值 (度) | 克尔椭率中心值 (度)")
    print("-" * 60)
    
    valid_count = 0
    for i, (angle, ellipticity) in enumerate(zip(angle_centres, ellipticity_centres)):
        if angle is not None and ellipticity is not None:
            print(f"{i+1:^8} | {angle:^20.6f} | {ellipticity:^20.6f}")
            valid_count += 1
        else:
            print(f"{i+1:^8} | {'无效数据':^20} | {'无效数据':^20}")
    
    print(f"\n有效数据点数量: {valid_count}")
    
    # 计算基本统计信息
    if valid_count > 0:
        valid_angles = [a for a in angle_centres if a is not None]
        valid_ellipticities = [e for e in ellipticity_centres if e is not None]
        
        print("\n统计信息:")
        print(f"克尔转角中心值范围: [{min(valid_angles):.6f}, {max(valid_angles):.6f}] 度")
        print(f"克尔椭率中心值范围: [{min(valid_ellipticities):.6f}, {max(valid_ellipticities):.6f}] 度")
        print(f"克尔转角中心值均值: {np.mean(valid_angles):.6f} 度")
        print(f"克尔椭率中心值均值: {np.mean(valid_ellipticities):.6f} 度")
    
    print("="*60)


def plot_relation(angle_centres, ellipticity_centres):
    """
    绘制克尔转角和克尔椭率关系图
    
    参数:
    angle_centres (list): 克尔转角中心值列表
    ellipticity_centres (list): 克尔椭率中心值列表
    """
    # 设置中文字体
    setup_chinese_font()
    
    # 过滤有效数据点
    valid_data = []
    for i, (a, e) in enumerate(zip(angle_centres, ellipticity_centres)):
        if a is not None and e is not None:
            # 对于实验4、5的克尔椭率中心值取负号（索引3和4，从0开始）
            if i in [3, 4]:  # 实验4和5
                e_modified = -e
                print(f"实验 {i+1}: 克尔椭率中心值取负号: {e:.6f} -> {e_modified:.6f}")
                valid_data.append((a, e_modified))
            else:
                valid_data.append((a, e))
    
    if not valid_data:
        print("错误: 没有有效数据点可绘制")
        return
    
    angles, ellipticities = zip(*valid_data)
    
    # 创建图形
    fig, ax = plt.subplots(figsize=(10, 7))
    
    # 绘制数据点（不显示序号标签）
    scatter = ax.scatter(angles, ellipticities, color='blue', s=100, 
                         alpha=0.8, edgecolors='black', linewidth=1.5, zorder=5)
    
    # 线性拟合（参考manual_calibration.py）
    if len(angles) >= 2:
        # 使用numpy的polyfit进行一阶多项式拟合
        coefficients = np.polyfit(angles, ellipticities, 1)
        k = coefficients[0]  # 斜率
        b = coefficients[1]  # 截距
        
        # 计算R²（拟合优度）
        # 预测值
        predicted = k * np.array(angles) + b
        
        # 残差平方和
        ss_res = np.sum((np.array(ellipticities) - predicted) ** 2)
        
        # 总平方和
        ss_tot = np.sum((np.array(ellipticities) - np.mean(ellipticities)) ** 2)
        
        # R²
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
        
        # 生成拟合线数据
        x_fit = np.linspace(min(angles), max(angles), 100)
        y_fit = k * x_fit + b
        
        # 绘制拟合线
        ax.plot(x_fit, y_fit, color='red', linestyle='-', linewidth=2, 
                label=f'线性拟合: y = {k:.6f}x + {b:.6f}\nR² = {r_squared:.6f}')
        
        print(f"\n线性拟合结果:")
        print(f"  斜率 k = {k:.6f}")
        print(f"  截距 b = {b:.6f}")
        print(f"  拟合公式: y = {k:.6f}x + {b:.6f}")
        print(f"  拟合优度 R² = {r_squared:.6f}")
        
        # 在图上添加拟合公式文本
        fit_text = f'y = {k:.4f}x + {b:.4f}\nR² = {r_squared:.4f}'
        ax.text(0.05, 0.95, fit_text, transform=ax.transAxes, fontsize=12,
                verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    # 设置图形属性
    ax.set_title("克尔转角与克尔椭率中心值关系图（实验4、5椭率中心值取负）", fontsize=16, pad=20)
    ax.set_xlabel("克尔转角中心值 (度)", fontsize=14)
    ax.set_ylabel("克尔椭率中心值 (度)", fontsize=14)
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # 设置坐标轴范围（增加一些边距）
    x_min, x_max = min(angles), max(angles)
    y_min, y_max = min(ellipticities), max(ellipticities)
    x_margin = (x_max - x_min) * 0.1
    y_margin = (y_max - y_min) * 0.1
    
    ax.set_xlim(x_min - x_margin, x_max + x_margin)
    ax.set_ylim(y_min - y_margin, y_max + y_margin)
    
    # 添加网格和背景
    ax.set_axisbelow(True)
    
    # 添加图例
    ax.legend(loc='best', fontsize=12)
    
    plt.tight_layout()
    
    # 保存图形
    output_path = "数据处理/kerr_relation.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"关系图已保存到: {output_path}")
    
    # 显示图形
    plt.show()
    
    # 返回拟合结果
    if len(angles) >= 2:
        return k, b, r_squared
    else:
        return None, None, None


def save_data_to_file(angle_centres, ellipticity_centres):
    """
    将数据保存到文本文件
    
    参数:
    angle_centres (list): 克尔转角中心值列表
    ellipticity_centres (list): 克尔椭率中心值列表
    """
    output_path = "数据处理/kerr_relation_data.txt"
    
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("克尔转角与克尔椭率中心值关系数据\n")
            f.write("=" * 50 + "\n")
            f.write("实验编号 | 克尔转角中心值 (度) | 克尔椭率中心值 (度)\n")
            f.write("-" * 50 + "\n")
            
            for i, (angle, ellipticity) in enumerate(zip(angle_centres, ellipticity_centres)):
                if angle is not None and ellipticity is not None:
                    f.write(f"{i+1:^8} | {angle:^20.6f} | {ellipticity:^20.6f}\n")
                else:
                    f.write(f"{i+1:^8} | {'无效数据':^20} | {'无效数据':^20}\n")
            
            # 添加统计信息
            valid_angles = [a for a in angle_centres if a is not None]
            valid_ellipticities = [e for e in ellipticity_centres if e is not None]
            
            if valid_angles and valid_ellipticities:
                f.write("\n统计信息:\n")
                f.write(f"克尔转角中心值范围: [{min(valid_angles):.6f}, {max(valid_angles):.6f}] 度\n")
                f.write(f"克尔椭率中心值范围: [{min(valid_ellipticities):.6f}, {max(valid_ellipticities):.6f}] 度\n")
                f.write(f"克尔转角中心值均值: {np.mean(valid_angles):.6f} 度\n")
                f.write(f"克尔椭率中心值均值: {np.mean(valid_ellipticities):.6f} 度\n")
        
        print(f"数据已保存到: {output_path}")
    except Exception as e:
        print(f"错误: 保存数据时发生错误: {e}")


def main():
    """主函数"""
    print("开始分析克尔转角与克尔椭率关系...")
    print("="*60)
    
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
    
    # 3. 计算中心值
    angle_centres, ellipticity_centres = calculate_centres(kerr_angle_data, kerr_ellipticity_data)
    
    # 4. 打印结果
    print_relation_results(angle_centres, ellipticity_centres)
    
    # 5. 绘制关系图
    plot_relation(angle_centres, ellipticity_centres)
    
    # 6. 保存数据到文件
    save_data_to_file(angle_centres, ellipticity_centres)
    
    print("\n克尔转角与克尔椭率关系分析完成！")


if __name__ == "__main__":
    main()

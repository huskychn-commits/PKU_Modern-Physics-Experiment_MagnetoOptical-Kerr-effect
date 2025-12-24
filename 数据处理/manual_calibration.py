#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
手动定标脚本
从定标.txt文件中读取角度和信号输出数据
按 s = k(theta + theta_0) 拟合
其中s是信号输出，theta是角度（分）
输出结果保存到txt文件
"""

import os
import sys
import numpy as np
from datetime import datetime

def read_calibration_data(filepath):
    """
    读取定标数据文件
    格式：角度(分)    信号输出(无单位)
    忽略以#开头的注释行
    """
    angles = []      # 角度（分）
    signals = []     # 信号输出
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # 跳过空行和注释行
                if not line or line.startswith('#'):
                    continue
                
                # 分割数据（可能用空格或制表符分隔）
                parts = line.split()
                if len(parts) >= 2:
                    try:
                        angle = float(parts[0])
                        signal = float(parts[1])
                        angles.append(angle)
                        signals.append(signal)
                    except ValueError:
                        print(f"Warning: Cannot parse line: {line}")
                        continue
    except FileNotFoundError:
        print(f"Error: File not found: {filepath}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: Failed to read file: {e}")
        sys.exit(1)
    
    return np.array(angles), np.array(signals)

def linear_fit(angles, signals):
    """
    执行线性拟合 s = k * (theta + theta_0) = k*theta + k*theta_0
    等价于 y = a*x + b，其中：
    y = s (信号输出)
    x = theta (角度)
    a = k
    b = k * theta_0
    
    使用numpy的polyfit进行一阶多项式拟合
    """
    # 使用最小二乘法拟合一次多项式
    coefficients = np.polyfit(angles, signals, 1)
    
    # coefficients[0] = a = k
    # coefficients[1] = b = k * theta_0
    k = coefficients[0]
    theta_0 = coefficients[1] / k if k != 0 else 0
    
    return k, theta_0, coefficients

def calculate_r_squared(angles, signals, k, theta_0):
    """
    计算R^2（拟合优度）
    R^2 = 1 - (SS_res / SS_tot)
    """
    # 预测值
    predicted = k * (angles + theta_0)
    
    # 残差平方和
    ss_res = np.sum((signals - predicted) ** 2)
    
    # 总平方和
    ss_tot = np.sum((signals - np.mean(signals)) ** 2)
    
    # R^2
    r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
    
    return r_squared

def save_results_to_file(output_file, angles, signals, k, theta_0, 
                         coefficients, r_squared, theta_0_deg, 
                         k_deg_per_signal, file_coefficient, relative_error):
    """
    将结果保存到文本文件
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 60 + "\n")
        f.write("手动定标分析结果\n")
        f.write("=" * 60 + "\n")
        f.write(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"数据文件: 20251217/定标.txt\n")
        f.write(f"数据点数: {len(angles)}\n\n")
        
        f.write("原始数据:\n")
        f.write("角度(分)   信号输出\n")
        for angle, signal in zip(angles, signals):
            f.write(f"{angle:8.1f} {signal:12.6f}\n")
        
        f.write("\n" + "=" * 60 + "\n")
        f.write("拟合结果\n")
        f.write("=" * 60 + "\n")
        f.write(f"拟合公式: s = k * (theta + theta_0)\n")
        f.write(f"斜率 k = {k:.6e} 信号单位/分\n")
        f.write(f"偏移 theta_0 = {theta_0:.6f} 分\n")
        f.write(f"偏移 theta_0 = {theta_0_deg:.6f} 度\n")
        f.write(f"线性系数: a = {coefficients[0]:.6e}, b = {coefficients[1]:.6e}\n")
        f.write(f"拟合优度 R^2 = {r_squared:.6f}\n\n")
        
        f.write("与文件中提供的定标系数比较:\n")
        f.write(f"文件中提供的系数: {file_coefficient:.6e} 度/信号单位\n")
        f.write(f"拟合得到的系数 k = {k:.6e} 信号单位/分\n")
        f.write(f"拟合得到的系数 k*60 = {k_deg_per_signal:.6e} 度/信号单位\n")
        f.write(f"相对误差: {relative_error:.2f}%\n\n")
        
        f.write("数据点与拟合曲线对比:\n")
        f.write("角度(分)  实际信号    预测信号    残差\n")
        for i in range(len(angles)):
            predicted = k * (angles[i] + theta_0)
            residual = signals[i] - predicted
            f.write(f"{angles[i]:8.1f} {signals[i]:12.6f} {predicted:12.6f} {residual:12.6f}\n")
        
        f.write("\n" + "=" * 60 + "\n")
        f.write("拟合参数总结:\n")
        f.write("=" * 60 + "\n")
        # 计算k以度为单位的系数：k_deg = k * 60 (信号单位/度)
        k_deg = k * 60.0
        f.write(f"k = {k_deg:.6e} 信号单位/度\n")
        f.write(f"theta_0 = {theta_0:.6f} 分\n")
        f.write(f"theta_0 = {theta_0_deg:.6f} 度\n")
        f.write(f"R^2 = {r_squared:.6f}\n")
        
    print(f"\n结果已保存到文件: {output_file}")

def main():
    # 数据文件路径
    data_file = "20251217/定标.txt"
    # 输出文件路径
    output_file = "数据处理/calibration_results.txt"
    
    print("=" * 50)
    print("Manual Calibration Analysis")
    print("=" * 50)
    print(f"Reading data file: {data_file}")
    
    # 读取数据
    angles, signals = read_calibration_data(data_file)
    
    print(f"Read {len(angles)} data points")
    print("Angle(min)  Signal Output")
    for angle, signal in zip(angles, signals):
        print(f"{angle:8.1f} {signal:12.6f}")
    
    # 执行拟合
    k, theta_0, coefficients = linear_fit(angles, signals)
    
    # 计算R^2
    r_squared = calculate_r_squared(angles, signals, k, theta_0)
    
    # 将theta_0转换为度
    theta_0_deg = theta_0 / 60.0
    
    # 将k转换为度/信号单位以便比较
    k_deg_per_signal = k * 60.0
    
    # 计算相对误差
    file_coefficient = 5.77573876180815E-02
    if k != 0:
        relative_error = abs(k_deg_per_signal - file_coefficient) / file_coefficient * 100
    else:
        relative_error = 0
    
    print("\n" + "=" * 50)
    print("Fitting Results")
    print("=" * 50)
    print(f"Fitting formula: s = k * (theta + theta_0)")
    print(f"Slope k = {k:.6e}")
    print(f"Offset theta_0 = {theta_0:.6f} min")
    print(f"Offset theta_0 = {theta_0_deg:.6f} deg")
    print(f"Linear coefficients: a = {coefficients[0]:.6e}, b = {coefficients[1]:.6e}")
    print(f"Goodness of fit R^2 = {r_squared:.6f}")
    
    print("\n" + "=" * 50)
    print("Comparison with calibration coefficient in file")
    print("=" * 50)
    print("Calibration coefficient in file: 5.77573876180815E-02 deg/signal unit")
    print(f"Fitted coefficient k = {k:.6e} signal unit/min")
    print(f"Fitted coefficient k*60 = {k_deg_per_signal:.6e} deg/signal unit")
    print(f"Relative error: {relative_error:.2f}%")
    print(f"Note: File coefficient = {file_coefficient:.6e}")
    print(f"      Fitted k*60 = {k_deg_per_signal:.6e}")
    
    print("\n" + "=" * 50)
    print("Data points vs fitted curve")
    print("=" * 50)
    print("Angle(min)  Actual Signal  Predicted Signal  Residual")
    for i in range(len(angles)):
        predicted = k * (angles[i] + theta_0)
        residual = signals[i] - predicted
        print(f"{angles[i]:8.1f} {signals[i]:12.6f} {predicted:12.6f} {residual:12.6f}")
    
    # 保存结果到文件
    save_results_to_file(output_file, angles, signals, k, theta_0, 
                        coefficients, r_squared, theta_0_deg, 
                        k_deg_per_signal, file_coefficient, relative_error)

if __name__ == "__main__":
    main()

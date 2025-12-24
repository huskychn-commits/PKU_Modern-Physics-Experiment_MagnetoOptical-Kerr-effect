#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
find_centre.py - 数据处理脚本
包含读取测试数据并绘图的函数
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import matplotlib

# 设置中文字体
def setup_chinese_font():
    """设置matplotlib中文字体支持"""
    # Windows系统中的中文字体
    font_names = [
        'Microsoft YaHei',     # 微软雅黑
        'SimHei',              # 黑体
        'SimSun',              # 宋体
        'FangSong',            # 仿宋
        'KaiTi',               # 楷体
        'Arial Unicode MS',    # Arial Unicode MS
        'DejaVu Sans'          # DejaVu Sans
    ]
    
    # 尝试设置中文字体
    for font_name in font_names:
        try:
            matplotlib.rcParams['font.sans-serif'] = [font_name]
            matplotlib.rcParams['axes.unicode_minus'] = False  # 正确显示负号
            print(f"已设置中文字体: {font_name}")
            return True
        except:
            continue
    
    print("警告: 未找到合适的中文字体，使用默认字体")
    return False


def plot_data(x_data, y_data, title="测试数据可视化", ax=None):
    """
    绘制第一列和第三列数据
    
    参数:
    x_data (array-like): x坐标数据
    y_data (array-like): y坐标数据
    title (str): 图形标题，默认为"测试数据可视化"
    ax (matplotlib.axes.Axes, optional): 要绘图的轴对象。如果为None，则创建新的图形和轴
    
    返回:
    matplotlib.axes.Axes: 绘制数据的轴对象
    """
    if x_data is None or y_data is None:
        return ax
    
    # 如果没有传入ax，则创建新的图形和轴
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 6))
        created_fig = True
    else:
        created_fig = False
    
    # 绘制散点图
    ax.scatter(x_data, y_data, color='blue', alpha=0.7, label='数据点', s=50)
        
    # 绘制连线（闭合：最后一个点连接到第一个点）
    # 创建闭合的数据：将第一个点添加到末尾
    x_closed = np.append(x_data, x_data[0])
    y_closed = np.append(y_data, y_data[0])
    ax.plot(x_closed, y_closed, color='red', alpha=0.5, linewidth=1, label='趋势线（闭合）')
        
    # 设置图形属性
    ax.set_title(title, fontsize=16)
    ax.set_xlabel("磁场/mT", fontsize=12)
    ax.set_ylabel("克尔转角/deg", fontsize=12)
    ax.grid(True, alpha=0.3)
    ax.legend()
    
    # 如果创建了新的图形，则自动调整布局
    if created_fig:
        plt.tight_layout()
    
    return ax
    

def read_testdata(csv_filepath=None, plot_graph=True):
    """
    从CSV文件中读取第一列和第三列数据
    
    参数:
    csv_filepath (str): CSV文件路径。如果为None，则使用默认路径
    plot_graph (bool): 是否绘制图像，默认为True
    
    返回:
    tuple: (x_data, y_data) 第一列和第三列数据，如果读取失败则返回(None, None)
    """
    # 设置默认文件路径
    if csv_filepath is None:
        # 默认路径：20251217/temp/test_findcentre.csv
        csv_filepath = os.path.join("20251217", "temp", "test_findcentre.csv")
    
    def read_csv_data(filepath):
        """内部函数：读取CSV文件并提取第一列和第三列"""
        try:
            # 读取CSV文件
            df = pd.read_csv(filepath)
            
            # 检查是否有足够的列
            if len(df.columns) < 3:
                raise ValueError(f"CSV文件需要至少3列，但只有{len(df.columns)}列")
            
            # 提取第一列和第三列
            # 假设第一列是Position，第三列是Measurement2
            x_data = df.iloc[:, 0].values  # 第一列
            y_data = df.iloc[:, 2].values  # 第三列
            
            return x_data, y_data
            
        except FileNotFoundError:
            return None, None
        except Exception as e:
            return None, None
    
    def plot_data(x_data, y_data, title="测试数据可视化"):
        """内部函数：绘制第一列和第三列数据"""
        # 调用外部的 plot_data 函数
        ax = globals()['plot_data'](x_data, y_data, title=title)
        # 显示图形（保持原有行为）
        if ax is not None:
            plt.show()
    
    # 读取数据
    x_data, y_data = read_csv_data(csv_filepath)
    
    # 如果成功读取数据且需要绘图，则绘图
    if x_data is not None and y_data is not None and plot_graph:
        plot_data(x_data, y_data, title="测试数据")
    
    return x_data, y_data


def parity_transform(x_data, y_data, x_c=0.0, y_c=0.0):
    """
    对数据点进行中心对称变换和循环移位
    
    参数:
    x_data (array-like): x坐标数据
    y_data (array-like): y坐标数据
    x_c (float): 对称中心x坐标，默认为0.0
    y_c (float): 对称中心y坐标，默认为0.0
    
    返回:
    tuple: (x_transformed, y_transformed) 变换后的x和y数据
    
    异常:
    ValueError: 如果数据长度不是偶数
    """
    import copy
    import numpy as np
    
    # 深拷贝输入数据
    x = copy.deepcopy(x_data)
    y = copy.deepcopy(y_data)
    
    # 转换为numpy数组以确保操作一致性
    x = np.array(x)
    y = np.array(y)
    
    # 检查数据长度是否为偶数
    N = len(x)
    if N != len(y):
        raise ValueError(f"x和y数据长度不一致: len(x)={N}, len(y)={len(y)}")
    
    if N % 2 != 0:
        raise ValueError(f"数据长度必须是偶数，当前长度: {N}")
    
    # 步骤1: 对每个数据点进行中心对称操作
    # 新点 = (2*x_c - x[i], 2*y_c - y[i])
    x_sym = 2 * x_c - x
    y_sym = 2 * y_c - y
    
    # 步骤2: 计算需要移动的位数
    shift = N // 2
    
    # 步骤3: 循环移位数据
    # 使用numpy的roll函数进行循环移位
    x_transformed = np.roll(x_sym, shift)
    y_transformed = np.roll(y_sym, shift)
    
    return x_transformed, y_transformed


def find_ycentre(y_data):
    """
    寻找使loss函数最小的y_opt值
    
    参数:
    x_data (array-like): x坐标数据
    y_data (array-like): y坐标数据
    
    返回:
    float: 最优的y_opt值
    
    数学推导:
    定义loss函数 L(y_opt) = Σ_i [(x[i] - x_trans[i])² + (y[i] - y_trans[i])²]
    其中 (x_trans[i], y_trans[i]) 是经过 parity_transform 变换后的点，
    变换中心为 (x_c=0, y_c=y_opt)。
    
    根据 parity_transform 的定义：
    1. 中心对称操作：点变为 (-x[i], 2*y_opt - y[i])
    2. 循环移位：移动 N//2 位，其中 N 是数据点数量
    
    因此，变换后的点为：
    x_trans[i] = -x[j], 其中 j = (i + N//2) mod N
    y_trans[i] = 2*y_opt - y[j], 其中 j = (i + N//2) mod N
    
    loss函数可写为：
    L(y_opt) = Σ_i [(x[i] + x[j])² + (y[i] + y[j] - 2*y_opt)²]
    
    这是一个关于 y_opt 的二次函数：
    L(y_opt) = Σ_i (x[i] + x[j])² + Σ_i (y[i] + y[j] - 2*y_opt)²
             = A + Σ_i [(y[i] + y[j])² - 4*(y[i] + y[j])*y_opt + 4*y_opt²]
             = A + Σ_i (y[i] + y[j])² - 4*y_opt*Σ_i (y[i] + y[j]) + 4*N*y_opt²
    
    其中 A = Σ_i (x[i] + x[j])² 是与 y_opt 无关的常数。
    
    这是一个关于 y_opt 的二次函数：L(y_opt) = 4N*y_opt² - 4B*y_opt + C
    其中：
    B = Σ_i (y[i] + y[j])
    C = A + Σ_i (y[i] + y[j])²
    
    对 y_opt 求导并令导数为零：
    dL/dy_opt = 8N*y_opt - 4B = 0
    => y_opt = B/(2N)
    
    由于 j = (i + N//2) mod N，每个 y[k] 会出现两次：
    一次作为 y[i]，一次作为 y[j]。所以：
    Σ_i (y[i] + y[j]) = 2Σ_k y[k]
    
    因此：
    y_opt = (1/(2N)) * 2Σ_k y[k] = (1/N) * Σ_k y[k] = mean(y)
    
    结论：使loss函数最小的最优 y_opt 就是 y 数据的均值。
    """
    y=y_data.copy()
    # 根据数学推导，最优的 y_opt 就是 y 数据的均值
    y_opt = np.mean(y)
    
    return y_opt

# 测试代码
if __name__ == "__main__":
    # 初始化中文字体
    setup_chinese_font()
    
    # 测试1: 读取数据
    print("测试: 读取数据")
    x, y = read_testdata(plot_graph=False)  # 不自动绘图，我们手动控制
    
    # 测试2: 测试中心对称变换函数
    if x is not None and y is not None:
        
        try:
            # 计算最优中心
            y_opt = find_ycentre(y)
            print(f"计算得到的最优y中心: {y_opt}")
            
            # 进行中心对称变换
            x_trans, y_trans = parity_transform(x, y, y_c=y_opt)
            
            # 创建图形和坐标轴，将x,y和x_trans,y_trans画在同一个ax上
            fig, ax = plt.subplots(figsize=(12, 8))
            
            # 绘制原始数据
            ax.scatter(x, y, color='blue', alpha=0.7, label='原始数据点', s=50)
            # 绘制原始数据连线（闭合）
            x_closed = np.append(x, x[0])
            y_closed = np.append(y, y[0])
            ax.plot(x_closed, y_closed, color='blue', alpha=0.5, linewidth=1, label='原始趋势线')
            
            # 绘制变换后的数据
            ax.scatter(x_trans, y_trans, color='red', alpha=0.7, label='变换后数据点', s=50, marker='s')
            # 绘制变换后数据连线（闭合）
            x_trans_closed = np.append(x_trans, x_trans[0])
            y_trans_closed = np.append(y_trans, y_trans[0])
            ax.plot(x_trans_closed, y_trans_closed, color='red', alpha=0.5, linewidth=1, linestyle='--', label='变换后趋势线')
            
            # 设置图形属性
            ax.set_title("原始数据与中心对称变换数据对比", fontsize=16)
            ax.set_xlabel("磁场/mT", fontsize=12)
            ax.set_ylabel("克尔转角/deg", fontsize=12)
            ax.grid(True, alpha=0.3)
            ax.legend()
            
            # 添加中心点标记
            ax.scatter(0, y_opt, color='green', s=100, marker='*', label=f'对称中心 (0, {y_opt:.4f})', zorder=5)
            
            plt.tight_layout()
            plt.show()
            
        except ValueError as e:
            print(f"错误: {e}")

"""
磁滞回线特征提取模块
包含计算矫顽力等磁滞回线特征的功能
"""

import json
import math


def calculate_coercivity(x, y):
    """
    计算矫顽力（磁滞回线围成的面积）
    
    参数:
    x: list, 横坐标数据（磁场强度）
    y: list, 纵坐标数据（磁化强度）
    
    返回:
    float: 矫顽力（积分结果）
    
    说明:
    使用梯形积分法计算磁滞回线围成的面积。
    数据点按顺序连接，积分方向根据x的变化方向决定正负。
    """
    if len(x) != len(y):
        raise ValueError("x和y数组长度必须相同")
    
    if len(x) < 2:
        raise ValueError("至少需要2个数据点")
    
    total_area = 0.0
    
    for i in range(len(x) - 1):
        x1, x2 = x[i], x[i + 1]
        y1, y2 = y[i], y[i + 1]
        
        # 梯形面积公式：0.5 * (y1 + y2) * (x2 - x1)
        # 注意：这里计算的是曲线与x轴围成的面积
        trapezoid_area = 0.5 * (y1 + y2) * (x2 - x1)
        total_area += trapezoid_area
    
    return total_area


def test_with_json_data():
    """使用improved_angle_data.json中的第一个实验数据测试函数"""
    try:
        # 获取当前脚本所在目录
        import os
        script_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(script_dir, 'improved_angle_data.json')
        
        # 读取JSON文件
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 获取第一个实验的数据
        first_experiment = data['data'][0]
        x_data = first_experiment[0]
        y_data = first_experiment[1]
        
        print(f"第一个实验数据信息:")
        print(f"  数据点数量: {len(x_data)}")
        print(f"  x范围: [{min(x_data):.2f}, {max(x_data):.2f}]")
        print(f"  y范围: [{min(y_data):.4f}, {max(y_data):.4f}]")
        
        # 计算矫顽力
        coercivity = calculate_coercivity(x_data, y_data)
        
        print(f"\n计算结果:")
        print(f"  矫顽力（积分面积）: {coercivity:.6f}")
        
        # 计算绝对值面积（物理意义上的面积大小）
        abs_area = abs(coercivity)
        print(f"  绝对值面积: {abs_area:.6f}")
        
        return coercivity
        
    except FileNotFoundError:
        print("错误: 未找到improved_angle_data.json文件")
        print("请确保文件在当前目录下")
        return None
    except Exception as e:
        print(f"错误: {e}")
        return None


def calculate_all_coercivities():
    """
    计算两个JSON文件中所有实验的矫顽力和平均饱和值
    
    返回:
    dict: 包含两个文件所有实验矫顽力和平均饱和值的字典
    """
    import os
    
    # 获取当前脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 两个JSON文件的路径
    angle_json_path = os.path.join(script_dir, 'improved_angle_data.json')
    ellipticity_json_path = os.path.join(script_dir, 'improved_ellipticity_data.json')
    
    results = {
        'angle_coercivities': [],
        'ellipticity_coercivities': [],
        'angle_saturation_values': [],  # 角度数据平均饱和值
        'ellipticity_saturation_values': []  # 椭率数据平均饱和值
    }
    
    try:
        # 读取角度数据
        with open(angle_json_path, 'r', encoding='utf-8') as f:
            angle_data = json.load(f)
        
        # 读取椭率数据
        with open(ellipticity_json_path, 'r', encoding='utf-8') as f:
            ellipticity_data = json.load(f)
        
        # 计算角度数据的矫顽力
        print("计算角度数据矫顽力...")
        for i, experiment in enumerate(angle_data['data']):
            x_data = experiment[0]
            y_data = experiment[1]
            coercivity = calculate_coercivity(x_data, y_data)
            results['angle_coercivities'].append(coercivity)
            print(f"  实验{i+1}: {coercivity:.6f}")
        
        # 计算椭率数据的矫顽力
        print("\n计算椭率数据矫顽力...")
        for i, experiment in enumerate(ellipticity_data['data']):
            x_data = experiment[0]
            y_data = experiment[1]
            coercivity = calculate_coercivity(x_data, y_data)
            results['ellipticity_coercivities'].append(coercivity)
            print(f"  实验{i+1}: {coercivity:.6f}")
        
        # 计算角度数据的平均饱和值 (max_ave - min_ave)/2
        print("\n计算角度数据平均饱和值...")
        if 'max_ave' in angle_data and 'min_ave' in angle_data:
            max_ave = angle_data['max_ave']
            min_ave = angle_data['min_ave']
            for i in range(len(max_ave)):
                saturation = (max_ave[i] - min_ave[i]) / 2
                results['angle_saturation_values'].append(saturation)
                print(f"  实验{i+1}: {saturation:.6f}")
        
        # 计算椭率数据的平均饱和值 (max_ave - min_ave)/2
        print("\n计算椭率数据平均饱和值...")
        if 'max_ave' in ellipticity_data and 'min_ave' in ellipticity_data:
            max_ave = ellipticity_data['max_ave']
            min_ave = ellipticity_data['min_ave']
            for i in range(len(max_ave)):
                saturation = (max_ave[i] - min_ave[i]) / 2
                results['ellipticity_saturation_values'].append(saturation)
                print(f"  实验{i+1}: {saturation:.6f}")
        
        return results
        
    except FileNotFoundError as e:
        print(f"错误: 未找到文件 - {e}")
        return None
    except Exception as e:
        print(f"错误: {e}")
        return None


def print_coercivity_table(results):
    """
    以表格形式打印矫顽力和平均饱和值结果
    
    参数:
    results: dict, 包含两个文件所有实验矫顽力和平均饱和值的字典
    """
    if not results:
        print("无有效结果可显示")
        return
    
    angle_coercivities = results['angle_coercivities']
    ellipticity_coercivities = results['ellipticity_coercivities']
    angle_saturation_values = results.get('angle_saturation_values', [])
    ellipticity_saturation_values = results.get('ellipticity_saturation_values', [])
    
    # 检查数据长度
    if len(angle_coercivities) != len(ellipticity_coercivities):
        print("警告: 两个文件的矫顽力数据长度不一致")
    
    if angle_saturation_values and ellipticity_saturation_values:
        if len(angle_saturation_values) != len(ellipticity_saturation_values):
            print("警告: 两个文件的平均饱和值数据长度不一致")
    
    # 打印表头 - 增加平均饱和值列
    print("\n" + "=" * 90)
    print("磁滞回线特征计算结果表格")
    print("=" * 90)
    print(f"{'实验编号':<10} {'角度矫顽力':<15} {'角度平均饱和':<15} {'椭率矫顽力':<15} {'椭率平均饱和':<15}")
    print("-" * 90)
    
    # 确定要显示的行数
    num_rows = max(len(angle_coercivities), len(ellipticity_coercivities),
                   len(angle_saturation_values), len(ellipticity_saturation_values))
    
    # 打印数据行
    for i in range(num_rows):
        # 获取角度数据
        angle_val = angle_coercivities[i] if i < len(angle_coercivities) else "N/A"
        angle_sat = angle_saturation_values[i] if i < len(angle_saturation_values) else "N/A"
        
        # 获取椭率数据
        ellipticity_val = ellipticity_coercivities[i] if i < len(ellipticity_coercivities) else "N/A"
        ellipticity_sat = ellipticity_saturation_values[i] if i < len(ellipticity_saturation_values) else "N/A"
        
        # 格式化角度数据
        if isinstance(angle_val, float):
            angle_str = f"{angle_val:>10.6f}"
        else:
            angle_str = str(angle_val).rjust(10)
            
        if isinstance(angle_sat, float):
            angle_sat_str = f"{angle_sat:>10.6f}"
        else:
            angle_sat_str = str(angle_sat).rjust(10)
        
        # 格式化椭率数据
        if isinstance(ellipticity_val, float):
            ellipticity_str = f"{ellipticity_val:>10.6f}"
        else:
            ellipticity_str = str(ellipticity_val).rjust(10)
            
        if isinstance(ellipticity_sat, float):
            ellipticity_sat_str = f"{ellipticity_sat:>10.6f}"
        else:
            ellipticity_sat_str = str(ellipticity_sat).rjust(10)
        
        print(f"{i+1:<10} {angle_str:<15} {angle_sat_str:<15} {ellipticity_str:<15} {ellipticity_sat_str:<15}")
    
    print("=" * 90)
    
    # 计算统计信息
    if all(isinstance(val, float) for val in angle_coercivities) and all(isinstance(val, float) for val in ellipticity_coercivities):
        print("\n矫顽力统计信息:")
        print(f"角度数据矫顽力平均值: {sum(angle_coercivities)/len(angle_coercivities):.6f}")
        print(f"椭率数据矫顽力平均值: {sum(ellipticity_coercivities)/len(ellipticity_coercivities):.6f}")
    
    if angle_saturation_values and ellipticity_saturation_values:
        if all(isinstance(val, float) for val in angle_saturation_values) and all(isinstance(val, float) for val in ellipticity_saturation_values):
            print("\n平均饱和值统计信息:")
            print(f"角度数据平均饱和值平均值: {sum(angle_saturation_values)/len(angle_saturation_values):.6f}")
            print(f"椭率数据平均饱和值平均值: {sum(ellipticity_saturation_values)/len(ellipticity_saturation_values):.6f}")


def save_results_to_csv(results, filename="hysteresis_results.csv"):
    """
    将结果保存为CSV文件
    
    参数:
    results: dict, 包含两个文件所有实验矫顽力和平均饱和值的字典
    filename: str, CSV文件名
    """
    if not results:
        print("无有效结果可保存")
        return False
    
    import os
    import csv
    
    angle_coercivities = results['angle_coercivities']
    ellipticity_coercivities = results['ellipticity_coercivities']
    angle_saturation_values = results.get('angle_saturation_values', [])
    ellipticity_saturation_values = results.get('ellipticity_saturation_values', [])
    
    # 获取当前脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(script_dir, filename)
    
    try:
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # 写入表头
            writer.writerow(['实验编号', '角度矫顽力', '角度平均饱和值', '椭率矫顽力', '椭率平均饱和值'])
            
            # 确定要写入的行数
            num_rows = max(len(angle_coercivities), len(ellipticity_coercivities),
                           len(angle_saturation_values), len(ellipticity_saturation_values))
            
            # 写入数据行
            for i in range(num_rows):
                # 获取角度数据
                angle_val = angle_coercivities[i] if i < len(angle_coercivities) else ""
                angle_sat = angle_saturation_values[i] if i < len(angle_saturation_values) else ""
                
                # 获取椭率数据
                ellipticity_val = ellipticity_coercivities[i] if i < len(ellipticity_coercivities) else ""
                ellipticity_sat = ellipticity_saturation_values[i] if i < len(ellipticity_saturation_values) else ""
                
                # 写入一行数据
                writer.writerow([i+1, angle_val, angle_sat, ellipticity_val, ellipticity_sat])
            
            # 写入统计信息
            writer.writerow([])  # 空行
            writer.writerow(['统计信息', '', '', '', ''])
            
            if all(isinstance(val, float) for val in angle_coercivities) and all(isinstance(val, float) for val in ellipticity_coercivities):
                writer.writerow(['矫顽力平均值', 
                                sum(angle_coercivities)/len(angle_coercivities),
                                '',
                                sum(ellipticity_coercivities)/len(ellipticity_coercivities),
                                ''])
            
            if angle_saturation_values and ellipticity_saturation_values:
                if all(isinstance(val, float) for val in angle_saturation_values) and all(isinstance(val, float) for val in ellipticity_saturation_values):
                    writer.writerow(['平均饱和值平均值',
                                    sum(angle_saturation_values)/len(angle_saturation_values),
                                    '',
                                    sum(ellipticity_saturation_values)/len(ellipticity_saturation_values),
                                    ''])
        
        print(f"\n结果已保存到: {csv_path}")
        return True
        
    except Exception as e:
        print(f"保存CSV文件时出错: {e}")
        return False


if __name__ == "__main__":
    print("=" * 50)
    print("磁滞回线特征提取程序")
    print("=" * 50)
    
    # 测试单个实验
    print("\n[测试单个实验]")
    result = test_with_json_data()
    
    # 计算所有实验
    print("\n[计算所有实验]")
    all_results = calculate_all_coercivities()
    
    if all_results:
        # 打印表格
        print_coercivity_table(all_results)
        
        # 保存结果到CSV文件
        save_results_to_csv(all_results, "hysteresis_results.csv")
    
    print("\n" + "=" * 50)
    print("测试完成")
    print("=" * 50)

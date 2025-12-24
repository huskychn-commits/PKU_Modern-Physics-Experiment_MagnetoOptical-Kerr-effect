#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将test_findcentre.txt文件转换为CSV格式
"""

import csv
import re

def convert_txt_to_csv(input_file, output_file):
    """
    将文本文件转换为CSV格式
    
    参数:
    input_file: 输入文本文件路径
    output_file: 输出CSV文件路径
    """
    try:
        # 读取原始文件
        with open(input_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 准备数据
        data_rows = []
        
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue
            
            # 使用正则表达式提取三个数字
            pattern = r'[-]?\d*\.?\d+'
            numbers = re.findall(pattern, line)
            
            if len(numbers) >= 3:
                col1 = numbers[0]
                col2 = numbers[1]
                col3 = numbers[2]
                
                # 修复第二列和第三列的格式（如果以点开头）
                if col2.startswith('.'):
                    col2 = '0' + col2
                elif col2.startswith('-.'):
                    col2 = '-0' + col2[1:]
                
                if col3.startswith('.'):
                    col3 = '0' + col3
                elif col3.startswith('-.'):
                    col3 = '-0' + col3[1:]
                
                # 转换为浮点数（CSV中存储为数字）
                try:
                    row = [float(col1), float(col2), float(col3)]
                    data_rows.append(row)
                except ValueError as e:
                    print(f"警告: 第{line_num}行转换数字失败: {line}")
                    print(f"错误: {e}")
            else:
                print(f"警告: 第{line_num}行数据列数不足: {line}")
        
        # 写入CSV文件
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # 写入列标题
            writer.writerow(['Position', 'Measurement1', 'Measurement2'])
            
            # 写入数据行
            writer.writerows(data_rows)
        
        print(f"转换完成!")
        print(f"输入文件: {input_file}")
        print(f"输出文件: {output_file}")
        print(f"转换行数: {len(data_rows)}")
        
        # 显示前3行数据示例
        if len(data_rows) > 0:
            print("\n前3行数据示例:")
            print("Position, Measurement1, Measurement2")
            for i in range(min(3, len(data_rows))):
                print(f"{data_rows[i][0]}, {data_rows[i][1]}, {data_rows[i][2]}")
        
    except FileNotFoundError:
        print(f"错误: 文件未找到: {input_file}")
        return False
    except Exception as e:
        print(f"错误: {e}")
        return False
    
    return True

def main():
    # 输入输出文件路径
    input_file = "test_findcentre.txt"
    output_file = "test_findcentre.csv"
    
    print("=" * 50)
    print("文本文件转CSV工具")
    print("=" * 50)
    
    # 执行转换
    success = convert_txt_to_csv(input_file, output_file)
    
    if success:
        print("\n" + "=" * 50)
        print("转换成功完成!")
        print("=" * 50)
    else:
        print("\n" + "=" * 50)
        print("转换失败!")
        print("=" * 50)

if __name__ == "__main__":
    main()

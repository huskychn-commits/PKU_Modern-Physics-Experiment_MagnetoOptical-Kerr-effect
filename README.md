# 磁光克尔效应实验项目

## 项目概述

本项目为北京大学近代物理实验课程中的磁光克尔效应实验，通过光弹调制器（PEM）系统研究磁性材料在外磁场作用下反射光偏振态的变化现象。实验重点测量极克尔效应下的克尔转角（θ_K）和克尔椭偏率（ε_K），验证理论模型，并为磁性材料表征提供可靠的实验方法。

**实验者**：本项目作者

**关键词**：磁光克尔效应、光弹调制器、克尔系数、磁滞回线、偏振调制

## 实验原理与依据

本实验的详细原理和理论推导可在以下文件中找到：

1. **[实验报告.pdf](实验报告.pdf)** - 完整介绍了实验方法、操作步骤、数据处理流程和实验结果分析
2. **[理论推导.md](理论推导.md)** - 提供了完整的数学推导，包括：
   - 磁光克尔效应的基本理论
   - 光弹调制器（PEM）系统的Jones矩阵分析
   - 45度检偏器配置下的信号解调原理
   - 入射光椭偏率对测量信号的影响分析
   - 两个介质界面反射的偏振态分析
   - 旋转半波片替代光弹调制器的理论推导

这些文档共同构成了本实验的理论基础，建议在深入了解实验细节时参考这些文件。

## 项目文件结构

```
磁光克尔效应/
├── README.md                          # 本项目说明文档
├── 理论推导.md                         # 完整的理论推导文档
├── 实验报告.pdf                        # 实验报告（PDF格式）
├── 实验报告.docx                       # 实验报告（Word格式）
├── 磁光克尔效应.pdf                    # 实验指导书
├── 总结文档.md                         # 实验总结
├── 20251217/                          # 原始实验数据目录
│   ├── 0deg.dat ~ 4deg.dat            # 不同起偏器角度的原始数据
│   ├── 定标.txt                        # 定标数据
│   └── dingbiao.dat                   # 定标数据文件
└── 数据处理/                           # 数据处理模块目录
    ├── README.md                      # 数据处理模块说明
    ├── experiment_data.json           # 实验数据汇总
    ├── calibration_curve.png          # 校准曲线图
    ├── kerr_relation.png              # 克尔关系图
    ├── 克尔转角_improved.png           # 改进后的克尔转角图
    ├── 克尔椭率_improved.png           # 改进后的克尔椭率图
    ├── hysteresis_results.csv         # 磁滞回线结果
    └── *.py                           # 各种数据处理脚本（共13个）
```

## 数据处理模块

数据处理模块包含13个Python脚本，用于实验数据的处理、分析和可视化：

### 核心脚本功能

1. **`read_data.py`** - 读取原始实验数据文件（.dat格式）
2. **`hysteresis_calibration.py`** - 进行线性校准，分析克尔转角中心值与起偏器额外转角的关系
3. **`hysteresis_feature.py`** - 从磁滞回线数据中提取关键特征参数（饱和磁化强度、矫顽力等）
4. **`kerr_relation.py`** - 分析克尔转角与克尔椭偏率之间的关系
5. **`reflection_correction.py`** - 计算两个介质界面反射的偏振态变化（基于理论推导第6章）
6. **`plot_improved_angle.py`** - 绘制经过改进处理的克尔转角数据
7. **`plot_improved_ellipticity.py`** - 绘制经过改进处理的克尔椭率数据

### 数据处理流程

1. **数据定标验证**：使用`manual_calibration.py`验证实验数据中使用的定标率正确性
2. **定标关系验证**：使用`hysteresis_calibration.py`验证定标关系的准确性
3. **数据读取与预处理**：使用`read_data.py`读取原始实验数据
4. **数据质量评估**：使用`plot_modified_data.py`初步观察原始数据的形状
5. **数据改进与饱和值分析**：使用`plot_improved_angle.py`和`plot_improved_ellipticity.py`绘制改进后的数据
6. **磁滞特征提取**：使用`hysteresis_feature.py`获取关键磁滞特征参数
7. **克尔关系分析**：使用`kerr_relation.py`分析克尔转角与克尔椭率之间的相关性
8. **理论辅助分析**：使用`reflection_correction.py`展示理论上反射镜的额外效应对偏振态的影响

## 使用方法

### 环境要求
- Python 3.6+
- 依赖库：numpy, matplotlib, pandas, scipy

### 运行示例
```bash
# 进入数据处理目录
cd 数据处理

# 运行反射校正分析
python reflection_correction.py --visualize

# 运行磁滞回线校准
python hysteresis_calibration.py

# 运行克尔关系分析
python kerr_relation.py
```

### 数据可视化
大多数脚本都包含可视化功能，可以直接生成图表文件（PNG格式）。使用`--visualize`参数或按照提示选择可视化选项。

## 参考文献

1. 《近代物理实验》(第四版) - 吴思诚，荀坤，高等教育出版社，2015
2. Q. Zhan, "Magneto-optical Kerr effect and its applications," *Journal of Physics: Condensed Matter*, vol. 19, no. 8, p. 083001, 2007.
3. J. Kerr, "On rotation of the plane of polarization by reflection from the pole of a magnet," *Philosophical Magazine*, vol. 3, pp. 321-343, 1877.
4. P. N. Argyres, "Theory of the Faraday and Kerr effects in ferromagnetics," *Physical Review*, vol. 97, no. 2, pp. 334-345, 1955.
5. 赵凯华, 钟锡华. 《光学》. 北京大学出版社, 1984.

## 许可证

本项目为北京大学近代物理实验课程作业，仅供学习和研究使用。

---

**最后更新**：2025年12月24日  
**实验完成时间**：2025年秋季学期

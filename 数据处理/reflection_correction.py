"""
反射光偏振态计算模块

根据理论推导.md第6章"两个介质界面反射的偏振态分析"实现严格计算。
用于计算从光密介质到光疏介质反射时，反射光的偏振态变化。

作者：磁光克尔效应实验数据处理
日期：2025-12-24
"""

import numpy as np
import cmath
from typing import Tuple

def calculate_reflection_polarization(
    n: float, 
    alpha: float, 
    theta: float
) -> Tuple[float, float, complex, complex, bool]:
    """
    计算两个介质界面反射的偏振态（严格计算版本）
    
    根据菲涅尔公式严格计算反射光的偏振态，包含小于临界角和全反射两种情形。
    
    参数：
    ----------
    n : float
        相对折射率 n = n1/n2 > 1（光密介质折射率/光疏介质折射率）
    alpha : float
        入射光偏振方向角（弧度），与s偏振方向的夹角
        0 ≤ alpha ≤ π/2，其中：
        - alpha = 0：纯s偏振
        - alpha = π/2：纯p偏振
        - alpha = π/4：45度线偏振
    theta : float
        入射角（弧度），0 ≤ theta < π/2
    
    返回：
    -------
    tuple: (alpha_prime, eta, rs, rp, is_total_reflection)
        alpha_prime : float
            反射光偏振椭圆主轴方向角（弧度），即反射光的光强最大方向
        eta : float
            反射光椭偏角（弧度），满足 tan(eta) = ε，其中ε为轴比
            对于线偏振光，η = 0；对于圆偏振光，η = π/4
        rs : complex
            s偏振反射系数（复数）
        rp : complex
            p偏振反射系数（复数）
        is_total_reflection : bool
            是否发生全反射
    
    数学基础：
    ----------
    1. 菲涅尔反射系数：
        r_s = (n1 cosθ - n2 cosθ₂) / (n1 cosθ + n2 cosθ₂)
        r_p = (n2 cosθ - n1 cosθ₂) / (n2 cosθ + n1 cosθ₂)
    
    2. 斯涅尔定律：
        n1 sinθ = n2 sinθ₂  =>  sinθ₂ = n sinθ
    
    3. 临界角：
        θ_c = arcsin(1/n)
        当 θ > θ_c 时发生全反射
    
    4. 反射光偏振态：
        - 小于临界角：反射光为线偏振光，η = 0
        - 全反射：反射光为椭圆偏振光，η ≠ 0
    
    参考文献：
    ----------
    理论推导.md 第6章 "两个介质界面反射的偏振态分析"
    """
    
    # 参数验证
    if n <= 1:
        raise ValueError(f"相对折射率 n 必须大于 1，当前 n = {n}")
    if not (0 <= alpha <= np.pi/2):
        raise ValueError(f"偏振角 alpha 必须在 [0, π/2] 范围内，当前 alpha = {alpha}")
    if not (0 <= theta < np.pi/2):
        raise ValueError(f"入射角 theta 必须在 [0, π/2) 范围内，当前 theta = {theta}")
    
    # 计算临界角
    theta_c = np.arcsin(1.0 / n)
    
    # 根据斯涅尔定律计算 sinθ₂ 和 cosθ₂
    sin_theta2 = n * np.sin(theta)
    
    # 判断是否发生全反射
    is_total_reflection = sin_theta2 > 1.0
    
    if not is_total_reflection:
        # 小于临界角情形：θ₂ 为实数
        cos_theta2 = np.sqrt(1.0 - sin_theta2**2)
        
        # 计算菲涅尔反射系数（实数）
        numerator_s = np.cos(theta) - cos_theta2 / n  # n1 cosθ - n2 cosθ₂，其中 n1/n2 = n
        denominator_s = np.cos(theta) + cos_theta2 / n
        rs = numerator_s / denominator_s
        
        numerator_p = np.cos(theta) - n * cos_theta2  # n2 cosθ - n1 cosθ₂
        denominator_p = np.cos(theta) + n * cos_theta2
        rp = numerator_p / denominator_p
        
        # 反射光为线偏振光
        # 偏振方向角 ψ = arctan[(r_p/r_s) tanα]
        if rs == 0:
            # 如果 r_s = 0，则反射光为纯p偏振
            if rp >= 0:
                alpha_prime = np.pi/2
            else:
                alpha_prime = -np.pi/2
        else:
            ratio = (rp / rs) * np.tan(alpha)
            alpha_prime = np.arctan(ratio)
        
        # 线偏振光，椭偏角 η = 0
        eta = 0.0
        
    else:
        # 全反射情形：θ₂ 为复数，cosθ₂ = exp[iκ]
        kappa = np.sqrt(sin_theta2**2 - 1.0)  # κ = √(n² sin²θ - 1)
        
        # 计算复数反射系数 r_s = e^{-iδ_s}, r_p = e^{-iδ_p}
        # 其中 tan(δ_s/2) = nκ/cosθ, tan(δ_p/2) = κ/(n cosθ)
        
        # 计算相位延迟 δ_s 和 δ_p
        tan_delta_s_half = n * kappa / np.cos(theta)
        tan_delta_p_half = kappa / (n * np.cos(theta))
        
        delta_s = 2.0 * np.arctan(tan_delta_s_half)
        delta_p = 2.0 * np.arctan(tan_delta_p_half)
        
        # 反射系数为模为1的复数
        rs = cmath.exp(-1j * delta_s)
        rp = cmath.exp(-1j * delta_p)
        
        # 相对相位差 Δ = δ_p - δ_s
        delta = delta_p - delta_s
        
        # 计算反射光偏振椭圆参数
        # 根据公式：tan(2ψ) = tan(2α) cosΔ
        # 和：tan(2η) = tan(2α) sinΔ
        
        tan_2alpha = np.tan(2.0 * alpha)
        
        # 计算偏振椭圆主轴方向角 ψ
        if np.abs(tan_2alpha) < 1e-12:
            # 当 α = 0 或 α = π/2 时，tan(2α) = 0
            alpha_prime = alpha
        else:
            tan_2psi = tan_2alpha * np.cos(delta)
            alpha_prime = 0.5 * np.arctan(tan_2psi)
        
        # 计算椭偏角 η
        if np.abs(tan_2alpha) < 1e-12:
            # 当 α = 0 或 α = π/2 时，反射光为线偏振
            eta = 0.0
        else:
            tan_2eta = tan_2alpha * np.sin(delta)
            eta = 0.5 * np.arctan(tan_2eta)
    
    return alpha_prime, eta, rs, rp, is_total_reflection


def calculate_reflection_polarization_deg(
    n: float, 
    alpha_deg: float, 
    theta_deg: float
) -> Tuple[float, float, complex, complex, bool]:
    """
    角度单位为度的版本
    
    参数：
    ----------
    n : float
        相对折射率 n = n1/n2 > 1
    alpha_deg : float
        入射光偏振方向角（度）
    theta_deg : float
        入射角（度）
    
    返回：
    -------
    tuple: (alpha_prime_deg, eta_deg, rs, rp, is_total_reflection)
        alpha_prime_deg : float
            反射光偏振椭圆主轴方向角（度）
        eta_deg : float
            反射光椭偏角（度）
        rs, rp, is_total_reflection : 同 calculate_reflection_polarization
    """
    # 角度转换
    alpha_rad = np.radians(alpha_deg)
    theta_rad = np.radians(theta_deg)
    
    # 调用弧度版本
    alpha_prime_rad, eta_rad, rs, rp, is_total_reflection = calculate_reflection_polarization(
        n, alpha_rad, theta_rad
    )
    
    # 转换回度
    alpha_prime_deg = np.degrees(alpha_prime_rad)
    eta_deg = np.degrees(eta_rad)
    
    return alpha_prime_deg, eta_deg, rs, rp, is_total_reflection


def analyze_reflection_polarization(
    n: float, 
    alpha: float, 
    theta: float,
    use_degrees: bool = False
) -> dict:
    """
    分析反射光偏振态，返回详细结果
    
    参数：
    ----------
    n, alpha, theta : 同 calculate_reflection_polarization
    use_degrees : bool
        输入角度是否为度
    
    返回：
    -------
    dict : 包含详细分析结果的字典
    """
    if use_degrees:
        alpha_prime, eta, rs, rp, is_total_reflection = calculate_reflection_polarization_deg(
            n, alpha, theta
        )
        alpha_rad = np.radians(alpha)
        theta_rad = np.radians(theta)
        alpha_prime_rad = np.radians(alpha_prime)
        eta_rad = np.radians(eta)
    else:
        alpha_prime, eta, rs, rp, is_total_reflection = calculate_reflection_polarization(
            n, alpha, theta
        )
        alpha_rad = alpha
        theta_rad = theta
        alpha_prime_rad = alpha_prime
        eta_rad = eta
    
    # 计算临界角
    theta_c = np.arcsin(1.0 / n)
    if use_degrees:
        theta_c = np.degrees(theta_c)
    
    # 计算反射系数幅度和相位
    rs_abs = abs(rs)
    rs_phase = np.angle(rs)
    rp_abs = abs(rp)
    rp_phase = np.angle(rp)
    
    # 计算相位差
    phase_diff = rp_phase - rs_phase
    
    # 计算轴比 ε = tan(η)
    # 注意：η可能是弧度或度，取决于use_degrees参数
    if use_degrees:
        # η是度，需要转换为弧度再计算tan
        if np.abs(eta) < 1e-12:
            epsilon = 0.0
        else:
            epsilon = np.tan(np.radians(eta))
    else:
        # η是弧度，直接计算tan
        if np.abs(eta) < 1e-12:
            epsilon = 0.0
        else:
            epsilon = np.tan(eta)
    
    # 构建结果字典
    result = {
        'input': {
            'n': n,
            'alpha': alpha if use_degrees else np.degrees(alpha),
            'theta': theta if use_degrees else np.degrees(theta),
            'alpha_rad': alpha_rad,
            'theta_rad': theta_rad,
            'units': 'degrees' if use_degrees else 'radians'
        },
        'critical_angle': theta_c,
        'is_total_reflection': is_total_reflection,
        'reflection_coefficients': {
            'rs': rs,
            'rp': rp,
            'rs_abs': rs_abs,
            'rs_phase_rad': rs_phase,
            'rs_phase_deg': np.degrees(rs_phase),
            'rp_abs': rp_abs,
            'rp_phase_rad': rp_phase,
            'rp_phase_deg': np.degrees(rp_phase),
            'phase_diff_rad': phase_diff,
            'phase_diff_deg': np.degrees(phase_diff)
        },
        'output': {
            'alpha_prime': alpha_prime if use_degrees else np.degrees(alpha_prime),
            'eta': eta if use_degrees else np.degrees(eta),
            'alpha_prime_rad': alpha_prime_rad,
            'eta_rad': eta_rad,
            'epsilon': epsilon,  # 轴比
            'polarization_type': 'elliptical' if abs(eta) > 1e-6 else 'linear'
        }
    }
    
    return result


def print_analysis_result(result: dict):
    """打印分析结果"""
    print("=" * 60)
    print("反射光偏振态分析结果")
    print("=" * 60)
    
    # 输入参数
    print("\n输入参数:")
    print(f"  相对折射率 n = {result['input']['n']:.4f}")
    print(f"  入射光偏振角 α = {result['input']['alpha']:.2f}°")
    print(f"  入射角 θ = {result['input']['theta']:.2f}°")
    print(f"  临界角 θ_c = {result['critical_angle']:.2f}°")
    
    # 反射类型
    reflection_type = "全反射" if result['is_total_reflection'] else "小于临界角反射"
    print(f"\n反射类型: {reflection_type}")
    
    # 反射系数
    print("\n反射系数:")
    rs = result['reflection_coefficients']['rs']
    rp = result['reflection_coefficients']['rp']
    print(f"  r_s = {rs.real:.4f} + {rs.imag:.4f}i")
    print(f"     幅度: {abs(rs):.4f}, 相位: {np.degrees(np.angle(rs)):.2f}°")
    print(f"  r_p = {rp.real:.4f} + {rp.imag:.4f}i")
    print(f"     幅度: {abs(rp):.4f}, 相位: {np.degrees(np.angle(rp)):.2f}°")
    print(f"  相位差 Δ = {result['reflection_coefficients']['phase_diff_deg']:.2f}°")
    
    # 输出结果
    print("\n反射光偏振态:")
    print(f"  偏振椭圆主轴方向角 α' = {result['output']['alpha_prime']:.4f}°")
    print(f"  椭偏角 η = {result['output']['eta']:.4f}°")
    print(f"  轴比 ε = tan(η) = {result['output']['epsilon']:.6f}")
    print(f"  偏振类型: {result['output']['polarization_type']}")
    
    print("=" * 60)


# 示例使用
if __name__ == "__main__":
    print("反射光偏振态计算模块示例")
    print("-" * 40)
    
    # 示例1：小于临界角情形
    print("\n示例1: 小于临界角情形")
    print("n=1.5, α=30°, θ=30°")
    result1 = analyze_reflection_polarization(1.5, 30, 30, use_degrees=True)
    print_analysis_result(result1)
    
    # 示例2：全反射情形
    print("\n示例2: 全反射情形")
    print("n=1.5, α=30°, θ=45°")
    result2 = analyze_reflection_polarization(1.5, 30, 45, use_degrees=True)
    print_analysis_result(result2)
    
    # 示例3：特殊情况 - 纯s偏振
    print("\n示例3: 纯s偏振 (α=0°)")
    print("n=1.5, α=0°, θ=45°")
    result3 = analyze_reflection_polarization(1.5, 0, 45, use_degrees=True)
    print_analysis_result(result3)
    
    # 示例4：特殊情况 - 纯p偏振
    print("\n示例4: 纯p偏振 (α=90°)")
    print("n=1.5, α=90°, θ=45°")
    result4 = analyze_reflection_polarization(1.5, 90, 45, use_degrees=True)
    print_analysis_result(result4)
    
    # 示例5：45度线偏振
    print("\n示例5: 45度线偏振")
    print("n=1.5, α=45°, θ=45°")
    result5 = analyze_reflection_polarization(1.5, 45, 45, use_degrees=True)
    print_analysis_result(result5)
    
    print("\n所有示例计算完成！")


def visualize_reflection_polarization():
    """
    反射光偏振态交互式可视化
    
    在alpha和theta的[0,π/2]平面上绘制反射光偏振转角α'和椭偏角η
    添加折射率n的滑动条，默认值1.7（重火石玻璃）
    """
    try:
        import matplotlib.pyplot as plt
        from matplotlib.widgets import Slider
        # 设置中文字体
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'DejaVu Sans']
        plt.rcParams['axes.unicode_minus'] = False
    except ImportError:
        print("错误: 需要安装matplotlib库来运行可视化功能")
        print("请运行: pip install matplotlib")
        return
    
    # 创建网格
    alpha_points = 100  # α方向点数
    theta_points = 100  # θ方向点数
    
    # 创建角度网格（弧度）
    alpha_vals = np.linspace(0, np.pi/2, alpha_points)
    theta_vals = np.linspace(0, np.pi/2, theta_points)
    Alpha, Theta = np.meshgrid(alpha_vals, theta_vals)
    
    # 初始折射率（重火石玻璃）
    n_initial = 1.7
    
    def calculate_data(n):
        """计算给定折射率下的数据"""
        alpha_prime_data = np.zeros_like(Alpha)
        eta_data = np.zeros_like(Alpha)
        
        # 遍历所有点计算
        for i in range(alpha_points):
            for j in range(theta_points):
                alpha = Alpha[j, i]
                theta = Theta[j, i]
                try:
                    alpha_prime, eta, _, _, _ = calculate_reflection_polarization(n, alpha, theta)
                    alpha_prime_data[j, i] = np.degrees(alpha_prime)  # 转换为度
                    eta_data[j, i] = np.degrees(eta)  # 转换为度
                except ValueError:
                    # 处理无效参数
                    alpha_prime_data[j, i] = np.nan
                    eta_data[j, i] = np.nan
        
        return alpha_prime_data, eta_data
    
    # 计算初始数据
    print("正在计算初始数据...")
    alpha_prime_initial, eta_initial = calculate_data(n_initial)
    
    # 创建图形
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle(f'反射光偏振态 vs 入射角θ和偏振角α (n={n_initial:.2f})', fontsize=14)
    
    # 绘制α'图
    im1 = ax1.imshow(alpha_prime_initial, 
                     extent=[0, 90, 0, 90], 
                     origin='lower',
                     aspect='auto',
                     cmap='viridis')
    ax1.set_xlabel('入射光偏振角 α (°)', fontsize=12)
    ax1.set_ylabel('入射角 θ (°)', fontsize=12)
    ax1.set_title('反射光偏振转角 α\' (°)', fontsize=12)
    cbar1 = fig.colorbar(im1, ax=ax1)
    cbar1.set_label('α\' (°)', fontsize=10)
    
    # 绘制η图
    im2 = ax2.imshow(eta_initial,
                     extent=[0, 90, 0, 90],
                     origin='lower',
                     aspect='auto',
                     cmap='plasma')
    ax2.set_xlabel('入射光偏振角 α (°)', fontsize=12)
    ax2.set_ylabel('入射角 θ (°)', fontsize=12)
    ax2.set_title('反射光椭偏角 η (°)', fontsize=12)
    cbar2 = fig.colorbar(im2, ax=ax2)
    cbar2.set_label('η (°)', fontsize=10)
    
    # 添加临界角线
    theta_c_deg = np.degrees(np.arcsin(1.0 / n_initial))
    for ax in [ax1, ax2]:
        ax.axhline(y=theta_c_deg, color='red', linestyle='--', alpha=0.7, linewidth=1.5)
        ax.text(5, theta_c_deg + 2, f'临界角 θ_c = {theta_c_deg:.1f}°', 
                color='red', fontsize=10, backgroundcolor='white', alpha=0.8)
    
    # 调整布局，增加底部空间给滑动条
    plt.tight_layout(rect=[0, 0.08, 1, 0.97])  # 底部留出8%的空间，顶部留出3%的空间
    
    # 添加滑动条（位置调整到更上方，避免重叠）
    ax_slider = plt.axes([0.25, 0.04, 0.5, 0.03])  # 从y=0.04开始，高度0.03
    # n范围改成[1,4]，包含1，不需要在默认n处标记
    n_slider = Slider(ax_slider, '折射率 n', 1.0, 4.0, valinit=n_initial, valstep=0.01)
    
    def update(val):
        """更新函数"""
        n = n_slider.val
        
        # 计算新数据
        print(f"正在计算 n={n:.2f} 的数据...")
        alpha_prime_new, eta_new = calculate_data(n)
        
        # 更新图像（保持-90°~90°范围）
        im1.set_data(alpha_prime_new)
        im1.set_clim(vmin=np.nanmin(alpha_prime_new), vmax=np.nanmax(alpha_prime_new))
        
        im2.set_data(eta_new)
        im2.set_clim(vmin=np.nanmin(eta_new), vmax=np.nanmax(eta_new))
        
        # 更新临界角线
        if n > 1.0:  # 只有当n>1时才有临界角
            theta_c_deg_new = np.degrees(np.arcsin(1.0 / n))
            for ax in [ax1, ax2]:
                # 移除旧的临界角线
                for line in ax.get_lines():
                    if line.get_color() == 'red' and line.get_linestyle() == '--':
                        line.remove()
                # 添加新的临界角线
                ax.axhline(y=theta_c_deg_new, color='red', linestyle='--', alpha=0.7, linewidth=1.5)
                # 更新文本
                for text in ax.texts:
                    if '临界角' in text.get_text():
                        text.remove()
                ax.text(5, theta_c_deg_new + 2, f'临界角 θ_c = {theta_c_deg_new:.1f}°', 
                        color='red', fontsize=10, backgroundcolor='white', alpha=0.8)
        else:
            # n=1时没有临界角，移除所有临界角线和文本
            for ax in [ax1, ax2]:
                for line in ax.get_lines():
                    if line.get_color() == 'red' and line.get_linestyle() == '--':
                        line.remove()
                for text in ax.texts:
                    if '临界角' in text.get_text():
                        text.remove()
        
        # 更新标题
        fig.suptitle(f'反射光偏振态 vs 入射角θ和偏振角α (n={n:.2f})', fontsize=14)
        
        # 重绘图形
        fig.canvas.draw_idle()
    
    # 连接滑动条事件
    n_slider.on_changed(update)
    
    # 添加滑动条说明
    fig.text(0.5, 0.01, 
             '使用滑动条调整折射率n，观察临界角和偏振态的变化',
             ha='center', fontsize=9, style='italic', color='gray')
    
    plt.show()


def run_visualization():
    """运行可视化工具"""
    print("=" * 60)
    print("反射光偏振态交互式可视化工具")
    print("=" * 60)
    print("正在启动可视化界面...")
    print("注意: 首次计算可能需要一些时间")
    print("-" * 40)
    
    visualize_reflection_polarization()


# 修改主程序以包含可视化选项
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--visualize":
        run_visualization()
    else:
        print("反射光偏振态计算模块示例")
        print("-" * 40)
        
        # 示例1：小于临界角情形
        print("\n示例1: 小于临界角情形")
        print("n=1.5, α=30°, θ=30°")
        result1 = analyze_reflection_polarization(1.5, 30, 30, use_degrees=True)
        print_analysis_result(result1)
        
        # 示例2：全反射情形
        print("\n示例2: 全反射情形")
        print("n=1.5, α=30°, θ=45°")
        result2 = analyze_reflection_polarization(1.5, 30, 45, use_degrees=True)
        print_analysis_result(result2)
        
        # 示例3：特殊情况 - 纯s偏振
        print("\n示例3: 纯s偏振 (α=0°)")
        print("n=1.5, α=0°, θ=45°")
        result3 = analyze_reflection_polarization(1.5, 0, 45, use_degrees=True)
        print_analysis_result(result3)
        
        # 示例4：特殊情况 - 纯p偏振
        print("\n示例4: 纯p偏振 (α=90°)")
        print("n=1.5, α=90°, θ=45°")
        result4 = analyze_reflection_polarization(1.5, 90, 45, use_degrees=True)
        print_analysis_result(result4)
        
        # 示例5：45度线偏振
        print("\n示例5: 45度线偏振")
        print("n=1.5, α=45°, θ=45°")
        result5 = analyze_reflection_polarization(1.5, 45, 45, use_degrees=True)
        print_analysis_result(result5)
        
        print("\n所有示例计算完成！")
        
        # 询问用户是否要运行交互式可视化
        print("\n" + "=" * 60)
        print("是否要运行交互式可视化工具？")
        print("=" * 60)
        print("交互式可视化将在alpha和theta的[0,π/2]平面上绘制：")
        print("1. 反射光偏振转角α'")
        print("2. 反射光椭偏角η")
        print("3. 包含折射率n的滑动条（默认值1.7，重火石玻璃）")
        print("\n注意: 首次计算可能需要一些时间（约1-2分钟）")
        
        try:
            response = input("\n是否运行交互式可视化？(y/n): ").strip().lower()
            if response == 'y' or response == 'yes' or response == '是':
                print("\n启动交互式可视化工具...")
                run_visualization()
            else:
                print("\n跳过交互式可视化。")
                print("要单独运行可视化，请使用: python reflection_correction.py --visualize")
        except KeyboardInterrupt:
            print("\n\n用户中断，跳过交互式可视化。")
            print("要单独运行可视化，请使用: python reflection_correction.py --visualize")
        except Exception as e:
            print(f"\n输入错误: {e}")
            print("跳过交互式可视化。")
            print("要单独运行可视化，请使用: python reflection_correction.py --visualize")

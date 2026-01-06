# -*- coding: utf-8 -*-
import matplotlib
# 如果在没有显示器的服务器上运行，取消下面这行的注释
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import splrep, splev

# 1. 数据准备
# -----------------------------------------------------------
raw_data = """
1.695,324,HPCC
1.708,400,HPCC
1.699,500,HPCC
1.704,600,HPCC
1.710,700,HPCC
1.706,1K,HPCC
1.742,7K,HPCC
2.581,46K,HPCC
3.315,120K,HPCC
4.828,300K,HPCC
3.505,324,DCTCP
3.540,400,DCTCP
3.544,500,DCTCP
3.511,600,DCTCP
3.537,700,DCTCP
3.526,1K,DCTCP
3.514,7K,DCTCP
3.573,46K,DCTCP
3.788,120K,DCTCP
4.720,300K,DCTCP
8.618,324,DCQCN
8.646,400,DCQCN
8.605,500,DCQCN
8.635,600,DCQCN
8.644,700,DCQCN
8.601,1K,DCQCN
8.527,7K,DCQCN
7.440,46K,DCQCN
6.746,120K,DCQCN
5.808,300K,DCQCN
4.321,324,DCQCN+Win
4.364,400,DCQCN+Win
4.361,500,DCQCN+Win
4.335,600,DCQCN+Win
4.342,700,DCQCN+Win
4.348,1K,DCQCN+Win
4.351,7K,DCQCN+Win
4.192,46K,DCQCN+Win
4.221,120K,DCQCN+Win
5.000,300K,DCQCN+Win
10.354,324,TIMELY
10.215,400,TIMELY
10.340,500,TIMELY
10.312,600,TIMELY
10.474,700,TIMELY
10.251,1K,TIMELY
10.314,7K,TIMELY
8.687,46K,TIMELY
7.765,120K,TIMELY
6.341,300K,TIMELY
4.147,324,TIMELY+Win
4.182,400,TIMELY+Win
4.178,500,TIMELY+Win
4.169,600,TIMELY+Win
4.177,700,TIMELY+Win
4.155,1K,TIMELY+Win
4.165,7K,TIMELY+Win
4.036,46K,TIMELY+Win
4.122,120K,TIMELY+Win
4.751,300K,TIMELY+Win
"""

# 解析数据
data = {}
x_labels = [] 
# 这里的顺序决定了X轴刻度位置：'120K'是index 8, '10M'是index 9
ordered_x_labels = ['324', '400', '500', '600', '700', '1K', '7K', '46K', '120K', '10M']

for line in raw_data.strip().split('\n'):
    if not line: continue
    parts = line.split(',')
    val = float(parts[0])
    size = parts[1].strip()
    algo = parts[2].strip()
    
    if algo not in data:
        data[algo] = {'x': [], 'y': []}
    
    # --- 修改重点开始 ---
    # 如果数据点是 300K，我们手动将其放置在 120K(index 8) 和 10M(index 9) 的中间，即 8.5
    if size == '300K':
        data[algo]['x'].append(8.5)
        data[algo]['y'].append(val)
    # 其他数据点正常查找索引
    elif size in ordered_x_labels:
        idx = ordered_x_labels.index(size)
        data[algo]['x'].append(float(idx)) # 转为float以保持一致性
        data[algo]['y'].append(val)
    # --- 修改重点结束 ---

# 2. 样式设置
# -----------------------------------------------------------
styles = {
    'HPCC':       {'color': '#0060a0', 'ls': '-',  'lw': 2.5}, 
    'DCTCP':      {'color': '#f0d040', 'ls': '--', 'lw': 2.5}, 
    'DCQCN':      {'color': '#8040a0', 'ls': ':',  'lw': 2.5}, 
    'DCQCN+Win':  {'color': '#60c0f0', 'ls': ':',  'lw': 2.5}, 
    'TIMELY':     {'color': '#00a060', 'ls': '--', 'lw': 2.5}, 
    'TIMELY+Win': {'color': '#d09040', 'ls': '--', 'lw': 2.5}, 
}
plot_order = ['DCQCN', 'DCQCN+Win', 'TIMELY', 'TIMELY+Win', 'DCTCP', 'HPCC']

# 3. 开始绘图
# -----------------------------------------------------------
fig, ax = plt.subplots(figsize=(7, 4.5))

for algo in plot_order:
    if algo not in data: continue
    
    # 确保根据x排序，否则spline插值会报错（虽然原始数据看似有序，但安全起见）
    xy_pairs = sorted(zip(data[algo]['x'], data[algo]['y']))
    x = np.array([p[0] for p in xy_pairs])
    y = np.array([p[1] for p in xy_pairs])
    
    # B-Spline 插值
    # 注意：插值范围 x_new 使用 x.max()，此时 x.max() 为 8.5
    # 这样画出来的线只会延伸到 8.5 处，而坐标轴会显示到 9 (10M)
    tck = splrep(x, y, s=0) 
    x_new = np.linspace(x.min(), x.max(), 300) 
    y_smooth = splev(x_new, tck, der=0)
    
    style = styles.get(algo, {'color': 'black', 'ls': '-'})
    
    ax.plot(x_new, y_smooth, label=algo, 
            color=style['color'], linestyle=style['ls'], linewidth=style['lw'])

# 4. 坐标轴与布局设置
# -----------------------------------------------------------
ax.set_yscale('log')
ax.set_ylim(1, 100)
ax.set_yticks([1, 10, 100])
ax.set_yticklabels(['1', '10', '100'])
ax.set_ylabel('FCT Slow down', fontsize=14, fontweight='bold')

# 设置 X 轴范围覆盖到 '10M' (索引9)
ax.set_xlim(0, len(ordered_x_labels) - 1)
ax.set_xticks(range(len(ordered_x_labels)))
ax.set_xticklabels(ordered_x_labels, rotation=45, ha='right', fontsize=12)
ax.set_xlabel('Flow size (Byte)', fontsize=14, fontweight='bold')

# 隐藏右边和上边的边框线 (Spines)
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)

# 设置刻度向内，并明确关闭 上侧(top) 和 右侧(right) 的刻度点
ax.tick_params(direction='in', length=5, width=1, top=False, right=False)

# 5. 图例设置
# -----------------------------------------------------------
ax.legend(loc='upper left', ncol=2, frameon=False, fontsize=10, 
          columnspacing=1.0, handlelength=2.5)

plt.tight_layout()
# 此时生成的图片，曲线会在 120K 后延伸，并停在 10M 刻度之前
plt.savefig('/home/xjg/HPCC/simulation/mix/results/50load/fct_slowdown.png', dpi=300)
# plt.show()
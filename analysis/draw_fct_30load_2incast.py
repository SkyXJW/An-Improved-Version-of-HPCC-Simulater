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
1.679,324,HPCC
1.709,400,HPCC
1.686,500,HPCC
1.711,600,HPCC
1.708,700,HPCC
1.688,1K,HPCC
1.727,7K,HPCC
2.145,46K,HPCC
2.572,120K,HPCC
7.882,300K,HPCC
3.233,324,DCTCP
3.303,400,DCTCP
3.269,500,DCTCP
3.300,600,DCTCP
3.329,700,DCTCP
3.291,1K,DCTCP
3.258,7K,DCTCP
3.166,46K,DCTCP
3.186,120K,DCTCP
4.774,300K,DCTCP
192.806,324,DCQCN
190.445,400,DCQCN
190.920,500,DCQCN
191.989,600,DCQCN
193.330,700,DCQCN
192.212,1K,DCQCN
186.365,7K,DCQCN
151.676,46K,DCQCN
122.752,120K,DCQCN
11.988,300K,DCQCN
5.052,324,DCQCN+Win
5.341,400,DCQCN+Win
5.021,500,DCQCN+Win
5.310,600,DCQCN+Win
5.294,700,DCQCN+Win
5.158,1K,DCQCN+Win
5.082,7K,DCQCN+Win
4.658,46K,DCQCN+Win
4.156,120K,DCQCN+Win
4.977,300K,DCQCN+Win
227.698,324,TIMELY
224.943,400,TIMELY
225.973,500,TIMELY
225.062,600,TIMELY
226.071,700,TIMELY
223.325,1K,TIMELY
222.365,7K,TIMELY
179.452,46K,TIMELY
146.304,120K,TIMELY
24.171,300K,TIMELY
8.317,324,TIMELY+Win
10.294,400,TIMELY+Win
8.670,500,TIMELY+Win
9.996,600,TIMELY+Win
10.256,700,TIMELY+Win
9.562,1K,TIMELY+Win
8.955,7K,TIMELY+Win
8.394,46K,TIMELY+Win
6.306,120K,TIMELY+Win
6.397,300K,TIMELY+Win
"""

# 解析数据
data = {}
x_labels = [] 
# 120K是索引8, 10M是索引9
ordered_x_labels = ['324', '400', '500', '600', '700', '1K', '7K', '46K', '120K', '10M']

for line in raw_data.strip().split('\n'):
    if not line: continue
    parts = line.split(',')
    val = float(parts[0])
    size = parts[1].strip()
    algo = parts[2].strip()
    
    if algo not in data:
        data[algo] = {'x': [], 'y': []}
    
    # --- 修改重点 ---
    # 手动处理 300K，将其放到 120K(index 8) 和 10M(index 9) 的中间位置 8.5
    if size == '300K':
        data[algo]['x'].append(8.5)
        data[algo]['y'].append(val)
    elif size in ordered_x_labels:
        idx = ordered_x_labels.index(size)
        data[algo]['x'].append(float(idx))
        data[algo]['y'].append(val)
    # ----------------

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
    
    # 必须对数据进行排序，因为 300K 可能出现在数据流的中间或末尾
    # 插值函数要求 x 单调递增
    xy_pairs = sorted(zip(data[algo]['x'], data[algo]['y']))
    x = np.array([p[0] for p in xy_pairs])
    y = np.array([p[1] for p in xy_pairs])
    
    # B-Spline 插值
    # x.max() 此时应该是 8.5，所以曲线会画到 8.5 截止
    tck = splrep(x, y, s=0) 
    x_new = np.linspace(x.min(), x.max(), 300) 
    y_smooth = splev(x_new, tck, der=0)
    
    style = styles.get(algo, {'color': 'black', 'ls': '-'})
    
    ax.plot(x_new, y_smooth, label=algo, 
            color=style['color'], linestyle=style['ls'], linewidth=style['lw'])

# 4. 坐标轴与布局设置
# -----------------------------------------------------------
ax.set_yscale('log')

# Y轴范围设置 (保留您的设置)
ax.set_ylim(1, 230)
ax.set_yticks([1, 10, 100, 230])
ax.set_yticklabels(['1', '10', '100', '230'])
ax.set_ylabel('FCT Slow down', fontsize=14, fontweight='bold')

# X轴范围设置：0 到 9 (即 '324' 到 '10M')
# 曲线只画到 8.5，所以 8.5 到 9 之间是空白
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
plt.savefig('/home/xjg/HPCC/simulation/mix/results/30load_2incast/fct_slowdown.png', dpi=300)
# plt.show()
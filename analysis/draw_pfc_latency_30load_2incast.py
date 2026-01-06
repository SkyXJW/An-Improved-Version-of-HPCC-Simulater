# -*- coding: utf-8 -*-
import matplotlib
# 设置后端为 Agg，适用于无显示器的服务器环境
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import numpy as np

# 1. 准备数据
# -----------------------------------------------------------
labels = ['DCQCN', 'DCQCN+W', 'TIMELY', 'TIMELY+W', 'DCTCP', 'HPCC']
pfc_pause = [0.0059, 0, 6.3684, 0.2621, 0, 0]          # 左轴数据 (Purple)
latency = [2.310940, 0.117893, 2.488211, 0.083283, 0.053496, 0.022587] # 右轴数据 (Green)

# 2. 设置绘图参数
# -----------------------------------------------------------
bar_width = 0.3
index = np.arange(len(labels))

fig, ax1 = plt.subplots(figsize=(8, 5))

color_pfc = '#884EA0'  # 紫色 (PFC pause)
color_lat = '#00A36C'  # 绿色 (Latency)

# 3. 绘制柱状图
# -----------------------------------------------------------
# 左侧 Y 轴 - PFC Pause (线性坐标)
rects1 = ax1.bar(index, pfc_pause, bar_width, color=color_pfc, label='PFC pause')

# 创建共享 X 轴的第二个 Y 轴
ax2 = ax1.twinx()

# --- 修改点 1: 设置右轴为对数坐标 ---
ax2.set_yscale('log')
# --------------------------------

# 右侧 Y 轴 - Latency (绿色柱子)
rects2 = ax2.bar(index + bar_width, latency, bar_width, color=color_lat, label='95pct-latency')

# 4. 调整坐标轴与标签
# -----------------------------------------------------------
# 设置左 Y 轴标签
ax1.set_ylabel('Fraction of pause time(%)', fontsize=14, color='black')
ax1.tick_params(axis='y', labelsize=12)

# 设置右 Y 轴标签
ax2.set_ylabel('Latency (ms)', fontsize=14, color='black')
ax2.tick_params(axis='y', labelsize=12)

# 设置 X 轴刻度
ax1.set_xticks(index + bar_width / 2.0)
ax1.set_xticklabels(labels, rotation=45, ha='right', fontsize=12)

# 左侧 Y 轴范围 (固定 0-20)
ax1.set_ylim(0, 20) 

# --- 修改点 2: 设置右轴范围和自定义刻度 ---
# 设置范围从 0.01 到 10
ax2.set_ylim(0.01, 10)

# 设置自定义的刻度位置
ticks = [0.01, 0.1, 1, 10]
ax2.set_yticks(ticks)

# 设置刻度对应的文本标签 (如果不设置这个，matplotlib可能会显示 10^-2 这种科学计数法)
ax2.set_yticklabels(['0.01', '0.1', '1', '10'])

# 去除对数坐标轴自带的次要刻度(minor ticks)，让图表更像参考图那样干净
# ax2.minorticks_off()
# --------------------------------------

# 5. 设置图例
# -----------------------------------------------------------
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()

ax2.legend(lines1 + lines2, labels1 + labels2, loc='upper right', 
           frameon=False, fontsize=12, bbox_to_anchor=(0.95, 1.0))

# 6. 布局调整与保存
# -----------------------------------------------------------
plt.tight_layout()
plt.savefig('pfc_latency.png', dpi=300)
# plt.show()
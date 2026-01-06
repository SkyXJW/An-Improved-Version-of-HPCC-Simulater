# -*- coding: utf-8 -*-
import matplotlib
# 设置后端为 Agg，适用于无显示器的服务器环境
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
import numpy as np

# 1. 准备数据
# -----------------------------------------------------------
labels = ['DCQCN', 'DCQCN+W', 'TIMELY', 'TIMELY+W', 'DCTCP', 'HPCC']
pfc_pause = [0, 0, 0.0048, 0, 0, 0]          # 左轴数据 (Purple)
latency = [108.79, 50.496, 149.565, 61.949, 40.685, 20.637] # 右轴数据 (Green)

# 2. 设置绘图参数
# -----------------------------------------------------------
# 设置柱状图的宽度
bar_width = 0.3

# 设置X轴的位置索引
index = np.arange(len(labels))

# 创建画布
fig, ax1 = plt.subplots(figsize=(8, 5))

# 参考图中的颜色近似值
color_pfc = '#884EA0'  # 紫色 (PFC pause)
color_lat = '#00A36C'  # 绿色 (Latency)

# 3. 绘制柱状图
# -----------------------------------------------------------
# 左侧 Y 轴 - PFC Pause (紫色柱子)
# 注意：你的数据中PFC几乎为0，所以柱子可能几乎看不见，这是正常的
rects1 = ax1.bar(index, pfc_pause, bar_width, color=color_pfc, label='PFC pause')

# 创建共享 X 轴的第二个 Y 轴
ax2 = ax1.twinx()

# 右侧 Y 轴 - Latency (绿色柱子)
# 将位置向右偏移 bar_width，以免重叠
rects2 = ax2.bar(index + bar_width, latency, bar_width, color=color_lat, label='95pct-latency')

# 4. 调整坐标轴与标签
# -----------------------------------------------------------
# 设置左 Y 轴标签
ax1.set_ylabel('Fraction of pause time(%)', fontsize=14, color='black')
ax1.tick_params(axis='y', labelsize=12)

# 设置右 Y 轴标签
ax2.set_ylabel('Latency (us)', fontsize=14, color='black')
ax2.tick_params(axis='y', labelsize=12)

# 设置 X 轴刻度
ax1.set_xticks(index + bar_width / 2.0)  # 将刻度居中于两组柱子之间
ax1.set_xticklabels(labels, rotation=45, ha='right', fontsize=12)

# --- 修改点 ---
# 将左侧Y轴范围设置为0到20
ax1.set_ylim(0, 20) 
# -------------

# 设置右轴上限，为了让图看起来更像参考图，稍微留点空间
ax2.set_ylim(0, max(latency) * 1.1)

# 5. 设置图例 (合并两个轴的图例)
# -----------------------------------------------------------
# 获取两个轴的图例句柄和标签
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()

# 将它们合并并在右上角显示，去掉边框
ax2.legend(lines1 + lines2, labels1 + labels2, loc='upper right', 
           frameon=False, fontsize=12, bbox_to_anchor=(0.95, 1.0))

# 6. 布局调整与保存
# -----------------------------------------------------------
# 自动调整布局防止标签被截断
plt.tight_layout()

# 保存图片
plt.savefig('pfc_latency.png', dpi=300)
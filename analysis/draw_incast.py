# -*- coding: utf-8 -*-
import matplotlib
# 设置后端为 Agg，适用于无显示器的服务器环境
matplotlib.use('Agg') 

import matplotlib.pyplot as plt
import csv
import sys
import numpy as np 

def main():
    # 使用你提供的绝对路径
    filename = '/home/xjg/HPCC/simulation/mix/micro/results/dcqcn/incast/throughput.txt'
    
    flows = {}
    min_time_ns = None
    
    # --- 1. 读取原始数据 ---
    try:
        with open(filename, 'rb') as f:
            reader = csv.reader(f)
            try:
                header = next(reader)
            except StopIteration:
                print "Error: File is empty."
                return

            for row in reader:
                if len(row) < 4:
                    continue
                try:
                    time_ns = float(row[0].strip())
                    flow_id = row[1].strip()
                    throughput = float(row[2].strip())
                    desc = row[3].strip()
                    
                    if min_time_ns is None or time_ns < min_time_ns:
                        min_time_ns = time_ns
                    
                    if flow_id not in flows:
                        flows[flow_id] = {
                            'time_ns': [], 
                            'throughput': [],
                            'label': desc
                        }
                    
                    flows[flow_id]['time_ns'].append(time_ns)
                    flows[flow_id]['throughput'].append(throughput)
                    
                except ValueError:
                    continue
                    
    except IOError:
        print "Error: Could not find or open " + filename
        sys.exit(1)

    if not flows:
        print "No valid data found to plot."
        return

    # --- 2. 数据平滑处理 ---
    bin_size_ms = 0.02
    
    smoothed_flows = {}
    start_t_ns = min_time_ns if min_time_ns is not None else 0

    for fid, data in flows.items():
        raw_times_ms = np.array([(t - start_t_ns) / 1000000.0 for t in data['time_ns']])
        raw_throughputs = np.array(data['throughput'])
        
        if len(raw_times_ms) == 0:
            continue
            
        max_time_ms = raw_times_ms[-1]
        
        smooth_times = []
        smooth_throughputs = []
        
        bins = np.arange(0, max_time_ms + bin_size_ms, bin_size_ms)
        inds = np.digitize(raw_times_ms, bins)
        
        for i in range(1, len(bins)):
            mask = (inds == i)
            if np.any(mask):
                avg_throughput = np.mean(raw_throughputs[mask])
                bin_midpoint = (bins[i-1] + bins[i]) / 2.0
                
                smooth_times.append(bin_midpoint)
                smooth_throughputs.append(avg_throughput)

        smoothed_flows[fid] = {
            'time': smooth_times,
            'throughput': smooth_throughputs,
            'label': data['label']
        }

    # --- 3. 开始绘图 (修改部分) ---
    plt.figure(figsize=(8, 6))
    plt.rcParams.update({'font.size': 14})
    
    sorted_flow_ids = sorted(smoothed_flows.keys())
    
    for fid in sorted_flow_ids:
        data = smoothed_flows[fid]
        
        # 修改：统一使用实线 linestyle='-'
        # Matplotlib 会自动为不同的 plot 循环分配不同的颜色
        plt.plot(data['time'], data['throughput'], 
                 label=data['label'], 
                 linewidth=2,
                 linestyle='-') 

    # 设置坐标轴标签
    plt.xlabel('Time (ms)', fontsize=16, fontweight='bold')
    plt.ylabel('Throughput (Gbps)', fontsize=16, fontweight='bold')
    
    # 修改：设置横轴最大 7ms，纵轴最大 30Gbps
    plt.xlim(0, 7)
    plt.ylim(0, 120)
    
    # 美化图表
    ax = plt.gca()
    for axis in ['top','bottom','left','right']:
        ax.spines[axis].set_linewidth(1.5)
    ax.tick_params(direction='in', length=6, width=1.5)

    plt.legend(loc='best', fontsize=12, frameon=False)
    
    output_filename = 'throughput_smooth_result.png'
    plt.tight_layout()
    plt.savefig(output_filename, dpi=300)
    print "Plot saved as " + output_filename

if __name__ == "__main__":
    main()
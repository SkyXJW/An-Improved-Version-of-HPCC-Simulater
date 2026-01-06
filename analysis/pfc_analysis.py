# -*- coding: utf-8 -*-
from __future__ import print_function  # 让 print 支持函数写法，兼容 Py2/Py3
import os
import argparse
import sys

def calculate_pfc_duration(file_path):
    # 检查文件是否存在
    if not os.path.exists(file_path):
        print("错误: 找不到文件 '{0}'".format(file_path))
        return

    # print("正在读取文件: {0} ...".format(file_path))
    
    # 用于存储正在进行的暂停事件
    # 格式: key=(node_id, port_id, queue_id), value=start_time
    active_pauses = {}
    
    total_duration = 0
    total_events = 0
    
    try:
        # Python 2.7 中 open 默认行为即可
        with open(file_path, 'r') as f:
            for line_num, line in enumerate(f, 1):
                parts = line.strip().split()
                
                # 简单的数据校验
                if len(parts) < 5:
                    continue
                
                try:
                    # 解析数据，Python 2 会自动处理大整数(long)
                    timestamp = int(parts[0])
                    node_id = int(parts[1])
                    port_id = int(parts[2])
                    queue_id = int(parts[3])
                    signal = int(parts[4])
                    
                    # 唯一流标识
                    flow_key = (node_id, port_id, queue_id)
                    
                    if signal == 1:
                        # 暂停开始 (XOFF)
                        active_pauses[flow_key] = timestamp
                        
                    elif signal == 0:
                        # 暂停结束 (XON)
                        if flow_key in active_pauses:
                            start_time = active_pauses[flow_key]
                            duration = timestamp - start_time
                            
                            total_duration += duration
                            total_events += 1
                            
                            del active_pauses[flow_key]
                        else:
                            # 只有结束没有开始，忽略
                            pass
                            
                except ValueError:
                    # 跳过无法解析的行
                    continue

        # 输出统计结果
        # print("-" * 40)
        # print("计算完成")
        # print("-" * 40)
        print("统计文件: {0}".format(file_path))
        print("有效PFC事件对: {0} 次".format(total_events))
        # 这里的 duration 可能是 long 类型，Python 2.7 会自动处理
        print("PFC暂停总时长: {0} (单位: ns)".format(total_duration))
        
        if active_pauses:
            print("注意: 有 {0} 个事件未闭合（只有开始没有结束）。".format(len(active_pauses)))

    except Exception as e:
        print("发生未知错误: {0}".format(e))

if __name__ == "__main__":
    # 初始化参数解析器
    parser = argparse.ArgumentParser(description="Calculate HPCC PFC Duration (Python 2.7)")
    
    # 添加 -p 参数
    parser.add_argument(
        '-p', '--path', 
        type=str, 
        required=True, 
        help='Path to the pfc.txt file'
    )
    
    # 解析参数
    args = parser.parse_args()
    
    # 运行计算函数
    calculate_pfc_duration(args.path)
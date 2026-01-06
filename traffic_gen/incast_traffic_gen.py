# -*- coding: utf-8 -*-
# 随机选择一个sender、一个receiver，发送一个长流，并且长流以full rate发送，
# 另外在中间某一时刻选择另外60个sender分别同时向该receiver发送500kb的数据，即Incast Flow
# 实验时，长流持续时间为0.003秒，即3毫秒，Incast流在仿真时间的中间时刻开始发送
import sys
import random
import math
from optparse import OptionParser

# 辅助函数：转换带宽字符串为数值
def translate_bandwidth(b):
    if b == None:
        return None
    if type(b)!=str:
        return None
    if b[-1] == 'G':
        return float(b[:-1])*1e9
    if b[-1] == 'M':
        return float(b[:-1])*1e6
    if b[-1] == 'K':
        return float(b[:-1])*1e3
    return float(b)

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-n", "--nhost", dest = "nhost", help = "number of hosts")
    parser.add_option("-b", "--bandwidth", dest = "bandwidth", help = "the bandwidth of host link (G/M/K), by default 10G", default = "10G")
    parser.add_option("-t", "--time", dest = "time", help = "the total run time (s), by default 10", default = "10")
    parser.add_option("-o", "--output", dest = "output", help = "the output file", default = "incast.txt")
    options,args = parser.parse_args()

    # 基础参数设置
    base_t = 2000000000 # 2秒作为基准偏移时间
    
    # 检查参数
    if not options.nhost:
        print "please use -n to enter number of hosts"
        sys.exit(0)
    
    nhost = int(options.nhost)
    bandwidth = translate_bandwidth(options.bandwidth)
    sim_time_sec = float(options.time)
    
    # Incast 参数设定
    num_incast_senders = 60
    incast_flow_size = 500 * 1000  # 500KB to Bytes
    
    if bandwidth == None:
        print "bandwidth format incorrect"
        sys.exit(0)

    # 计算长流大小：为了确保占满带宽，使用 带宽 x 时间 x 1.2 (冗余)
    long_flow_size = int(bandwidth * sim_time_sec / 8 * 1.2)

    # --- 1. 节点选择逻辑 ---
    # 生成所有主机的列表 ID
    all_hosts = list(range(nhost))
    
    # 随机选择 Receiver (dst)
    dst = random.choice(all_hosts)
    
    # 候选 Sender 列表（排除掉 dst）
    candidates = [h for h in all_hosts if h != dst]
    
    # 检查主机数量是否足够支持 unique senders
    # 我们需要 1 个长流 Sender + 60 个 Incast Senders
    required_senders = 1 + num_incast_senders
    
    long_src = -1
    incast_srcs = []

    if len(candidates) >= required_senders:
        # 如果主机足够，使用 sample 保证所有 Sender 互不相同
        selected = random.sample(candidates, required_senders)
        long_src = selected[0]
        incast_srcs = selected[1:]
        print "Mode: Unique Hosts. Selected 1 long sender and %d unique incast senders." % num_incast_senders
    else:
        # 如果主机不够（例如只有16个节点但要60个并发），则允许重复 Sender
        print "Warning: Not enough hosts for unique senders. Senders will be reused."
        long_src = random.choice(candidates)
        # 允许重复选择
        for i in range(num_incast_senders):
            incast_srcs.append(random.choice(candidates))

    # --- 2. 时间计算 ---
    # 长流开始时间 (base_t)
    start_time_long = base_t * 1e-9
    
    # Incast 开始时间 (仿真时间的中间时刻)
    # base_t (ns) + (total_time (s) / 2 * 1e9)
    incast_start_ns = base_t + (sim_time_sec / 2.0 * 1e9)
    start_time_incast = incast_start_ns * 1e-9

    # --- 3. 写入文件 ---
    output = options.output
    ofile = open(output, "w")
    
    print "Generating Incast Traffic:"
    print "  Receiver (Dst): %d" % dst
    print "  Long Flow: Src %d -> Dst %d, Size %d Bytes" % (long_src, dst, long_flow_size)
    print "  Incast Flows: %d flows, each %d Bytes, starting at %.4fs" % (num_incast_senders, incast_flow_size, start_time_incast)
    
    # 写入流的总数: 1个长流 + 60个Incast流
    total_flows = 1 + num_incast_senders
    ofile.write("%d \n" % total_flows)

    # 写入长流
    # 格式: src dst 3 100 size start_time
    ofile.write("%d %d 3 100 %d %.9f\n" % (long_src, dst, long_flow_size, start_time_long))

    # 写入 Incast 流
    for i in range(num_incast_senders):
        sender = incast_srcs[i]
        ofile.write("%d %d 3 200 %d %.9f\n" % (sender, dst, incast_flow_size, start_time_incast))

    ofile.close()
    print "Done. Traffic file written to %s" % output
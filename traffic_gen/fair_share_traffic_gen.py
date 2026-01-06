# -*- coding: utf-8 -*-
# 随机选择四个sender、一个receiver，每个sender分别发送一个长流，并且长流都以full rate发送，
# 四个sender的开始发送时间不同，其中，1号sender在仿真开始时发送，后续的sender都在前一个sender开始发送后隔固定一段时间后开始发送，
# 并且1号sender的长流持续时间为全程，后续sender的长流持续时间不尽相同，以模拟不同大小的长流竞争同一receiver的场景。
# 实验时，1号sender的长流持续时间为仿真全程，即0.1秒，2号sender的长流持续时间为0.033秒，3号sender的长流持续时间为0.016秒，4号sender的长流持续时间为0.0055秒
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
    parser.add_option("-o", "--output", dest = "output", help = "the output file", default = "fair_share.txt")
    options,args = parser.parse_args()

    # 基础参数设置
    # base_t 是仿真器中文本描述的时间偏移量，通常设为2秒，给系统预留初始化时间
    base_t_ns = 2000000000 
    
    # 检查参数
    if not options.nhost:
        print "please use -n to enter number of hosts"
        sys.exit(0)
    
    nhost = int(options.nhost)
    bandwidth = translate_bandwidth(options.bandwidth)
    sim_time_sec = float(options.time)
    
    if bandwidth == None:
        print "bandwidth format incorrect"
        sys.exit(0)

    # --- 1. 节点选择逻辑 ---
    # 生成所有主机的列表 ID
    all_hosts = list(range(nhost))
    
    # 随机选择 1 个 Receiver (dst)
    dst = random.choice(all_hosts)
    
    # 候选 Sender 列表（排除掉 dst）
    candidates = [h for h in all_hosts if h != dst]
    
    # 我们需要 4 个 Sender
    required_senders = 4
    senders = []

    if len(candidates) >= required_senders:
        # 主机足够，选择4个不重复的Sender
        senders = random.sample(candidates, required_senders)
        print "Mode: Unique Hosts. Selected 4 unique senders."
    else:
        # 主机不够，允许重复
        print "Warning: Not enough hosts for unique senders. Senders will be reused."
        for i in range(required_senders):
            senders.append(random.choice(candidates))

    # --- 2. 定义流的规格 (Start Delay, Duration) ---
    # 格式: (启动延迟秒数, 持续时间秒数)
    # Sender 1: 0.00s开始, 全程 (sim_time_sec)
    # Sender 2: 0.02s开始, 0.033s
    # Sender 3: 0.04s开始, 0.016s
    # Sender 4: 0.06s开始, 0.0055s
    flow_specs = [
        (0.0, sim_time_sec), 
        (0.02, 0.033),
        (0.04, 0.016),
        (0.06, 0.0055)
    ]

    # --- 3. 写入文件 ---
    output = options.output
    ofile = open(output, "w")
    
    print "Generating Staggered Traffic to Dst %d:" % dst
    
    # 写入流的总数: 4条
    ofile.write("%d \n" % len(flow_specs))

    for i in range(len(flow_specs)):
        src = senders[i]
        delay = flow_specs[i][0]
        duration = flow_specs[i][1]
        
        # 计算开始时间
        # 实际开始时间 = (base_t + delay * 1e9) 转回秒
        start_time = (base_t_ns + delay * 1e9) * 1e-9
        
        # 计算流大小 (Bytes) = Bandwidth (bps) * Duration (s) / 8
        # 注意：如果是第1个流（全程流），乘以1.2系数作为冗余，确保仿真结束前流不中断
        if i == 0:
            flow_size = int(bandwidth * duration / 8 * 1.2)
        else:
            flow_size = int(bandwidth * duration / 8)

        print "  Sender %d (Host %d): Start +%.1fs, Duration %.1fs, Size %d Bytes" % (i+1, src, delay, duration, flow_size)

        # 写入格式: src dst 3 100 size start_time
        # 注意：flow_id, priority 等字段这里硬编码为 3 100，如需修改请调整
        ofile.write("%d %d 3 100 %d %.9f\n" % (src, dst, flow_size, start_time))

    ofile.close()
    print "Done. Traffic file written to %s" % output
# -*- coding: utf-8 -*-
# 随机选择两个sender、一个receiver，其中一个sender发送一个长流，另外一个sender则发送一个短流，
# 并且长流以full rate发送，短流在长流开始后的某一中间时刻开始发送，且大小为1MB
# 实验时，长流持续时间为0.003秒，即3毫秒，短流则在仿真开始后的0.5毫秒后发送
import sys
import random
import math
import heapq
from optparse import OptionParser

class Flow:
	def __init__(self, src, dst, size, t):
		self.src, self.dst, self.size, self.t = src, dst, size, t
	def __str__(self):
		return "%d %d 3 100 %d %.9f"%(self.src, self.dst, self.size, self.t)

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

def poisson(lam):
	return -math.log(1-random.random())*lam

if __name__ == "__main__":
	port = 80
	parser = OptionParser()
	parser.add_option("-n", "--nhost", dest = "nhost", help = "number of hosts")
	parser.add_option("-b", "--bandwidth", dest = "bandwidth", help = "the bandwidth of host link (G/M/K), by default 10G", default = "10G")
	parser.add_option("-t", "--time", dest = "time", help = "the total run time (s), by default 10", default = "10")
	parser.add_option("--short_flowSize", dest = "short_flowSize", help = "flow size (MB) of long flow", default="1")
	parser.add_option("-o", "--output", dest = "output", help = "the output file", default = "long_short.txt")
	options,args = parser.parse_args()

	base_t = 2000000000

	if not options.nhost:
		print "please use -n to enter number of hosts"
		sys.exit(0)
	nhost = int(options.nhost)
	bandwidth = translate_bandwidth(options.bandwidth)
	time = float(options.time)*1e9 # translates to ns
	short_flow_size = int(options.short_flowSize)*1000*1000  # MB to Bytes
	# 为了让长流能够“以full rate发送”并持续整个仿真时间，我们需要计算所需的总字节数。
	# Size = Bandwidth (bps) * Time (s) / 8
	# 增加一点冗余(* 1.2)确保流不会在仿真结束前发完
	long_flow_size = int(bandwidth * float(options.time) / 8 * 1.2)
	output = options.output
	if bandwidth == None:
		print "bandwidth format incorrect"
		sys.exit(0)

	ofile = open(output, "w")

	# 1. 随机选择一对 Sender 和 Receiver
	src1 = random.randint(0, nhost-1)
	src2 = random.randint(0, nhost-1)
	while (src2 == src1):
		src2 = random.randint(0, nhost-1)
	dst = random.randint(0, nhost-1)
	while (dst == src1 or dst == src2):
		dst = random.randint(0, nhost-1)
	
	print "Generating traffic: Src1 %d -> Dst %d, Src2 %d -> Dst %d"%(src1, dst, src2, dst)
	print "Long Flow Size: %d Bytes (Calculated to fill %.3fs)"%(long_flow_size, float(options.time))
	print "Short Flow Size: %d Bytes"%(short_flow_size)

	# 2. 写入流的数量 (2条)
	ofile.write("2 \n")

	# 3. 生成 Long Flow (从 base_t 开始)
	# start_time 使用 base_t，单位转为秒
	start_time_long = base_t * 1e-9
	ofile.write("%d %d 3 100 %d %.9f\n"%(src1, dst, long_flow_size, start_time_long))

	# 4. 生成 Short Flow (在仿真中间某一时刻插入)
	# 插入时间点 = base_t + 0.5ms
	start_time_short_ns = base_t + 0.5 * 1000000
	start_time_short = start_time_short_ns * 1e-9
	ofile.write("%d %d 3 100 %d %.9f\n"%(src2, dst, short_flow_size, start_time_short))

	ofile.close()
	print "Done. Traffic file written to %s"%output

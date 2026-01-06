#include <cstdio>
#include <unistd.h>
#include <unordered_map>
#include <unordered_set>
#include <iomanip> // 用于格式化输出
#include "trace-format.h"
#include "trace_filter.hpp"
#include "utils.hpp"
#include "sim-setting.h"

using namespace ns3;
using namespace std;

int main(int argc, char** argv){
	if (argc != 2 && argc != 3){
		printf("Usage: ./trace_reader <trace_file> [filter_expr]\n");
		return 0;
	}
	FILE* file = fopen(argv[1], "r");
	TraceFilter f;
	if (argc == 3){
		f.parse(argv[2]);
		if (f.root == NULL){
			printf("Invalid filter\n");
			return 0;
		}
	}
	//printf("filter: %s\n", f.str().c_str());

	// first read SimSetting
	SimSetting sim_setting;
	sim_setting.Deserialize(file);
	#if 0
	// print sim_setting
	for (auto i : sim_setting.port_speed)
		for (auto j : i.second)
			printf("%u,%u:%lu\n", i.first, j.first, j.second);
	#endif

	// read trace
	TraceFormat tr;
    // 设定拟要统计的链路 Node, Port ，保存文件名，时间窗口(ns)
    PerFlowThroughputTracker flowTracker1(124, 1, "path/to/save/throughput.txt", 1000);
	PerFlowThroughputTracker flowTracker2(109, 1, "path/to/save/throughput.txt", 1000);
	// PerFlowThroughputTracker flowTracker3(203, 1, "path/to/save/throughput.txt", 1000);
	// PerFlowThroughputTracker flowTracker4(74, 1, "path/to/save/throughput.txt", 1000);
	LatencyTracker latencyTracker; // 新增实例化统计器
	while (tr.Deserialize(file) > 0){
		if (!f.test(tr))
			continue;
		// print_trace(tr);
		flowTracker1.ProcessEvent(tr); // 处理链路吞吐量统计
		flowTracker2.ProcessEvent(tr); // 处理链路吞吐量统计
		// flowTracker3.ProcessEvent(tr); // 处理链路吞吐量统计
		// flowTracker4.ProcessEvent(tr); // 处理链路吞吐量统计
		// latencyTracker.ProcessEvent(tr);// 新增统计处理
	}
	flowTracker1.SaveStatsToFile();; // 输出链路吞吐量统计
	flowTracker2.SaveStatsToFile();; // 输出链路吞吐量统计
	// flowTracker3.SaveStatsToFile();; // 输出链路吞吐量统计
	// flowTracker4.SaveStatsToFile();; // 输出链路吞吐量统计
	// // 循环结束后输出平均值
    // printf("--------------------------------\n");
    // latencyTracker.PrintStats();
    // printf("--------------------------------\n");
}

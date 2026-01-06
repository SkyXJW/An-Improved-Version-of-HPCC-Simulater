#ifndef UTILS_HPP
#define UTILS_HPP

#include "trace-format.h"
#include <iostream>
#include <fstream> // 必须引入，用于文件写入
#include <string>  // 必须引入，用于处理文件名
#include <vector>
#include <algorithm> // 必须引入，用于排序
#include <map>

typedef uint64_t FlowInt;

static uint32_t GetDevInt(uint16_t node, uint8_t intf){
	return ((uint32_t)node << 8) | intf;
}
struct Device{
	uint16_t node;
	uint8_t intf;

	Device(uint16_t _node, uint8_t _intf): node(_node), intf(_intf) {}
	uint32_t GetDevInt(){
		return ::GetDevInt(node, intf);
	}
};

static inline bool IsFlow(ns3::TraceFormat &tr){
	return tr.l3Prot == 0x6 || tr.l3Prot == 0x11 || tr.l3Prot == 0xFC || tr.l3Prot == 0xFD || tr.l3Prot == 0x0;
}

static inline FlowInt GetFlowInt(uint32_t sip, uint32_t dip, uint16_t sport, uint16_t dport){
	FlowInt res;
	uint64_t src = (sip >> 8) & 0xffff, dst = (dip >> 8) & 0xffff;
	res = ((src << 16) | dst);
	res = (((res << 16) | sport) << 16) | dport;
	return res;
}
static inline FlowInt GetFlowInt(ns3::TraceFormat &tr){
	switch (tr.l3Prot){
		case 0x6:
		case 0x11:
			return GetFlowInt(tr.sip, tr.dip, tr.data.sport, tr.data.dport);
		case 0xFC: // ACK
		case 0xFD: // NACK
			return GetFlowInt(tr.sip, tr.dip, tr.ack.sport, tr.ack.dport);
		case 0x0: // QpAv
			return GetFlowInt(tr.sip, tr.dip, tr.qp.sport, tr.qp.dport);
		default:
			return GetFlowInt(tr.sip, tr.dip, 0, 0);
	}
}
static inline FlowInt GetReverseFlowInt(ns3::TraceFormat &tr){
	switch (tr.l3Prot){
		case 0x6:
		case 0x11:
			return GetFlowInt(tr.dip, tr.sip, tr.data.dport, tr.data.sport);
		case 0xFC: // ACK
		case 0xFD: // NACK
			return GetFlowInt(tr.dip, tr.sip, tr.ack.dport, tr.ack.sport);
		case 0x0: // QpAv
			return GetFlowInt(tr.dip, tr.sip, tr.qp.dport, tr.qp.sport);
		default:
			return GetFlowInt(tr.dip, tr.sip, 0, 0);
	}
}

// Return the forward direction FlowInt for data, and reverse FlowInt for ACK
static inline FlowInt GetStandardFlowInt(ns3::TraceFormat &tr){
	if (tr.l3Prot == 0xFC || tr.l3Prot == 0xFD)
		return GetReverseFlowInt(tr);
	else
		return GetFlowInt(tr);
}

static inline char l3ProtToChar(uint8_t p){
	switch (p){
		case 0x6:
			return 'T';
		case 0x11:
			return 'U';
		case 0xFC: // ACK
			return 'A';
		case 0xFD: // NACK
			return 'N';
		case 0xFE: // PFC
			return 'P';
		case 0xFF:
			return 'C';
		default:
			return 'X';
	}
}

static inline void print_trace(ns3::TraceFormat &tr){
	switch (tr.l3Prot){
		case 0x6:
		case 0x11:
			printf("%lu n:%u %u:%u %u %s ecn:%x %08x %08x %hu %hu %c %u %lu %u %hu(%hu)", tr.time, tr.node, tr.intf, tr.qidx, tr.qlen, EventToStr((ns3::Event)tr.event), tr.ecn, tr.sip, tr.dip, tr.data.sport, tr.data.dport, l3ProtToChar(tr.l3Prot), tr.data.seq, tr.data.ts, tr.data.pg, tr.size, tr.data.payload);
			break;
		case 0xFC: // ACK
			printf("%lu n:%u %u:%u %u %s ecn:%x %08x %08x %u %u %c 0x%02X %u %u %lu %hu", tr.time, tr.node, tr.intf, tr.qidx, tr.qlen, EventToStr((ns3::Event)tr.event), tr.ecn, tr.sip, tr.dip, tr.ack.sport, tr.ack.dport, l3ProtToChar(tr.l3Prot), tr.ack.flags, tr.ack.pg, tr.ack.seq, tr.ack.ts, tr.size);
			break;
		case 0xFD: // NACK
			printf("%lu n:%u %u:%u %u %s ecn:%x %08x %08x %u %u %c 0x%02X %u %u %lu %hu", tr.time, tr.node, tr.intf, tr.qidx, tr.qlen, EventToStr((ns3::Event)tr.event), tr.ecn, tr.sip, tr.dip, tr.ack.sport, tr.ack.dport, l3ProtToChar(tr.l3Prot), tr.ack.flags, tr.ack.pg, tr.ack.seq, tr.ack.ts, tr.size);
			break;
		case 0xFE: // PFC
			printf("%lu n:%u %u:%u %u %s ecn:%x %08x %08x %c %u %u %u %hu", tr.time, tr.node, tr.intf, tr.qidx, tr.qlen, EventToStr((ns3::Event)tr.event), tr.ecn, tr.sip, tr.dip, l3ProtToChar(tr.l3Prot), tr.pfc.time, tr.pfc.qlen, tr.pfc.qIndex, tr.size);
			break;
		case 0xFF: // CNP
			printf("%lu n:%u %u:%u %u %s ecn:%x %08x %08x %c %u %u %u %u %u", tr.time, tr.node, tr.intf, tr.qidx, tr.qlen, EventToStr((ns3::Event)tr.event), tr.ecn, tr.sip, tr.dip, l3ProtToChar(tr.l3Prot), tr.cnp.fid, tr.cnp.qIndex, tr.cnp.ecnBits, tr.cnp.seq, tr.size);
			break;
		case 0x0: // QpAv
			printf("%lu n:%u %u:%u %s %08x %08x %u %u", tr.time, tr.node, tr.intf, tr.qidx, EventToStr((ns3::Event)tr.event), tr.sip, tr.dip, tr.qp.sport, tr.qp.dport);
			break;
		default:
			printf("%lu n:%u %u:%u %u %s ecn:%x %08x %08x %x %u", tr.time, tr.node, tr.intf, tr.qidx, tr.qlen, EventToStr((ns3::Event)tr.event), tr.ecn, tr.sip, tr.dip, tr.l3Prot, tr.size);
			break;
	}
	printf("\n");
}

class LatencyTracker {
public:
    double total_latency_sum = 0;
    uint64_t total_packet_count = 0;
	std::vector<double> latency_samples;

    // 嵌套 Map: [FlowID] -> [SequenceNumber + Flow_Size] -> SendTime
    std::map<FlowInt, std::map<uint32_t, uint64_t>> sent_times;

    void ProcessEvent(ns3::TraceFormat &tr) {
        // 获取标准化的 FlowID (让 Data 和 ACK 属于同一个 FlowID)
        FlowInt flow_id = GetStandardFlowInt(tr);

        // 判断是 Data Packet 还是 ACK
        bool is_data = (tr.l3Prot == 0x11 || tr.l3Prot == 0x6); // UDP(HPCC Data) or TCP
        bool is_ack  = (tr.l3Prot == 0xFC); // HPCC ACK

        // 1. 处理发送端发送数据 (Sender Enqueue)
        // 我们关注 Dequ 事件，并且为了避免中间交换机的 Dequ 干扰，
        // 这里的逻辑最好配合 IP 判断。但如果没有拓扑信息，利用 map.insert 的特性(不覆盖)
        // 可以保证我们记录的是最早的一次 Dequ (即源端发送)。
        if (is_data && tr.event == ns3::Dequ) {
            // insert 只有在 key 不存在时才插入。
            // 这样能保证我们记录的是源主机第一次发出的时间，而不是中间交换机转发的时间。
            sent_times[flow_id].insert({tr.data.seq + tr.data.payload, tr.time});
        }

        // 2. 处理发送端收到 ACK (Sender Receive ACK)
		// 为了保证记录的不是中间交换机接收到ACK的时间，这里需要判断当前收到ACK的设备类型是不是主机(nodeType=0)
        else if (is_ack && tr.nodeType == 0 && tr.event == ns3::Recv) {
            // 查找这个 Flow 是否有对应的未确认包
            if (sent_times.find(flow_id) != sent_times.end()) {
                auto &flow_seq_map = sent_times[flow_id];
                // 查找对应的 Sequence Number
                // 注意：这里假设 ACK 的 seq 字段与 Data 的 seq 字段是对应的
                auto it = flow_seq_map.find(tr.ack.seq-tr.data.payload); // 减去 payload 得到原始数据包的 seq
                
                if (it != flow_seq_map.end()) {
                    uint64_t send_time = it->second;
                    uint64_t rtt = tr.time - send_time;
					// printf("Flow: %lu Seq: %u ts: %lu ns send_time: %lu ns\n", flow_id, tr.ack.seq-1000, tr.time, send_time);

                    // 累计统计数据
                    total_latency_sum += rtt;
                    total_packet_count++;
					latency_samples.push_back(rtt);

                    // 移除已计算的记录以释放内存 (如果不是累积ACK机制)
                    flow_seq_map.erase(it);
                    
                    // 可选：打印单个包的延迟用于调试
                    // printf("Flow: %lu Seq: %u RTT: %lu ns\n", flow_id, tr.ack.seq, rtt);
                }
            }
        }
    }

    void PrintStats() {
        if (total_packet_count > 0) {
            double avg_latency = total_latency_sum / total_packet_count;
            printf("Total Packets: %lu\n", total_packet_count);
            printf("Total Latency: %.0f ns\n", total_latency_sum);
            printf("Average Latency: %.4f ns\n", avg_latency);
			double p95_latency = Get95PercentileFast();
			printf("95th Percentile Latency: %.4f ns\n", p95_latency);
        } else {
            printf("No completed packet exchanges found.\n");
        }
    }

	double Get95PercentileFast() {
    	if (latency_samples.empty()) return 0.0;

    	size_t index_95 = (size_t)(latency_samples.size() * 0.95);

    	// nth_element 会将第 n 个位置的元素放到它排好序后应该在的位置
    	// 并且保证左边的都比它小，右边的都比它大
    	std::nth_element(latency_samples.begin(), 
        	             latency_samples.begin() + index_95, 
            	         latency_samples.end());

    	return latency_samples[index_95];
	}
};

class PerFlowThroughputTracker {
public:
    uint16_t target_node;
    uint8_t target_intf;
    uint64_t window_size_ns;
    std::string output_filename;

    // 嵌套 Map 结构:
    // 外层 Key: 时间窗口索引 (time / window_size)
    // 内层 Key: FlowID (由 GetStandardFlowInt 获取)
    // 内层 Value: 该流在该窗口内的字节数
    std::map<uint64_t, std::map<FlowInt, uint64_t>> bytes_per_window_per_flow;

    // 辅助 Map: 记录 FlowID 到可读字符串的映射 (方便调试知道是哪个IP对)
    std::map<FlowInt, std::string> flow_descriptions;

    PerFlowThroughputTracker(uint16_t node, uint8_t intf, std::string filename, uint64_t window = 1000) 
        : target_node(node), target_intf(intf), output_filename(filename), window_size_ns(window) {}

    void ProcessEvent(ns3::TraceFormat &tr) {
        // 1. 过滤：只处理目标链路
        if (tr.node != target_node || tr.intf != target_intf) {
            return;
        }

        // 2. 过滤：只处理出队事件 (Dequ) 且只处理数据包 (排除纯ACK，视需求而定)
        // 注意：GetStandardFlowInt 会把 ACK 归类到原 FlowID。
        // 如果你只想统计 Data 流量的带宽，建议加上 is_data 判断。
        bool is_data = (tr.l3Prot == 0x11 || tr.l3Prot == 0x6); // UDP(HPCC) or TCP
        
        if (tr.event == ns3::Dequ && is_data) { 
            uint64_t window_idx = tr.time / window_size_ns;
            
            // 获取流 ID
            FlowInt flow_id = GetStandardFlowInt(tr);

            // 累加该流的字节数
            bytes_per_window_per_flow[window_idx][flow_id] += tr.size;

            // (可选) 记录流的描述信息，只需记录一次
            if (flow_descriptions.find(flow_id) == flow_descriptions.end()) {
                char buf[128];
                // 简单的描述：SIP -> DIP
                sprintf(buf, "%u.%u.%u.%u -> %u.%u.%u.%u", 
                    (tr.sip>>24)&0xff, (tr.sip>>16)&0xff, (tr.sip>>8)&0xff, tr.sip&0xff,
                    (tr.dip>>24)&0xff, (tr.dip>>16)&0xff, (tr.dip>>8)&0xff, tr.dip&0xff);
                flow_descriptions[flow_id] = std::string(buf);
            }
        }
    }

    void SaveStatsToFile() {
        std::ofstream outfile(output_filename);

        if (!outfile.is_open()) {
            std::cerr << "Error: Could not open file " << output_filename << std::endl;
            return;
        }

        // 写入 CSV 头部
        outfile << "TimeWindow_Start(ns),FlowID,Throughput(Gbps),Description\n";

        // 遍历所有时间窗口
        for (auto const& [window_idx, flow_map] : bytes_per_window_per_flow) {
            uint64_t start_time = window_idx * window_size_ns;
  
            // 遍历该窗口内的每一条流
            for (auto const& [flow_id, total_bytes] : flow_map) {
                // 计算吞吐量
                double throughput_gbps = (double)(total_bytes * 8) / window_size_ns;

                // 写入文件
                // 格式: 时间, FlowID(十六进制), 吞吐量, IP描述
                outfile << start_time << "," 
                        << std::hex << "0x" << flow_id << std::dec << "," 
                        << throughput_gbps << ","
                        << flow_descriptions[flow_id] << "\n";
            }
        }

        outfile.close();
        printf("Saved per-flow throughput to %s\n", output_filename.c_str());
        
        // 打印一下流的对应关系到控制台，方便你区分 Long/Short Flow
        printf("--- Flow ID Legend ---\n");
        for(auto const& [fid, desc] : flow_descriptions) {
            printf("ID: 0x%lx represents %s\n", fid, desc.c_str());
        }
    }
};

#endif /* UTILS_HPP */

#!/usr/bin/env python3
import struct

def read_pcap(filename):
    """读取 pcap 文件并提取 HTTP POST 请求"""
    with open(filename, 'rb') as f:
        # 读取全局头部 (24 字节)
        global_header = f.read(24)
        if len(global_header) < 24:
            print("文件太小，不是有效的 pcap 文件")
            return
        
        magic = struct.unpack('I', global_header[0:4])[0]
        print(f"PCAP Magic: {hex(magic)}")
        
        packets = []
        packet_num = 0
        
        while True:
            # 读取数据包头部 (16 字节)
            packet_header = f.read(16)
            if len(packet_header) < 16:
                break
            
            # 解析数据包头部
            ts_sec, ts_usec, incl_len, orig_len = struct.unpack('IIII', packet_header)
            
            # 读取数据包数据
            packet_data = f.read(incl_len)
            if len(packet_data) < incl_len:
                break
            
            packets.append((packet_num, packet_data))
            packet_num += 1
        
        print(f"总共读取了 {len(packets)} 个数据包\n")
        return packets

def extract_http_data(packet_data):
    """从数据包中提取 HTTP 数据"""
    try:
        # 跳过以太网头部 (14 字节)
        if len(packet_data) < 14:
            return None
        
        # 检查是否是 IP 包 (EtherType = 0x0800)
        ether_type = struct.unpack('!H', packet_data[12:14])[0]
        if ether_type != 0x0800:
            return None
        
        # 解析 IP 头部
        ip_header = packet_data[14:34]
        if len(ip_header) < 20:
            return None
        
        # 获取 IP 头部长度
        ip_header_len = (ip_header[0] & 0x0F) * 4
        
        # 检查协议 (6 = TCP)
        protocol = ip_header[9]
        if protocol != 6:
            return None
        
        # 解析 TCP 头部
        tcp_start = 14 + ip_header_len
        if len(packet_data) < tcp_start + 20:
            return None
        
        tcp_header = packet_data[tcp_start:tcp_start + 20]
        
        # 获取 TCP 头部长度
        tcp_header_len = ((tcp_header[12] >> 4) & 0x0F) * 4
        
        # 提取 TCP 数据
        tcp_data_start = tcp_start + tcp_header_len
        if tcp_data_start >= len(packet_data):
            return None
        
        tcp_data = packet_data[tcp_data_start:]
        
        # 检查是否包含 HTTP POST
        if tcp_data.startswith(b'POST'):
            return tcp_data
        
        return None
    except Exception as e:
        return None

# 主程序
print("开始分析 pcap 文件...\n")
packets = read_pcap('pcapExfil.pcap')

if packets:
    post_count = 0
    all_post_data = []
    
    for pkt_num, pkt_data in packets:
        http_data = extract_http_data(pkt_data)
        if http_data:
            post_count += 1
            print(f"{'='*60}")
            print(f"找到 POST 请求 #{post_count} (数据包 #{pkt_num})")
            print(f"{'='*60}")
            
            try:
                decoded = http_data.decode('utf-8', errors='ignore')
                print(decoded)
                all_post_data.append(decoded)
            except:
                print("无法解码数据")
                print(http_data[:200])
            
            print()
    
    print(f"\n总共找到 {post_count} 个 POST 请求")
    
    # 尝试提取所有 POST 数据体
    print("\n" + "="*60)
    print("提取的 POST 数据:")
    print("="*60)
    for data in all_post_data:
        if '\r\n\r\n' in data:
            body = data.split('\r\n\r\n', 1)[1]
            print(body)
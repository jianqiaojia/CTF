#!/usr/bin/env python3
import struct

def extract_tcp_stream(filename):
    """从 pcap 文件中提取完整的 TCP 流"""
    with open(filename, 'rb') as f:
        # 跳过全局头部
        f.read(24)
        
        # 用于存储特定 TCP 流的数据
        tcp_streams = {}
        packet_num = 0
        
        while True:
            # 读取数据包头部
            packet_header = f.read(16)
            if len(packet_header) < 16:
                break
            
            ts_sec, ts_usec, incl_len, orig_len = struct.unpack('IIII', packet_header)
            packet_data = f.read(incl_len)
            
            if len(packet_data) < incl_len:
                break
            
            # 解析以太网、IP、TCP 头部
            try:
                # 跳过以太网头部 (14 字节)
                if len(packet_data) < 54:  # 以太网 + IP + TCP 最小长度
                    packet_num += 1
                    continue
                
                # 检查 IP 协议
                ip_start = 14
                protocol = packet_data[ip_start + 9]
                
                if protocol != 6:  # 不是 TCP
                    packet_num += 1
                    continue
                
                # 获取 IP 头部长度
                ip_header_len = (packet_data[ip_start] & 0x0F) * 4
                
                # 获取源和目标端口
                tcp_start = ip_start + ip_header_len
                src_port = struct.unpack('!H', packet_data[tcp_start:tcp_start+2])[0]
                dst_port = struct.unpack('!H', packet_data[tcp_start+2:tcp_start+4])[0]
                
                # 获取 TCP 头部长度
                tcp_header_len = ((packet_data[tcp_start + 12] >> 4) & 0x0F) * 4
                
                # 提取 TCP 数据
                tcp_data_start = tcp_start + tcp_header_len
                if tcp_data_start >= len(packet_data):
                    packet_num += 1
                    continue
                
                tcp_data = packet_data[tcp_data_start:]
                
                # 如果这是 HTTP 流（端口 80）
                if dst_port == 80 or src_port == 80:
                    stream_id = f"{src_port}-{dst_port}"
                    
                    if stream_id not in tcp_streams:
                        tcp_streams[stream_id] = []
                    
                    tcp_streams[stream_id].append((packet_num, tcp_data))
                    
                    if b'POST /upload' in tcp_data:
                        print(f"包 #{packet_num}: 找到 POST 请求开始 (流 {stream_id})")
                    elif len(tcp_data) > 0:
                        print(f"包 #{packet_num}: 流 {stream_id}, 数据长度 {len(tcp_data)}")
            
            except Exception as e:
                pass
            
            packet_num += 1
        
        return tcp_streams

print("分析 TCP 流...")
streams = extract_tcp_stream('pcapExfil.pcap')

print(f"\n找到 {len(streams)} 个 TCP 流")

# 找到包含 POST 的流
for stream_id, packets in streams.items():
    print(f"\n流 {stream_id}:")
    
    # 合并所有数据
    full_data = b''.join([data for _, data in packets])
    
    if b'POST /upload' in full_data:
        print(f"  这是上传流，总数据大小: {len(full_data)} 字节")
        
        # 查找文件数据
        if b'Content-Type: application/zip' in full_data:
            parts = full_data.split(b'Content-Type: application/zip')
            if len(parts) > 1:
                after_header = parts[1]
                
                # 查找数据开始位置
                if b'\r\n\r\n' in after_header:
                    file_data = after_header.split(b'\r\n\r\n', 1)[1]
                else:
                    # 跳过空行
                    lines = after_header.split(b'\n')
                    for i, line in enumerate(lines):
                        if line.strip() == b'':
                            file_data = b'\n'.join(lines[i+1:])
                            break
                
                # 查找结尾的 boundary
                boundary = b'------WebKitFormBoundary7MA4YWxkTrZu0gW'
                if boundary in file_data:
                    file_data = file_data.split(boundary)[0]
                
                # 清理数据
                file_data = file_data.rstrip(b'\r\n-')
                
                print(f"  提取的文件大小: {len(file_data)} 字节")
                print(f"  文件头: {file_data[:20]}")
                print(f"  文件尾: {file_data[-20:]}")
                
                # 保存文件
                with open('exfil_data_full.zip', 'wb') as f:
                    f.write(file_data)
                print(f"  已保存为 exfil_data_full.zip")
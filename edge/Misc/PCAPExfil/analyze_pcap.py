#!/usr/bin/env python3
from scapy.all import rdpcap, TCP, Raw
import binascii

# 读取 pcap 文件
print("正在读取 pcap 文件...")
pkts = rdpcap('pcapExfil.pcap')

print(f"总共有 {len(pkts)} 个数据包\n")

# 查找 HTTP POST 请求
post_requests = []
for i, pkt in enumerate(pkts):
    if TCP in pkt and Raw in pkt:
        payload = bytes(pkt[Raw].load)
        if payload.startswith(b'POST'):
            post_requests.append((i, pkt, payload))
            print(f"找到 POST 请求 - 数据包 #{i}")

print(f"\n共找到 {len(post_requests)} 个 POST 请求\n")

# 分析每个 POST 请求
for idx, (pkt_num, pkt, payload) in enumerate(post_requests):
    print(f"\n{'='*60}")
    print(f"POST 请求 #{idx+1} (数据包 #{pkt_num})")
    print(f"{'='*60}")
    
    try:
        # 尝试解码为文本
        decoded = payload.decode('utf-8', errors='ignore')
        print(decoded)
        
        # 查找 POST 数据
        if '\r\n\r\n' in decoded:
            headers, body = decoded.split('\r\n\r\n', 1)
            print(f"\n--- POST 数据 ---")
            print(body)
            
    except Exception as e:
        print(f"解码错误: {e}")
        print("原始十六进制数据:")
        print(binascii.hexlify(payload).decode())

print("\n分析完成！")
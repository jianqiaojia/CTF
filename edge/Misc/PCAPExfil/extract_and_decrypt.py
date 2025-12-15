#!/usr/bin/env python3
import struct
import zipfile
import io

def extract_zip_from_pcap(filename):
    """从 pcap 文件中提取 ZIP 文件"""
    with open(filename, 'rb') as f:
        # 跳过全局头部
        f.read(24)
        
        while True:
            # 读取数据包头部
            packet_header = f.read(16)
            if len(packet_header) < 16:
                break
            
            ts_sec, ts_usec, incl_len, orig_len = struct.unpack('IIII', packet_header)
            packet_data = f.read(incl_len)
            
            if len(packet_data) < incl_len:
                break
            
            # 查找 ZIP 文件标识 (PK)
            if b'PK\x03\x04' in packet_data:
                # 找到 ZIP 文件的起始位置
                zip_start = packet_data.find(b'PK\x03\x04')
                
                # 提取从 PK 开始的所有数据
                zip_data = packet_data[zip_start:]
                
                print(f"找到 ZIP 文件数据，大小: {len(zip_data)} 字节")
                return zip_data
    
    return None

print("从 pcap 文件中提取 ZIP 文件...")
zip_data = extract_zip_from_pcap('pcapExfil.pcap')

if zip_data:
    # 保存 ZIP 文件
    with open('extracted.zip', 'wb') as f:
        f.write(zip_data)
    print("ZIP 文件已保存为 extracted.zip")
    
    # 尝试解压
    try:
        with zipfile.ZipFile(io.BytesIO(zip_data), 'r') as zip_ref:
            print("\nZIP 文件内容:")
            for name in zip_ref.namelist():
                print(f"  - {name}")
            
            # 提取加密的文件
            zip_ref.extractall('.')
            print("\n文件已解压到当前目录")
    except Exception as e:
        print(f"解压错误: {e}")
else:
    print("未找到 ZIP 文件数据")
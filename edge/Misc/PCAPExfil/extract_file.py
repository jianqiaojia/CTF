#!/usr/bin/env python3
import struct

def extract_http_post_data(filename):
    """从 pcap 文件中提取 HTTP POST 的文件数据"""
    with open(filename, 'rb') as f:
        # 跳过全局头部
        f.read(24)
        
        all_data = b''
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
            
            # 检查是否是第一个包（包含 POST 和文件头）
            if b'POST /upload' in packet_data and b'exfil_data.zip' in packet_data:
                print(f"找到 POST 请求包 #{packet_num}")
                
                # 找到 HTTP 头部结束和数据开始的位置
                boundary = b'------WebKitFormBoundary7MA4YWxkTrZu0gW'
                
                # 查找文件数据的开始（在 Content-Type: application/zip 后面的空行）
                parts = packet_data.split(b'Content-Type: application/zip')
                if len(parts) > 1:
                    # 找到两个连续换行后的数据
                    after_header = parts[1]
                    # 查找 \r\n\r\n 或 \n\n
                    if b'\r\n\r\n' in after_header:
                        file_data = after_header.split(b'\r\n\r\n', 1)[1]
                    elif b'\n\n' in after_header:
                        file_data = after_header.split(b'\n\n', 1)[1]
                    else:
                        file_data = after_header[4:]  # 跳过一些字节
                    
                    # 移除结尾的 boundary
                    if boundary in file_data:
                        file_data = file_data.split(boundary)[0]
                    
                    # 移除可能的尾部换行
                    file_data = file_data.rstrip(b'\r\n-')
                    
                    print(f"提取的文件数据大小: {len(file_data)} 字节")
                    print(f"前20字节: {file_data[:20]}")
                    return file_data
            
            packet_num += 1
    
    return None

print("提取 ZIP 文件...")
file_data = extract_http_post_data('pcapExfil.pcap')

if file_data:
    # 保存文件
    with open('exfil_data.zip', 'wb') as f:
        f.write(file_data)
    print(f"\n文件已保存为 exfil_data.zip ({len(file_data)} 字节)")
    
    # 尝试解压
    import zipfile
    try:
        with zipfile.ZipFile('exfil_data.zip', 'r') as zip_ref:
            print("\nZIP 文件内容:")
            for name in zip_ref.namelist():
                info = zip_ref.getinfo(name)
                print(f"  - {name} ({info.file_size} 字节)")
            
            zip_ref.extractall('.')
            print("\n文件已解压")
    except Exception as e:
        print(f"\n解压错误: {e}")
        print("尝试使用 7zip 或手动检查文件")
else:
    print("未找到文件数据")
#!/usr/bin/env python3

# 读取原始hex文件
with open('unzip', 'r') as f:
    hex_str = f.read().strip()

print(f"原始hex字符串长度: {len(hex_str)}")
print(f"="*80)

# 将hex转为bytes
import binascii
data = binascii.unhexlify(hex_str)

print(f"二进制数据长度: {len(data)} 字节")
print(f"="*80)

# 尝试1: 直接在hex字符串中查找EdgeCTF
print("在hex字符串中搜索'EdgeCTF':")
if 'EdgeCTF' in hex_str:
    idx = hex_str.find('EdgeCTF')
    print(f"找到! 位置: {idx}")
    print(f"上下文: {hex_str[max(0,idx-20):idx+50]}")
else:
    print("未找到")

# 尝试2: 将'EdgeCTF'转为hex然后搜索
edge_hex = ''.join(f'{ord(c):02x}' for c in 'EdgeCTF{')
print(f"\n'EdgeCTF{{' 的hex编码: {edge_hex}")
if edge_hex in hex_str:
    idx = hex_str.find(edge_hex)
    print(f"找到! 位置: {idx}")
    print(f"上下文: {hex_str[idx:idx+100]}")
else:
    print("未找到")

# 尝试3: 在二进制数据中搜索
print(f"\n在二进制数据中搜索 b'EdgeCTF':")
if b'EdgeCTF' in data:
    idx = data.find(b'EdgeCTF')
    print(f"找到! 位置: {idx}")
    print(f"上下文: {data[max(0,idx-20):idx+100]}")
    
    # 尝试提取完整flag
    end_idx = data.find(b'}', idx)
    if end_idx != -1:
        flag = data[idx:end_idx+1].decode('utf-8', errors='ignore')
        print(f"\n🎯🎯🎯 FLAG: {flag}")
else:
    print("未找到")

# 尝试4: 也许flag在ZIP文件comment或extra字段?
# 但我们已经检查过了...

# 尝试5: 检查是否有其他隐藏数据
print(f"\n" + "="*80)
print("检查ZIP文件结构之外的数据:")
print("="*80)

# ZIP文件应该从PK开始
pk_start = data.find(b'PK\x03\x04')
print(f"ZIP文件开始位置: {pk_start}")

if pk_start > 0:
    print(f"ZIP之前有 {pk_start} 字节数据:")
    pre_zip = data[:pk_start]
    print(f"  Hex: {pre_zip.hex()}")
    print(f"  尝试UTF-8: {pre_zip.decode('utf-8', errors='ignore')}")
    
    if b'EdgeCTF' in pre_zip:
        print(f"  🎯 在ZIP之前的数据中找到EdgeCTF!")

# ZIP文件应该在EOCD结束
eocd = data.rfind(b'PK\x05\x06')
if eocd != -1:
    # EOCD长度至少22字节
    eocd_end = eocd + 22
    # 但如果有comment,会更长
    comment_len = int.from_bytes(data[eocd+20:eocd+22], 'little')
    eocd_end += comment_len
    
    print(f"\nZIP文件结束位置: {eocd_end}")
    
    if eocd_end < len(data):
        print(f"ZIP之后有 {len(data) - eocd_end} 字节数据:")
        post_zip = data[eocd_end:]
        print(f"  Hex: {post_zip.hex()}")
        print(f"  尝试UTF-8: {post_zip.decode('utf-8', errors='ignore')}")
        
        if b'EdgeCTF' in post_zip:
            print(f"  🎯 在ZIP之后的数据中找到EdgeCTF!")
            idx = post_zip.find(b'EdgeCTF')
            end_idx = post_zip.find(b'}', idx)
            if end_idx != -1:
                flag = post_zip[idx:end_idx+1].decode('utf-8')
                print(f"  🎯🎯🎯 FLAG: {flag}")
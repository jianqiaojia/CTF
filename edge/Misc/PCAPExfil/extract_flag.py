#!/usr/bin/env python3
import re

print("正在分析 flag.png...")

with open('flag.png', 'rb') as f:
    data = f.read()

print(f"文件大小: {len(data)} 字节")

# 搜索 EdgeCTF 格式的 flag
matches = re.findall(b'EdgeCTF\\{[^}]+\\}', data)

if matches:
    print("\n找到 Flag:")
    for match in matches:
        flag = match.decode('utf-8', errors='ignore')
        print(f"  {flag}")
else:
    print("\n未找到 EdgeCTF{...} 格式的 flag")
    print("尝试搜索其他模式...")
    
    # 尝试搜索可打印的字符串
    printable = re.findall(b'[ -~]{20,}', data)
    if printable:
        print("\n找到的可打印字符串:")
        for s in printable[:10]:  # 只显示前10个
            print(f"  {s.decode('utf-8', errors='ignore')}")

# 检查 PNG 文本块
print("\n检查 PNG 文本块...")
i = 8  # 跳过 PNG 签名
while i < len(data) - 12:
    chunk_len = int.from_bytes(data[i:i+4], 'big')
    chunk_type = data[i+4:i+8]
    
    if chunk_type == b'tEXt' or chunk_type == b'zTXt' or chunk_type == b'iTXt':
        chunk_data = data[i+8:i+8+chunk_len]
        print(f"找到 {chunk_type.decode()} 块:")
        try:
            # tEXt 格式: keyword\0text
            if b'\x00' in chunk_data:
                keyword, text = chunk_data.split(b'\x00', 1)
                print(f"  关键字: {keyword.decode('utf-8', errors='ignore')}")
                print(f"  内容: {text.decode('utf-8', errors='ignore')}")
            else:
                print(f"  内容: {chunk_data.decode('utf-8', errors='ignore')}")
        except:
            print(f"  (无法解码)")
    
    i += 4 + 4 + chunk_len + 4  # length + type + data + crc

print("\n完成!")
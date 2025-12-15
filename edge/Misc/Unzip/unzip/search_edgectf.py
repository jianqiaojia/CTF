#!/usr/bin/env python3
import base64
import re

# 读取XZ解压后的数据并解码Base64
with open('data_decompressed.bin', 'rb') as f:
    base64_data = f.read()

decoded = base64.b64decode(base64_data)
text = decoded.decode('utf-8')

# 搜索 EdgeCTF{...} 格式的flag
pattern = r'EdgeCTF\{[^}]+\}'
matches = re.findall(pattern, text)

if matches:
    print("找到Flag:")
    for match in matches:
        print(match)
else:
    print("未找到 EdgeCTF{...} 格式的flag")
    
    # 也搜索包含 EdgeCTF 的任何内容
    if 'EdgeCTF' in text:
        idx = text.find('EdgeCTF')
        print(f"\n找到 'EdgeCTF' 在位置 {idx}")
        print(f"上下文: {text[max(0, idx-50):idx+100]}")
    else:
        print("\n文件中不包含 'EdgeCTF'")
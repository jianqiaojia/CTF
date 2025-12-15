#!/usr/bin/env python3
# 读取十六进制文件并转换为二进制ZIP文件

with open('unzip', 'r') as f:
    hex_data = f.read().strip()

# 将十六进制字符串转换为字节
binary_data = bytes.fromhex(hex_data)

# 保存为ZIP文件
with open('data.zip', 'wb') as f:
    f.write(binary_data)

print(f"成功转换！生成的ZIP文件大小: {len(binary_data)} 字节")
print(f"原始十六进制文件大小: {len(hex_data)} 字节")
print(f"'压缩'比率: {len(hex_data) / len(binary_data):.2f}x (变大了！)")
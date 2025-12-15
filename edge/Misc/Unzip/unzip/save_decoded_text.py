#!/usr/bin/env python3
import base64

# 读取XZ解压后的数据
with open('data_decompressed.bin', 'rb') as f:
    base64_data = f.read()

# 解码Base64
decoded = base64.b64decode(base64_data)
text = decoded.decode('utf-8')

# 保存为文本文件
with open('decoded_text.txt', 'w', encoding='utf-8') as f:
    f.write(text)

print(f"已保存解码文本到 decoded_text.txt")
print(f"文件大小: {len(text)} 字符")
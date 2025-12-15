#!/usr/bin/env python3
import lzma

# 读取XZ压缩文件
with open('data.bin', 'rb') as f:
    compressed_data = f.read()

# 解压
decompressed_data = lzma.decompress(compressed_data)

# 保存解压后的数据
with open('data_decompressed.bin', 'wb') as f:
    f.write(decompressed_data)

print(f"解压成功！")
print(f"压缩后大小: {len(compressed_data)} 字节")
print(f"解压后大小: {len(decompressed_data)} 字节")
print(f"前64字节内容:")
print(decompressed_data[:64])
print(f"\n尝试解码为文本:")
try:
    text = decompressed_data.decode('utf-8')
    print(text)
except:
    print("不是UTF-8文本")
    print(f"十六进制: {decompressed_data.hex()}")
#!/usr/bin/env python3
import base64

# 读取XZ解压后的数据并解码Base64
with open('data_decompressed.bin', 'rb') as f:
    base64_data = f.read()

decoded = base64.b64decode(base64_data)
text = decoded.decode('utf-8')

# 获取最后1000个字符
print("文件最后1000个字符:")
print(text[-1000:])
print("\n" + "="*80)

# 查找最后一个不同于重复模式的部分
pattern = "LRx4!F+o`-Q(1XNt&;&?jsyUp000Oe05E_}Mna$^sS1FXF+"

# 找到模式最后一次出现的位置
last_pos = text.rfind(pattern)
if last_pos != -1:
    # 获取之后的所有内容
    ending = text[last_pos:]
    
    # 找到第一个不属于模式的字符位置
    unique_start = len(pattern)
    for i in range(len(pattern), len(ending)):
        # 检查从这个位置开始是否还是模式
        if ending[i:i+len(pattern)] != pattern:
            # 找到了不同的部分
            unique_part = ending[i:]
            print(f"\n完全独特的部分 ({len(unique_part)} 字符):")
            print(repr(unique_part))
            print("\n实际内容:")
            print(unique_part)
            break
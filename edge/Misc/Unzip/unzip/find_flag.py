#!/usr/bin/env python3
import base64
import lzma

# 读取XZ解压后的数据
with open('data_decompressed.bin', 'rb') as f:
    base64_data = f.read()

# 解码Base64
decoded = base64.b64decode(base64_data)
text = decoded.decode('utf-8')

# 找到重复模式
pattern = "LRx4!F+o`-Q(1XNt&;&?jsyUp000Oe05E_}Mna$^sS1FXF+"

# 找到最后一个完整模式的位置
last_pattern_pos = text.rfind(pattern)

if last_pattern_pos != -1:
    # 提取最后一个模式之后的内容
    unique_part = text[last_pattern_pos + len(pattern):]
    print("找到独特的结尾部分:")
    print(unique_part)
    print(f"\n长度: {len(unique_part)} 字符")
    
    # 查找可能的flag格式
    if '{' in unique_part and '}' in unique_part:
        start = unique_part.find('{')
        end = unique_part.find('}', start)
        if start != -1 and end != -1:
            potential_flag = unique_part[start-20:end+1]  # 包含一些前缀
            print(f"\n可能的FLAG:")
            print(potential_flag)
else:
    print("未找到模式")
    # 直接查看文本末尾
    print("文本末尾1000字符:")
    print(text[-1000:])
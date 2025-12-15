#!/usr/bin/env python3
import base64

# 读取XZ解压后的数据并解码Base64
with open('data_decompressed.bin', 'rb') as f:
    base64_data = f.read()

decoded = base64.b64decode(base64_data)
text = decoded.decode('utf-8')

# 找到重复模式
pattern = "LRx4!F+o`-Q(1XNt&;&?jsyUp000Oe05E_}Mna$^sS1FXF+"

# 获取文件最后的内容
print("文件最后500个字符:")
print(text[-500:])
print("\n" + "="*80 + "\n")

# 找到最后一个完整模式后的内容
last_pattern_pos = text.rfind(pattern)
if last_pattern_pos != -1:
    after_last = text[last_pattern_pos + len(pattern):]
    print(f"最后一个模式后有 {len(after_last)} 个字符")
    print("内容:")
    print(after_last)
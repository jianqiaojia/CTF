#!/usr/bin/env python3
import base64

unique_ending = '&}K9zrO$g0}p`Y04o3l0EW+88UP3&0Cf$iKmdA=Q#68VsRn~gKxlgJyIptv{ScHD(h!sth5`Wz03_|#6IgbwXw&zxYAfDN=FkEG6czkk$rRy2L03CHH~'

print(f"尝试ASCII85/Base85解码")
print(f"原始字符串: {unique_ending}\n")

# ASCII85 (也称为Base85)使用字符集: !-u (ASCII 33-117)
# 标准的ASCII85格式是 <~...~>

# 尝试1: 添加ASCII85的标准包装
wrapped = f"<~{unique_ending}~>"
try:
    import base64
    decoded = base64.a85decode(wrapped)
    print(f"ASCII85解码成功!")
    print(f"解码结果(bytes): {decoded}")
    print(f"解码结果(UTF-8): {decoded.decode('utf-8', errors='ignore')}")
except Exception as e:
    print(f"ASCII85解码失败: {e}\n")

# 尝试2: 不添加包装直接解码
try:
    decoded = base64.a85decode(unique_ending)
    print(f"直接ASCII85解码成功!")
    print(f"解码结果(bytes): {decoded}")
    print(f"解码结果(UTF-8): {decoded.decode('utf-8', errors='ignore')}")
except Exception as e:
    print(f"直接ASCII85解码失败: {e}\n")

# 尝试3: Base85 (不同于ASCII85)
try:
    decoded = base64.b85decode(unique_ending)
    print(f"Base85解码成功!")
    print(f"解码结果(bytes): {decoded}")
    print(f"解码结果(UTF-8): {decoded.decode('utf-8', errors='ignore')}")
except Exception as e:
    print(f"Base85解码失败: {e}\n")

# 尝试4: 也许flag就是这个字符串重新排列?
# 观察: 字符串中有 {, 让我看看是否能找到 EdgeCTF{ 的组成部分
print("="*80)
print("字符频率分析:")
from collections import Counter
counter = Counter(unique_ending)
for char, count in counter.most_common():
    print(f"  '{char}': {count}")

print("\n检查是否包含'EdgeCTF'的所有字母:")
needed = set('EdgeCTF{}')
available = set(unique_ending)
print(f"需要的字符: {needed}")
print(f"可用的字符中包含的: {needed & available}")
print(f"缺少的字符: {needed - available}")
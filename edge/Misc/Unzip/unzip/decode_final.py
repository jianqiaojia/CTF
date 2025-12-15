#!/usr/bin/env python3
import base64

# 这是我们在文件末尾找到的独特字符串
unique_string = "&}K9zrO$g0}p`Y04o3l0EW+88UP3&0Cf$iKmdA=Q#68VsRn~gKxlgJyIptv{ScHD(h!sth5`Wz03_|#6IgbwXw&zxYAfDN=FkEG6czkk$rRy2L03CHH~"

print(f"原始字符串: {unique_string}")
print(f"长度: {len(unique_string)}")

# 尝试各种解码方法

# 1. 尝试Base64解码
try:
    # 去掉特殊字符，只保留可能的Base64字符
    import re
    base64_chars = re.sub(r'[^A-Za-z0-9+/=]', '', unique_string)
    print(f"\n提取的Base64字符: {base64_chars}")
    
    if base64_chars:
        decoded = base64.b64decode(base64_chars)
        print(f"Base64解码: {decoded}")
        try:
            print(f"UTF-8: {decoded.decode('utf-8')}")
        except:
            print(f"十六进制: {decoded.hex()}")
except Exception as e:
    print(f"Base64解码失败: {e}")

# 2. 查看是否是某种替换密码
print(f"\n字符统计:")
from collections import Counter
print(Counter(unique_string))

# 3. 尝试ROT13
print(f"\nROT13:")
import codecs
print(codecs.encode(unique_string, 'rot_13'))

# 4. 检查ASCII值
print(f"\nASCII值:")
print([ord(c) for c in unique_string[:20]])
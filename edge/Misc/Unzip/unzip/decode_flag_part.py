#!/usr/bin/env python3

# '{' 后的内容
flag_part = 'ScHD(h!sth5`Wz03_|#6IgbwXw&zxYAfDN=FkEG6czkk$rRy2L03CHH~'
full_ending = '&}K9zrO$g0}p`Y04o3l0EW+88UP3&0Cf$iKmdA=Q#68VsRn~gKxlgJyIptv{ScHD(h!sth5`Wz03_|#6IgbwXw&zxYAfDN=FkEG6czkk$rRy2L03CHH~'
before_brace = '&}K9zrO$g0}p`Y04o3l0EW+88UP3&0Cf$iKmdA=Q#68VsRn~gKxlgJyIptv'

print("="*80)
print("分析 '{' 后的内容")
print("="*80)
print("'{' 后内容:", flag_part)
print("长度:", len(flag_part))

# 也许需要组合 '{' 前后的内容?
print("\n" + "="*80)
print("尝试1: 也许 '{' 前的部分也是flag的一部分?")
print("="*80)

# 也许flag格式是: EdgeCTF{...}
# 让我检查 '{' 前的内容能否解码成 'EdgeCTF'
print("'{' 前内容:", before_brace)
print("长度:", len(before_brace))

# 'EdgeCTF' 有7个字符,让我看看前7个字符
print("\n前7个字符:", before_brace[:7])

# 尝试各种解码
import base64

# 也许整个独特结尾是Base64编码的?
print("\n" + "="*80)
print("尝试2: Base64解码整个独特结尾")
print("="*80)

try:
    # 可能需要padding
    for padding in ['', '=', '==', '===']:
        try:
            decoded = base64.b64decode(full_ending + padding)
            print(f"Padding '{padding}': {decoded}")
            if b'EdgeCTF' in decoded or b'Edge' in decoded:
                print("🎯 找到EdgeCTF!")
        except Exception as e:
            pass
except Exception as e:
    print(f"失败: {e}")

# 也许需要去掉某些字符后再Base64解码?
print("\n" + "="*80)
print("尝试3: 提取Base64有效字符后解码")
print("="*80)

import re
# Base64只包含: A-Z, a-z, 0-9, +, /, =
valid_b64_chars = re.findall(r'[A-Za-z0-9+/=]', full_ending)
b64_string = ''.join(valid_b64_chars)
print(f"提取的Base64字符: {b64_string}")

try:
    for padding in ['', '=', '==', '===']:
        try:
            decoded = base64.b64decode(b64_string + padding)
            print(f"Padding '{padding}': {decoded}")
            if b'EdgeCTF' in decoded or b'Edge' in decoded:
                print("🎯 找到EdgeCTF!")
                print(f"完整flag: EdgeCTF{{{decoded.decode('utf-8', errors='ignore')}}}")
        except Exception as e:
            pass
except Exception as e:
    print(f"失败: {e}")

# 也许'{' 标记了某个位置,需要从那里开始读取?
print("\n" + "="*80)
print("尝试4: 从 '{' 位置开始,每隔N个字符读取")
print("="*80)

for step in [2, 3, 4, 5, 7]:
    extracted = flag_part[::step]
    print(f"步长{step}: {extracted}")
    if 'Edge' in extracted or 'CTF' in extracted:
        print("🎯 可能找到了!")

# 也许需要反转?
print("\n" + "="*80)
print("尝试5: 反转字符串")
print("="*80)
reversed_part = flag_part[::-1]
print(f"反转后: {reversed_part}")

reversed_full = full_ending[::-1]
print(f"完整反转: {reversed_full}")

# 检查反转后的Base64
valid_b64_reversed = re.findall(r'[A-Za-z0-9+/=]', reversed_full)
b64_reversed = ''.join(valid_b64_reversed)
print(f"\n反转后提取Base64: {b64_reversed}")

try:
    for padding in ['', '=', '==', '===']:
        try:
            decoded = base64.b64decode(b64_reversed + padding)
            print(f"Padding '{padding}': {decoded}")
            if b'EdgeCTF' in decoded or b'Edge' in decoded:
                print("🎯 找到EdgeCTF!")
        except Exception as e:
            pass
except Exception as e:
    print(f"失败: {e}")
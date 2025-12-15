#!/usr/bin/env python3

# 基础旋转模式
base_pattern = 'LRx4!F+o`-Q(1XNt&;&?jsyUp000Oe05E_}Mna$^sS1FXF+'

# 独特结尾
unique_ending = '&}K9zrO$g0}p`Y04o3l0EW+88UP3&0Cf$iKmdA=Q#68VsRn~gKxlgJyIptv{ScHD(h!sth5`Wz03_|#6IgbwXw&zxYAfDN=FkEG6czkk$rRy2L03CHH~'

print("="*80)
print("最终解码尝试: 使用基础模式作为密码本")
print("="*80)

print(f"基础模式: {base_pattern}")
print(f"模式长度: {len(base_pattern)}")
print(f"\n独特结尾: {unique_ending}")
print(f"结尾长度: {len(unique_ending)}\n")

# 思路: 独特结尾中的每个字符,在基础模式中查找其位置
# 然后用该位置对应的另一个字符替换(或者用位置索引本身)

# 方法1: 建立基础模式的字符到索引的映射
print("="*80)
print("方法1: 用基础模式的字符位置解码")
print("="*80)

# 为基础模式中的每个唯一字符建立索引
char_to_first_pos = {}
for i, char in enumerate(base_pattern):
    if char not in char_to_first_pos:
        char_to_first_pos[char] = i

decoded = ''
for char in unique_ending:
    if char in char_to_first_pos:
        # 用该字符在基础模式中的第一次出现位置
        pos = char_to_first_pos[char]
        decoded += chr(ord('A') + pos) if pos < 26 else chr(ord('a') + pos - 26) if pos < 52 else str(pos)
    else:
        decoded += char

print(f"解码结果: {decoded}")
if 'Edge' in decoded or 'CTF' in decoded:
    print("🎯 找到flag标记!")

# 方法2: 用基础模式作为替换表
print("\n" + "="*80)
print("方法2: 字符替换 (unique char -> base pattern char)")
print("="*80)

# 也许独特结尾的每个位置,应该用基础模式对应位置的字符替换
decoded2 = ''
for i, char in enumerate(unique_ending):
    base_pos = i % len(base_pattern)
    decoded2 += base_pattern[base_pos]

print(f"解码结果: {decoded2}")
if 'Edge' in decoded2 or 'CTF' in decoded2:
    print("🎯 找到flag标记!")

# 方法3: XOR解码
print("\n" + "="*80)
print("方法3: XOR with base pattern")
print("="*80)

decoded3 = ''
for i, char in enumerate(unique_ending):
    base_char = base_pattern[i % len(base_pattern)]
    xor_val = ord(char) ^ ord(base_char)
    if 32 <= xor_val < 127:
        decoded3 += chr(xor_val)
    else:
        decoded3 += '?'

print(f"解码结果: {decoded3}")
if 'Edge' in decoded3 or 'CTF' in decoded3:
    print("🎯 找到flag标记!")

# 方法4: 也许flag的长度就是116个字符,直接就是那个unique_ending?
# 让我检查它是否符合某种已知的编码格式
print("\n" + "="*80)
print("方法4: 检查独特结尾是否本身就是某种编码的flag")
print("="*80)

# 尝试各种常见的CTF技巧
# 1. 也许就是flag,只是格式化了?
if '{' in unique_ending:
    brace_idx = unique_ending.find('{')
    print(f"包含 '{{' 在位置 {brace_idx}")
    print(f"'{{' 前的内容: {unique_ending[:brace_idx]}")
    print(f"'{{' 后的内容: {unique_ending[brace_idx:]}")
    
# 2. Base58解码?
print("\n尝试Base58解码...")
try:
    import base58
    decoded_b58 = base58.b58decode(unique_ending)
    print(f"Base58解码: {decoded_b58}")
    if b'EdgeCTF' in decoded_b58:
        print("🎯 在Base58解码中找到EdgeCTF!")
except Exception as e:
    print(f"Base58解码失败: {e}")
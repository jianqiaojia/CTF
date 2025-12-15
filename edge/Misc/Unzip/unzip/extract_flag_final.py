#!/usr/bin/env python3

with open('decoded_text.txt', 'r') as f:
    content = f.read()

# 独特结尾的116个字符
unique_ending = content[-116:]
print(f"独特结尾116字符: {unique_ending}\n")

# 重复部分
repetitive_part = content[:-116]
print(f"重复部分长度: {len(repetitive_part)}")
print(f"总长度: {len(content)}\n")

# 想法: 116个字符可能是116个索引位置
# 每个字符的ASCII值可能指向重复部分中的某个位置

# 方法1: 使用unique ending中每个字符的ASCII值作为索引
print("="*80)
print("方法1: 使用字符ASCII值作为步长提取")
print("="*80)

extracted = ''
pos = 0
for char in unique_ending:
    step = ord(char)
    pos = (pos + step) % len(repetitive_part)
    extracted += repetitive_part[pos]

print(f"提取结果: {extracted}")
if 'EdgeCTF{' in extracted:
    print(f"🎯 找到FLAG!")

# 方法2: 直接使用ASCII值作为索引
print("\n" + "="*80)
print("方法2: 直接使用ASCII值作为索引")
print("="*80)

extracted2 = ''
for char in unique_ending:
    idx = ord(char) % len(repetitive_part)
    extracted2 += repetitive_part[idx]

print(f"提取结果: {extracted2}")
if 'EdgeCTF{' in extracted2:
    print(f"🎯 找到FLAG!")

# 方法3: 也许unique ending本身通过某种变换就是flag?
print("\n" + "="*80)
print("方法3: ROT变换")
print("="*80)

for rot in range(1, 26):
    transformed = ''
    for char in unique_ending:
        if char.isalpha():
            if char.isupper():
                transformed += chr((ord(char) - ord('A') + rot) % 26 + ord('A'))
            else:
                transformed += chr((ord(char) - ord('a') + rot) % 26 + ord('a'))
        else:
            transformed += char
    
    if 'EdgeCTF' in transformed or 'edge' in transformed.lower():
        print(f"ROT{rot}: {transformed}")
        print(f"🎯 找到FLAG!")
        break

# 方法4: 反向思考 - 也许重复部分的某个特定序列就是flag?
print("\n" + "="*80)
print("方法4: 在重复部分中搜索EdgeCTF")
print("="*80)

if 'EdgeCTF{' in repetitive_part:
    idx = repetitive_part.find('EdgeCTF{')
    end_idx = repetitive_part.find('}', idx)
    if end_idx != -1:
        flag = repetitive_part[idx:end_idx+1]
        print(f"🎯🎯🎯 找到FLAG: {flag}")
else:
    print("重复部分中未找到EdgeCTF")
    
    # 尝试不区分大小写
    lower_rep = repetitive_part.lower()
    if 'edgectf{' in lower_rep:
        print("找到小写版本的flag标记!")
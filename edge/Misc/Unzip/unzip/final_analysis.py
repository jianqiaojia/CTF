#!/usr/bin/env python3

with open('decoded_text.txt', 'r') as f:
    content = f.read()

print(f"文件总长度: {len(content)} 字符")
print(f"="*80)

# 基础模式
base_pattern = 'LRx4!F+o`-Q(1XNt&;&?jsyUp000Oe05E_}Mna$^sS1FXF+'
print(f"基础模式: {base_pattern}")
print(f"模式长度: {len(base_pattern)}")

# 文件由旋转的52字符chunks组成
# 总共约18427个chunks
# 每个chunk是基础模式的某个旋转

# 关键想法: 如果这是一个旋转密码,那么正确的"解旋转"方式
# 应该会显示出flag

# 让我尝试: 从每个chunk的相同位置取字符
print("\n" + "="*80)
print("从每个chunk的每个位置提取字符:")
print("="*80)

chunk_size = 52
num_chunks = len(content) // chunk_size

for pos in range(52):
    extracted = ''
    for chunk_idx in range(min(200, num_chunks)):
        start = chunk_idx * chunk_size
        if start + pos < len(content):
            extracted += content[start + pos]
    
    # 检查这个extracted字符串
    if 'EdgeCTF' in extracted or 'Edge' in extracted[:50]:
        print(f"\n位置 {pos} 发现flag标记!")
        print(f"提取的字符串: {extracted}")
        
        # 找到完整的flag
        if 'EdgeCTF{' in extracted:
            flag_start = extracted.find('EdgeCTF{')
            flag_end = extracted.find('}', flag_start)
            if flag_end != -1:
                flag = extracted[flag_start:flag_end+1]
                print(f"\n🎯🎯🎯 找到FLAG: {flag} 🎯🎯🎯")
                break

print("\n" + "="*80)
print("如果上面没找到,尝试其他方法...")
print("="*80)

# 也许需要考虑文件末尾的独特字符串
# 独特字符串长度116,也许它告诉我们如何解码?

unique_ending = content[-116:]
print(f"\n独特结尾: {unique_ending}")
print(f"长度: {len(unique_ending)}")

# 也许116个字符对应116个不同的提取位置?
# 或者这116个字符是某种密钥?
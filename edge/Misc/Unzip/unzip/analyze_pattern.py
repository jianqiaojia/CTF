# 分析从重复模式到独特字符串的过渡
with open('decoded_text.txt', 'r', encoding='utf-8') as f:
    content = f.read()

# 重复模式
pattern = 'LRx4!F+o`-Q(1XNt&;&?jsyUp000Oe05E_}Mna$^sS1FXF+'

# 找到最后一个完整模式的位置
last_pattern_pos = content.rfind(pattern)
print(f"最后一个完整模式的位置: {last_pattern_pos}")

# 从最后一个模式开始，显示接下来的500个字符
if last_pattern_pos != -1:
    ending_section = content[last_pattern_pos:last_pattern_pos + 500]
    print(f"\n从最后一个完整模式开始的500个字符:")
    print(ending_section)
    print("\n" + "="*80)
    
    # 尝试找到可能的flag格式
    # 看看是否有EdgeCTF或其他模式
    
# 检查独特字符串本身
unique_str = '&}K9zrO$g0}p`Y04o3l0EW+88UP3&0Cf$iKmdA=Q#68VsRn~gKxlgJyIptv{ScHD(h!sth5`Wz03_|#6IgbwXw&zxYAfDN=FkEG6czkk$rRy2L03CHH~'
print(f"\n独特字符串长度: {len(unique_str)}")
print(f"独特字符串: {unique_str}")

# 检查是否包含{ 和 }
if '{' in unique_str and '}' in unique_str:
    start_idx = unique_str.find('{')
    end_idx = unique_str.find('}', start_idx)
    print(f"\n找到花括号: {{ 在位置 {start_idx}, }} 在位置 {end_idx}")
    if end_idx > start_idx:
        between_braces = unique_str[start_idx:end_idx+1]
        print(f"花括号之间的内容: {between_braces}")

# 尝试将独特字符串与前面的模式末尾拼接，看看是否能形成EdgeCTF{
# 模式的结尾是: ...FXF+
# 独特字符串开头是: o`-Q
print("\n检查过渡区域:")
transition = content[-200:]
print(transition)
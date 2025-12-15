with open('data_decoded.txt', 'r', encoding='utf-8') as f:
    text = f.read()

# 找到重复模式
pattern = "LRx4!F+o`-Q(1XNt&;&?jsyUp000Oe05E_}Mna$^sS1FXF+"

# 从文件末尾往前找，找到最后一个完整模式的位置
last_pattern_pos = text.rfind(pattern)

if last_pattern_pos != -1:
    # 提取最后一个模式之后的所有内容
    after_pattern = text[last_pattern_pos + len(pattern):]
    
    # 从这个内容中移除所有还存在的重复模式字符
    # 找到真正独特的部分（不包含模式中的任何字符序列）
    unique_chars = ""
    i = 0
    while i < len(after_pattern):
        # 检查从当前位置开始是否还有重复模式
        found_pattern = False
        for length in range(10, len(pattern) + 1):
            if i + length <= len(after_pattern):
                substring = after_pattern[i:i+length]
                if substring in pattern:
                    found_pattern = True
                    i += length
                    break
        
        if not found_pattern:
            unique_chars += after_pattern[i]
            i += 1
    
    print("真正独特的内容:")
    print(unique_chars)
    print(f"\n长度: {len(unique_chars)} 字符")
    
    # 也打印最后100个字符看看
    print("\n文件最后100个字符:")
    print(text[-100:])
else:
    print("未找到重复模式")
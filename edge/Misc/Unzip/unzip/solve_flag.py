#!/usr/bin/env python3

# 独特的结尾字符串
unique_ending = '&}K9zrO$g0}p`Y04o3l0EW+88UP3&0Cf$iKmdA=Q#68VsRn~gKxlgJyIptv{ScHD(h!sth5`Wz03_|#6IgbwXw&zxYAfDN=FkEG6czkk$rRy2L03CHH~'

print("="*80)
print("分析独特结尾字符串")
print("="*80)
print(f"字符串: {unique_ending}")
print(f"长度: {len(unique_ending)}\n")

# 注意到字符串中有 { 符号
# 位置59有 '{', 让我们看看它周围的内容
brace_pos = unique_ending.find('{')
print(f"找到 '{{' 在位置 {brace_pos}")
print(f"上下文: ...{unique_ending[max(0,brace_pos-10):brace_pos+20]}...\n")

# 也许这个字符串需要和基础模式进行某种操作?
# 或者maybe整个思路不对——让我检查原始ZIP文件中是否有其他线索

print("="*80)
print("重新检查所有文件")
print("="*80)

# 读取原始的hex编码文件
with open('unzip', 'r') as f:
    hex_content = f.read().strip()
    
print(f"原始hex文件长度: {len(hex_content)} 字符")

# 让我看看hex内容的结尾
print(f"Hex结尾200字符:")
print(hex_content[-200:])

# 转换为二进制并查看ZIP文件的实际内容
import binascii
binary_data = binascii.unhexlify(hex_content)

print(f"\n二进制数据长度: {len(binary_data)} 字节")
print(f"ZIP magic number检查: {binary_data[:4].hex()}")

# ZIP文件末尾通常有comment,让我检查
# ZIP文件结构: 文件数据 + Central Directory + End of Central Directory Record
# EOCD 的signature是 50 4b 05 06

eocd_sig = b'PK\x05\x06'
eocd_pos = binary_data.rfind(eocd_sig)
if eocd_pos != -1:
    print(f"\n找到EOCD在位置: {eocd_pos}")
    # EOCD结构:
    # 0-3: signature (PK\x05\x06)
    # 4-5: disk number
    # 6-7: disk with central directory  
    # 8-9: entries on this disk
    # 10-11: total entries
    # 12-15: size of central directory
    # 16-19: offset of central directory
    # 20-21: comment length
    # 22+: comment
    
    comment_len = int.from_bytes(binary_data[eocd_pos+20:eocd_pos+22], 'little')
    print(f"ZIP comment长度: {comment_len}")
    
    if comment_len > 0:
        comment = binary_data[eocd_pos+22:eocd_pos+22+comment_len]
        print(f"ZIP comment: {comment}")
        try:
            print(f"ZIP comment (UTF-8): {comment.decode('utf-8')}")
        except:
            print(f"ZIP comment (hex): {comment.hex()}")
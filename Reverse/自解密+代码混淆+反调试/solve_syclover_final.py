#!/usr/bin/env python3
"""
Syclover CTF - 完整解密脚本
根据trace分析的完整程序逻辑来获取flag
"""

def decrypt_char(encrypted_byte, position):
    """
    反向解密算法
    加密: encrypted = ((c >> shift_r) | (c << shift_l)) ^ position
    解密: 需要找到原始字符c
    """
    shift_right = position % 8
    shift_left = 8 - shift_right
    
    # 先移除位置XOR
    merged = encrypted_byte ^ position
    
    # 尝试所有可能的ASCII可见字符
    for c in range(32, 127):
        # 模拟加密过程
        part1 = c >> shift_right
        part2 = (c << shift_left) & 0xFFFF
        test_merged = (part1 | part2) & 0xFFFF
        
        # 只比较低8位
        if (test_merged & 0xFF) == merged:
            return chr(c)
    
    # 如果没找到可见字符，尝试所有字节
    for c in range(256):
        part1 = c >> shift_right
        part2 = (c << shift_left) & 0xFFFF
        test_merged = (part1 | part2) & 0xFFFF
        
        if (test_merged & 0xFF) == merged:
            return chr(c) if 32 <= c < 127 else f"\\x{c:02x}"
    
    return "?"

# 从trace中提取的密钥数据（加密后应该匹配的值）
key_bytes = [
    0x53, 0xAD, 0xD2, 0x6C, 0xE7, 0xF4, 0x5B, 0xD7,
    0x38, 0x12, 0x51, 0x2D, 0xEF, 0xFC, 0x47, 0x6F,
    0x5F, 0x2B, 0x4D
]

print("="*70)
print("Syclover CTF - Flag解密")
print("="*70)

print("\n密钥字节 (加密后的目标值):")
print(' '.join(f'{b:02x}' for b in key_bytes))

print("\n开始反向解密...")
print("-"*70)

flag = ""
for i, encrypted in enumerate(key_bytes):
    char = decrypt_char(encrypted, i)
    flag += char
    print(f"位置 {i:2d}: 0x{encrypted:02x} -> '{char}'")

print("\n" + "="*70)
print(f"解密的Flag: {flag}")
print("="*70)

# 验证：加密flag应该得到密钥
print("\n验证解密是否正确:")
print("-"*70)

def encrypt_char(c, position):
    """加密单个字符"""
    byte_val = ord(c)
    shift_right = position % 8
    shift_left = 8 - shift_right
    
    part1 = byte_val >> shift_right
    part2 = (byte_val << shift_left) & 0xFFFF
    merged = part1 | part2
    encrypted = (merged ^ position) & 0xFF
    
    return encrypted

print(f"原始: {flag}")
encrypted_flag = [encrypt_char(c, i) for i, c in enumerate(flag)]
print(f"加密: {' '.join(f'{b:02x}' for b in encrypted_flag)}")
print(f"密钥: {' '.join(f'{b:02x}' for b in key_bytes)}")

if encrypted_flag == key_bytes:
    print("\n✓ 验证成功！Flag正确！")
else:
    print("\n✗ 验证失败，可能需要调整...")
    print("\n差异:")
    for i, (enc, key) in enumerate(zip(encrypted_flag, key_bytes)):
        if enc != key:
            print(f"  位置 {i}: 加密得到 0x{enc:02x}, 期望 0x{key:02x}")

print("\n" + "="*70)
print("Flag格式可能是: flag{...} 或 syclover{...}")
print("="*70)
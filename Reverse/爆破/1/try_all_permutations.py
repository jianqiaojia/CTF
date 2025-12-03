#!/usr/bin/env python3
# 尝试所有可能的4字节块排列

import itertools

# 6个破解出的4字节块
blocks = [
    b'juhu',  # 位置0
    b'hfen',  # 位置1  
    b'laps',  # 位置2
    b'iuer',  # 位置3
    b'hjif',  # 位置4
    b'dunu',  # 位置5
]

block_strs = ['juhu', 'hfen', 'laps', 'iuer', 'hjif', 'dunu']

# 加密的flag数据
encrypted_data = bytes([
    0xfe, 0xe9, 0xf4, 0xe2, 0xf1, 0xfa, 0xf4, 0xe4,
    0xf0, 0xe7, 0xe4, 0xe5, 0xe3, 0xf2, 0xf5, 0xef,
    0xe8, 0xff, 0xf6, 0xf4, 0xfd, 0xb4, 0xa5, 0xb2
])

def calculate_checksum(input_bytes):
    """计算checksum"""
    checksum = 0
    for i in range(len(input_bytes)):
        if input_bytes[i] != 0:
            checksum ^= (input_bytes[i] + i) & 0xFF
    return checksum

def decrypt_flag(output_bytes, checksum):
    """解密flag"""
    flag = bytearray()
    for i in range(len(encrypted_data)):
        if i < len(output_bytes):
            decrypted = checksum ^ encrypted_data[i] ^ output_bytes[i]
        else:
            decrypted = checksum ^ encrypted_data[i]
        flag.append(decrypted)
    return bytes(flag)

def is_valid_flag(flag_bytes):
    """检查flag是否只包含合法字符 (0x30-0x7a)"""
    for b in flag_bytes:
        if b < 0x30 or b > 0x7a:
            return False
        # 还要排除 0x3a-0x40 (between '9' and 'A') 
        # 和 0x5b-0x60 (between 'Z' and 'a')
        if (0x3a <= b <= 0x40) or (0x5b <= b <= 0x60):
            return False
    return True

print("=" * 70)
print("尝试所有排列组合")
print("=" * 70)
print()

count = 0
valid_count = 0

# 尝试所有排列
for perm in itertools.permutations(range(6)):
    count += 1
    
    # 构造输入（按原始顺序）
    input_bytes = b''.join([blocks[i] for i in range(6)])
    
    # 构造输出（按线程完成顺序）
    output_bytes = b''.join([blocks[perm[i]] for i in range(6)])
    output_str = ''.join([block_strs[perm[i]] for i in range(6)])
    
    # 计算checksum（使用原始输入）
    checksum = calculate_checksum(input_bytes)
    
    # 解密flag（使用输出顺序）
    flag = decrypt_flag(output_bytes, checksum)
    
    # 检查是否有效
    if is_valid_flag(flag):
        valid_count += 1
        try:
            flag_str = flag.decode('ascii')
            print(f"排列 {count}: {perm}")
            print(f"  输出顺序: {output_str}")
            print(f"  Checksum: 0x{checksum:02x}")
            print(f"  Flag: {flag_str}")
            print(f"  ✓ 有效!")
            print()
        except:
            pass

print("=" * 70)
print(f"总共测试: {count} 个排列")
print(f"有效flag: {valid_count} 个")
print("=" * 70)
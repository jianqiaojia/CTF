#!/usr/bin/env python3
# CTF题目暴力破解脚本 - 针对4字节ASCII字符串

import hashlib
import struct
import itertools
import string
from multiprocessing import Pool, cpu_count

# 从IDA提取的目标哈希值（qword，即MD5的前8字节）
target_qwords = [
    0x0f59bb02bdbb4647,   # 线程0: input[0:4]
    0x5cfce8ec2128acbe,   # 线程1: input[4:8]
    0x0ef0375ca659274ad,   # 线程2: input[8:12]
    0x27422cc18fb38643,   # 线程3: input[12:16]
    0x0a72deca745cc3eb0,   # 线程4: input[16:20]
    0x0e8341712fe5f3cbe,   # 线程5: input[20:24]
]

# 加密的flag数据
encrypted_data = bytes([
    0xfe, 0xe9, 0xf4, 0xe2, 0xf1, 0xfa, 0xf4, 0xe4,
    0xf0, 0xe7, 0xe4, 0xe5, 0xe3, 0xf2, 0xf5, 0xef,
    0xe8, 0xff, 0xf6, 0xf4, 0xfd, 0xb4, 0xa5, 0xb2
])

def md5_to_qword(data):
    """计算MD5并返回前8字节作为小端qword"""
    md5_hash = hashlib.md5(data).digest()
    return struct.unpack('<Q', md5_hash[:8])[0]

def brute_force_position(args):
    """暴力破解单个位置的4字节"""
    pos, target_qword, charset = args
    
    print(f"[线程{pos}] 开始暴力破解，目标: 0x{target_qword:016x}")
    
    tested = 0
    # 尝试不同长度的字符串（1-4个字符）
    for length in range(1, 5):
        for combo in itertools.product(charset, repeat=length):
            # 构造4字节数据：字符串 + null填充
            test_str = ''.join(combo)
            test_bytes = test_str.encode('ascii') + b'\x00' * (4 - length)
            
            qword = md5_to_qword(test_bytes)
            tested += 1
            
            # if tested % 100000 == 0:
            #     print(f"[线程{pos}] 已测试 {tested} 个组合...")
            
            if qword == target_qword:
                print(f"[线程{pos}] *** 找到匹配! ***")
                print(f"[线程{pos}] 字符串: '{test_str}'")
                print(f"[线程{pos}] 字节: {test_bytes.hex()}")
                print(f"[线程{pos}] MD5前8字节: 0x{qword:016x}")
                return (pos, test_bytes, test_str)
    
    print(f"[线程{pos}] 未找到匹配 (测试了 {tested} 个组合)")
    return (pos, None, None)

def solve_parallel():
    """并行暴力破解所有位置"""
    print("=" * 70)
    print("开始暴力破解CTF题目")
    print("=" * 70)
    print()
    
    # 定义字符集 - 可打印ASCII字符
    charset = string.ascii_letters + string.digits + string.punctuation
    print(f"字符集大小: {len(charset)}")
    print(f"字符集: {charset[:50]}...")
    print()
    
    # 准备参数
    tasks = [(i, target_qwords[i], charset) for i in range(6)]
    
    # 使用多进程并行破解
    print(f"使用 {cpu_count()} 个CPU核心进行并行破解\n")
    
    with Pool(processes=min(6, cpu_count())) as pool:
        results = pool.map(brute_force_position, tasks)
    
    print("\n" + "=" * 70)
    print("破解结果汇总")
    print("=" * 70)
    
    # 收集结果
    found_blocks = {}
    for pos, block_bytes, block_str in results:
        if block_bytes:
            found_blocks[pos] = (block_bytes, block_str)
            print(f"位置 {pos}: '{block_str}' -> {block_bytes.hex()}")
        else:
            print(f"位置 {pos}: 未找到")
    
    if len(found_blocks) < 6:
        print("\n警告: 并非所有位置都找到了匹配")
        return None
    
    # 重构完整输入
    full_input_bytes = b''.join([found_blocks[i][0] for i in range(6)])
    full_input_str = ''.join([found_blocks[i][1] for i in range(6)])
    
    print("\n" + "=" * 70)
    print("完整输入")
    print("=" * 70)
    print(f"字符串: {full_input_str}")
    print(f"字节数: {full_input_bytes.hex()}")
    print()
    
    # 计算checksum
    checksum = 0
    for i, byte in enumerate(full_input_bytes):
        if byte != 0:  # 只计算非null字符
            checksum ^= (byte + i) & 0xFF
    
    print(f"Checksum: 0x{checksum:02x}")
    
    # 解密flag
    # 注意：main函数中使用的是线程输出缓冲区(dword_602220)，而不是原始输入
    # 但由于验证成功的线程会将输入复制到输出，所以两者内容相同
    print("\n" + "=" * 70)
    print("解密FLAG")
    print("=" * 70)
    print("注意: 使用线程输出缓冲区的数据(验证成功后复制的输入)")
    print()
    
    # 线程输出缓冲区内容（验证成功后与输入相同）
    output_bytes = full_input_bytes
    
    flag = bytearray()
    for i in range(len(encrypted_data)):
        if i < len(output_bytes):
            # flag[i] = checksum ^ encrypted[i] ^ output[i]
            decrypted = checksum ^ encrypted_data[i] ^ output_bytes[i]
        else:
            decrypted = checksum ^ encrypted_data[i]
        flag.append(decrypted)
    
    try:
        flag_str = flag.decode('ascii', errors='replace')
        print(f"FLAG: {flag_str}")
    except:
        print(f"FLAG (hex): {flag.hex()}")
    
    print("=" * 70)
    
    return full_input_str, flag_str

def solve_sequential():
    """顺序破解（单线程，用于调试）"""
    print("=" * 70)
    print("开始顺序暴力破解 (单线程)")
    print("=" * 70)
    print()
    
    charset = string.ascii_letters + string.digits + '_-{}!@#$%'
    print(f"字符集: {charset}\n")
    
    found_blocks = {}
    
    for pos in range(6):
        result = brute_force_position((pos, target_qwords[pos], charset))
        if result[1]:
            found_blocks[pos] = (result[1], result[2])
        print()
    
    if len(found_blocks) == 6:
        full_input_str = ''.join([found_blocks[i][1] for i in range(6)])
        print(f"\n完整输入: {full_input_str}")
        return full_input_str
    else:
        print("\n未能找到所有位置的匹配")
        return None

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--sequential':
        solve_sequential()
    else:
        solve_parallel()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
EasyRE CTF - 正确的完整解法
包含我之前遗漏的关键第三阶段
"""

def solve_all_stages():
    print("EasyRE CTF - 完整正确解法")
    print("=" * 50)
    
    # 第一阶段：XOR解密
    print("=== 第一阶段：XOR解密 ===")
    arr = [73,111,100,108,62,81,110,98,40,111,99,121,127,121,46,105,127,100,96,51,119,125,
           119,101,107,57,123,105,121,61,126,121,76,64,69,67]
    
    stage1_result = ''
    for i in range(36):
        stage1_result += chr(arr[i] ^ i)
    
    print(f"第一个输入: {stage1_result}")
    
    # 第二阶段：Base64解密（直接使用已知结果）
    print("\n=== 第二阶段：Base64解密 ===")
    stage2_result = "https://bbs.pediy.com/thread-254172.htm"
    print(f"第二个输入: {stage2_result}")
    print("(Base64 10次解码略过)")
    
    # 第三阶段：隐藏的flag生成算法（我之前遗漏的关键部分！）
    print("\n=== 第三阶段：隐藏的flag解密 (.fini_array中的函数) ===")
    
    # 从byte_6CC0A0数组得到的加密数据
    enc = [0x40,0x35,0x20,0x56,0x5D,0x18,0x22,0x45,0x17,0x2F,0x24,0x6E,0x62,0x3C,0x27,0x54,0x48,0x6C,0x24,0x6E,0x72,0x3C,0x32,0x45,0x5B]
    
    # 已知flag前4个字符是'flag'，用来反推密钥
    known_prefix = 'flag'
    key = ''
    
    print("使用已知的'flag'前缀反推密钥...")
    for i in range(4):
        key += chr(enc[i] ^ ord(known_prefix[i]))
    
    print(f"解出的4字节密钥: {repr(key)}")
    
    # 使用密钥解密完整的flag
    final_flag = ''
    for i in range(len(enc)):
        final_flag += chr(enc[i] ^ ord(key[i % 4]))
    
    print(f"解密后的完整flag: {final_flag}")
    
    print("\n" + "=" * 50)
    print("解题总结:")
    print(f"1. 第一个输入 (XOR解密): {stage1_result}")
    print(f"2. 第二个输入 (Base64解密): {stage2_result}")
    print(f"3. 最终flag (.fini_array函数): {final_flag}")
    
    print(f"\n我之前的错误:")
    print("- 我只关注了程序的主要验证逻辑")
    print("- 忽略了.fini_array中的sub_400D35函数")
    print("- 这个函数在程序退出时自动执行，生成真正的flag")
    print("- 它使用复杂的随机数生成和XOR解密算法")
    
    return final_flag

if __name__ == "__main__":
    result = solve_all_stages()
    print(f"\n🎯 最终答案: {result}")
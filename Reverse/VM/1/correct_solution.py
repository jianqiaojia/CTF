#!/usr/bin/env python3
"""
正确的VM逆向解密脚本

关键发现：R1寄存器在每次迭代中保持上一次的计算结果！
这导致每个字符的计算都依赖于前一个字符。

算法（每个字符i）：
1. a16 = input[i]
2. a16 = a16 - i
3. a17 = a16 ^ a17  (注意：a17保留了上一次的值！)
4. a16 = 0xCD (也就是-51的unsigned char表示)
5. a16 = a16 ^ a17
6. 比较 a16 == target[i]
7. 如果相等，a17 = a16 (将结果保存到a17，用于下一次迭代)

解密推导：
- 对于第一个字符 (i=0)：
  a17初始为0
  input[0] - 0 = temp
  a17 = temp ^ 0 = temp
  a16 = 0xCD ^ temp
  a16 == target[0]
  => temp = 0xCD ^ target[0]
  => input[0] = temp = 0xCD ^ target[0]

- 对于后续字符 (i>0)：
  已知：a17 = target[i-1] (上一次的结果)
  input[i] - i = temp
  a17_new = temp ^ a17 = temp ^ target[i-1]
  a16 = 0xCD ^ a17_new = 0xCD ^ temp ^ target[i-1]
  a16 == target[i]
  => 0xCD ^ temp ^ target[i-1] = target[i]
  => temp = 0xCD ^ target[i] ^ target[i-1]
  => input[i] = (0xCD ^ target[i] ^ target[i-1]) + i
"""

# 目标数组
target = [
    0xF4, 0x0A, 0xF7, 0x64, 0x99, 0x78, 0x9E, 0x7D,
    0xEA, 0x7B, 0x9E, 0x7B, 0x9F, 0x7E, 0xEB, 0x71,
    0xE8, 0x00, 0xE8, 0x07, 0x98, 0x19, 0xF4, 0x25,
    0xF3, 0x21, 0xA4, 0x2F, 0xF4, 0x2F, 0xA6, 0x7C
]

def solve_flag():
    """解密flag"""
    flag = []
    
    print("开始解密...")
    print()
    
    # 第一个字符特殊处理
    # input[0] = 0xCD ^ target[0]
    char0 = 0xCD ^ target[0]
    flag.append(char0)
    print(f"位置 0: 0xCD ^ 0x{target[0]:02X} = 0x{char0:02X} = '{chr(char0)}'")
    
    # 后续字符
    for i in range(1, 32):
        # input[i] = (0xCD ^ target[i] ^ target[i-1]) + i
        temp = 0xCD ^ target[i] ^ target[i-1]
        char_value = (temp + i) & 0xFF
        flag.append(char_value)
        print(f"位置 {i:2d}: (0xCD ^ 0x{target[i]:02X} ^ 0x{target[i-1]:02X}) + {i:2d} = 0x{char_value:02X} = '{chr(char_value)}'")
    
    return flag

def verify_flag(flag):
    """验证flag是否正确"""
    print("\n验证flag...")
    a17 = 0  # R1寄存器初始值
    
    for i in range(32):
        a16 = flag[i]  # 加载输入字符
        a16 = (a16 - i) & 0xFF  # 减去索引
        a17 = a16 ^ a17  # 异或上次的a17
        a16 = 0xCD  # 加载常量
        a16 = a16 ^ a17  # 异或
        
        if a16 == target[i]:
            a17 = a16  # 保存结果给下次使用
            status = "✓"
        else:
            print(f"位置 {i}: 失败 (得到 0x{a16:02X}, 期望 0x{target[i]:02X})")
            return False
    
    print("✓ 所有32个字符验证成功！")
    return True

if __name__ == "__main__":
    print("="*80)
    print("CTF VM逆向 - 正确解法")
    print("="*80)
    print()
    
    # 解密
    flag = solve_flag()
    
    # 转换为字符串
    flag_str = ''.join(chr(c) for c in flag)
    
    print()
    print("="*80)
    print(f"解密结果: {flag_str}")
    print("="*80)
    print()
    
    # 验证
    if verify_flag(flag):
        print()
        print("="*80)
        print(f"最终FLAG: UNCTF{{{flag_str}}}")
        print("="*80)
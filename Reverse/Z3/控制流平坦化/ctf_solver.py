#!/usr/bin/env python3
"""
CTF逆向题Z3求解器

分析：
1. 程序读取21字节的输入（第一个字符用getchar，后续20字符用fgets）
2. 对每个字节进行复杂的Lambda函数变换
3. 将结果与enc数组对比
4. enc数组 @ 0x602060: f3 2e 18 36 e1 4c 22 d1 f9 8c 40 76 f4 0e 00 05 a3 90 0e a5

加密流程（针对每个字节，在case 1299792285中）：
- v35 = v38 ^ user_input[i]  # v38是时间差time_diff
- 经过多个lambda函数变换：
  * Lambda_0内部: 加法 (a + b) & 0xFF
  * Lambda_1内部: 取模 a % b
  * Lambda_2内部: 异或 a ^ b
  * Lambda_3内部: 乘法 (a * b) & 0xFF
- 最终结果v15应该等于enc[i]

由于搜索空间巨大(94^21)，使用Z3约束求解器是最优解
"""

from z3 import *

# enc数组的值（从IDA @ 0x602060提取）
enc = [0xf3, 0x2e, 0x18, 0x36, 0xe1, 0x4c, 0x22, 0xd1, 
       0xf9, 0x8c, 0x40, 0x76, 0xf4, 0x0e, 0x00, 0x05, 
       0xa3, 0x90, 0x0e, 0xa5]

def encrypt_byte_z3(user_byte, s_byte, time_diff):
    """
    Z3版本的加密函数（根据IDA反编译精确实现）
    
    对应main函数中case 1299792285的加密逻辑：
    参考地址: 0x400def (case 1299792285) 和 0x401188 (重复逻辑)
    """
    # v35 = v38 ^ user_input[v36 - 1]
    v35 = user_byte ^ time_diff
    
    # v34[0] = main::$_0::operator()(v44, (unsigned int)v35)
    v34 = v35 & 0xFF
    
    # v33[0] = main::$_1::operator()(v42, (unsigned int)*(&s + v38 + v36 - 1))
    v33 = s_byte & 0xFF
    
    # v11 = main::$_1::operator() const(char)::{lambda(int)#1}::operator()(v33, 7LL)
    # Lambda_1内部lambda @ 0x4014c0: 取模运算
    v11 = URem(v33, 7)
    
    # v35 = main::$_0::operator() const(char)::{lambda(char)#1}::operator()(v34, (unsigned int)v11)
    # Lambda_0内部lambda @ 0x401310: 加法运算
    v35 = (v34 + v11) & 0xFF
    
    # v32[0] = main::$_2::operator()(v45, (unsigned int)v35)
    v32 = v35 & 0xFF
    
    # v31[0] = main::$_2::operator()(v45, (unsigned int)*(&s + v38 + v36 - 1))
    v31 = s_byte & 0xFF
    
    # v12 = main::$_2::operator() const(char)::{lambda(char)#1}::operator()(v31, 18LL)
    # Lambda_2内部lambda @ 0x401690: 异或运算
    v12 = (18 ^ v31) & 0xFF
    
    # v30[0] = main::$_3::operator()(v43, (unsigned int)v12)
    v30 = v12 & 0xFF
    
    # v13 = main::$_3::operator() const(char)::{lambda(char)#1}::operator()(v30, 3LL)
    # Lambda_3内部lambda @ 0x401870: 乘法运算
    v13 = (3 * v30) & 0xFF
    
    # v29[0] = main::$_0::operator()(v44, (unsigned int)v13)
    v29 = v13 & 0xFF
    
    # v14 = main::$_0::operator() const(char)::{lambda(char)#1}::operator()(v29, 2LL)
    # Lambda_0内部lambda: 加法运算
    v14 = (v29 + 2) & 0xFF
    
    # v15 = main::$_2::operator() const(char)::{lambda(char)#1}::operator()(v32, (unsigned int)v14)
    # Lambda_2内部lambda: 异或运算
    v15 = (v14 ^ v32) & 0xFF
    
    # v52 = enc[v36 - 1] != v15;
    return v15

def solve_with_z3():
    """使用Z3约束求解器求解"""
    print("使用Z3求解器解密...")
    
    # 创建求解器
    solver = Solver()
    
    # 创建变量：20个用户输入字节 + 第一个字符 + 时间差
    user_input = [BitVec(f'input_{i}', 8) for i in range(20)]
    first_char = BitVec('first_char', 8)
    time_diff = BitVec('time_diff', 8)
    
    # 添加约束：所有字节都是可打印ASCII字符
    for i in range(20):
        solver.add(user_input[i] >= 0x20)
        solver.add(user_input[i] <= 0x7E)
    solver.add(first_char >= 0x20)
    solver.add(first_char <= 0x7E)
    
    # 添加时间约束（时间差应该很小）
    solver.add(time_diff >= 0)
    solver.add(time_diff <= 10)
    
    # 为每个位置添加加密约束
    # s数组结构: s @ 0x6020E0, user_input @ 0x6020E1
    # 在加密时使用: *(&s + v38 + v36 - 1)
    # 相当于: s[0]=first_char, s[i]=user_input[i-1] for i>0
    for i in range(20):
        if i == 0:
            s_byte = first_char
        else:
            s_byte = user_input[i - 1]
        
        # 加密后的值应该等于enc[i]
        encrypted = encrypt_byte_z3(user_input[i], s_byte, time_diff)
        solver.add(encrypted == enc[i])
    
    # 求解
    print("开始求解...")
    if solver.check() == sat:
        model = solver.model()
        print("\n找到解！")
        
        # 提取结果
        result = chr(model[first_char].as_long())
        for i in range(20):
            result += chr(model[user_input[i]].as_long())
        
        print(f"Flag: {result}")
        print(f"时间差: {model[time_diff].as_long()}")
        return result
    else:
        print("无解或求解失败")
        return None

if __name__ == "__main__":
    print("=" * 60)
    print("CTF逆向题Z3求解器")
    print("=" * 60)
    print(f"\nenc数组: {' '.join(f'{x:02x}' for x in enc)}")
    print(f"期望输出: 01abfc750a0c942167651c40d088531d (MD5格式)")
    print("\n正在分析加密算法...\n")
    
    # 使用Z3求解器
    result = solve_with_z3()
    
    if result:
        print(f"\n成功！Flag是: {result}")
    else:
        print("\n求解失败")
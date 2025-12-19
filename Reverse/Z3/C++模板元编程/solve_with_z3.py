#!/usr/bin/env python3
"""
使用 Z3 求解 Task8 的密码
所有约束条件已经从修改后的源码中提取
"""

from z3 import *

def solve_password():
    print("="*70)
    print("CTF Task8 - Z3 约束求解器")
    print("="*70)
    
    # 创建 13 个字符变量 (ASCII 值)
    p = [Int(f'p{i}') for i in range(13)]
    
    # 创建求解器
    s = Solver()
    
    # 添加可打印 ASCII 字符约束
    print("\n添加基本约束...")
    for i in range(13):
        s.add(p[i] >= 32)   # 空格
        s.add(p[i] <= 126)  # ~
    
    # 从修改后的源码中提取的约束条件
    print("添加密码约束...")
    
    # 约束 1-3: p[0], p[1], p[2]
    s.add(p[0] + p[1] == 101)
    s.add(p[1] + p[2] == 143)
    s.add(p[0] * p[2] == 5035)
    
    # 约束 4-6: p[3], p[4], p[5]
    s.add(p[3] + p[5] == 163)
    s.add(p[3] + p[4] == 226)
    s.add(p[4] * p[5] == 5814)
    
    # 约束 7-9: p[6], p[7], p[8]
    s.add(p[7] + p[8] == 205)
    s.add(p[6] + p[8] == 173)
    s.add(p[6] * p[7] == 9744)
    
    # 约束 10-12: p[9], p[10], p[11]
    s.add(p[9] + p[10] * p[11] == 5375)
    s.add(p[10] + p[9] * p[11] == 4670)
    s.add(p[9] + p[10] == 205)
    
    # 约束 13: p[12]
    s.add(p[12] == ord('w'))
    
    print("\n开始求解...")
    
    # 检查是否有解
    if s.check() == sat:
        print("\n✓ 找到解!")
        print("="*70)
        
        # 获取模型
        m = s.model()
        
        # 提取密码
        password = ''
        for i in range(13):
            val = m[p[i]].as_long()
            password += chr(val)
        
        print(f"\n密码: {password}")
        print(f"Flag: {password}")
        
        # 显示每个字符的详细信息
        print("\n" + "="*70)
        print("详细信息:")
        print("="*70)
        for i in range(13):
            val = m[p[i]].as_long()
            char = chr(val)
            print(f"p[{i:2d}] = {val:3d} ('{char}')")
        
        # 验证约束
        print("\n" + "="*70)
        print("验证约束:")
        print("="*70)
        vals = [m[p[i]].as_long() for i in range(13)]
        
        constraints = [
            (f"p[0]+p[1]", vals[0]+vals[1], 101),
            (f"p[1]+p[2]", vals[1]+vals[2], 143),
            (f"p[0]*p[2]", vals[0]*vals[2], 5035),
            (f"p[3]+p[5]", vals[3]+vals[5], 163),
            (f"p[3]+p[4]", vals[3]+vals[4], 226),
            (f"p[4]*p[5]", vals[4]*vals[5], 5814),
            (f"p[7]+p[8]", vals[7]+vals[8], 205),
            (f"p[6]+p[8]", vals[6]+vals[8], 173),
            (f"p[6]*p[7]", vals[6]*vals[7], 9744),
            (f"p[9]+p[10]*p[11]", vals[9]+vals[10]*vals[11], 5375),
            (f"p[10]+p[9]*p[11]", vals[10]+vals[9]*vals[11], 4670),
            (f"p[9]+p[10]", vals[9]+vals[10], 205),
            (f"p[12]", vals[12], ord('w')),
        ]
        
        all_valid = True
        for expr, actual, expected in constraints:
            status = "✓" if actual == expected else "✗"
            print(f"{status} {expr:20s} = {actual:6d} (期望: {expected})")
            if actual != expected:
                all_valid = False
        
        if all_valid:
            print("\n" + "="*70)
            print("所有约束验证通过! ✓")
            print("="*70)
        
        return password
    else:
        print("\n✗ 无解")
        return None

if __name__ == "__main__":
    password = solve_password()
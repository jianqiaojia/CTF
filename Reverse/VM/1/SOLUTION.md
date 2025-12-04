# CTF VM逆向题解

## 题目概述

这是一个虚拟机（VM）逆向挑战。程序实现了一个自定义VM，通过执行字节码来验证32字节的flag。

## 解题过程

### 1. VM结构分析

VM对象大小为0x28（40字节），结构如下：

```
偏移 0x00 (8字节): vtable指针
偏移 0x08 (8字节): PC（程序计数器）
偏移 0x10 (1字节): 寄存器R0 (对应代码中的a16)
偏移 0x11 (1字节): 寄存器R1 (对应代码中的a17)
偏移 0x12 (1字节): 寄存器R2 (循环索引)
偏移 0x14 (4字节): Flag寄存器（比较结果）
偏移 0x18 (8字节): 字节码指针
偏移 0x20 (8字节): 目标值数组指针
偏移 0x28 (8字节): 输入字符串指针
```

### 2. VM指令集

VM有16条指令（操作码0xA0-0xAF）：

| 操作码 | 功能 | PC调整 |
|--------|------|--------|
| 0xA0 | R0++ | 0 |
| 0xA1 | R1++ | 0 |
| 0xA2 | R2++ | +11 |
| 0xA3 | R0 -= R2 | +2 |
| 0xA4 | R0 ^= R1 | +7 |
| 0xA5 | R1 ^= R0 | +1 |
| 0xA6 | R0 = 0xCD | -2 |
| 0xA7 | R1 = R0 | +7 |
| 0xA8 | R2 = 0xCD | 0 |
| 0xA9 | R0 = input[R2] | -6 |
| 0xAA | R1 = input[R2] | 0 |
| 0xAB | 比较R0与target[R2] | -4 |
| 0xAC | 比较R1与target[R2] | 0 |
| 0xAD | Flag = (R2 > 31) | +2 |
| 0xAE | 如果Flag==0返回失败，否则PC-=12 | -12/返回 |
| 0xAF | 如果Flag==1返回成功，否则PC-=6 | -6/返回 |

### 3. 执行流程追踪

字节码从位置9开始执行（0xA9指令），形成一个处理每个字符的循环：

```
步骤1: PC=9  [0xA9] R0 = input[R2]     (加载输入字符)
步骤2: PC=3  [0xA3] R0 = R0 - R2        (减去索引)
步骤3: PC=5  [0xA5] R1 = R1 ^ R0        (关键：R1异或新值)
步骤4: PC=6  [0xA6] R0 = 0xCD           (加载常量)
步骤5: PC=4  [0xA4] R0 = R0 ^ R1        (异或R1)
步骤6: PC=11 [0xAB] 比较R0与target[R2] (验证结果)
步骤7: PC=7  [0xA7] R1 = R0             (保存结果到R1!)
步骤8: PC=14 [0xAE] 如果不等则跳转     (验证失败处理)
步骤9: PC=2  [0xA2] R2++                (索引+1)
步骤10: PC=13 [0xAD] 检查R2>31         (检查是否完成)
步骤11: PC=15 [0xAF] 如果未完成则循环  (继续或返回)
```

**关键发现**：R1寄存器在每次迭代中保持上一次的值！这是解题的关键。

### 4. 算法分析

对于每个字符i的处理算法：

```python
# 初始状态：R1(a17) = 0
for i in range(32):
    R0 = input[i]        # 加载字符
    R0 = R0 - i          # 减去索引
    R1 = R0 ^ R1         # R1异或R0（R1保留了上一次的值！）
    R0 = 0xCD            # 加载常量-51
    R0 = R0 ^ R1         # 异或R1
    # 验证：R0 必须等于 target[i]
    R1 = R0              # 将结果保存到R1，供下次使用
```

### 5. 解密推导

**对于第一个字符（i=0）**：
```
R1初始 = 0
temp = input[0] - 0 = input[0]
R1 = temp ^ 0 = temp
R0 = 0xCD ^ temp
要求：R0 == target[0]
因此：temp = 0xCD ^ target[0]
所以：input[0] = 0xCD ^ target[0]
```

**对于后续字符（i>0）**：
```
已知：R1 = target[i-1]（上一次的结果）
temp = input[i] - i
R1_new = temp ^ R1 = temp ^ target[i-1]
R0 = 0xCD ^ R1_new = 0xCD ^ temp ^ target[i-1]
要求：R0 == target[i]
因此：0xCD ^ temp ^ target[i-1] = target[i]
所以：temp = 0xCD ^ target[i] ^ target[i-1]
     input[i] = (0xCD ^ target[i] ^ target[i-1]) + i
```

### 6. 解密代码

```python
target = [
    0xF4, 0x0A, 0xF7, 0x64, 0x99, 0x78, 0x9E, 0x7D,
    0xEA, 0x7B, 0x9E, 0x7B, 0x9F, 0x7E, 0xEB, 0x71,
    0xE8, 0x00, 0xE8, 0x07, 0x98, 0x19, 0xF4, 0x25,
    0xF3, 0x21, 0xA4, 0x2F, 0xF4, 0x2F, 0xA6, 0x7C
]

# 第一个字符
flag = [0xCD ^ target[0]]

# 后续字符
for i in range(1, 32):
    temp = 0xCD ^ target[i] ^ target[i-1]
    char_value = (temp + i) & 0xFF
    flag.append(char_value)

flag_str = ''.join(chr(c) for c in flag)
print(f"Flag: UNCTF{{{flag_str}}}")
```

## 最终答案

**UNCTF{942a4115be2359ffd675fa6338ba23b6}**

## 关键教训

1. **状态保持**：在VM逆向中，必须仔细追踪寄存器状态在循环迭代之间的变化
2. **依赖关系**：本题的每个字符依赖于前一个字符的计算结果，形成了链式依赖
3. **细节观察**：指令0xA7（MOV R1, R0）将当前结果保存到R1，这是解题的关键
4. **完整追踪**：需要完整追踪至少一个循环的11条指令，才能理解完整的算法流程

## 工具和文件

- [`vm_analysis.md`](vm_analysis.md) - VM指令集详细分析
- [`vm_detailed_trace.py`](vm_detailed_trace.py) - 单次循环详细追踪
- [`correct_solution.py`](correct_solution.py) - 正确的解密脚本
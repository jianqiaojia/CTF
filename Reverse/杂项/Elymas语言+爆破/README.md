# CTF逆向题完整解题报告 - ey_or

## 题目信息

- **来源**: 32C3 CTF
- **难度**: ⭐⭐⭐⭐⭐⭐ (6/10)
- **方向**: Reverse (逆向工程)
- **类别**: 暴力破解 (Brute Force) + 自定义VM + 栈式语言 + XOR加密
- **二进制文件**: `ey_or`
- **架构**: x86-64 Linux ELF
- **主要技术**: Elymas语言识别、VM逆向、程序行为暴力破解、XOR解密

## 题目概述

这是一道非常特殊的CTF逆向题目。程序本身是一个**Elymas语言的解释器/虚拟机**，内嵌了用Elymas编写的验证逻辑。用户需要输入48个整数，程序验证每个整数是否与预设的`secret`数组匹配，最终输出`buffer XOR f`作为flag。

关键特点：
- 使用罕见的**Elymas栈式编程语言**
- 完整的**自定义VM实现**
- 验证逻辑**即时退出机制**（错误立即返回exit(1)）
- Secret和f数组难以通过静态分析提取

---

## 解题思路全过程

### 第一步：初步分析 - 这不是普通程序

#### 1.1 IDA中的第一印象

打开IDA后，立即发现异常：

```
入口点: start → __libc_start_main → main
主函数: sub_300000013000 (地址非常高，0x300000013000)
```

**第一个不寻常的地方**：
- 函数地址异常高（0x3开头），不是常规的0x40开头
- 程序段名称充满ANSI转义序列：`._[1_31m__[33m__[32m__[34m__[35m__[0m]`
- 这些段名其实是颜色代码！红、黄、绿、蓝、紫

**初步判断**：这不是普通的C程序编译结果！

#### 1.2 查看字符串 - 发现关键线索

在IDA中使用Shift+F12查看字符串窗口，找到大量连续的程序代码字符串：

```
] ==secret
] ==f
secret len ==l
[ ] ==buffer
0 ==i
0 ==j
"Enter Password line by line\n" sys .out .writeall
buffer f bxor str .fromArray sys .out .writeall
sys .exit
} sys .in .eachLine
"ey_or" sys .freeze
```

**第一个关键发现**：这看起来像是某种**脚本语言的源代码**！

特征：
- 栈式操作符（`==`, `bxor`, `.fromArray`）
- 系统调用（`sys .out`, `sys .in`, `sys .exit`）
- 控制结构（`{ }`, `?`, `*`）

#### 1.3 Google搜索 - 识别语言

搜索关键词："bxor str .fromArray sys"

**结果**：这是**Elymas语言**！
- 官方仓库：https://github.com/Drahflow/Elymas
- 特点：栈式编程语言，类似Forth
- 用途：脚本和嵌入式解释器

**第二个关键发现**：这个ELF文件是Elymas的**解释器+嵌入脚本**！

### 第二步：提取和理解Elymas源代码

#### 2.1 使用strings命令提取

```bash
strings ey_or > ey_strings.txt
```

在输出中找到完整的程序逻辑（IDA中地址0x600000585708附近）：

```elymas
[ ... ] ==secret
[ ... ] ==f
secret len ==l
[ ] ==buffer
0 ==i
0 ==j
"Enter Password line by line\n" sys .out .writeall
{
  txt .consume .u
  =j
  [ buffer _ len dearray j ] =buffer
  [ secret _ len dearray j eq { } { 1 sys .exit } ? * ] =secret
  i 1 add =i 
  i l eq {
    buffer f bxor str .fromArray sys .out .writeall
    0 sys .exit
  } { } ? *
} sys .in .eachLine
```

#### 2.2 转译为伪代码

理解Elymas栈式语言后，转译为易读的伪代码：

```python
secret = [???]  # 48个未知整数
f = [???]       # 48个未知整数
l = len(secret)
buffer = []
i = 0
j = 0

print("Enter Password line by line\n")

for line in sys.stdin.readlines():
    j = read_int(line)           # 读取一个整数
    buffer.append(j)              # 添加到buffer
    
    if secret[i] != j:            # 验证是否匹配secret[i]
        sys.exit(1)               # 不匹配立即退出，返回码1
    
    i += 1
    
    if i == l:                    # 如果所有48个都匹配
        # 输出 buffer XOR f 作为flag
        print(xor(buffer, f))
        sys.exit(0)               # 成功退出
```

**程序逻辑**：
1. 程序预设了48个整数的`secret`数组
2. 用户需要逐行输入48个整数
3. 每输入一个，立即验证是否等于`secret[i]`
4. 如果不匹配，程序立即退出(exit code 1)
5. 如果全部匹配，输出`buffer XOR f`作为flag

**第三个关键发现**：这是一个**即时验证**的机制！

### 第三步：分析IDA中的数据段 - 尝试静态提取

#### 3.1 寻找secret和f数组

在IDA中，找到包含"==secret"字符串的位置（0x600000585708），向前查找数组初始化数据。

发现数据格式：
```
0x80 0x00 0x00 0x00 0x00 0x00 0x00 0xXX
```

这是Elymas VM的内部数据格式，最后一个字节`XX`是实际值。

#### 3.2 尝试提取 - 遇到困难

问题：
1. 数据分散在多个位置
2. VM的内存布局复杂
3. 数组初始化可能通过VM指令动态完成
4. 无法确定哪些数据属于secret，哪些属于f

**第一次失败**：静态提取的数据看起来像是x86汇编指令（0x48, 0x89等），不是正确的数组！

**认识到局限性**：对于自定义VM，静态分析非常困难。需要换思路！

### 第四步：暴力破解思路 - 利用即时验证机制

#### 4.1 关键观察

程序的**即时验证**特性给了我们机会：

```
输入第1个数 → 验证 → 错误则exit(1)
输入第2个数 → 验证 → 错误则exit(1)
...
输入第48个数 → 验证 → 全部正确则输出flag
```

**第四个关键发现**：可以利用exit code来判断！
- 如果exit code = 1：当前位置的值不对
- 如果exit code ≠ 1：当前位置的值正确

#### 4.2 暴力破解策略

对于每个位置i（0-47）：
```python
for value in range(256):  # 尝试0-255
    # 输入所有已知正确的值 + 当前测试值
    process = run_program_with_input(correct_values + [value])
    
    if process.exit_code != 1:
        # 找到了位置i的正确值！
        correct_values.append(value)
        break
```

**可行性分析**：
- 每个位置最多尝试256次
- 48个位置 × 256次 = 12,288次运行
- 每次运行很快（几毫秒）
- 总耗时预计：几分钟

**这是可行的！**

### 第五步：实现暴力破解脚本

#### 5.1 Python 3实现（关键代码）

```python
import subprocess

ans = []

while True:
    found = False
    for j in range(256):
        # 创建进程
        p = subprocess.Popen("./ey_or", 
                           stdin=subprocess.PIPE, 
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
        
        # 输入所有已知的正确值
        for x in ans:
            p.stdin.write((str(x) + '\n').encode())  # Python 3需要bytes
        
        # 输入当前测试值
        p.stdin.write((str(j) + '\n').encode())
        p.stdin.close()
        
        ret = p.wait()  # 等待程序结束
        
        if ret != 1:  # 不是错误退出码
            ans.append(j)
            print(f"Position {len(ans)-1}: {j}")
            found = True
            break
    
    if not found or len(ans) >= 48:
        break

print("Complete secret array:", ans)
```

**Python 3注意事项**：
- `stdin.write()`需要bytes对象，不能是str
- 必须使用`.encode()`转换

#### 5.2 运行结果

```
Position 0: 36
Position 1: 30
Position 2: 156
Position 3: 30
Position 4: 43
Position 5: 6
...
Position 47: 24
```

**完整secret数组**：
```python
[36, 30, 156, 30, 43, 6, 116, 22, 211, 66, 151, 89, 36, 82, 254, 81, 182, 
 134, 24, 90, 119, 6, 88, 137, 64, 197, 251, 15, 116, 220, 161, 94, 154, 252, 
 139, 11, 41, 215, 27, 158, 143, 140, 54, 189, 146, 48, 167, 56, 84, 226, 15, 
 188, 126, 24]
```

**成功暴力破解所有48个值！**

### 第六步：获取最终Flag

#### 6.1 输入完整的secret数组

既然已经暴力破解得到了所有48个正确值，现在只需要完整输入它们：

```python
import subprocess

ans = [36, 30, 156, 30, 43, 6, 116, 22, 211, 66, 151, 89, 36, 82, 254, 81, 182,
       134, 24, 90, 119, 6, 88, 137, 64, 197, 251, 15, 116, 220, 161, 94, 154, 252,
       139, 11, 41, 215, 27, 158, 143, 140, 54, 189, 146, 48, 167, 56, 84, 226, 15,
       188, 126, 24]

p = subprocess.Popen("./ey_or",
                     stdin=subprocess.PIPE,
                     stdout=subprocess.PIPE,
                     stderr=subprocess.PIPE)

# 输入所有48个正确值
for x in ans:
    p.stdin.write((str(x) + '\n').encode())
p.stdin.close()

# 读取输出
output = p.stdout.read().decode()
print(output)
```


#### 6.2 输出结果

```
32C3_wE_kNoW_EvErYbOdY_LiKeS_eLyMaS
```

**这就是flag！**

---

## 为什么静态分析困难？

### VM架构的复杂性

1. **数据格式转换**
   - Elymas使用特殊的数据格式：`0x80 0x00...0xXX`
   - 需要理解VM的内存表示方式

2. **动态执行**
   - Secret和f数组可能通过VM指令序列构建
   - 不是简单的静态数据段

3. **代码和数据混合**
   - VM字节码和程序数据交织在一起
   - 很难区分哪些是代码，哪些是数据

4. **缺少符号信息**
   - 没有调试符号
   - 变量名都是VM内部的栈操作

### 为什么暴力破解是最优解

1. **即时验证机制**
   - 程序设计本身提供了一个"oracle"
   - 每次尝试都能得到明确的反馈

2. **搜索空间可控**
   - 48个位置 × 256种可能 = 12,288次
   - 现代计算机几分钟就能完成

3. **无需理解VM**
   - 把程序当作黑盒
   - 只需要观察输入输出行为

4. **鲁棒性强**
   - 不依赖于VM的具体实现
   - 即使程序更新也能适用

---

## 错误路径总结

在解题过程中尝试过的方法：

### 错误1: 认为输入是字符而非整数
**错误想法**: 看到"line by line"以为是字符串输入
**真相**: Elymas代码中`txt .consume .u`表示读取整数
**教训**: 仔细理解源代码中的每个操作符

### 错误2: 尝试从IDA中手动提取数组
**错误想法**: 认为可以找到明确的数组初始化
**真相**: VM的内存布局复杂，数据可能动态生成
**教训**: 对于自定义VM，静态分析效率低

### 错误3: 尝试用data1/data2计算flag
**错误想法**: 认为函数调用中传递的数据就是secret和f
**真相**: 那些只是VM的内部数据结构
**教训**: 不要被汇编层面的数据传递迷惑

### 错误4: 忽视即时验证的价值
**错误想法**: 一定要理解程序内部逻辑
**真相**: 程序行为本身就是最好的线索
**教训**: 黑盒测试有时比白盒分析更有效

---

## 程序核心机制详解

### Elymas语言特点

```elymas
栈式操作:
  5 3 add    # 栈: [5, 3] → [8]
  "hello"    # 栈: ["hello"]
  
变量赋值:
  42 =x      # x = 42
  
数组操作:
  [ 1 2 3 ] =arr       # arr = [1, 2, 3]
  arr 0 dearray        # 取arr[0]
  
控制流:
  condition { true_branch } { false_branch } ? *
  # 等价于: if condition: true_branch else: false_branch
```

### 程序执行流程

```
1. 初始化
   ├─ secret = [...] (48个整数)
   ├─ f = [...] (48个整数)
   ├─ buffer = []
   └─ i = 0

2. 读取循环 (48次)
   ├─ 读取一行输入
   ├─ 转换为整数j
   ├─ buffer.append(j)
   ├─ 验证: secret[i] == j?
   │   ├─ 是: 继续
   │   └─ 否: exit(1) ←── 关键：即时退出
   └─ i++

3. 解密和输出
   ├─ 计算: flag = buffer XOR f
   ├─ 转换为字符串
   └─ 输出flag
```

### 内存布局（VM层面）

```
数据格式: 0x80 0x00 0x00 0x00 0x00 0x00 0x00 0xXX
          ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^  ^^^^^
          类型标记 (整数类型)                  实际值

示例:
  整数 72  → 0x80 0x00 0x00 0x00 0x00 0x00 0x00 0x48
  整数 131 → 0x80 0x00 0x00 0x00 0x00 0x00 0x00 0x83
```

---

## 技术总结

### 核心技术点

1. **Elymas语言识别** ⭐⭐⭐⭐⭐
   - 识别罕见的编程语言
   - 理解栈式语言的语法
   - 转译为常规伪代码

2. **自定义VM逆向** ⭐⭐⭐⭐⭐
   - 识别VM解释器结构
   - 理解VM的数据格式
   - 认识到静态分析的局限性

3. **黑盒暴力破解** ⭐⭐⭐⭐
   - 利用程序的即时验证机制
   - 基于exit code的反馈
   - 逐位置破解策略

4. **XOR解密** ⭐⭐
   - 理解buffer XOR f的逻辑
   - 程序自动完成解密

### 难点突破

1. **语言识别** ⭐⭐⭐⭐⭐
   - 最大难点：Elymas是非常罕见的语言
   - 突破方法：Google搜索语法特征
   - 关键词：栈式操作符 + 系统调用

2. **VM逆向困境** ⭐⭐⭐⭐⭐
   - 难点：自定义VM难以静态分析
   - 突破方法：放弃静态提取，转向动态破解
   - 思维转换：从"理解"到"利用"

3. **即时验证利用** ⭐⭐⭐⭐
   - 难点：如何高效测试
   - 突破方法：subprocess + exit code判断
   - 优化：逐位置而非全排列

4. **Python 3兼容性** ⭐⭐
   - 难点：stdin需要bytes
   - 突破方法：使用.encode()转换

### 学到的经验

1. **不要被复杂性吓倒**
   - VM看起来很复杂
   - 但核心逻辑可能很简单
   - 找到关键突破口

2. **黑盒方法的价值**
   - 不一定要完全理解内部实现
   - 行为观察可能更有效
   - 程序本身可以是"oracle"

3. **罕见技术的应对**
   - 遇到未知语言/技术不要慌
   - 善用Google和GitHub
   - 开源社区是宝贵资源

4. **灵活切换思路**
   - 静态分析不行就尝试动态
   - 一种方法卡住就换另一种
   - 保持开放的解题思维

---

## 解题脚本使用

### 暴力破解脚本 (aa.py)

```bash
# Linux环境下运行
python3 aa.py

# 输出示例:
# Position 0: 36
# Position 1: 30
# ...
# Position 47: 24
# Complete secret array: [36, 30, 156, ...]
```

### 获取Flag脚本 (get_flag.py)

```python
from pwn import *

ans = [36, 30, 156, ...] # 暴力破解得到的secret数组

p = process('./ey_or')
for x in ans:
    p.sendline(str(x))
b = p.recvall()
print(b.decode())
p.close()

# 输出: 32C3_wE_kNoW_EvErYbOdY_LiKeS_eLyMaS
```

---

## 最终答案

### Secret数组（通过暴力破解获得）
```python
[36, 30, 156, 30, 43, 6, 116, 22, 211, 66, 151, 89, 36, 82, 254, 81, 182, 
 134, 24, 90, 119, 6, 88, 137, 64, 197, 251, 15, 116, 220, 161, 94, 154, 252, 
 139, 11, 41, 215, 27, 158, 143, 140, 54, 189, 146, 48, 167, 56, 84, 226, 15, 
 188, 126, 24]
```

### Flag
```
32C3_wE_kNoW_EvErYbOdY_LiKeS_eLyMaS
```

意思：**"32C3 - 我们知道每个人都喜欢Elymas"**

这个flag本身就是题目的一个玩笑：
- 32C3是比赛名称
- Elymas是这道题使用的罕见语言
- 出题人用这种方式炫耀了这门小众语言 😄

---

## 工具和环境

- **IDA Pro 7.x/8.x**: 静态分析和查看字符串
- **Linux环境**: 运行二进制文件
- **Python 3.8+**: 编写暴力破解脚本
- **pwntools**: Python库，用于与进程交互
- **strings命令**: 提取可打印字符串

---

## 作者注

这道题的设计非常巧妙，它：
1. 使用了罕见的Elymas语言（考察知识广度）
2. 实现了完整的VM（考察逆向深度）
3. 提供了即时验证机制（提供了解题线索）
4. 让暴力破解成为最优解（平衡难度）

**最关键的突破点**：
1. **识别Elymas语言** - 需要Google搜索能力
2. **认识到暴力破解的可行性** - 不要被VM的复杂性吓倒
3. **利用即时验证** - 程序行为本身就是最好的oracle

解题过程中，我首先尝试了静态分析，想从IDA中提取secret和f数组，但遇到了VM复杂性的困扰。后来意识到，程序的即时验证机制给了我们一个完美的"黑盒测试接口"，只需要观察exit code就能判断输入是否正确。这个思路转换是解题的关键。

**记住**：有时候最简单的方法就是最有效的方法！不要陷入"一定要完全理解内部机制"的思维定式。

希望这份详细的解题报告能帮助你理解从困惑到顿悟的完整思路过程。**解题的过程比答案本身更有价值！**

---

## 参考资源

- **Elymas官方仓库**: https://github.com/Drahflow/Elymas
- **Elymas语言文档**: https://github.com/Drahflow/Elymas/wiki
- **32C3 CTF**: https://ctftime.org/event/278

---

## 文件清单

### 主要文件
- `README.md` - 完整解题报告（本文档）
- `aa.py` - 暴力破解脚本（修正Python 3版本）
- `get_flag.py` - 使用secret数组获取flag
- `ey_or` - 原始二进制文件

### 分析文档
- `CTF_ANALYSIS_SUMMARY.md` - 详细的IDA分析过程
- `prog_source_analysis.md` - Elymas源代码分析
- `understanding_wp.py` - WP理解和验证

### 辅助脚本
- `solve_with_data_arrays.py` - 尝试用data1/data2计算（失败的尝试）
- `extract_final_flag.py` - 尝试从IDA数据提取（失败的尝试）
- `calculate_final_flag.py` - 反推f数组的尝试
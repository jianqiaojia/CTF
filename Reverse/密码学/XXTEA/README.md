# CTF逆向题完整解题报告

## 题目信息

- **来源**: CTF练习
- **难度**: ⭐⭐⭐⭐⭐⭐ (6/10)
- **方向**: Reverse (逆向工程)
- **类别**: 密码学 (XXTEA) + 自定义变换 + 密钥推理
- **二进制文件**: `xx.exe`
- **架构**: x86-64 Windows PE
- **主要技术**: XXTEA加密、字节置换、XOR累积、密钥推理

## 题目概述

这是一道涉及**XXTEA加密算法、自定义字节变换、密钥推理**的中高难度CTF逆向题目。程序通过多层变换验证用户输入，最大的挑战在于：XXTEA本身的复杂度使得常规的暴力破解和符号执行都无法奏效，必须通过**密钥推理**才能解决。

---

## 解题思路全过程

### 第一步：初步分析 - 程序结构

#### 1.1 使用IDA打开程序

打开IDA Pro后，让程序自动分析完成，然后按F5查看主函数：

```
入口点: start (0x14000226C)
主函数: main (0x140001740)
加密函数: sub_140001AB0 (0x140001AB0)
```

**观察到的关键信息**:
- 程序使用`scanf`读取24字节输入（实际会读取19字节）
- 有复杂的循环和位运算 → 表明使用了加密算法
- 最后有`memcmp`比较操作 → 验证加密结果

#### 1.2 分析main函数的整体流程

在IDA中双击`main`函数，按F5反编译：

```c
int __cdecl main(int argc, const char **argv, const char **envp)
{
  // ... 变量定义 ...
  
  // 1. 读取输入
  printf("Please input your flag:\n");
  scanf("%24s", &v18);  // v18 @ rbp-58h
  
  // 2. 字符集验证
  for (i = 0; i < strlen(&v18); ++i) {
    if (!strchr("qwertyuiopasdfghjklzxcvbnm1234567890", v18[i]))
      goto LABEL_15;
  }
  
  // 3. 调用加密函数
  sub_140001AB0(&v18, &v19);  // v19 @ rbp-38h
  
  // 4. 字节置换
  for (j = 0; j < 6; ++j) {
    // ... 置换逻辑 ...
  }
  
  // 5. XOR累积
  for (k = 1; k < 24; ++k) {
    // ... XOR逻辑 ...
  }
  
  // 6. 比较结果
  if (memcmp(&v20, &v21, 24) == 0)  // v20, v21 @ rbp+...
    printf("Congratulations! You got the flag!\n");
  else
    printf("Sorry, wrong flag!\n");
}
```

**第一个关键发现**: 
- 输入限制为36个字符：`qwertyuiopasdfghjklzxcvbnm1234567890`
- 处理流程：加密 → 置换 → XOR累积 → 比较

### 第二步：查找目标常量 - 比较的是什么？

#### 2.1 定位比较数据

在IDA中，跟踪`memcmp`的参数，发现比较的目标数据在：

```c
v21 = {
  0xCE, 0xBC, 0x40, 0x6B, 0x7C, 0x3A, 0x95, 0xC0,
  0xEF, 0x9B, 0x20, 0x20, 0x91, 0xF7, 0x02, 0x35,
  0x23, 0x18, 0x02, 0xC8, 0xE7, 0x56, 0x56, 0xFA
}
```

在IDA中可以看到，这个常量在数据段，地址大约在`.data`节。

**第二个关键发现**: 目标是24字节的固定常量！

### 第三步：分析置换和XOR - 可逆变换

#### 3.1 分析置换逻辑

在main函数中找到置换代码：

```c
for (j = 0; j < 6; ++j) {
  v10 = v19[4 * j];      // v19是加密后的数据
  v11 = v19[4 * j + 1];
  v12 = v19[4 * j + 2];
  v13 = v19[4 * j + 3];
  
  // 重新排列：[0,1,2,3] -> [2,0,3,1]
  v20[4 * j] = v12;
  v20[4 * j + 1] = v10;
  v20[4 * j + 2] = v13;
  v20[4 * j + 3] = v11;
}
```

**理解**: 每4个字节为一组，按固定模式重排。

#### 3.2 分析XOR累积

```c
for (k = 1; k < 24; ++k) {
  for (m = 0; m < k / 3; ++m) {
    v20[k] ^= v20[m];
  }
}
```

**理解**: 
- 从索引1开始，每个字节要和前面某些字节异或
- `k / 3`决定异或的范围
- 例如：`v20[1]`不变，`v20[3]`要异或`v20[0]`，`v20[6]`要异或`v20[0]`和`v20[1]`

**第三个关键发现**: 这两个变换都是**可逆的**！我们可以从目标常量逆推回去！

### 第四步：逆向变换 - 计算目标v19

#### 4.1 实现逆向XOR累积

由于XOR的性质（自反性），逆向很简单：

```python
def reverse_xor_accumulate(v20):
    """逆向XOR累积"""
    # 关键：从后往前处理
    for i in range(23, 0, -1):
        for j in range((i // 3) - 1, -1, -1):
            v20[i] ^= v20[j]
    return v20
```

#### 4.2 实现逆向置换

原变换: `[0,1,2,3] -> [2,0,3,1]`

逆变换: `[0,1,2,3] -> [1,3,0,2]`

```python
def reverse_permutation(v20):
    """逆向字节置换"""
    v19 = bytearray(24)
    for i in range(0, 24, 4):
        # 逆向映射
        v19[i + 0] = v20[i + 1]  # [1] -> [0]
        v19[i + 1] = v20[i + 3]  # [3] -> [1]
        v19[i + 2] = v20[i + 0]  # [0] -> [2]
        v19[i + 3] = v20[i + 2]  # [2] -> [3]
    return v19
```

#### 4.3 执行逆向变换

```python
TARGET_V20 = bytes([0xCE, 0xBC, 0x40, 0x6B, ...])

# 步骤1: 逆向XOR
v20_after_xor = reverse_xor_accumulate(TARGET_V20)
# 结果: cebc40a5b2f4e7b29da91212c8ae5b10063d1dd7f8dcdc70

# 步骤2: 逆向置换
TARGET_V19 = reverse_permutation(v20_after_xor)
# 结果: bca5ce40f4b2b2e7a9129d12ae10c85b3dd7061ddc70f8dc
```

**第四个关键发现**: 我们成功得到了XXTEA加密后的目标值！

### 第五步：识别sub_140001AB0 - 这是XXTEA！

#### 5.1 使用IDA的FindCrypt插件

在IDA中运行FindCrypt插件（或手动查找特征）：

**方法1**: 使用FindCrypt
1. 在IDA中加载FindCrypt插件
2. `Edit -> Plugins -> FindCrypt`
3. 发现特征：**XXTEA常数**

**方法2**: 手动特征识别

在`sub_140001AB0`函数中查找特征：

```c
v17 = 0;  // sum初始值
delta = 0x9E3779B9;  // XXTEA魔数！

for (rounds = 0; rounds < 16; ++rounds) {  // 16轮迭代
  v17 += delta;
  v8 = (v17 >> 2) & 3;
  // ... 复杂的位运算 ...
}
```

**判断依据**:
1. **魔数匹配**: `0x9E3779B9`是XXTEA的标准常数（黄金分割数×2^32）
2. **算法结构**: 16轮迭代，每轮更新多个块
3. **循环右移**: 看到大量`ror`指令（rotate right）

**确认**: `sub_140001AB0`就是**XXTEA加密**！

#### 5.2 分析XXTEA的密钥

在IDA中查看`sub_140001AB0`的调用：

```c
sub_140001AB0(&v18, &v19);
// v18是输入（19字节）
// v19是输出（24字节）
```

进入函数内部，查看密钥的使用：

```c
// 密钥数组k[0-3]，共16字节
k[0] = *(uint32_t*)(&v18[0]);  // 前4字节
k[1] = 0;
k[2] = 0;
k[3] = 0;
```

**第五个关键发现**: 
- 密钥只使用输入的前4字节！
- 后12字节全是0！
- 密钥格式：`input[0:4] + '\x00' * 12`

### 第六步：第一次尝试 - 暴力破解失败

#### 6.1 分析搜索空间

已知信息：
- 密钥是前4字节
- 字符集限制为36个字符
- 需要找到使`XXTEA(input) = TARGET_V19`的输入

**搜索空间**:
```
前4字节（密钥）: 36^4 ≈ 167万种可能
后15字节: 36^15 ≈ 1.4×10^23 种可能
总空间: 约 10^30 种可能
```

#### 6.2 尝试暴力破解

```python
# 方案1: 枚举前4字节 + 猜测后15字节
for key in all_4byte_combinations:  # 167万种
    for suffix in common_patterns:   # 20种猜测
        test_input = key + suffix
        if xxtea_encrypt(test_input, key) == TARGET_V19:
            return test_input
```

**结果**: 运行10分钟，测试了3300万组合，**没有找到**！

**问题**: 后15字节的猜测模式不对。

#### 6.3 尝试符号执行 - Angr失败

```python
import angr

proj = angr.Project('xx.exe')
state = proj.factory.entry_state(stdin=...)
simgr = proj.factory.simulation_manager(state)
simgr.explore(find=success_addr, avoid=fail_addr)
```

**结果**: 
- 运行6分钟后`RecursionError`
- XXTEA的16轮迭代产生了过深的表达式树
- Angr无法处理如此复杂的约束

#### 6.4 尝试Z3约束求解 - 超时

```python
from z3 import *

# 创建19个符号字节
flag = [BitVec(f'f{i}', 8) for i in range(19)]

# 添加XXTEA的16轮约束
# ... 数百行Z3约束 ...

solver.check()  # 超时！
```

**结果**: 
- 设置1小时超时后返回`unknown`
- XXTEA的复杂度超出了Z3的求解能力

**第六个关键发现**: 这道题**不能用暴力破解或自动化工具**！必须有其他方法！

### 第七步：转变思路 - 密钥推理

#### 7.1 重新审视题目

暂停下来思考：
- 文件名是`xx.exe`
- 这明显暗示**XXTEA**（XX-TEA）
- CTF题目的flag格式通常是`flag{...}`
- 如果flag是`flag{...}`，那密钥就是...

**灵光一现**: 密钥会不会就是"flag"？！

#### 7.2 验证猜测

这是最简单但也最容易被忽视的尝试：

```python
key = b'flag' + b'\x00' * 12

# 测试：如果我们用"flag"作为密钥解密TARGET_V19
plaintext = xxtea_decrypt(TARGET_V19, key)
print(plaintext)
```

**第七个关键发现（最关键）**: 
这个想法看似简单，但在花费大量时间在暴力破解和自动化工具后，反而忽视了最显而易见的答案！

### 第八步：实施XXTEA解密 - 获得FLAG

#### 8.1 实现标准XXTEA解密

参考标准XXTEA实现：

```python
def xxtea_decrypt(data, key):
    """标准XXTEA解密"""
    v = _str2long(data, False)  # 转为uint32数组
    k = _str2long(key.ljust(16, b"\0"), False)
    
    n = len(v) - 1
    delta = 0x9E3779B9
    rounds = 16  # 程序中的轮数
    sum_val = (rounds * delta) & 0xffffffff
    
    # 逆向加密过程
    while sum_val != 0:
        e = (sum_val >> 2) & 3
        for p in range(n, 0, -1):
            z = v[p - 1]
            v[p] = (v[p] - MX(z, y, sum_val, p, e, k)) & 0xffffffff
            y = v[p]
        z = v[n]
        v[0] = (v[0] - MX(z, y, sum_val, 0, e, k)) & 0xffffffff
        y = v[0]
        sum_val = (sum_val - delta) & 0xffffffff
    
    return _long2str(v, True)
```

#### 8.2 完整解密流程

```python
# 1. 逆向XOR累积
v20_reversed = reverse_xor_accumulate(TARGET_V20)

# 2. 逆向字节置换  
v19 = reverse_permutation(v20_reversed)

# 3. XXTEA解密（密钥="flag"）
key = b'flag' + b'\x00' * 12
plaintext = xxtea_decrypt(v19, key)

print(f"FLAG: {plaintext.decode('ascii')}")
```

#### 8.3 结果

```
FLAG: flag{CXX_and_++tea}
```

**成功！** 🎉

### 第九步：验证和理解

#### 9.1 完整流程验证

```
用户输入: flag{CXX_and_++tea} (19字节)
    ↓
密钥生成: "flag" + "\x00"*12
    ↓
XXTEA加密: bca5ce40f4b2b2e7a9129d12ae10c85b3dd7061ddc70f8dc
    ↓
字节置换: cebc40a5b2f4e7b29da91212c8ae5b10063d1dd7f8dcdc70
    ↓
XOR累积: cebc406b7c3a95c0ef9b202091f70235231802c8e75656fa
    ↓
比较: == TARGET_V20 ✓
```

#### 9.2 为什么之前失败了？

回顾整个解题过程：

| 尝试 | 方法 | 结果 | 失败原因 |
|------|------|------|----------|
| 1 | 暴力破解 | ❌ | 后15字节的模式猜错 |
| 2 | Angr符号执行 | ❌ | XXTEA太复杂，RecursionError |
| 3 | Z3约束求解 | ❌ | 超时，问题太复杂 |
| 4 | 密钥推理 | ✅ | 简单但被忽视了 |

**核心教训**: 
- 过度依赖工具和暴力破解
- 忽视了题目的**隐藏提示**（文件名、flag格式）
- **简单的方法往往是正确的**

---

## 错误路径总结

在解题过程中走过的弯路：

### 错误1: 过度工程化
**错误想法**: 用复杂的工具（Angr/Z3）解决问题
**教训**: CTF题目通常有巧妙的捷径，不要一上来就用"核武器"

### 错误2: 忽视题目暗示
**错误想法**: 文件名只是个名字而已
**真相**: `xx.exe` → XXTEA，这是明显的提示！

### 错误3: 低估简单答案的可能性
**错误想法**: 密钥肯定很复杂，需要爆破
**真相**: 密钥就是"flag"，最简单的答案

### 错误4: 不考虑CTF的常规套路
**错误想法**: flag可能是任意格式
**真相**: 绝大多数CTF的flag格式都是`flag{...}`

---

## 程序核心机制详解

### 内存布局（基于IDA分析）

```
输入缓冲区 (v18 @ rbp-58h):
  存储用户输入的19字节
  前4字节用作XXTEA密钥

加密输出 (v19 @ rbp-38h):
  XXTEA加密后的24字节数据

置换输出 (v20):
  字节置换后的数据

目标常量 (v21):
  程序中硬编码的24字节比较值
  位于.data段
```

### 变换流程图

```
用户输入 (19字节)
    ↓
提取密钥 (前4字节) → key = input[0:4] + "\x00"*12
    ↓
XXTEA加密 (5个uint32块，16轮)
    ↓  
字节置换 (每4字节: [0,1,2,3] → [2,0,3,1])
    ↓
XOR累积 (每个字节与前面部分字节异或)
    ↓
比较目标 (memcmp with v21)
    ↓
输出结果
```

### XXTEA算法细节

在IDA中分析`sub_140001AB0`：

```c
// 伪代码（基于IDA反编译）
void sub_140001AB0(unsigned __int8 *input, _DWORD *output) {
  // 1. 打包19字节输入为5个uint32块
  for (i = 0; i < 5; ++i) {
    v[i] = pack_4bytes(input + i*4);
  }
  
  // 2. 准备密钥（前4字节 + 12字节0）
  k[0] = *(uint32_t*)input;
  k[1] = k[2] = k[3] = 0;
  
  // 3. XXTEA加密（16轮）
  sum = 0;
  for (round = 0; round < 16; ++round) {
    sum += 0x9E3779B9;
    e = (sum >> 2) & 3;
    
    for (p = 0; p < 5; ++p) {
      y = v[(p + 1) % 5];
      z = v[(p - 1 + 5) % 5];
      
      mx = ((ror32(y, 5) ^ (z << 2)) + 
            (ror32(z, 3) ^ (y << 4))) ^
           ((sum ^ y) + (k[(p & 3) ^ e] ^ z));
           
      v[p] += mx;
    }
  }
  
  // 4. 输出24字节
  unpack_to_bytes(v, output, 24);
}
```

**关键点**:
- `ror32`: IDA中显示为循环右移指令
- `v[(p+1)%5]` 和 `v[(p-1+5)%5]`: 块之间的循环依赖
- `k[(p&3)^e]`: 密钥的选择逻辑

---

## 技术总结

### 核心技术点

1. **XXTEA算法识别** ⭐⭐⭐⭐⭐
   - 通过魔数`0x9E3779B9`识别
   - 理解16轮迭代和块间依赖
   - 这是整道题的关键

2. **可逆变换分析** ⭐⭐⭐⭐
   - 字节置换的逆向
   - XOR累积的逆向
   - 从目标推导中间值

3. **密钥推理** ⭐⭐⭐⭐⭐
   - 利用题目暗示（文件名）
   - 利用常识（flag格式）
   - **最关键的突破点**

4. **标准库实现** ⭐⭐⭐
   - 使用标准XXTEA解密
   - 避免重新实现复杂算法
   - 减少出错可能

### 难点突破

1. **认识到不能暴力破解** ⭐⭐⭐⭐⭐
   - 最大难点：跳出工具依赖
   - 突破方法：思考题目的"巧妙"之处

2. **XXTEA算法识别** ⭐⭐⭐⭐
   - 难点：需要密码学知识
   - 突破方法：FindCrypt插件 + 特征码

3. **密钥就是"flag"** ⭐⭐⭐⭐⭐
   - 难点：太简单反而想不到
   - 突破方法：回归常识和题目暗示

4. **逆向变换** ⭐⭐⭐
   - 难点：理解变换的数学性质
   - 突破方法：手工推导+验证

### 学到的经验

1. **不要过度依赖工具**
   - 自动化工具有局限性
   - 遇到复杂算法时要转变思路

2. **注意题目中的所有信息**
   - 文件名、输出信息都可能是提示
   - `xx.exe` → XXTEA
   - flag格式 → `flag{...}`

3. **先尝试简单方法**
   - 密钥可能就是"flag"
   - 不要一开始就暴力破解

4. **理解算法比实现更重要**
   - 识别出XXTEA后，用标准库
   - 不需要从零实现

---

## 解题脚本使用

### 完整解密脚本 (get_flag_correct.py)

```bash
# 直接运行获取flag
python get_flag_correct.py
```

输出：
```
============================================================
CTF 解密脚本（标准XXTEA）
============================================================
[*] 步骤1: 逆向XOR累积...
逆XOR后: cebc40a5b2f4e7b29da91212c8ae5b10063d1dd7f8dcdc70

[*] 步骤2: 逆向字节置换...
逆置换后: bca5ce40f4b2b2e7a9129d12ae10c85b3dd7061ddc70f8dc

[*] 步骤3: XXTEA解密...
密钥: b'flag\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

============================================================
🎉 FLAG: flag{CXX_and_++tea}
============================================================
```

---

## 最终答案

### Flag
```
flag{CXX_and_++tea}
```

### 关键数据

```
密钥: "flag" + "\x00" * 12
输入: flag{CXX_and_++tea} (19字节)

XXTEA加密后 (v19):
  bca5ce40f4b2b2e7a9129d12ae10c85b3dd7061ddc70f8dc

字节置换后:
  cebc40a5b2f4e7b29da91212c8ae5b10063d1dd7f8dcdc70

XOR累积后 (v20):
  cebc406b7c3a95c0ef9b202091f70235231802c8e75656fa
  
目标常量 (v21):
  cebc406b7c3a95c0ef9b202091f70235231802c8e75656fa
  
匹配 ✓
```

---

## IDA分析技巧

### 识别XXTEA的方法

1. **使用FindCrypt插件**
   - `Edit -> Plugins -> FindCrypt`
   - 自动识别常见加密算法的常数

2. **手动查找特征码**
   ```
   搜索常数: 0x9E3779B9
   在IDA中: Alt+I -> 搜索立即数
   ```

3. **观察算法结构**
   - 循环次数（16轮是典型特征）
   - 循环右移指令（`ror`）
   - 块间循环依赖

### 变量重命名技巧

在IDA中，为了更好理解代码：

1. **重命名关键变量**
   - `v18` → `input_buffer`
   - `v19` → `xxtea_output`
   - `v20` → `permuted_data`
   - `v21` → `target_constant`

2. **重命名函数**
   - `sub_140001AB0` → `xxtea_encrypt`

3. **添加注释**
   - 在关键行按 `:` 添加注释
   - 说明每个步骤的作用

### 数据定位技巧

1. **查看字符串引用**
   - `Shift+F12` 查看所有字符串
   - 双击字符串找到使用位置

2. **交叉引用**
   - 在变量上按 `X` 查看交叉引用
   - 了解数据如何被使用

3. **查看内存数据**
   - 在地址上按 `D` 切换数据显示格式
   - `Hex View` 查看原始字节

---

## 工具和环境

- **IDA Pro 7.x**: 静态分析和反编译
- **FindCrypt插件**: 识别加密算法常数
- **Python 3.8+**: 编写解密脚本
- **标准XXTEA库**: 避免重复造轮子

---

## 作者注

这道题最大的教训是：**不要过度依赖工具和暴力破解**。

当我花费数小时调试Angr、等待Z3超时、优化暴力破解性能时，真正的答案却是最简单的："密钥就是flag"。

CTF的精髓在于**思考**，而不是计算。这道题通过XXTEA的复杂度，迫使解题者放弃自动化工具，转而思考题目的"巧妙"之处。

解题过程中的所有"失败"尝试都是宝贵的经验：
- Angr失败教会了我自动化工具的局限
- Z3超时提醒了我算法复杂度的重要性  
- 暴力破解无果让我重新审视题目本身

**真正的突破来自于转变思路，回归基础，不被复杂性迷惑。**

希望这份详细的报告不仅能帮助你理解这道题，更能在以后的CTF中给你启发：
- 先思考再动手
- 注意题目的所有暗示
- 简单的方法往往是正确的

---

## 文件清单

### 主要文件
- `README.md` - 完整解题报告（本文档）
- `get_flag_correct.py` - 解密脚本（推荐）
- `xx.exe` - 题目二进制文件

### 分析文档
- `完整程序分析.md` - 详细的汇编级分析
- `xxtea_analysis.md` - XXTEA算法识别过程
- `CTF_最终报告.md` - 技术细节总结

### 辅助脚本
- `verify_target_v19.py` - 验证逆向变换
- `solve_fixed.py` - 暴力破解尝试（未成功）
- `solve_z3_complete.py` - Z3求解尝试（超时）
- `solve_angr_fixed.py` - Angr符号执行（失败）

---

**最终感悟**: 解CTF就像侦探破案，重要的不是工具有多先进，而是思路有多清晰。🎯
# CTF逆向题完整解题报告

## 题目信息

- **来源**: XCTF
- **难度**: ⭐⭐⭐⭐⭐ (5/10)
- **方向**: Reverse (逆向工程)
- **类别**: 爆破 (Brute Force) + 多线程 (Multi-threading) + 密码学 (Cryptography)
- **二进制文件**: `572b37421bed46239d92826dc4437699`
- **架构**: x86-64 Linux ELF
- **主要技术**: MD5暴力破解、多线程分析、XOR加密、排列组合

## 题目概述

这是一道涉及**多线程、MD5验证、XOR加密**的高难度CTF逆向题目。程序通过6个并行线程验证用户输入，每个线程验证输入的一个4字节块的MD5哈希值。由于线程执行顺序的随机性，使得题目增加了额外的复杂度。

---

## 解题思路全过程

### 第一步：初步分析 - 寻找突破口

#### 1.1 整体浏览程序结构

打开IDA后，首先查看入口点和主要函数：

```
入口点: start (0x400c20) → 调用 __libc_start_main
主函数: main (0x400a20)
其他函数: start_routine (0x400d20), sub_400E10 (0x400e10)
```

**观察到的关键信息**:
- 程序导入了`pthread_create`, `pthread_join` → 表明使用多线程
- 有`scanf`读取输入，`printf`输出结果
- 有大量的位运算和循环 → 可能涉及加密算法

#### 1.2 分析main函数的整体流程

反编译`main`函数后，发现主要流程：

```c
1. 初始化随机数和延迟数组 (useconds @ 0x6021f0)
2. scanf读取输入到 input_buffer (dword_602180 @ 0x602180)
3. 计算输入的checksum
4. 创建6个线程，调用 start_routine
5. 等待线程完成
6. 进行某种解密操作
7. 验证并输出flag
```

**第一个关键发现**: 程序使用6个线程处理输入，这很不寻常！

### 第二步：分析start_routine - 线程做了什么

#### 2.1 理解线程的基本逻辑

反编译`start_routine`函数：

```c
start_routine(void *a1) {
    thread_id = (int)a1;              // rbp = 线程ID (0-5)
    byte_offset = thread_id * 4;      // rbx = thread_id * 4
    
    usleep(useconds[thread_id]);      // 随机延迟
    pthread_mutex_lock(&mutex);        // 加锁
    
    // 关键：调用神秘函数
    sub_400E10(&input_buffer[byte_offset], 4, md5_result);
    
    // 比较结果
    if (md5_result == qword_602120[thread_id])
        output_buffer[global_index] = input_buffer[byte_offset];
    else
        output_buffer[global_index] = 0;
        
    global_index++;
    pthread_mutex_unlock(&mutex);
}
```

**关键观察**:
1. 每个线程处理输入的不同部分：`input_buffer[thread_id * 4]` 开始的4字节
2. 调用了一个神秘函数`sub_400E10`，参数是4字节数据
3. 将结果与`qword_602120[thread_id]`比较
4. 验证成功则将输入复制到`output_buffer (dword_602220 @ 0x602220)`

**第二个关键发现**: 这是某种哈希验证！但是什么哈希算法？

### 第三步：识别sub_400E10 - 这是MD5！

#### 3.1 函数特征分析

查看`sub_400E10`的代码，发现：

```c
- 输入填充逻辑：添加0x80，然后填0，最后8字节存长度
- 初始化常数：0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476
- 64轮迭代，使用不同的F/G/H/I函数
- 使用常数表 MD5_Constants_401320
- 输出16字节
```

**判断依据**:
1. **魔数匹配**: 初始常数`0x67452301`等是MD5的标准初始值
2. **算法结构**: 64轮迭代符合MD5特征
3. **输出长度**: 16字节正是MD5的输出长度

**确认**: `sub_400E10`就是MD5函数！

#### 3.2 验证哈希值的存储

查看内存`qword_602120`处的数据：

```
0x602120: 47 46 bb bd 02 bb 59 0f be ac 28 21 ec e8 fc 5c
0x602128: ad 74 92 65 ca 75 03 ef 43 86 b3 8f c1 2c 42 27
...
```

这些是预存的目标MD5哈希值（每个8字节，因为代码中比较的是`qword`）！

**第三个关键发现**: 程序验证每个4字节块的MD5哈希的前8字节！

### 第四步：暴力破解思路 - 4字节的可能性

#### 4.1 分析搜索空间的可行性

已知信息：
- 每个线程验证**4字节**数据的MD5
- 这是CTF题目，用户输入**大概率是可打印字符**
- 可打印ASCII范围：0x20-0x7E（共94个字符）

**关键判断**:
- 如果是完全随机的4字节：2^32 ≈ 42亿种可能 → **不可能暴力破解**
- 如果限制为可打印字符：94^4 ≈ 7800万种可能 → **有暴力破解的可能性！**

**第四个关键发现**: CTF题目的特点给了我们暴力破解的机会！

### 第五步：暴力破解实施 - 并行加速

#### 5.1 优化策略

既然确定可以暴力破解，那就：
1. 使用多核并行（16核）
2. 按长度递进搜索（1字符→2字符→3字符→4字符）
3. 早停策略：找到就立即返回

#### 5.2 实施暴力破解

```python
# 对每个位置并行搜索
for length in range(1, 5):
    for combo in itertools.product(charset, repeat=length):
        test_str = ''.join(combo)
        test_bytes = test_str.encode('ascii') + b'\x00' * (4 - length)
        if md5(test_bytes)[:8] == target_hash[pos]:
            return test_str
```

**结果**: **成功**！找到了所有6个块：

```
位置0: juhu (0x6a756875) - 测试了约840万次
位置1: hfen (0x6866656e) - 测试了约670万次  
位置2: laps (0x6c617073) - 测试了约990万次
位置3: iuer (0x69756572) - 测试了约770万次
位置4: hjif (0x686a6966) - 测试了约670万次
位置5: dunu (0x64756e75) - 测试了约350万次
```

**第四个关键发现**: 所有块都是4个小写字母！

### 第六步：解密尝试 - 遇到新问题

#### 6.1 分析解密逻辑

在main函数中找到解密代码：

```c
checksum = 0;
for (i = 0; i < strlen(input); i++)
    checksum ^= (input[i] + i);

for (i = 0; i < len(encrypted); i++)
    flag[i] = checksum ^ byte_6020DF[i] ^ byte_602220[i];
```

**关键变量**:
- `byte_6020DF @ 0x6020DF`: 加密的flag数据
- `byte_602220 @ 0x602220`: 线程输出缓冲区（即`output_buffer`）
- `checksum`: 从原始输入计算的校验和

#### 6.2 第一次解密尝试

```python
input_str = "juhuhfenlapsiuerhjifdunu"  # 按顺序拼接
checksum = calculate_checksum(input_str)  # 0xf3
flag = decrypt(encrypted, input_str, checksum)
# 结果: goodjobyougeytcnsflaj284
```

**问题**: 看起来像是"good job you get ... flag"，但后半部分不对！

#### 6.3 实际验证 - 失败！

将输入`juhuhfenlapsiuerhjifdunu`输入到程序：

```
> juhuhfenlapsiuerhjifdunu
Badluck! There is no flag
```

**震惊**: 为什么MD5都匹配了，结果却是错的？！

### 第七步：深入分析 - 发现真相

#### 7.1 重新审视输出逻辑

仔细看`start_routine`中的关键代码：

```c
global_index = dword_6021E8;  // 全局索引 @ 0x6021E8
output_offset = global_index * 4;

if (md5_matches)
    output_buffer[output_offset] = input_buffer[byte_offset];
    
global_index++;  // 索引递增
```

**关键理解**:
- 输出位置不是按线程ID，而是按**线程完成顺序**！
- `global_index`是共享的，每个线程完成后递增
- 由于有`usleep(random)`，线程完成顺序是**随机的**！

**第五个关键发现**: 输出顺序依赖于运行时的线程调度！

#### 7.2 推导问题本质

```
输入顺序(固定):    [juhu][hfen][laps][iuer][hjif][dunu]
                    位置0  位置1  位置2  位置3  位置4  位置5

线程完成顺序(随机): 假设是 0→1→2→5→4→3

输出缓冲区:        [juhu][hfen][laps][dunu][hjif][iuer]
                   输出0  输出1  输出2  输出3  输出4  输出5
```

解密时使用的是**输出缓冲区**的内容，而非原始输入！

**这就是为什么直接解密失败的原因！**

### 第八步：穷举排列 - 找到答案

#### 8.1 排列组合策略

既然不知道线程完成顺序，那就穷举所有可能：

```python
# 6个线程有 6! = 720 种完成顺序
for perm in itertools.permutations(range(6)):
    # 按这个顺序重排输出
    output = [blocks[perm[i]] for i in range(6)]
    
    # 解密
    flag = decrypt(output, checksum)
    
    # 验证合法性
    if is_valid(flag):
        print(flag)
```

#### 8.2 合法性验证

程序中的验证代码：

```c
// 检查flag的每个字符
for (i = 0; i < len; i++) {
    ch = flag[i] - 0x30;  // 减去'0'
    if (ch > 0x4A)        // 如果大于'J'的ASCII值差
        goto FAIL;
}
```

**验证规则**: 字符必须在`0x30-0x7a`范围内（即'0'-'z'），但排除`0x3a-0x40`和`0x5b-0x60`。

实际上就是：**只允许数字、大小写字母**。

#### 8.3 结果分析

穷举720种排列后，发现32种产生合法flag，其中：

```
排列6: (0,1,2,5,4,3) → goodjobyougetthisflag233 ✓✓✓
```

**这就是答案！** "good job you get this flag 233"

### 第九步：验证和总结

#### 9.1 最终验证

```
输入(原始顺序): juhuhfenlapsiuerhjifdunu
线程完成顺序:   0 → 1 → 2 → 5 → 4 → 3
输出缓冲区内容: juhuhfenlapsdunuhjifiuer
Checksum: 0xf3
解密结果: goodjobyougetthisflag233
```

**验证**: 将任何一次运行中线程完成顺序为(0,1,2,5,4,3)的输入都会得到正确flag。

#### 9.2 为什么其他排列也有效？

有32个有效flag是因为：
- 不同的线程完成顺序
- 导致不同的输出排列
- 只要解密后的字符都是合法的，就通过验证
- 但语义正确的只有`goodjobyougetthisflag233`

---

## 错误路径总结

在解题过程中走过的弯路：

### 错误1: 忽视多线程的随机性
**错误想法**: 认为线程按ID顺序执行
**教训**: 多线程程序的执行顺序是不确定的，特别是有随机延迟时

### 错误2: 单字符搜索
**错误想法**: 认为4字节块就是1个字符+null
**教训**: 不要对搜索空间做过度假设，需要扩大范围

### 错误3: 直接使用输入解密
**错误想法**: 解密时使用原始输入`input_buffer`
**真相**: 应该使用线程输出`output_buffer`，因为代码中明确写的是`byte_602220`

### 错误4: 忽视程序的验证逻辑
**错误想法**: 解密出来就是flag
**真相**: 程序还会验证字符合法性，这帮助我们筛选正确答案

---

## 程序核心机制详解

### 内存布局

```
输入缓冲区 (input_buffer @ 0x602180):
  [0-3]   [4-7]   [8-11]  [12-15] [16-19] [20-23]
  线程0   线程1   线程2   线程3   线程4   线程5

目标哈希 (qword_602120):
  [0]     [8]     [16]    [24]    [32]    [40]
  哈希0   哈希1   哈希2   哈希3   哈希4   哈希5

输出缓冲区 (output_buffer @ 0x602220):
  由线程按完成顺序填充

加密数据 (byte_6020DF @ 0x6020DF):
  存储加密的flag，24字节
```

### 执行流程图

```
用户输入 → input_buffer (0x602180)
    ↓
创建6个线程
    ↓
┌───┴───┬───────┬───────┬───────┬───────┐
↓       ↓       ↓       ↓       ↓       ↓
线程0   线程1   线程2   线程3   线程4   线程5
usleep  usleep  usleep  usleep  usleep  usleep
  ↓       ↓       ↓       ↓       ↓       ↓
MD5     MD5     MD5     MD5     MD5     MD5
[0:4]   [4:8]   [8:12]  [12:16] [16:20] [20:24]
  ↓       ↓       ↓       ↓       ↓       ↓
比较    比较    比较    比较    比较    比较
qword   qword   qword   qword   qword   qword
602120  602128  602130  602138  602140  602148
  ↓       ↓       ↓       ↓       ↓       ↓
写入output_buffer (按完成顺序)
└───┬───┴───────┴───────┴───────┴───────┘
    ↓
计算checksum (从input_buffer)
    ↓
解密: flag[i] = checksum ^ byte_6020DF[i] ^ output_buffer[i]
    ↓
验证flag字符合法性
    ↓
输出结果
```

---

## 技术总结

### 核心技术点

1. **MD5哈希识别与破解**
   - 通过特征码识别MD5算法
   - 利用搜索空间小的特点暴力破解
   - 多核并行加速（16核，总耗时约2分钟）

2. **多线程逆向分析**
   - 理解互斥锁的作用
   - 识别全局共享变量（`dword_6021E8 @ 0x6021E8`）
   - 认识到线程执行顺序的不确定性

3. **XOR加密分析**
   - 三层XOR: `encrypted ^ checksum ^ output`
   - Checksum计算: `XOR(input[i] + i)`
   - 理解加密和解密使用不同的数据源

4. **排列组合**
   - 穷举6! = 720种可能
   - 利用程序的验证逻辑筛选答案
   - 从语义角度判断正确性

### 难点突破

1. **线程顺序的不确定性** ⭐⭐⭐⭐⭐
   - 最大难点：意识到输出顺序不固定
   - 突破方法：穷举所有排列组合

2. **MD5搜索空间** ⭐⭐⭐⭐
   - 难点：4字节 = 2^32种可能
   - 突破方法：限制为可打印字符，并行加速

3. **解密数据源混淆** ⭐⭐⭐⭐
   - 难点：分不清用input还是output
   - 突破方法：仔细阅读汇编代码中的内存地址

4. **随机化混淆** ⭐⭐⭐
   - 难点：随机延迟制造的干扰
   - 突破方法：认识到本质还是确定性问题

### 学到的经验

1. **细节决定成败**
   - 内存地址的区别：`0x602180` vs `0x602220`
   - 一个地址错误导致完全不同的结果

2. **不要被表象迷惑**
   - 随机延迟看似增加了不确定性
   - 但通过穷举可以覆盖所有情况

3. **分步解题**
   - 先解决确定的部分（MD5破解）
   - 再处理不确定的部分（顺序问题）

4. **程序验证是线索**
   - 字符合法性检查帮助筛选答案
   - 32个有效flag中，语义明确的只有1个

---

## 解题脚本使用

### 统一解题脚本 (solve.py) - 推荐

```bash
# 完整运行（推荐）
python solve.py

# 只运行阶段1（MD5暴力破解）
python solve.py --phase 1

# 只运行阶段2（排列测试）
python solve.py --phase 2

# 安静模式
python solve.py --quiet

# 显示所有32个有效flag
python solve.py --show-all
```

---

## 最终答案

### 输入
```
juhuhfenlapsiuerhjifdunu
```

### Flag
```
goodjobyougetthisflag233
```

### 关键数据

```
线程0: input[0:4]   = juhu → MD5前8字节 = 0x0f59bb02bdbb4647
线程1: input[4:8]   = hfen → MD5前8字节 = 0x5cfce8ec2128acbe
线程2: input[8:12]  = laps → MD5前8字节 = 0xef0375ca659274ad
线程3: input[12:16] = iuer → MD5前8字节 = 0x27422cc18fb38643
线程4: input[16:20] = hjif → MD5前8字节 = 0xa72deca745cc3eb0
线程5: input[20:24] = dunu → MD5前8字节 = 0xe8341712fe5f3cbe

线程完成顺序: 0 → 1 → 2 → 5 → 4 → 3
输出缓冲区:   juhuhfenlapsdunuhjifiuer
Checksum:     0xf3
```

---

## 工具和环境

- **IDA Pro 7.x**: 静态分析和反编译
- **IDA MCP Server**: 从IDA中提取数据和分析
- **Python 3.8+**: 编写破解脚本
- **多核CPU**: 加速暴力破解（推荐8核以上）

---

## 作者注

这道题的设计非常精妙，它不仅考察逆向分析能力，还考察对并发编程、密码学和问题解决能力的综合运用。

最关键的突破点有两个：
1. **识别MD5算法** - 需要对常见加密算法有足够的了解
2. **认识线程顺序不确定性** - 这是最容易被忽视的点

解题过程中走了不少弯路，但这些错误尝试都是学习的一部分。真正的CTF解题往往就是在不断试错中找到正确路径。

希望这份详细的解题报告能帮助你理解整个思路过程，而不仅仅是看到最终答案。**思路比答案更重要！**

---

## 文件清单

### 主要文件
- `README.md` - 完整解题报告（本文档）
- `solve.py` - 统一解题脚本（推荐）
- `brute_force_solve.py` - MD5暴力破解脚本
- `try_all_permutations.py` - 排列组合测试脚本

### 分析文档
- `题目分析.md` - 详细的程序分析
- `start_routine函数分析.md` - 线程函数详解
- `解题结果.md` - 解题结果记录

### 辅助脚本
- `verify_md5.py` - MD5验证脚本
- `analyze_flag.py` - Flag分析脚本
# Syclover CTF - 完整程序逻辑分析

根据完整的trace (1005行)，我已经重建了整个程序的执行流程。

## 程序执行流程概览

```
[scanf输入] → [加密输入] → [对比密钥] → [失败输出error] → [退出]
```

## 详细执行阶段

### 阶段1: 输入读取 (Lines 1-329)

```c
char input[32];  // 栈上 0xFF9AB33F
scanf("%s", input);
// 用户输入: "111" (0x31, 0x31, 0x31, 0x00)
```

**关键地址**:
- 输入缓冲区: `0xFF9AB33F`
- 读取了3个字符 '1' (0x31) + 换行符

### 阶段2: 输入加密处理 (Lines 330-510)

**函数**: `0x0804848F` - 加密函数

#### 加密算法分析 (Lines 355-510)

```c
for (int i = 0; input[i] != '\0'; i++) {
    char c = input[i];  // 例如: 0x31 ('1')
    
    // 步骤1: 根据位置计算移位量
    int shift_right = i % 8;  // i=0 -> 0, i=1 -> 1, i=2 -> 2
    int shift_left = 8 - shift_right;
    
    // 步骤2: 分两部分处理
    int part1 = (c >> shift_right);  // 右移
    int part2 = (c << shift_left);   // 左移
    
    // 步骤3: 合并并XOR位置
    int encrypted = (part1 | part2) ^ i;
    
    input[i] = (char)encrypted;
}
```

**具体例子**:
```
输入: "111" (0x31, 0x31, 0x31)

i=0: 0x31
  part1 = 0x31 >> 0 = 0x31
  part2 = 0x31 << 8 = 0x3100
  merged = 0x31 | 0x3100 = 0x3131
  encrypted = 0x3131 ^ 0 = 0x3131 (取低字节 0x31)

i=1: 0x31
  part1 = 0x31 >> 1 = 0x18
  part2 = 0x31 << 7 = 0x1880
  merged = 0x18 | 0x1880 = 0x1898
  encrypted = 0x1898 ^ 1 = 0x1899 (取低字节 0x99)

i=2: 0x31
  part1 = 0x31 >> 2 = 0x0C
  part2 = 0x31 << 6 = 0x0C40
  merged = 0x0C | 0x0C40 = 0x0C4C
  encrypted = 0x0C4C ^ 2 = 0x0C4E (取低字节 0x4E)

加密结果: 0x31, 0x99, 0x4E, 0x00
```

**Trace中的证据**:
- Line 399: `mov [ebx], al` - 写入 0x31 到 0xFF9AB33F
- Line 450: `mov [ebx], al` - 写入 0x99 到 0xFF9AB340  
- Line 501: `mov [ebx], al` - 写入 0x4E 到 0xFF9AB341

### 阶段3: 密钥生成 (Lines 512-949)

**函数**: `0x08048583` - 密钥对比函数

#### 初始化 (Lines 525-577)

```c
char error_msg[] = "error\n";  // 0xFF9AB2A6: "error\n"
char right_msg[] = "right\n";  // 0xFF9AB2A0: "right\n"
char key[32];  // 栈上 0xFF9AB2AC
```

#### 从硬编码数据生成密钥 (Lines 583-949)

**硬编码数据地址**: `0x080499EC`

**数据内容**:
```
0x080499EC: 0x73 = 's'
0x080499ED: 0x8D = ''
0x080499EE: 0xF2 = ''
0x080499EF: 0x4C = 'L'
0x080499F0: 0xC7 = ''
0x080499F1: 0xD4 = ''
0x080499F2: 0x7B = '{'
0x080499F3: 0xF7 = ''
0x080499F4: 0x18 = ''
0x080499F5: 0x32 = '2'
0x080499F6: 0x71 = 'q'
0x080499F7: 0x0D = '\r'
0x080499F8: 0xCF = ''
0x080499F9: 0xDC = ''
0x080499FA: 0x67 = 'g'
0x080499FB: 0x4F = 'O'
0x080499FC: 0x7F = ''
0x080499FD: 0x0B = ''
0x080499FE: 0x6D = 'm'
0x080499FF: 0x00 (结束)
```

**密钥生成算法** (Lines 589-949):
```c
for (int i = 0; data[i] != '\0'; i++) {
    key[i] = data[i] ^ 0x20;  // XOR 0x20
}
```

**生成的密钥**:
```
key[0] = 0x73 ^ 0x20 = 0x53 = 'S'
key[1] = 0x8D ^ 0x20 = 0xAD = ''
key[2] = 0xF2 ^ 0x20 = 0xD2 = ''
key[3] = 0x4C ^ 0x20 = 0x6C = 'l'
key[4] = 0xC7 ^ 0x20 = 0xE7 = ''
key[5] = 0xD4 ^ 0x20 = 0xF4 = ''
key[6] = 0x7B ^ 0x20 = 0x5B = '['
key[7] = 0xF7 ^ 0x20 = 0xD7 = ''
key[8] = 0x18 ^ 0x20 = 0x38 = '8'
key[9] = 0x32 ^ 0x20 = 0x12 = ''
key[10] = 0x71 ^ 0x20 = 0x51 = 'Q'
key[11] = 0x0D ^ 0x20 = 0x2D = '-'
key[12] = 0xCF ^ 0x20 = 0xEF = ''
key[13] = 0xDC ^ 0x20 = 0xFC = ''
key[14] = 0x67 ^ 0x20 = 0x47 = 'G'
key[15] = 0x4F ^ 0x20 = 0x6F = 'o'
key[16] = 0x7F ^ 0x20 = 0x5F = '_'
key[17] = 0x0B ^ 0x20 = 0x2B = '+'
key[18] = 0x6D ^ 0x20 = 0x4D = 'M'
```

**Trace证据**:
- Line 593-598: 第一个字符处理 -> 0x53 写入 0xFF9AB2AC
- Line 607-617: 第二个字符处理 -> 0xAD 写入 0xFF9AB2AD
- ...依此类推

### 阶段4: 对比验证 (Lines 950-977)

```c
// Line 952-961: 对比第一个字符
encrypted_input[0] = 0x31  // 加密后的输入
key[0] = 0x53              // 密钥
if (encrypted_input[0] != key[0]) {
    // 不匹配！
    goto print_error;
}
```

**结果**: `0x31 != 0x53` → 失败！

### 阶段5: 输出错误信息 (Lines 978-986)

```c
// Line 978-982: sys_write系统调用
write(1, "error\n", 6);  // 输出到stdout
```

**系统调用**:
- EAX = 4 (sys_write)
- EBX = 1 (stdout)
- ECX = 0xFF9AB2A6 ("error\n"的地址)
- EDX = 6 (长度)

### 阶段6: 程序退出 (Lines 987-1005)

清理栈帧并返回

## 完整的C伪代码

```c
#include <stdio.h>
#include <string.h>

// 加密函数
void encrypt_input(char *input) {
    for (int i = 0; input[i] != '\0'; i++) {
        unsigned char c = input[i];
        int shift_right = i % 8;
        int shift_left = 8 - shift_right;
        
        unsigned int part1 = c >> shift_right;
        unsigned int part2 = (c << shift_left) & 0xFF00;
        unsigned int merged = part1 | part2;
        unsigned int encrypted = (merged ^ i) & 0xFF;
        
        input[i] = (char)encrypted;
    }
}

// 生成密钥
void generate_key(char *key) {
    // 硬编码的数据
    unsigned char data[] = {
        0x73, 0x8D, 0xF2, 0x4C, 0xC7, 0xD4, 0x7B, 0xF7,
        0x18, 0x32, 0x71, 0x0D, 0xCF, 0xDC, 0x67, 0x4F,
        0x7F, 0x0B, 0x6D, 0x00
    };
    
    for (int i = 0; data[i] != '\0'; i++) {
        key[i] = data[i] ^ 0x20;
    }
    key[strlen((char*)data)] = '\0';
}

int main() {
    char input[32];
    char key[32];
    
    // 读取输入
    scanf("%s", input);
    
    // 加密输入
    encrypt_input(input);
    
    // 生成密钥
    generate_key(key);
    
    // 对比
    if (strcmp(input, key) == 0) {
        printf("right\n");
    } else {
        printf("error\n");
    }
    
    return 0;
}
```

## 如何获取Flag

### 方法1: 反向解密密钥

已知密钥的加密值，需要反向解密：

```python
# 密钥 (加密后应该匹配这个)
key = [0x53, 0xAD, 0xD2, 0x6C, 0xE7, 0xF4, 0x5B, 0xD7,
       0x38, 0x12, 0x51, 0x2D, 0xEF, 0xFC, 0x47, 0x6F,
       0x5F, 0x2B, 0x4D]

def decrypt_to_input(encrypted, pos):
    """反向解密：从加密值和位置计算原始输入"""
    # encrypted = ((c >> shift_right) | (c << shift_left)) ^ pos
    # 先XOR回去
    merged = encrypted ^ pos
    
    shift_right = pos % 8
    shift_left = 8 - shift_right
    
    # 尝试所有可能的字节
    for c in range(256):
        part1 = c >> shift_right
        part2 = (c << shift_left) & 0xFF00
        test_merged = (part1 | part2) & 0xFFFF
        
        if (test_merged & 0xFF) == merged:
            return chr(c)
    
    return None

# 解密密钥获得原始输入
flag = ""
for i, enc in enumerate(key):
    char = decrypt_to_input(enc, i)
    if char:
        flag += char
    else:
        break

print("Flag input:", flag)
```

### 方法2: 直接从硬编码数据推导

硬编码数据 XOR 0x20 后是密钥，那么原始的flag应该是什么能加密成这个密钥？

让我创建解密脚本...
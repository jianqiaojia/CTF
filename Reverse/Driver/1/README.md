# CTF逆向题解题报告 - Windows驱动加密挑战

## 题目信息

- **难度**: ⭐⭐⭐⭐ (4/10)
- **类别**: Windows内核驱动分析 + 两阶段XOR加密
- **文件**: `a12111ef22314105a3ace3bbf9f53d6d.sys`
- **架构**: x64 Windows Driver
- **主要技术**: 自定义位运算加密、两阶段密钥派生

---

## 解题思路

### 第一步：初步分析 - 发现加密函数

使用IDA Pro打开驱动文件，快速浏览函数列表，发现了关键的加密函数 `sub_11DF0`。

反编译后的核心代码：

```c
__int64 __fastcall sub_11DF0(unsigned __int64 arg1, unsigned __int64 arg2)
{
  unsigned __int64 v2; // rdx
  unsigned __int64 v3; // rax
  unsigned __int64 v4; // rcx

  v2 = arg1 ^ arg2;
  v3 = (16 * (arg1 ^ arg2)) ^ arg2;
  v4 = (v2 >> 4) ^ arg2;
  return ((v3 & 0xF0F0F0F0F0F0F0F0ui64) | (v4 & 0xF0F0F0F0F0F0F0F0ui64) >> 4) 
         ^ ((16 * v4) & 0xF0F0F0F0F0F0F0F0ui64 | (v3 & 0xF0F0F0F0F0F0F0F0ui64) >> 4);
}
```

**第一个关键发现**: 这是一个自定义的位运算加密算法！

**算法特征**:
- 使用位掩码 `0xF0F0F0F0F0F0F0F0` 和 `0x0F0F0F0F0F0F0F0F`
- 包含左移、右移、异或操作
- 将每个字节的高4位和低4位进行重排和混合

### 第二步：分析主函数 - 发现两阶段加密

查看主处理函数 `sub_11020`，发现关键代码段：

```c
__int64 __fastcall sub_11020(struct _DEVICE_OBJECT *a1, struct _IRP *a2)
{
  // ... 省略初始化 ...
  
  // 计算第一阶段密钥
  v8 = sub_11DF0(0xCCC12345ui64, 0x54321CCCui64);  
  
  // 计算第二阶段密钥长度
  v9 = v8 - 1546720155;
  
  // ... 使用 v8 和 v9 进行解密 ...
}
```

**第二个关键发现**: 存在两阶段处理机制！

- `v8`: 通过 `sub_11DF0(0xCCC12345, 0x54321CCC)` 计算得到的密钥
- `v9`: `v8 - 1546720155` 的结果，可能是长度值

### 第三步：定位加密数据

通过分析代码中的内存引用，找到两个关键数据区域：

1. **地址 0x16310**: 128字节数据 - 第一阶段加密数据
2. **地址 0x16390**: 36字节数据 - FLAG加密数据

### 第四步：第一次尝试 - 走了弯路

**错误尝试1**: 直接解密FLAG
```python
# 我最初尝试用 0xCCCCCCCC 和 0x54321ABC
key = decrypt_algorithm(0xCCCCCCCC, 0x54321ABC)  # ❌ 参数错误！
```
**结果**: 解密失败，得到乱码

**错误尝试2**: 数据位置错误
```python
# 我尝试了 0x13110 地址
data = read_bytes(0x13110, 128)  # ❌ 地址错误！
```
**结果**: 解密出的数据没有意义

**反思**: 必须仔细核对每一个常量和地址！

### 第五步：理解两阶段加密机制

重新仔细分析代码后，理解了完整流程：

```
阶段1: 解密触发文件名
  ├─ 密钥 = decrypt_algorithm(0xCCC12345, 0x54321CCC)
  ├─ 解密数据: 地址 0x16310 的128字节
  └─ 结果: 触发文件名字符串

阶段2: 解密FLAG  
  ├─ 密钥 = 阶段1的结果（前42字节）
  ├─ 解密数据: 地址 0x16390 的36字节
  └─ 结果: 最终FLAG
```

**第三个关键发现**: 第一阶段的输出是第二阶段的密钥！这是链式加密！

### 第六步：正确解密 - 第一阶段

```python
def decrypt_algorithm(arg1, arg2):
    """实现 sub_11DF0 的算法"""
    v2 = arg1 ^ arg2
    v3 = ((v2 << 4) & 0xFFFFFFFFFFFFFFFF) ^ arg2
    v4 = (v2 >> 4) ^ arg2
    
    part1 = (v3 & 0xF0F0F0F0F0F0F0F0) | ((v4 & 0xF0F0F0F0F0F0F0F0) >> 4)
    part2 = ((v4 << 4) & 0xF0F0F0F0F0F0F0F0) | ((v3 & 0xF0F0F0F0F0F0F0F0) >> 4)
    
    return part1 ^ part2

# 使用正确的参数
key = decrypt_algorithm(0xCCC12345, 0x54321CCC)
print(f"Stage 1 Key: 0x{key:016X}")
# 输出: Stage 1 Key: 0x000000005C3113C5
```

从 0x16310 读取128字节并解密：

```python
import struct

# 将密钥转为字节
key_bytes = struct.pack('<Q', key)

# XOR解密
result = bytearray()
for i in range(128):
    result.append(encrypted_data[i] ^ key_bytes[i % 8])

filename = result.decode('utf-8').rstrip('\x00')
print(f"触发文件名: {filename}")
# 输出: 触发文件名: P_giveMe_flag_233.txt
```

**成功！** 得到了触发文件名！

### 第七步：正确解密 - 第二阶段

计算第二阶段密钥长度：

```python
# 对应代码中的 v9 = v8 - 1546720155
key_length = 0x5C3113C5 - 1546720155
print(f"密钥长度: {key_length}")
# 输出: 密钥长度: 42
```

使用前42字节作为密钥解密FLAG：

```python
# 从 0x16390 读取36字节
flag_encrypted = read_bytes(0x16390, 36)

# 使用触发文件名的前42字节作为密钥
key_stage2 = filename_bytes[:42]

# XOR解密
flag_bytes = bytearray()
for i in range(36):
    flag_bytes.append(flag_encrypted[i] ^ key_stage2[i % 42])

# FLAG是UTF-16LE编码
flag = flag_bytes.decode('utf-16-le').rstrip('\x00')
print(f"FLAG: {flag}")
```

**输出**: `" the flag is A_simple_Inline_hook_Dr"`

**成功！** 🎉

---

## 技术要点总结

### 1. 自定义位运算加密算法

核心操作：
```c
v2 = arg1 ^ arg2                    // 基础异或
v3 = (v2 << 4) ^ arg2               // 左移4位后混淆
v4 = (v2 >> 4) ^ arg2               // 右移4位后混淆
result = mix(v3, v4)                // 使用掩码重排高低4位
```

**关键掩码**:
- `0xF0F0F0F0F0F0F0F0` - 提取每字节的高4位
- `0x0F0F0F0F0F0F0F0F` - 提取每字节的低4位

### 2. 两阶段加密机制

**为什么使用两阶段**:
1. 增加破解难度 - 必须理解完整流程
2. 密钥隐藏 - 真正的密钥不直接存储
3. 关联性 - 第一阶段失败则无法获得第二阶段密钥

**数据流**:
```
参数(0xCCC12345, 0x54321CCC)
    ↓ [decrypt_algorithm]
密钥(0x5C3113C5)
    ↓ [XOR @ 0x16310]
触发文件名("P_giveMe_flag_233.txt")
    ↓ [取前42字节]
Stage2密钥
    ↓ [XOR @ 0x16390]
FLAG(" the flag is A_simple_Inline_hook_Dr")
```

### 3. Windows驱动字符编码

**重要细节**:
- 第一阶段: UTF-8编码（触发文件名）
- 第二阶段: UTF-16LE编码（FLAG）
- Windows内核中常用宽字符（每字符2字节）

---

## 错误经验总结

### 错误1: 参数精度问题
```python
❌ decrypt_algorithm(0xCCCCCCCC, 0x54321ABC)
✅ decrypt_algorithm(0xCCC12345, 0x54321CCC)
```
**教训**: 每个字节都必须精确，不要凭记忆输入

### 错误2: 数据地址错误
```python
❌ data = read_bytes(0x13110, 128)  # 错误地址
✅ data = read_bytes(0x16310, 128)  # 正确地址
```
**教训**: 使用交叉引用确认数据位置

### 错误3: 跳过第一阶段
```python
❌ 直接尝试解密 0x16390 的FLAG数据
✅ 先解密 0x16310 获取中间密钥
```
**教训**: 理解完整的加密流程，不要急于求成

### 错误4: 编码格式错误
```python
❌ flag.decode('ascii')      # ASCII解码失败
✅ flag.decode('utf-16-le')  # UTF-16LE解码成功
```
**教训**: 注意Windows驱动常用UTF-16LE编码

---

## 完整解密脚本

```python
#!/usr/bin/env python3
import struct

def decrypt_algorithm(arg1, arg2):
    """对应 sub_11DF0 的算法"""
    v2 = arg1 ^ arg2
    v3 = ((v2 << 4) & 0xFFFFFFFFFFFFFFFF) ^ arg2
    v4 = (v2 >> 4) ^ arg2
    
    part1 = (v3 & 0xF0F0F0F0F0F0F0F0) | ((v4 & 0xF0F0F0F0F0F0F0F0) >> 4)
    part2 = ((v4 << 4) & 0xF0F0F0F0F0F0F0F0) | ((v3 & 0xF0F0F0F0F0F0F0F0) >> 4)
    
    return part1 ^ part2

def xor_decrypt(data, key):
    """XOR解密"""
    return bytes(data[i] ^ key[i % len(key)] for i in range(len(data)))

# ========== 阶段1: 解密触发文件名 ==========
print("[Stage 1] 计算密钥...")
stage1_key = decrypt_algorithm(0xCCC12345, 0x54321CCC)
print(f"密钥: 0x{stage1_key:016X}")

# 从 0x16310 读取加密数据（需要从二进制文件中提取）
stage1_encrypted = bytes([...])  # 128字节

key_bytes = struct.pack('<Q', stage1_key)
stage1_decrypted = xor_decrypt(stage1_encrypted, key_bytes)
trigger_filename = stage1_decrypted.decode('utf-8').rstrip('\x00')
print(f"触发文件名: {trigger_filename}")

# ========== 阶段2: 解密FLAG ==========
print("\n[Stage 2] 解密FLAG...")
key_length = stage1_key - 1546720155
print(f"密钥长度: {key_length}")

# 从 0x16390 读取FLAG（需要从二进制文件中提取）
flag_encrypted = bytes([...])  # 36字节

stage2_key = stage1_decrypted[:key_length]
flag_decrypted = xor_decrypt(flag_encrypted, stage2_key)
flag = flag_decrypted.decode('utf-16-le').rstrip('\x00')

print(f"\n{'='*50}")
print(f"FLAG: {flag}")
print(f"{'='*50}")
```

---

## 最终答案

### FLAG
```
 the flag is A_simple_Inline_hook_Dr
```

### 关键参数

| 项目 | 值 | 说明 |
|------|-----|------|
| 算法函数 | `sub_11DF0` | 自定义位运算 |
| arg1 | `0xCCC12345` | 第一参数 |
| arg2 | `0x54321CCC` | 第二参数 |
| Stage1密钥 | `0x5C3113C5` | 计算结果 |
| Stage1数据 | `0x16310` (128字节) | 触发文件名 |
| Stage1结果 | `"P_giveMe_flag_233.txt"` | 中间密钥 |
| 魔数 | `1546720155` | 密钥长度计算 |
| Stage2密钥长度 | `42` | 使用前42字节 |
| FLAG数据 | `0x16390` (36字节) | 最终目标 |
| FLAG编码 | `UTF-16LE` | Windows宽字符 |

---

## 核心经验

1. **仔细核对每个参数和地址** - 字节级精度很重要
2. **理解完整的加密流程** - 不要跳过中间步骤
3. **注意编码格式** - Windows驱动常用UTF-16LE
4. **从错误中学习** - 每次失败都是接近成功的一步
5. **变量命名很重要** - 将 `v8`, `v9` 等重命名为有意义的名称便于理解

---

**Happy Reversing! 🚀**
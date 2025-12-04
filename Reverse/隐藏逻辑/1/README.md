# EasyRE CTF 题目完整解题报告

## 题目类型

- **来源**: 2019_Redhat
- **难度**: ⭐⭐⭐⭐⭐ (5/10)
- **类别**: : 隐藏逻辑型 / 析构函数反混淆题 (Constructor/Destructor Obfuscation)

这是一道典型的**隐藏逻辑反混淆题目**，核心考点是对ELF特殊段的理解。

### 常见逆向题型对比

| 题型 | 特征 | 代表技术 |
|------|------|----------|
| **迷宫类** | 路径搜索、图遍历 | DFS/BFS算法 |
| **VM虚拟机** | 自实现指令集、解释器 | 字节码、虚拟栈 |
| **花指令** | 垃圾代码、控制流混淆 | 无效跳转、SMC |
| **隐藏逻辑型** ⭐本题 | 利用特殊段/构造析构函数 | .init_array/.fini_array |
| **加壳/反调试** | 动态保护、检测 | 反调试、代码加密 |
| **算法还原** | 复杂数学运算 | 密码学、哈希 |

### 本题特点：隐藏逻辑型

**核心技巧**: 利用ELF的`.fini_array`段隐藏关键逻辑

- `.init_array`: 程序启动前执行的构造函数数组
- `.fini_array`: 程序退出时执行的析构函数数组
- 真正的flag生成代码隐藏在析构函数中，不在主逻辑流程里
- 容易被逆向分析者忽略，因为大多数人只关注main函数和主要控制流

**类似技术还包括**:
- `.init_array`中的隐藏初始化
- TLS回调函数（Windows平台）
- 静态构造函数（C++）
- `__attribute__((constructor/destructor))`

## 题目分析

这是一道多阶段反向工程CTF题目，包含三个验证阶段：

### 程序基本信息
- **文件名**: easyRE
- **基址**: 0x400000
- **MD5**: d3a4848e6baadd6f0ec2cb77bca24dfd
- **SHA256**: c1c1545de254a09d6affae0800b7385b037abd54095a8b1fe07bb8c2a9ad1800

## 解题思路

### 第一阶段：XOR解密 (地址: 0x4009C6)

主函数中的第一个验证：
```c
char v12[13] = "Iodl>Qnb(ocy";
v12[12] = 127;
char v13[4] = "y.i";
v13[3] = 127;
char v14[19] = "d`3w}wek9{iy=~yL@EC";

// 验证：input[i] ^ i == v12[i]
```

**解密方法**：对目标数组进行索引XOR
```python
arr = [73,111,100,108,62,81,110,98,40,111,99,121,127,121,46,105,127,
       100,96,51,119,125,119,101,107,57,123,105,121,61,126,121,76,64,69,67]

stage1_result = ''
for i in range(36):
    stage1_result += chr(arr[i] ^ i)
```

**第一个输入**: `Info:The first four chars are 'flag'`

### 第二阶段：Base64多重解码 (地址: 0x400E44)

程序将第二个输入进行10次Base64编码后，与预存的长字符串比较：
```
Vm0wd2VHUXhTWGhpUm1SWVYwZDRWVll3Wkc5WFJsbDNXa1pPVlUxV2NIcFhhMk0xVmpKS1NHVkdXbFpOYmtKVVZtcEtTMUl5VGtsaVJtUk9ZV3hhZVZadGVHdFRNVTVYVW01T2FGSnRVbGhhVjNoaFZWWmtWMXBFVWxSTmJFcElWbTAxVDJGV1NuTlhia0pXWWxob1dGUnJXbXRXTVZaeVdrWm9hVlpyV1hwV1IzaGhXVmRHVjFOdVVsWmlhMHBZV1ZSR1lWZEdVbFZTYlhSWFRWWndNRlZ0TVc5VWJGcFZWbXR3VjJKSFVYZFdha1pXWlZaT2NtRkhhRk5pVjJoWVYxZDBhMVV3TlhOalJscFlZbGhTY1ZsclduZGxiR1J5VmxSR1ZXSlZjRWhaTUZKaFZqSktWVkZZYUZkV1JWcFlWV3BHYTFkWFRrZFRiV3hvVFVoQ1dsWXhaRFJpTWtsM1RVaG9hbEpYYUhOVmJUVkRZekZhY1ZKcmRGTk5Wa3A2VjJ0U1ExWlhTbFpqUldoYVRVWndkbFpxUmtwbGJVWklZVVprYUdFeGNHOVhXSEJIWkRGS2RGSnJhR2hTYXpWdlZGVm9RMlJzV25STldHUlZUVlpXTlZadE5VOVdiVXBJVld4c1dtSllUWGhXTUZwell6RmFkRkpzVWxOaVNFSktWa1phVTFFeFduUlRhMlJxVWxad1YxWnRlRXRXTVZaSFVsUnNVVlZVTURrPQ==
```

**解密方法**：对base64字符串进行10次解码
```python
import base64
result = encoded
for i in range(10):
    result = base64.b64decode(result).decode('utf-8')
```

**第二个输入**: `https://bbs.pediy.com/thread-254172.htm`

### 第三阶段：隐藏的Flag生成 (地址: 0x400D35)

**关键发现**：真正的flag不在主验证逻辑中，而是在`.fini_array`段的析构函数中生成！

该函数在程序退出时自动执行：
1. 使用复杂的随机数生成算法（1234次迭代）生成4字节密钥
2. 使用该密钥对地址`0x6CC0A0`处的25字节数据进行XOR解密
3. 输出真正的flag

**加密数据**（地址 0x6CC0A0）:
```
0x40 0x35 0x20 0x56 0x5d 0x18 0x22 0x45 0x17 0x2f 0x24 0x6e 0x62 0x3c 0x27 
0x54 0x48 0x6c 0x24 0x6e 0x72 0x3c 0x32 0x45 0x5b
```

**解密方法**：
- 第一个提示告诉我们flag前4个字符是'flag'
- 使用已知前缀反推4字节密钥: `'&YA1'`
- 用该密钥循环XOR解密完整数据

```python
enc = [0x40,0x35,0x20,0x56,0x5D,0x18,0x22,0x45,0x17,0x2F,0x24,0x6E,0x62,0x3C,
       0x27,0x54,0x48,0x6C,0x24,0x6E,0x72,0x3C,0x32,0x45,0x5B]

known_prefix = 'flag'
key = ''
for i in range(4):
    key += chr(enc[i] ^ ord(known_prefix[i]))

final_flag = ''
for i in range(len(enc)):
    final_flag += chr(enc[i] ^ ord(key[i % 4]))
```

## 最终答案

🎯 **Flag**: `flag{Act1ve_Defen5e_Test}`

## 解题要点

1. **多阶段验证**：不要被表面的验证逻辑迷惑
2. **隐藏逻辑**：检查`.fini_array`等特殊段中的析构函数
3. **信息利用**：第一阶段的提示是解第三阶段的关键
4. **密钥反推**：利用已知明文攻击推导密钥

## 题目巧妙之处

- 使用析构函数隐藏真正的flag生成逻辑
- 多次base64编码增加分析难度
- 前后阶段相互关联，形成完整的解题链
- 混淆真假验证，误导逆向分析

## 工具使用

- IDA Pro（反汇编与反编译）
- Python（编写解题脚本）
- MCP IDA工具（自动化分析）
# Edge CTF 2025 - foreign-affair 完整解题报告

## 题目信息

- **来源**: Edge CTF 2025
- **难度**: ⭐⭐⭐⭐⭐⭐ (6/10)
- **方向**: Reverse (逆向工程)
- **类别**: FFI漏洞利用 (Foreign Function Interface) + 信号处理 (Signal Handler) + 编码攻击 (Encoding Attack)
- **二进制文件**: `chall` (MD5: `e61e62e6c15464a7f7d48e3aef931048`)
- **架构**: x86-64 Linux ELF
- **主要技术**: C++/Rust混合编程、UTF-8验证绕过、SIGABRT信号劫持、字符串反转

## 题目概述

这是一道非常有趣的**C++和Rust混合编程**（FFI）逆向题目。程序通过cxxbridge实现C++和Rust的互操作，表面上看需要输入正确的字符串来获取flag，但实际的突破口在于利用**FFI边界的UTF-8验证机制**触发panic，进而劫持SIGABRT信号处理器来调用隐藏的`stuff()`函数。

题目名称"foreign-affair"暗示了这是关于"外来事务"（Foreign Function Interface）的题目，flag的内容`Never trust words of foreign origins!`（永远不要相信外来的话！）也完美呼应了FFI安全问题的主题。

---

## 解题思路全过程

### 第一步：初步分析 - 程序结构概览

#### 1.1 使用IDA打开二进制文件

首先用IDA Pro打开二进制文件，查看主要函数结构：

```
Functions窗口中看到的关键函数：
- main (0x1b0f0)
- edge_ctf_2025_rustffi::main (0x1b0c0)
- start (0x1cb96) - C++函数
- edge_ctf_2025_rustffi::flag (0x1afa0) - Rust函数
- edge_ctf_2025_rustffi::stuff (0x1ae80) - Rust函数
- handler (0x1c883) - 信号处理器
```

**第一个关键观察**：
- 有两个Rust函数：`flag()`和`stuff()`
- 有一个信号处理器`handler()`
- C++和Rust混合编程（通过cxxbridge）

#### 1.2 分析程序流程

在IDA中按F5反编译`main`函数（0x1b0f0）：

```c
int __fastcall main(int argc, const char **argv, const char **envp)
{
  return std::rt::lang_start::h75208bee92c36e08(
    edge_ctf_2025_rustffi::main::ha8775d12630c7802, 
    argc, 
    (u8 **)argv, 
    0);
}
```

继续查看Rust的main函数（0x1b0c0）：

```c
void __cdecl edge_ctf_2025_rustffi::main::ha8775d12630c7802()
{
  core::fmt::Arguments_0 v0; // [rsp+8h] [rbp-30h] BYREF
  
  // 打印提示信息
  core::fmt::rt::_$LT$impl$u20$core..fmt..Arguments$GT$::new_const::h9876e42c1d4ce572(
    &v0, 
    (_str (*)[1])off_60DC8);
  std::io::stdio::_print::h87d04f1826f04caf();
  
  // 调用start函数
  edge_ctf_2025_rustffi::ffi::start::he65b2d9ad2b3f40f();
}
```

**关键发现**：主函数调用了`ffi::start`，这是FFI的入口点。

### 第二步：分析start函数 - 核心逻辑

#### 2.1 理解start函数的控制流

在IDA中反编译`start()`函数（0x1cb96），代码较长，关键部分：

```c
int __cdecl start()
{
  std::string s;              // [rsp+0h] [rbp-A0h]
  std::string partial;        // [rsp+20h] [rbp-80h]
  std::string gate;           // [rsp+40h] [rbp-60h]
  rust::cxxbridge1::String p_arg0; // [rsp+70h] [rbp-30h]
  
  // 注册SIGABRT信号处理器！
  signal(6, (__sighandler_t)handler);
  
  // 初始化gate字符串为"NOCXXEXCEPTIONS"
  std::string::basic_string(&gate, "NOCXXEXCEPTIONS", &__a);
  std::string::basic_string(&s);
  
  // 循环读取输入
  while ( 1 )
  {
    // 读取一行输入到字符串s
    std::getline<char,std::char_traits<char>,std::allocator<char>>(&std::cin, &s);
    if ( !std::ios::operator bool(...) )
      break;
      
    // 反转字符串s
    std::reverse<__gnu_cxx::__normal_iterator<...>>(...);
    
    // 提取前15个字符到partial
    v2 = std::string::size(&gate);  // v2 = 15
    std::string::substr(&partial, &s, 0LL, v2);
    
    // 比较partial和gate
    if ( std::operator==<char>(&partial, &gate) )
    {
      // 匹配成功，调用flag函数
      rust::cxxbridge1::String::String(&p_arg0, &s);
      flag(&p_arg0);
      rust::cxxbridge1::String::~String(&p_arg0);
    }
    else
    {
      // 不匹配，输出"NO :("
      std::operator<<<std::char_traits<char>>(&std::cout, "NO :(");
      std::ostream::operator<<(..., &std::endl<char,std::char_traits<char>>);
    }
    
    std::ostream::flush((std::ostream *)&std::cout);
    std::string::~string(&partial);
  }
  
  return 0;
}
```

**第一个关键发现**：
1. 程序注册了**SIGABRT**（信号6）的处理器`handler`
2. 主循环读取输入，**反转字符串**，检查前15个字符是否等于"NOCXXEXCEPTIONS"
3. 如果匹配，调用`flag()`函数；否则输出"NO :("

#### 2.2 第一次尝试

根据分析，我们需要输入的字符串反转后前15个字符是"NOCXXEXCEPTIONS"：

```
"NOCXXEXCEPTIONS"的反转 = "SNOITPECXEXXCON"
```

编写Python脚本测试：

```python
import socket

host = "foreign-affair.chall.edgesecurity.team"
port = 1338

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host, port))

welcome = s.recv(4096)
print(welcome.decode())  # "TRY!"

s.sendall(b"SNOITPECXEXXCON\n")
response = s.recv(4096)
print(response.decode())  # "NotYetFlag{You_are_getting_closer}"
```

**结果**：得到提示`NotYetFlag{You_are_getting_closer}`，说明方向对了，但还不是真正的flag！

### 第三步：分析flag和stuff函数 - 发现隐藏函数

#### 3.1 反编译flag函数

在IDA中查看`flag()`函数（0x1afa0）：

```c
void __fastcall edge_ctf_2025_rustffi::flag::hf4fd4be8ed93601d(alloc::string::String *a1)
{
  _str v1;
  alloc::string::String v2;
  core::result::Result<alloc::string::String,std::io::error::Error> p_self;
  
  // 读取文件"galf.txt"
  std::fs::read_to_string::hd768795283f40b68(&p_self, (_str)__PAIR128__(8LL, "galf.txt"));
  
  v1.data_ptr = (u8 *)"Failed to read file\n";
  v1.length = 19LL;
  
  // 如果读取失败，panic并显示错误消息
  core::result::Result$LT$T$C$E$GT$::expect::h5a14476cbb22186d(&v2, &p_self, v1);
  
  // 打印文件内容
  core::fmt::rt::Argument::new_display::hd6cb2775973dfaec(&x);
  // ... 格式化和打印代码 ...
  std::io::stdio::_print::h87d04f1826f04caf();
  
  // 清理
  core::ptr::drop_in_place$LT$alloc..string..String$GT$::hace1b0e2d872108d(&v2);
  core::ptr::drop_in_place$LT$alloc..string..String$GT$::hace1b0e2d872108d(a1);
}
```

**关键观察**：
- `flag()`函数读取文件`"galf.txt"`（注意是反转的"flag"）
- 参数`a1`在函数中**从未被使用**！只是在最后被drop
- 这个函数输出的就是我们看到的`NotYetFlag{...}`提示

#### 3.2 反编译stuff函数

同样查看`stuff()`函数（0x1ae80）：

```c
void __fastcall edge_ctf_2025_rustffi::stuff::h9e7c4b54de86147cE(alloc::string::String *a1)
{
  _str v1;
  alloc::string::String v2;
  core::result::Result<alloc::string::String,std::io::error::Error> p_self;
  
  // 读取文件"stuff.txt"
  std::fs::read_to_string::hd768795283f40b68(&p_self, (_str)__PAIR128__(9LL, "stuff.txt"));
  
  v1.data_ptr = (u8 *)"Failed to read file\n";
  v1.length = 19LL;
  
  // 如果读取失败，panic
  core::result::Result$LT$T$C$E$GT$::expect::h5a14476cbb22186d(&v2, &p_self, v1);
  
  // 打印文件内容
  // ... (代码结构与flag函数完全相同) ...
  
  core::ptr::drop_in_place$LT$alloc..string..String$GT$::hace1b0e2d872108d(&v2);
  core::ptr::drop_in_place$LT$alloc..string..String$GT$::hace1b0e2d872108d(a1);
}
```

**第二个关键发现**：
- `stuff()`函数读取文件`"stuff.txt"`
- 结构与`flag()`完全相同
- 但在C++的`start()`函数中，**从未调用过stuff()函数**！

**重要问题**：如何才能调用到`stuff()`函数来读取真正的flag？

### 第四步：分析handler函数 - 发现突破口

#### 4.1 反编译handler函数

查看信号处理器`handler()`函数（0x1c883）：

```c
void __cdecl handler(int sig)
{
  rust::cxxbridge1::String p_arg0; // [rsp+10h] [rbp-20h]
  
  if ( sig == 6 )  // SIGABRT
  {
    // 使用全局变量's'创建String
    rust::cxxbridge1::String::String(&p_arg0, s);
    
    // 调用stuff函数！
    stuff(&p_arg0);
    
    rust::cxxbridge1::String::~String(&p_arg0);
  }
}
```

**第三个关键发现**：
- 当程序收到**SIGABRT信号（信号6）**时
- `handler()`会调用`stuff()`函数！
- 使用的是某个变量`s`（在IDA中显示为全局变量）

#### 4.2 查看变量s的内容

在IDA中查看`s`的地址（0xcdf0）：

```
View → Open subviews → Hex dump
跳转到地址 0xcdf0

0xcdf0: 00 00 00 00 00 00 00 00 62 61 73 69 63 5f 73 74
        ^^^^^^^^^^^^^^^^^^^^^^^^ (8个null字节)
                                 b  a  s  i  c  _  s  t
```

**发现**：`s`是一个空字符串（8个null字节），后面跟着"basic_st"（应该是"basic_string"）。

**第四个关键发现**：如果触发SIGABRT，`handler`会用**空字符串**调用`stuff()`！

### 第五步：寻找触发SIGABRT的方法

#### 5.1 搜索panic和abort相关代码

在IDA的Strings窗口中（Shift+F12），搜索"panic"、"abort"：

找到一个关键字符串：
```
"panic in ffi function , aborting."
```

这说明**当FFI函数中发生panic时，程序会abort**，从而触发SIGABRT！

#### 5.2 分析FFI边界的验证

查看C++如何将字符串传递给Rust。在IDA中找到`rust::cxxbridge1::String`的构造函数：

反编译`rust::cxxbridge1::String::String()`（0x1e898）：

```c
void __cdecl rust::cxxbridge1::String::String(
    rust::cxxbridge1::String *const this, 
    const std::string *s)
{
  std::size_t v2;
  const char *v3;
  
  v2 = std::string::length(s);
  v3 = std::string::data(s);
  
  // 关键：调用initString初始化
  rust::cxxbridge1::initString(this, v3, v2);
}
```

继续查看`initString`函数（0x1e853）：

```c
void __cdecl rust::cxxbridge1::initString(
    rust::cxxbridge1::String *self, 
    const char *s, 
    std::size_t len)
{
  // 检查字符串是否为有效UTF-8
  if ( !cxxbridge1_string_from_utf8(
        (core::mem::maybe_uninit::MaybeUninit<alloc::string::String> *)self, 
        (u8 *)s, 
        len) )
  {
    // 如果不是有效UTF-8，触发panic！
    rust::cxxbridge1::panic<std::invalid_argument>(
      "data for rust::String is not utf-8");
  }
}
```

**第五个关键发现**（最重要的突破！）：
1. 当C++传递字符串给Rust时，`initString`会验证UTF-8有效性
2. 如果字符串包含**无效的UTF-8字节序列**，会触发panic
3. FFI中的panic会导致`abort()` → SIGABRT → `handler()` → `stuff()`！

### 第六步：构造利用payload

#### 6.1 设计payload的要求

我们需要一个payload满足：
1. 反转后前15个字符是"NOCXXEXCEPTIONS"（通过C++的检查）
2. 包含无效的UTF-8字节（触发Rust的panic）

**问题**：如何同时满足这两个条件？

#### 6.2 解决方案

关键思路：
- 字符串反转是**整个字符串**反转
- 但C++只检查**前15个字符**
- 所以我们可以在**开头**放置无效UTF-8，反转后它们会在**结尾**

payload构造：
```
原始：  [无效UTF-8] + "SNOITPECXEXXCON"
反转：  "NOCXXEXCEPTIONS" + [无效UTF-8的反转]
        ^^^^^^^^^^^^^^^^   ^^^^^^^^^^^^^^^
        前15个字符匹配      在后面，不影响匹配
```

#### 6.3 选择无效UTF-8字节

在UTF-8编码中，`0xFF`和`0xFE`是永远不会出现的字节（它们保留给UTF-16/UTF-32的BOM）。

最终payload：
```python
invalid_utf8 = b"\xff\xfe"
valid_part = b"SNOITPECXEXXCON"
payload = invalid_utf8 + valid_part + b"\n"
```

### 第七步：编写exploit并验证

#### 7.1 完整的exploit脚本

```python
#!/usr/bin/env python3
import socket

host = "foreign-affair.chall.edgesecurity.team"
port = 1338

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.settimeout(10)
s.connect((host, port))

# 接收欢迎信息
welcome = s.recv(4096)
print(f"[<] {welcome.decode('utf-8', errors='replace')}")

# 构造payload
# 无效UTF-8在前面，这样反转后在后面，不影响前15个字符的匹配
invalid_utf8 = b"\xff\xfe"
valid_part = b"SNOITPECXEXXCON"
payload = invalid_utf8 + valid_part + b"\n"

print(f"\n[*] Payload: {repr(payload)}")
print(f"[*] 反转后: {repr(payload[:-1][::-1])}")
print(f"[*] 前15个字符: {repr(payload[:-1][::-1][:15])}")

s.sendall(payload)

import time
time.sleep(2)

response = b""
s.settimeout(5)
try:
    while True:
        chunk = s.recv(4096)
        if not chunk:
            break
        response += chunk
except socket.timeout:
    pass

print(f"\n[+] 响应:")
print("="*70)
if response:
    print(response.decode('utf-8', errors='replace'))
print("="*70)
```

#### 7.2 执行结果

```bash
$ python exploit_v2.py

[<] TRY!

[*] Payload: b'\xff\xfeSNOITPECXEXXCON\n'
[*] 反转后: b'NOCXXEXCEPTIONS\xfe\xff'
[*] 前15个字符: b'NOCXXEXCEPTIONS'

[+] 响应:
======================================================================
EdgeCTF{n3v3r_7ru57_w0rd5_0f_f0r31gn_0r1g1n5!}
======================================================================
```

**成功！获得flag！**

### 第八步：理解完整的攻击链

#### 8.1 攻击流程图

```
用户输入: \xff\xfe + "SNOITPECXEXXCON"
    ↓
C++ start()函数
    ↓
反转字符串 → "NOCXXEXCEPTIONS" + \xfe\xff
    ↓
提取前15字符 → "NOCXXEXCEPTIONS"
    ↓
比较匹配 ✓ (通过检查)
    ↓
创建rust::cxxbridge1::String
    ↓
调用initString()进行UTF-8验证
    ↓
检测到无效UTF-8 (\xfe\xff)
    ↓
触发panic("data for rust::String is not utf-8")
    ↓
FFI panic → abort()
    ↓
发送SIGABRT信号
    ↓
handler()捕获信号
    ↓
调用stuff("")
    ↓
读取stuff.txt
    ↓
输出真正的flag!
```

#### 8.2 为什么这个攻击有效？

1. **C++的检查是基于位置的**：只检查前15个字符
2. **Rust的检查是基于内容的**：检查整个字符串的UTF-8有效性
3. **字符串反转**：让我们可以把无效字节放在前面，反转后到后面
4. **FFI的panic机制**：Rust在FFI边界panic会触发abort
5. **信号处理器**：程序预设了SIGABRT处理器，给了我们后门

---

## 错误路径总结

在解题过程中走过的弯路：

### 错误1：忽视了stuff函数的存在
**错误想法**：以为flag()函数就是最终答案
**教训**：在逆向时要注意所有导出的函数，即使它们看起来没被调用

### 错误2：尝试通过正常输入触发stuff
**错误想法**：尝试通过特殊输入让程序调用stuff()
**教训**：仔细分析代码逻辑，start()函数中确实没有调用stuff()的路径

### 错误3：在payload后面添加无效UTF-8
**错误想法**：`b"SNOITPECXEXXCON\xff\xfe\n"`
**问题**：反转后变成`b"\xfe\xffNOCXXEXCEPTIONS"`，前15个字符不匹配
**教训**：要考虑反转操作对payload结构的影响

### 错误4：尝试触发其他类型的panic
**错误想法**：发送超长字符串、NULL字节等
**问题**：这些都不会触发UTF-8验证失败
**教训**：要精确理解触发点的条件

---

## 程序核心机制详解

### 内存布局和关键变量

```
.rodata段:
  s @ 0xcdf0:           空字符串 (用于handler)
  "NOCXXEXCEPTIONS" @ 0x...: gate字符串
  "galf.txt" @ 0xca28:  flag函数读取的文件名
  "stuff.txt" @ 0xc9f0: stuff函数读取的文件名

栈变量 (start函数):
  gate:    "NOCXXEXCEPTIONS" (15字节)
  s:       用户输入的字符串
  partial: 从s提取的前15个字符
  p_arg0:  传递给Rust的String对象
```

### C++与Rust的FFI桥接

```c
// C++侧调用
rust::cxxbridge1::String::String(&p_arg0, &s);
flag(&p_arg0);

// 转换过程
C++ std::string → 提取data和length
                ↓
         initString(ptr, len)
                ↓
         验证UTF-8 (cxxbridge1_string_from_utf8)
                ↓
    有效？创建Rust String : panic!
                ↓
           调用Rust函数
```

### UTF-8验证机制

UTF-8的编码规则：
- 单字节：0x00-0x7F
- 多字节起始：0xC0-0xFD
- 后续字节：0x80-0xBF
- **永远不会出现：0xFE, 0xFF**

所以`\xfe\xff`是明确的无效UTF-8序列。

### 信号处理流程

```c
1. 程序启动
   ↓
2. signal(SIGABRT, handler)  // 注册处理器
   ↓
3. 正常执行...
   ↓
4. FFI panic → abort()
   ↓
5. 内核发送SIGABRT给进程
   ↓
6. 进程调用handler(6)
   ↓
7. handler检查sig==6，调用stuff()
   ↓
8. 读取并输出flag
```

---

## 技术总结

### 核心技术点

1. **FFI安全分析** ⭐⭐⭐⭐⭐
   - 理解C++和Rust之间的类型转换
   - 识别FFI边界的验证机制
   - 利用验证失败触发panic

2. **UTF-8编码攻击** ⭐⭐⭐⭐⭐
   - 了解UTF-8编码规则
   - 构造无效UTF-8序列
   - 绕过字符串匹配的同时触发验证失败

3. **信号处理劫持** ⭐⭐⭐⭐
   - 识别信号处理器的注册
   - 理解SIGABRT的触发条件
   - 利用预设的处理器作为后门

4. **字符串操作** ⭐⭐⭐
   - 理解字符串反转的影响
   - 精确控制payload的结构
   - 利用位置检查和内容检查的差异

### 难点突破

1. **发现隐藏的stuff函数** ⭐⭐⭐⭐
   - 难点：函数存在但从未被调用
   - 突破：分析所有导出函数，注意到handler中的调用

2. **理解FFI的UTF-8验证** ⭐⭐⭐⭐⭐
   - 难点：找到触发panic的方法
   - 突破：深入分析cxxbridge的实现细节

3. **构造双重满足的payload** ⭐⭐⭐⭐
   - 难点：同时满足C++检查和触发Rust panic
   - 突破：利用字符串反转和位置检查的特性

4. **连接整个攻击链** ⭐⭐⭐⭐⭐
   - 难点：理解panic → abort → SIGABRT → handler → stuff的完整流程
   - 突破：系统性分析每个环节的触发条件

### 学到的经验

1. **关注所有函数**
   - 即使某个函数看起来没被调用，也可能通过间接方式触发
   - signal handler是一个常见的隐藏调用路径

2. **FFI是潜在的攻击面**
   - 不同语言的类型系统和验证机制可能不一致
   - 跨语言边界的数据传递需要仔细验证

3. **编码攻击的威力**
   - UTF-8、UTF-16等编码的特殊性可以用于绕过检查
   - 无效编码序列可能触发panic或其他异常行为

4. **逆向需要耐心**
   - 从NotYetFlag到真正的flag需要深入分析
   - "You are getting closer"的提示说明方向正确，需要继续探索

---

## 最终答案

### Flag
```
EdgeCTF{n3v3r_7ru57_w0rd5_0f_f0r31gn_0r1g1n5!}
```

**Flag含义**：Never trust words of foreign origins!（永远不要相信外来的话！）

这完美呼应了题目"foreign-affair"（外交事务/FFI）的主题，暗示了FFI接口的安全风险。

### Payload
```python
b"\xff\xfe" + b"SNOITPECXEXXCON" + b"\n"
```

### 攻击原理
```
1. C++检查：反转后前15字节 = "NOCXXEXCEPTIONS" ✓
2. Rust验证：包含无效UTF-8 (\xfe\xff) → panic
3. FFI panic → abort() → SIGABRT
4. handler捕获 → 调用stuff() → 读取flag
```

---

## 工具和环境

- **IDA Pro 7.x/8.x**: 静态分析和反编译
  - 使用F5查看伪代码
  - 使用Shift+F12搜索字符串
  - 使用交叉引用分析函数调用关系
- **Python 3.8+**: 编写exploit脚本
- **Linux环境**: 运行和测试二进制文件

---

## 作者注

这道题的设计非常精妙，它考察了：
1. **逆向分析能力**：理解C++/Rust混合程序的结构
2. **编码知识**：了解UTF-8编码和无效序列
3. **系统知识**：理解信号处理机制
4. **创造性思维**：找到非常规的函数调用路径

最关键的突破点有两个：
1. **识别FFI的UTF-8验证** - 这是触发panic的关键
2. **理解信号处理器的作用** - 这是调用隐藏函数的途径

题目名称"foreign-affair"不仅指FFI（Foreign Function Interface），也暗示了"不要相信外来的输入"这个安全原则。flag的内容`Never trust words of foreign origins!`更是明确了这个主题。

希望这份详细的解题报告能帮助你理解整个思路过程，特别是如何系统性地分析一个复杂的逆向题目。**理解攻击链的每个环节比知道最终答案更重要！**

---

## 文件清单

### 主要文件
- `README.md` - 完整解题报告（本文档）
- `exploit_v2.py` - 最终的exploit脚本（成功版本）
- `solve_edge_ctf.py` - 初始分析脚本（获得NotYetFlag提示）

### 辅助测试脚本
- `final_solve.py` - 扩展测试脚本
- `extended_crack.py` - payload模糊测试
- `test_methods.py` - 多种方法测试
- `trigger_panic.py` - 尝试触发panic
- `comprehensive_test.py` - 综合测试
- `final_exploit.py` - 早期exploit尝试（失败版本）
- `final_solution.py` - 解决方案文档

### 二进制文件
- `chall` - 题目二进制文件（MD5: e61e62e6c15464a7f7d48e3aef931048）
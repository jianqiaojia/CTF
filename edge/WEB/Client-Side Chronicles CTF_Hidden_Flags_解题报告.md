# CTF题目解答报告 - Hidden Flags

**题目链接**: https://hidden-flags.chall.edgesecurity.team/  
**题目作者**: dr3dd  
**Flag格式**: EdgeCTF{random_string_here}  
**解题日期**: 2025-12-12

---

## 题目概述

这是一道关于现代Web应用中JavaScript使用的CTF题目。题目名称为"Hidden Flags"，提示我们需要在网页的各个地方寻找隐藏的flag。

---

## 找到的Flag

### Flag 1: HTML注释中的Flag

**Flag**: `EdgeCTF{c0mm3nt5_4r3_n0t_s3cr3t}`

**位置**: 主页HTML源代码的注释中

**发现方法**: 
1. 访问主页
2. 查看HTML源代码
3. 在第20行左右发现注释：`<!-- Flag 1: EdgeCTF{c0mm3nt5_4r3_n0t_s3cr3t} -->`

**Flag含义**: Comments are not secret（注释不是秘密）

---

### Flag 2: JavaScript混淆代码中的Flag

**Flag**: `EdgeCTF{d0nt_put_s3ns1t1v3_d4t4_1n_j4v45cr1pt}`

**位置**: `/static/app.js` 文件中

**发现方法**:
1. 在主页HTML中发现引用了JavaScript文件：`<script src="/static/app.js"></script>`
2. 访问 https://hidden-flags.chall.edgesecurity.team/static/app.js
3. 发现混淆的JavaScript代码，其中包含一个Base64编码的字符串

**混淆代码分析**:
```javascript
var _0x4f2a = ['RWRnZUNURntkMG50X3B1dF9zM25zMXQxdjNfZDR0NF8xbl9qNHY0NWNyMXB0fQ==', 'atob', 'log'];

function _0x3b8d(d) {
    return window[_0x4f2a[1]](d);  // 相当于 window.atob(d)
}

var checkAccess = function() {
    var encoded = _0x4f2a[0];  // Base64编码的字符串
    var step1 = _0x3b8d(encoded);  // 进行Base64解码
    return step1;
};
```

**解码过程**:
- Base64字符串: `RWRnZUNURntkMG50X3B1dF9zM25zMXQxdjNfZDR0NF8xbl9qNHY0NWNyMXB0fQ==`
- 使用atob()或Base64解码工具解码
- 得到Flag: `EdgeCTF{d0nt_put_s3ns1t1v3_d4t4_1n_j4v45cr1pt}`

**Flag含义**: Don't put sensitive data in JavaScript（不要在JavaScript中放置敏感数据）

---

## 解题步骤总结

1. **查看HTML源代码**
   - 使用curl或浏览器开发者工具查看页面源代码
   - 发现HTML注释中的第一个flag

2. **分析JavaScript文件**
   - 注意到页面加载了`/static/app.js`
   - 获取并分析JavaScript代码
   - 识别出混淆的代码模式

3. **解码混淆内容**
   - 识别Base64编码的字符串
   - 使用Base64解码获得第二个flag

---

## 使用的工具和命令

```bash
# 获取主页HTML
curl https://hidden-flags.chall.edgesecurity.team/

# 获取JavaScript文件
curl https://hidden-flags.chall.edgesecurity.team/static/app.js

# Base64解码（PowerShell）
powershell -Command "[System.Text.Encoding]::UTF8.GetString([System.Convert]::FromBase64String('RWRnZUNURntkMG50X3B1dF9zM25zMXQxdjNfZDR0NF8xbl9qNHY0NWNyMXB0fQ=='))"
```

---

## 安全知识点

这道题目揭示了两个重要的Web安全原则：

### 1. ❌ 不要在HTML注释中存放敏感信息
- HTML注释会随页面源代码一起发送到客户端
- 任何人都可以查看页面源代码
- 即使是"隐藏"的注释也是完全公开的

### 2. ❌ 不要在客户端JavaScript中存放敏感数据
- 所有发送到客户端的JavaScript代码都可以被查看和分析
- 代码混淆或Base64编码**不是**真正的加密
- 这些技术只能轻微增加逆向难度，但无法真正保护敏感信息
- 任何有基本技能的人都可以还原混淆的代码

### 正确做法
✅ 敏感数据应该只存储在服务器端  
✅ 使用服务器端API来处理敏感操作  
✅ 客户端代码应该假设会被完全暴露  
✅ 使用真正的加密和身份验证机制保护数据

---

## 结论

成功找到2个flag：
1. `EdgeCTF{c0mm3nt5_4r3_n0t_s3cr3t}` - HTML注释
2. `EdgeCTF{d0nt_put_s3ns1t1v3_d4t4_1n_j4v45cr1pt}` - JavaScript混淆代码

这道题目很好地演示了客户端代码安全的重要性，提醒开发者永远不要在客户端存储真正的秘密信息。
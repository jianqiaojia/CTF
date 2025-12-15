# Hidden Flags CTF 挑战 - 解题总结

**挑战地址：** https://hidden-flags.chall.edgesecurity.team/  
**作者：** dr3dd  
**主题：** 安全最佳实践和信息泄露漏洞

---

## 挑战概述

这个CTF挑战测试了常见的Web安全漏洞知识和RFC 9116标准（安全联系信息）。目标是通过不同的Web侦察技术找到三个隐藏的flag。

---

## 获得的Flag

### Flag 1: HTML注释泄露
**Flag：** `EdgeCTF{c0mm3nt5_4r3_n0t_s3cr3t}`

**位置：** 主页HTML源代码  
**方法：** 查看页面源代码或检查HTML注释

**漏洞分析：** 敏感信息存储在HTML注释中
- HTML注释对任何查看页面源代码的人都是可见的
- 永远不要在注释中存储flag、凭证或敏感数据
- 注释会发送到客户端，很容易被发现

**教训：** 
- 开发时的调试信息要及时清理
- 不要假设注释是"隐藏"的

---

### Flag 2: JavaScript混淆
**Flag：** `EdgeCTF{d0nt_put_s3ns1t1v3_d4t4_1n_j4v45cr1pt}`

**位置：** `/static/app.js`  
**编码值：** `RWRnZUNURntkMG50X3B1dF9zM25zMXQxdjNfZDR0NF8xbl9qNHY0NWNyMXB0fQ==`  
**编码方式：** Base64

**解题步骤：**
1. 在主页中发现引用的JavaScript文件：`<script src="/static/app.js"></script>`
2. 访问 `/static/app.js` 查看混淆后的代码
3. 识别代码中的Base64编码字符串
4. 使用 `atob()` 函数或任何Base64解码器进行解码

**代码分析：**
```javascript
var _0x4f2a = ['RWRnZUNURntkMG50X3B1dF9zM25zMXQxdjNfZDR0NF8xbl9qNHY0NWNyMXB0fQ==', 'atob', 'log'];

function _0x3b8d(d) {
    return window[_0x4f2a[1]](d);  // 调用 atob
}

var checkAccess = function() {
    var encoded = _0x4f2a[0];
    var step1 = _0x3b8d(encoded);  // Base64解码
    return step1;
};
```

**漏洞分析：** 客户端JavaScript中的敏感数据
- JavaScript混淆不等于加密 - 它只是让代码难以阅读
- 发送到客户端的任何数据都可以被解码
- 永远不要在JavaScript中存储API密钥、秘密或敏感信息
- 客户端代码应该被视为公开的

**教训：**
- 混淆≠安全
- 关键数据和逻辑应该放在服务器端
- 使用后端API验证，不要依赖前端验证

---

### Flag 3: RFC 9116 - security.txt
**Flag：** `EdgeCTF{s3cur1ty_txt_f0r_vuln_r3p0rt5}`

**位置：** `/.well-known/security.txt`  
**标准：** RFC 9116

**文件内容：**
```
Contact: security@edgectf.team
Expires: 2026-12-31T23:59:59.000Z
Preferred-Languages: en
Canonical: https://edgectf.team/.well-known/security.txt

# Flag 3: EdgeCTF{s3cur1ty_txt_f0r_vuln_r3p0rt5}

# Please report security vulnerabilities to the contact above
```

**解题步骤：**
1. 理解题目提示中关于RFC 9116和标准化安全联系位置的线索
2. 访问 `/.well-known/security.txt`（标准位置）
3. 找到安全联系信息和flag

**关于RFC 9116：**
- 定义了发布安全联系信息的标准
- 帮助安全研究人员负责任地报告漏洞
- 标准位置：
  - `/.well-known/security.txt`（首选）
  - `/security.txt`（传统位置）
- 常见字段：Contact（联系方式）、Expires（过期时间）、Preferred-Languages（首选语言）、Canonical（规范URL）

**重要性：**
- 提供了一个标准化的方式让研究人员联系安全团队
- 促进负责任的漏洞披露
- 所有面向公众的网站都应该实现这个标准

---

## 核心要点总结

### 1. HTML注释是公开的
- 永远不要在HTML注释中存储敏感信息
- 注释在页面源代码和开发者工具中都是可见的
- 生产环境代码应该清理所有调试信息

### 2. 客户端安全不是真正的安全
- JavaScript混淆 ≠ 安全保护
- 所有客户端代码和数据都可以被访问和分析
- 对敏感数据使用服务器端验证和存储
- 前端验证只是用户体验优化，不是安全措施

### 3. RFC 9116 - security.txt标准
- 对于负责任的漏洞披露很重要
- 提供了研究人员联系安全团队的标准化方式
- 应该在所有公开网站上实现
- 体现了组织对安全的重视程度

### 4. 信息泄露漏洞
- 始终考虑发送到客户端的信息
- 审查源代码、JavaScript文件和API响应
- 使用适当的安全头和配置
- 最小化暴露给客户端的信息

---

## 使用的工具

- **Microsoft Edge浏览器** 配合Puppeteer自动化
- **Base64解码器**（`atob()`函数）
- **HTML源代码检查器**
- **RFC 9116标准知识**

---

## 难度等级
⭐⭐☆☆☆ (初级到中级)

### 这个挑战非常适合学习：
- Web侦察基础知识
- 常见的信息泄露漏洞
- 安全标准和最佳实践
- Base64编码/解码技术
- 客户端安全的局限性

---

## 技术栈分析

**前端：**
- HTML5 + CSS3（渐变背景、毛玻璃效果）
- JavaScript（混淆代码）
- 响应式设计

**安全特性：**
- security.txt文件（RFC 9116）
- 多层信息隐藏（注释、编码、标准位置）

---

## 实战价值

### 对渗透测试的启示：
1. **信息收集阶段** - 总是检查：
   - HTML源代码和注释
   - JavaScript文件
   - 标准安全文件（robots.txt, security.txt, sitemap.xml）
   - 开发者工具中的网络请求

2. **常见发现：**
   - API端点暴露
   - 调试信息泄露
   - 旧版本文件未删除
   - 敏感路径在JavaScript中硬编码

3. **防御建议：**
   - 使用构建工具自动清理注释
   - 环境变量管理敏感配置
   - 实施内容安全策略（CSP）
   - 定期审计前端代码

---

## 延伸思考

### 如果是真实场景：
- **HTML注释泄露** 可能暴露：内部API、管理员路径、数据库结构
- **JavaScript混淆** 可能隐藏：API密钥、加密算法、业务逻辑
- **security.txt** 应该包含：安全团队联系方式、PGP密钥、漏洞赏金计划

### 防护措施：
1. 使用CI/CD pipeline自动化代码审查
2. 实施代码混淆和压缩（但不依赖它作为安全措施）
3. 分离前后端，敏感逻辑放在后端
4. 定期进行安全审计和渗透测试

---

**完成日期：** 2025年12月12日  
**总Flag数：** 3/3 ✅

**作者总结：** 这是一个设计精良的入门级Web安全挑战，通过三个不同层次的信息泄露漏洞，系统地教授了Web安全的基础知识。特别是RFC 9116的引入，体现了负责任的安全文化的重要性。
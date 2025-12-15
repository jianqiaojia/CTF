# Order Tracker - CTF Web 解题报告

## 题目信息

**题目名称**: Order Tracker  
**题目链接**: https://order-tracker.chall.edgesecurity.team/  
**题目描述**: Welcome to EdgeMart! Track your orders securely... or so we thought. Our admin placed a special order containing something valuable. Can you find it?  
**出题人**: utkarshpal  
**Flag格式**: EdgeCTF{random_string_here}

## 解题过程

### 1. 信息收集

访问目标网站后发现这是一个在线购物订单追踪系统 EdgeMart。网站提供以下功能：
- 用户注册
- 用户登录
- 订单追踪
- 创建新订单

### 2. 账户注册与登录

首先注册一个测试账户：
- 用户名: testuser123
- 邮箱: test@example.com
- 密码: password123

注册成功后登录系统，自动获得一个欢迎礼物订单 #78。

### 3. 探索订单系统

访问自己的订单详情页面：
```
https://order-tracker.chall.edgesecurity.team/order/78
```

观察URL结构，发现订单ID是通过URL参数直接传递的，这可能存在 IDOR（Insecure Direct Object Reference，不安全的直接对象引用）漏洞。

### 4. 漏洞利用

尝试修改URL中的订单ID，访问其他订单：
```
https://order-tracker.chall.edgesecurity.team/order/1
```

成功！系统没有进行权限验证，允许我们访问管理员的订单。

### 5. 获取Flag

在订单 #1 的详情页面中发现：

**订单信息**:
- 订单ID: #1
- 日期: 2025-12-02 06:45:44
- 状态: 已送达 (Delivered)

**客户信息**:
- 客户: admin
- 邮箱: admin@edgectf.local
- 账户类型: Admin

**产品信息**:
- 产品: CTF Flag Package - Premium Edition
- 数量: 1
- 总价: $1337.00

**订单备注**:
```
EdgeCTF{1D0R_3xpl01t_0rd3r_1337_f0und}
```

## Flag

```
EdgeCTF{1D0R_3xpl01t_0rd3r_1337_f0und}
```

## 漏洞分析

### 漏洞类型
IDOR (Insecure Direct Object Reference) - 不安全的直接对象引用

### 漏洞描述
应用程序通过URL参数直接引用内部对象（订单ID），但没有实现适当的访问控制验证。任何经过身份验证的用户都可以通过简单地修改URL中的订单ID来访问其他用户的订单信息。

### 漏洞影响
- 信息泄露：攻击者可以查看任意用户的订单信息
- 隐私侵犯：可以获取客户的个人信息、购买记录等敏感数据
- 业务风险：可能导致商业机密泄露

### 安全建议
1. **实施严格的访问控制**：在服务器端验证当前用户是否有权限访问请求的订单
2. **使用间接引用**：使用难以猜测的随机标识符（UUID）而不是连续的数字ID
3. **实施会话管理**：将订单与用户会话绑定，确保用户只能访问自己的订单
4. **日志记录**：记录所有订单访问尝试，便于检测异常行为
5. **安全审计**：定期进行代码审查和安全测试

## 解题思路总结

1. 通过注册和登录熟悉系统功能
2. 观察URL结构，发现使用数字ID作为订单标识
3. 尝试访问其他订单ID（从1开始尝试）
4. 成功利用IDOR漏洞访问管理员订单
5. 在订单备注中找到flag

## 学习要点

- IDOR漏洞是OWASP Top 10中的常见漏洞
- 永远不要相信客户端传来的数据
- 必须在服务器端实施访问控制验证
- 使用不可预测的标识符可以增加安全性
- 安全是多层防护，不能仅依赖前端限制

## 作者

解题时间: 2025-12-12  
解题工具: Microsoft Edge Puppeteer Tools
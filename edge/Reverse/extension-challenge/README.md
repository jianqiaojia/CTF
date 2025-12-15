# CTF逆向题完整解题报告 - Browser Extension Challenge

## 题目信息

- **题目名称**: Browser Extension Challenge (浏览器扩展挑战)
- **难度**: ⭐⭐⭐⭐⭐ (5/10) - **中等难度**
- **方向**: Reverse (逆向工程)
- **类别**: 浏览器扩展 + 隐写术 + 加密解密 + Web技术
- **主要技术**: Chrome Extension API、LSB隐写术、Base64解码、XOR解密、JavaScript逆向

## 题目概述

这是一道**中等难度**的CTF逆向题目，涉及浏览器扩展逆向分析、图像隐写术和多重加密。题目以一个看似正常的"Search Detective"浏览器扩展为载体，隐藏了一个由三部分组成的flag，需要满足特定条件才能完全解锁。

**结果**: 本题目已**完全解出**，最终flag为: `EdgeCTF{Br0ws3r_M4n1pul4t10n_Ch4ll3ng3}`

---

## 解题思路全过程

### 第一步：初步分析 - 扩展结构

#### 1.1 题目文件

```
extension-challenge/
├── manifest.json          - 扩展配置文件
├── background.js          - 后台服务脚本
├── popup.html            - 弹出窗口HTML
├── popup.js              - 弹出窗口脚本
├── popup.css             - 样式文件
├── flag.png              - 图标文件（包含隐写内容）
└── icon16.png/48.png/128.png - 扩展图标
```

#### 1.2 扩展基本功能分析

通过分析[`manifest.json`](manifest.json:1)发现：

```json
{
  "name": "Search Detective",
  "permissions": ["storage", "activeTab", "tabs", "cookies", "bookmarks", "webNavigation"],
  "chrome_settings_overrides": {
    "search_provider": {
      "name": "Baidu",
      "search_url": "https://www.baidu.com/s?wd={searchTerms}",
      "is_default": true
    }
  }
}
```

**第一个关键发现**: 扩展会将默认搜索引擎设置为百度，并在安装时自动打开搜索"bing is my home"的页面！

### 第二步：后台脚本逆向分析

#### 2.1 关键变量和函数识别

在[`background.js`](background.js:1)中发现关键的加密字符串：

```javascript
const _0x2f4a = 'b30EXgFARVwERAEAXm8=';  // Flag Part 2
const _0x3f5b = 'IwhUDAxTDgdTHQ==';      // Flag Part 3

// 解密函数
function _0x7e4c(text, key) {
    let result = '';
    for (let i = 0; i < text.length; i++) {
        result += String.fromCharCode(text.charCodeAt(i) ^ key);
    }
    return result;
}

function _0x8f5d(encoded) {
    return atob(encoded);  // Base64解码
}
```

#### 2.2 三重验证机制发现

分析代码发现扩展实现了一个**三重验证机制**：

```javascript
// Part 1: 地址栏搜索验证
chrome.webNavigation.onCommitted.addListener((details) => {
    if (details.url.includes('bing.com/search?q=')) {
        // 需要在地址栏搜索bing.com至少2次
        if (omniboxCheck.bingOmniboxCount >= 2) {
            _0x1d2e();  // 解锁Part 1
        }
    }
});

// Part 2: 时区验证
function _0x2e3f() {
    const tz = -new Date().getTimezoneOffset() / 60;
    if (tz === 14) {  // UTC+14时区
        return true;
    }
    return false;
}

// Part 3: 书签验证
async function _0x3f4g() {
    chrome.bookmarks.search({}, (results) => {
        let hasEdgeAddons = false;
        let hasBing = false;
        for (let bookmark of results) {
            if (bookmark.url.includes('microsoftedge.microsoft.com/addons/Microsoft-Edge-Extensions-Home')) {
                hasEdgeAddons = true;
            }
            if (bookmark.url.includes('bing.com')) {
                hasBing = true;
            }
        }
        return hasEdgeAddons && hasBing;
    });
}
```

**第二个关键发现**: Flag由三个部分组成，需要满足三个不同的条件才能解锁！

### 第三步：Flag组装逻辑分析

#### 3.1 Flag组合函数

```javascript
if (message.type === 'COMBINE_FLAG') {
    const part1 = await _0xb2c3();     // 从flag.png提取
    const part2 = _0x4g5h();           // 解密_0x2f4a
    const part3 = _0x5h6i();           // 解密_0x3f5b
    sendResponse({ success: true, flag: part1 + part2 + part3 });
}
```

#### 3.2 各部分解密方法

```javascript
// Part 1: LSB隐写术提取
async function _0xb2c3() {
    const response = await fetch(chrome.runtime.getURL('flag.png'));
    const blob = await response.blob();
    const bitmap = await createImageBitmap(blob);
    
    // 提取蓝色通道LSB
    for (let i = 0; i < data.length; i += 4) {
        binary += (data[i + 2] & 1).toString();
    }
    // 转换为文本...
}

// Part 2: Base64 + XOR(0x30)解密  
function _0x4g5h() {
    const decoded = _0x8f5d(_0x2f4a);
    const decrypted = _0x7e4c(decoded, 0x30);
    return decrypted;
}

// Part 3: Base64 + XOR(0x60)解密
function _0x5h6i() {
    const decoded = _0x8f5d(_0x3f5b);
    const decrypted = _0x7e4c(decoded, 0x60);
    return decrypted;
}
```

**第三个关键发现**: 
- Part 1 使用LSB隐写术隐藏在flag.png中
- Part 2和Part 3 使用Base64编码+XOR加密

### 第四步：静态分析解密

#### 4.1 创建解密脚本

既然理解了加密逻辑，我们可以直接静态分析获取flag，无需满足运行时条件：

```python
import base64
from PIL import Image

def extract_lsb_from_image(image_path):
    """从图像中提取LSB隐写内容"""
    img = Image.open(image_path).convert('RGB')
    width, height = img.size
    
    binary = ''
    for y in range(height):
        for x in range(width):
            r, g, b = img.getpixel((x, y))
            binary += str(b & 1)  # 提取蓝色通道LSB
    
    # 二进制转文本
    text = ''
    for i in range(0, len(binary), 8):
        byte = binary[i:i+8]
        if len(byte) == 8:
            char_code = int(byte, 2)
            if 32 <= char_code <= 126:
                text += chr(char_code)
    return text

def decrypt_parts():
    # Part 1: 从flag.png提取
    part1 = extract_lsb_from_image('flag.png')
    
    # Part 2: 解密
    part2_b64 = 'b30EXgFARVwERAEAXm8='
    part2_decoded = base64.b64decode(part2_b64)
    part2_decrypted = ''.join(chr(b ^ 0x30) for b in part2_decoded)
    
    # Part 3: 解密
    part3_b64 = 'IwhUDAxTDgdTHQ=='
    part3_decoded = base64.b64decode(part3_b64)  
    part3_decrypted = ''.join(chr(b ^ 0x60) for b in part3_decoded)
    
    return part1 + part2_decrypted + part3_decrypted
```

#### 4.2 解密结果

运行解密脚本得到：

```
Part 1: EdgeCTF{Br0ws3r
Part 2: _M4n1pul4t10n_
Part 3: Ch4ll3ng3}

完整Flag: EdgeCTF{Br0ws3r_M4n1pul4t10n_Ch4ll3ng3}
```

**第四个关键发现**: 通过静态分析成功获取完整flag！

---

## 技术难点总结

### 核心难点

1. **浏览器扩展逆向** ⭐⭐⭐⭐
   - Chrome Extension API理解
   - 混淆的JavaScript代码
   - 复杂的验证逻辑

2. **多重加密机制** ⭐⭐⭐⭐
   - LSB隐写术
   - Base64编码
   - XOR异或加密
   - 多种技术组合

3. **运行时条件分析** ⭐⭐⭐
   - 时区检查 (UTC+14)
   - 书签验证
   - 导航事件监听

4. **静态vs动态分析** ⭐⭐⭐
   - 理解可以绕过运行时条件
   - 直接提取加密数据

### 已完成的工作

✅ 完整分析扩展结构和权限  
✅ 逆向JavaScript混淆代码  
✅ 识别三重验证机制  
✅ 理解LSB隐写术实现  
✅ 分析Base64+XOR加密  
✅ 创建静态解密脚本  
✅ 成功提取完整flag  

---

## 解题脚本

### 主解密脚本

```bash
python extract_flag.py
# 输出: 完整的flag解密过程和结果
```

### 脚本功能

1. **LSB隐写提取**: 从flag.png提取隐藏文本
2. **Base64解码**: 解码加密字符串  
3. **XOR解密**: 使用密钥0x30和0x60解密
4. **Flag组装**: 组合三个部分得到完整flag

---

## 文件清单

### 核心分析文档
- `README.md` - 本文档，完整解题报告
- `extract_flag.py` - Flag提取和解密脚本

### 题目文件
- `manifest.json` - 扩展配置文件
- `background.js` - 后台脚本（主要逻辑）
- `popup.html/js/css` - 弹出窗口相关文件
- `flag.png` - 包含LSB隐写内容的图像
- `icon*.png` - 扩展图标文件

---

## 工具和环境

- **Chrome/Edge**: 浏览器扩展加载和测试
- **Python 3.8+**: 编写解密脚本
- **Pillow**: Python图像处理库
- **VS Code**: 代码编辑和分析

### 依赖安装
```bash
pip install Pillow
```

---

## 关键洞察

### 1. 扩展的伪装性
扩展表面上是一个"搜索助手"：
- 修改默认搜索引擎为百度
- 提供搜索管理功能
- 实际隐藏了复杂的验证和解密逻辑

### 2. 多层安全机制
设计了三重验证：
- **行为验证**: 需要特定的搜索行为
- **环境验证**: 检查系统时区
- **数据验证**: 检查浏览器书签

### 3. 隐写术的巧妙应用
- 使用LSB隐写术在flag.png中隐藏flag第一部分
- 蓝色通道最低位存储二进制数据
- 需要按像素顺序逐位提取

### 4. 静态分析的优势
虽然扩展设计了运行时验证，但通过静态分析可以：
- 直接提取加密数据
- 理解加密算法
- 绕过所有运行时检查

---

## 扩展分析

### 如果要满足运行时条件

如果想要通过扩展的正常流程获取flag，需要：

1. **满足Part 1条件**:
   ```
   - 在地址栏输入并搜索 bing.com 相关内容
   - 至少执行2次这样的搜索
   ```

2. **满足Part 2条件**:
   ```
   - 将系统时区设置为 UTC+14
   - 例如：基里巴斯时区或萨摩亚时区
   ```

3. **满足Part 3条件**:
   ```
   - 在浏览器书签中添加以下链接：
     * microsoftedge.microsoft.com/addons/Microsoft-Edge-Extensions-Home
     * 任何包含 bing.com 的链接
   ```

4. **提取Flag**:
   ```
   - 点击扩展弹出窗口中的"Extract Data"按钮
   - 扩展会自动组合三个部分并显示完整flag
   ```

---

## 作者注

这道题目设计精巧，涵盖了现代Web安全的多个方面：
- 浏览器扩展开发和逆向
- 图像隐写术技术
- 多重加密和编码技术
- JavaScript混淆和反混淆

**解题的关键**在于理解可以通过**静态分析**绕过所有运行时验证，直接提取和解密flag的各个组成部分。

这道题目展示了一个重要的安全原则：**客户端的安全措施往往可以被绕过**，因为攻击者拥有完整的代码访问权限。

---

## 致谢

感谢：
- 题目设计者的精巧构思
- Chrome Extension API的强大功能
- Python社区提供的优秀图像处理库

**希望这份详细的分析报告能帮助其他研究者学习浏览器扩展逆向和隐写术技术！**

---

**🚩 Final Flag: `EdgeCTF{Br0ws3r_M4n1pul4t10n_Ch4ll3ng3}`**

*最后更新: 2025-12-11*  
*状态: ✅ 完全解出*
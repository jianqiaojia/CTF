# CTF Steganography Challenge - Solution Report

## Challenge Information

- **Challenge Name**: Can you see me
- **Category**: Misc / Steganography
- **File**: [`airobot_stego.png`](airobot_stego.png:1)
- **Flag**: `EdgeCTF{Y0u_C4n_5ee_M3_N0w_C4pt4in_Via_L5B}`

---

## Challenge Description

题目提示："There's something hidden in this image that you can't see with the naked eye."

这是一个经典的隐写术（Steganography）题目，需要从PNG图像中提取隐藏的信息。

---

## Solution Approach

### 1. 初步分析

首先对图像进行基础分析：
- 检查文件结构和元数据
- 查看PNG块信息
- 检查是否有额外数据附加在文件末尾

### 2. 工具开发

创建了三个Python脚本进行渐进式分析：

#### [`solve_stego.py`](solve_stego.py:1)
基础隐写分析工具，包含：
- 文件结构检查（IEND块后是否有额外数据）
- LSB（最低有效位）提取
- 元数据分析
- 颜色通道分离

#### [`advanced_stego.py`](advanced_stego.py:1)
高级分析工具，包含：
- PNG块详细解析（包括文本块）
- 所有8个位平面的提取（bit 0-7）
- 像素值差异分析
- 生成各位平面的可视化图像

#### [`extract_strings.py`](extract_strings.py:1) ⭐
最终成功的解决方案：
- 提取文件中的可读字符串
- 检查嵌入的文件签名
- **按行顺序读取所有像素的LSB并转换为文本**

### 3. 成功方法

使用LSB隐写术提取：

```python
# 关键代码片段
bits = ''
for row in img_array:
    for pixel in row:
        for channel in pixel:
            bits += str(channel & 1)  # 提取最低有效位

# 将二进制转换为ASCII
message = ''
for i in range(0, len(bits), 8):
    byte = bits[i:i+8]
    char_code = int(byte, 2)
    if 32 <= char_code <= 126:
        message += chr(char_code)
```

---

## Technical Details

### LSB隐写术原理

LSB（Least Significant Bit）隐写术是一种常见的图像隐写技术：

1. **原理**：修改每个像素颜色值的最低位来存储数据
2. **优点**：对图像视觉效果影响极小，肉眼难以察觉
3. **提取**：按照特定顺序读取所有像素的LSB，重组为原始消息

### 在本题中的应用

- **存储方式**：消息按照RGB通道顺序存储在每个像素的LSB中
- **读取顺序**：从左到右，从上到下，依次读取R、G、B通道
- **编码格式**：ASCII文本，每个字符8位

---

## Flag Explanation

**`EdgeCTF{Y0u_C4n_5ee_M3_N0w_C4pt4in_Via_L5B}`**

解码后的含义：
- **Y0u_C4n_5ee_M3_N0w** = "You Can See Me Now"（现在你能看见我了）
- **C4pt4in** = "Captain"（船长）
- **Via_L5B** = "Via LSB"（通过LSB技术）

这个flag巧妙地呼应了题目标题"Can you see me"，暗示了隐藏的信息现在可以通过LSB技术"看见"了。

---

## Tools and Files Created

| 文件 | 说明 |
|------|------|
| [`solve_stego.py`](solve_stego.py:1) | 基础隐写分析工具 |
| [`advanced_stego.py`](advanced_stego.py:1) | PNG高级分析和位平面提取 |
| [`extract_strings.py`](extract_strings.py:1) | 字符串提取和LSB读取（成功） |
| `lsb_visual.png` | LSB可视化图像 |
| `bit[0-7]_[RGB]_visual.png` | 各位平面可视化（24个文件） |
| `plane_[rgb].png` | RGB通道分离图像 |
| `extracted_strings.txt` | 提取的所有字符串 |

---

## Key Takeaways

1. **题目提示很重要**："can't see with the naked eye"直接指向隐写术
2. **LSB是最常见的图像隐写方法**，应该首先尝试
3. **读取顺序很关键**：不同的读取顺序会得到不同的结果
4. **使用多种工具和方法**：逐步深入分析，从简单到复杂
5. **自动化脚本很有用**：可以快速测试多种提取方法

---

## Commands to Reproduce

```bash
# 运行解决方案
python extract_strings.py

# 查看其他分析结果
python solve_stego.py
python advanced_stego.py
```

---

## Conclusion

这是一个经典的LSB隐写术CTF题目。通过系统化的分析方法和工具开发，成功从PNG图像中提取出隐藏的flag。关键在于理解LSB隐写术的原理，并按照正确的顺序读取像素数据。
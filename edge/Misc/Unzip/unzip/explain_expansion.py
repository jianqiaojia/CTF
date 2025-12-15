#!/usr/bin/env python3
import os

print("="*80)
print("数据'压缩'过程分析 - 为什么数据反而变大了?")
print("="*80)

# 检查每一层的大小
files = {
    "1. 原始hex文件 (unzip)": "unzip",
    "2. ZIP文件 (data.zip)": "data.zip", 
    "3. XZ压缩文件 (data.bin)": "data.bin",
    "4. XZ解压后 (data_decompressed.bin)": "data_decompressed.bin",
    "5. Base64解码后 (decoded_text.txt)": "decoded_text.txt"
}

sizes = {}
for name, filename in files.items():
    if os.path.exists(filename):
        size = os.path.getsize(filename)
        sizes[name] = size
        print(f"{name:45} {size:>12,} 字节")

print("\n" + "="*80)
print("数据变化分析:")
print("="*80)

print(f"""
层次1: Hex → Binary (ZIP)
  - 原始: 1,436 字符的hex文本
  - 转换: 718 字节的二进制ZIP文件
  - 变化: 缩小约50% (这是正常的,因为hex编码每个字节用2个字符表示)

层次2: ZIP解压
  - ZIP中: 718 字节
  - 解压出: 604 字节的data.bin (XZ压缩文件)
  - 变化: 缩小 (ZIP压缩类型为0,即无压缩,只是打包)

层次3: XZ解压 ⚠️ 关键的"反压缩"发生在这里!
  - XZ压缩: 604 字节
  - XZ解压: 1,277,716 字节
  - 变化: 扩大约 2,114 倍! 💥
  - 原因: XZ压缩算法非常高效,它将高度重复的Base64数据压缩到极小
         但解压时,这些重复数据被还原成原始的巨大文本

层次4: Base64解码
  - Base64编码: 1,277,716 字节
  - Base64解码: 958,287 字节
  - 变化: 缩小约25% (Base64编码会增加约33%,解码就会减少)

总体效果:
  - 起始(unzip文件): 718 字节 (binary)
  - 最终(decoded_text.txt): 958,287 字节
  - 总扩展比: 约 1,334 倍! 🎭
""")

print("="*80)
print("为什么XZ能压缩得这么小?")
print("="*80)

# 读取decoded_text看看内容
with open('decoded_text.txt', 'r') as f:
    content = f.read()

# 统计重复模式
base_pattern = 'LRx4!F+o`-Q(1XNt&;&?jsyUp000Oe05E_}Mna$^sS1FXF+'
pattern_occurrences = content.count(base_pattern)

print(f"""
decoded_text.txt的内容特征:
  - 总长度: {len(content):,} 字符
  - 基础模式: '{base_pattern}'
  - 模式长度: {len(base_pattern)} 字符
  - 这是一个旋转重复的模式
  - 估计重复次数: 约 18,000+ 次

XZ压缩算法检测到这种高度重复性:
  1. 使用LZMA算法识别重复模式
  2. 将重复部分用引用替代 (如: "重复前面的52字符")
  3. 只存储很少的原始数据 + 大量的"重复指令"
  4. 最终: 958,287字节 → 604字节 (压缩比 1:1586!)

这就是为什么题目叫"Unzip"的讽刺:
  - 表面上是"压缩文件"
  - 实际上"解压"后数据暴增
  - 这是反向的"压缩" - 实际是数据扩展/膨胀!
""")

print("="*80)
print("题目的讽刺点:")
print("="*80)
print("""
题目描述: "Someone sent me this 'compressed file' and claimed it would 
save storage space. I'm starting to think they have a very different 
definition of 'compression' than I do..."

翻译: "有人给我发了这个'压缩文件'并声称它能节省存储空间。
我开始觉得他们对'压缩'的定义和我很不一样..."

确实! 这个"压缩文件"最终让数据扩大了1334倍! 😄
""")
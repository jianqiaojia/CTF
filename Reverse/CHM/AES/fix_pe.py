#!/usr/bin/env python3

with open('20201122.tmp', 'rb') as f:
    data = bytearray(f.read())

print(f'原始文件大小: {len(data)} 字节')
print(f'前16字节: {data[:16].hex()}')
print(f'DOS签名: {hex(data[0] | (data[1] << 8))} (应该是0x5A4D = "MZ")')

# DOS签名应该是 0x5A4D (MZ)，但现在是 0x0090
# 看起来文件头被修改了

# 检查是否在文件中能找到正确的PE结构
# 标准DOS头在0x3C位置有PE头的偏移
pe_offset_location = 0x3C
if pe_offset_location < len(data):
    pe_offset = int.from_bytes(data[pe_offset_location:pe_offset_location+4], 'little')
    print(f'\n0x3C处的PE偏移: {hex(pe_offset)}')
    
    if pe_offset < len(data) - 4:
        pe_sig = data[pe_offset:pe_offset+4]
        print(f'PE偏移{hex(pe_offset)}处的签名: {pe_sig.hex()} ({pe_sig})')

# 搜索"PE\x00\x00"签名
print('\n搜索PE签名...')
for i in range(len(data) - 4):
    if data[i:i+4] == b'PE\x00\x00':
        print(f'找到PE签名在偏移: {hex(i)}')
        
        # 标准PE文件，PE签名应该在0xF8附近
        # 修复DOS头
        if i > 0x40:  # PE头在合理位置
            print(f'\n修复PE文件结构...')
            # 修复MZ签名
            data[0] = 0x4D  # 'M'
            data[1] = 0x5A  # 'Z'
            
            # 修复PE偏移指针
            data[0x3C] = i & 0xFF
            data[0x3D] = (i >> 8) & 0xFF
            data[0x3E] = (i >> 16) & 0xFF
            data[0x3F] = (i >> 24) & 0xFF
            
            print(f'已修复MZ签名为: {hex(data[0] | (data[1] << 8))}')
            print(f'已修复PE偏移为: {hex(i)}')
            
            # 保存修复后的文件
            with open('20201122_fixed.exe', 'wb') as f:
                f.write(data)
            
            print('\n修复后的文件已保存为: 20201122_fixed.exe')
            print('现在可以尝试运行或用IDA分析这个文件了')
            break
else:
    print('未找到PE签名，文件可能不是有效的PE格式')

# 也检查是否直接就是正确的PE文件（从偏移0xF8开始）
print('\n检查偏移0xF8处...')
if len(data) > 0xF8 + 4:
    maybe_pe = data[0xF8:0xF8+4]
    print(f'0xF8处的4字节: {maybe_pe.hex()} ({maybe_pe})')
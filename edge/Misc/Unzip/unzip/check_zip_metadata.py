#!/usr/bin/env python3
import zipfile
import os

print("="*80)
print("检查ZIP文件的详细信息")
print("="*80)

# 打开ZIP文件
with zipfile.ZipFile('data.zip', 'r') as zf:
    print(f"ZIP文件信息:")
    print(f"  文件列表: {zf.namelist()}")
    print()
    
    # 获取每个文件的详细信息
    for info in zf.infolist():
        print(f"文件名: {info.filename}")
        print(f"  压缩前大小: {info.file_size} 字节")
        print(f"  压缩后大小: {info.compress_size} 字节")
        print(f"  压缩类型: {info.compress_type}")
        print(f"  CRC: {hex(info.CRC)}")
        print(f"  创建时间: {info.date_time}")
        print(f"  Extra数据: {info.extra}")
        print(f"  Comment: {info.comment}")
        print(f"  Flag bits: {bin(info.flag_bits)}")
        print()
        
        # 检查extra字段
        if info.extra:
            print(f"  Extra字段内容(hex): {info.extra.hex()}")
            try:
                print(f"  Extra字段内容(UTF-8): {info.extra.decode('utf-8', errors='ignore')}")
            except:
                pass
        
        # 检查comment字段  
        if info.comment:
            print(f"  Comment内容(hex): {info.comment.hex()}")
            try:
                print(f"  Comment内容(UTF-8): {info.comment.decode('utf-8')}")
            except:
                pass

# 也检查ZIP文件整体的comment
with zipfile.ZipFile('data.zip', 'r') as zf:
    if zf.comment:
        print(f"\nZIP文件整体Comment:")
        print(f"  Hex: {zf.comment.hex()}")
        try:
            print(f"  UTF-8: {zf.comment.decode('utf-8')}")
        except:
            pass

print("\n" + "="*80)
print("直接读取data.bin文件的前1000字节(XZ压缩的)")
print("="*80)

with open('data.bin', 'rb') as f:
    raw_data = f.read(1000)
    print(f"文件大小: {os.path.getsize('data.bin')} 字节")
    print(f"文件开头(hex): {raw_data[:100].hex()}")
    print(f"XZ magic: {raw_data[:6].hex()} (应该是 fd377a585a00)")
    
    # XZ文件可能在末尾有数据
    with open('data.bin', 'rb') as f2:
        f2.seek(-100, 2)  # 从文件末尾往前100字节
        end_data = f2.read()
        print(f"\n文件末尾100字节(hex): {end_data.hex()}")
        print(f"文件末尾100字节(尝试UTF-8): {end_data.decode('utf-8', errors='ignore')}")
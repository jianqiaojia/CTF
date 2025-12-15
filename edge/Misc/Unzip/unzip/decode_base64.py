#!/usr/bin/env python3
import base64
import lzma

# 读取XZ解压后的数据
with open('data_decompressed.bin', 'rb') as f:
    base64_data = f.read()

# 解码Base64
try:
    decoded = base64.b64decode(base64_data)
    print(f"Base64解码成功！")
    print(f"解码后大小: {len(decoded)} 字节")
    
    # 尝试作为文本输出
    try:
        text = decoded.decode('utf-8')
        print(f"\n解码内容（UTF-8）:")
        print(text)
    except:
        print(f"\n不是UTF-8文本，输出前256字节:")
        print(decoded[:256])
        
        # 保存为文件
        with open('final_decoded.bin', 'wb') as f:
            f.write(decoded)
        print(f"\n已保存到 final_decoded.bin")
        
        # 检查文件类型
        if decoded[:2] == b'PK':
            print("检测到ZIP文件头！")
        elif decoded[:4] == b'\x1f\x8b\x08':
            print("检测到GZIP文件头！")
        elif decoded[:6] == b'\xfd7zXZ\x00':
            print("检测到XZ文件头！")
            
except Exception as e:
    print(f"解码失败: {e}")
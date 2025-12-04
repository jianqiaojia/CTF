#!/usr/bin/env python3
from Crypto.Cipher import AES

# 从0x1000103C处提取的32字节数据
data_block1 = bytes([
    0x2b, 0x7e, 0x15, 0x16,
    0x28, 0xae, 0xd2, 0xa6,
    0xab, 0xf7, 0x15, 0x88,
    0x09, 0xcf, 0x4f, 0x3c
])

data_block2 = bytes([
    0x1f, 0xea, 0xc7, 0x79,
    0x55, 0x3b, 0xf8, 0x82,
    0x51, 0xb3, 0x54, 0x80,
    0xcf, 0xa6, 0xb6, 0x75
])

print('找到的两个16字节块:')
print(f'块1: {data_block1.hex()}')
print(f'块2: {data_block2.hex()}\n')

# 尝试1: 块1作为密钥，块2作为密文
print('=== 尝试1: 块1作为密钥解密块2 ===')
try:
    cipher = AES.new(data_block1, AES.MODE_ECB)
    decrypted = cipher.decrypt(data_block2)
    print(f'解密结果: {decrypted}')
    print(f'解密结果(hex): {decrypted.hex()}')
    print(f'可打印字符: {all(32 <= b <= 126 for b in decrypted)}\n')
except Exception as e:
    print(f'解密失败: {e}\n')

# 尝试2: 块2作为密钥，块1作为密文
print('=== 尝试2: 块2作为密钥解密块1 ===')
try:
    cipher = AES.new(data_block2, AES.MODE_ECB)
    decrypted = cipher.decrypt(data_block1)
    print(f'解密结果: {decrypted}')
    print(f'解密结果(hex): {decrypted.hex()}')
    print(f'可打印字符: {all(32 <= b <= 126 for b in decrypted)}\n')
except Exception as e:
    print(f'解密失败: {e}\n')

# 尝试3: 整个32字节是两个连续的加密块，需要找密钥
# 常见的AES测试密钥
test_keys = [
    bytes([0] * 16),  # 全0
    bytes([0xFF] * 16),  # 全FF
    bytes(range(16)),  # 0-15
    b'YELLOW SUBMARINE',  # 常见测试密钥
    b'0123456789ABCDEF',
    b'reverse_html_ctf',  # 题目相关
]

print('=== 尝试3: 使用常见测试密钥 ===')
for i, key in enumerate(test_keys):
    try:
        cipher = AES.new(key, AES.MODE_ECB)
        decrypted1 = cipher.decrypt(data_block1)
        decrypted2 = cipher.decrypt(data_block2)
        combined = decrypted1 + decrypted2
        
        print(f'密钥{i+1}: {key}')
        if b'flag' in combined.lower() or b'ctf' in combined.lower():
            print(f'  *** 可能的FLAG! ***')
            print(f'  解密结果: {combined}')
        elif all(32 <= b <= 126 for b in combined):
            print(f'  全部可打印: {combined}')
        else:
            print(f'  解密结果(hex): {combined.hex()[:40]}...')
    except Exception as e:
        print(f'密钥{i+1}失败: {e}')

# 尝试4: 这可能本身就是密钥，让我们看看用它解密文件中的其他数据
print('\n=== 尝试4: 作为密钥解密文件中的其他16字节块 ===')
with open('20201122_fixed.exe', 'rb') as f:
    file_data = f.read()

# 搜索其他可能的16字节加密块
for offset in [0x3000, 0x3010, 0x3020, 0x3030, 0x3040, 0x3050]:
    if offset + 16 <= len(file_data):
        block = file_data[offset:offset+16]
        if block.count(0) < 12:  # 不是全0
            try:
                cipher = AES.new(data_block1, AES.MODE_ECB)
                decrypted = cipher.decrypt(block)
                if b'flag' in decrypted.lower() or all(32 <= b <= 126 for b in decrypted):
                    print(f'偏移 {hex(offset)}:')
                    print(f'  原始: {block.hex()}')
                    print(f'  解密: {decrypted}')
            except:
                pass
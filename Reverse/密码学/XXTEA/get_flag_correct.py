#!/usr/bin/env python3
"""
CTF解密脚本 - 使用标准XXTEA
参考官方WP
"""
import struct

# 目标常量
TARGET_V20 = bytes([
    0xCE, 0xBC, 0x40, 0x6B, 0x7C, 0x3A, 0x95, 0xC0,
    0xEF, 0x9B, 0x20, 0x20, 0x91, 0xF7, 0x02, 0x35,
    0x23, 0x18, 0x02, 0xC8, 0xE7, 0x56, 0x56, 0xFA
])

print("=" * 60)
print("CTF 解密脚本（标准XXTEA）")
print("=" * 60)

# XXTEA标准实现
_DELTA = 0x9E3779B9

def _long2str(v, w):
    n = (len(v) - 1) << 2
    if w:
        m = v[-1]
        if (m < n - 3) or (m > n):
            return b''
        n = m
    s = struct.pack('<%iL' % len(v), *v)
    return s[0:n] if w else s

def _str2long(s, w):
    n = len(s)
    m = (4 - (n & 3) & 3) + n
    s = s + b"\0" * (m - n)
    v = list(struct.unpack('<%iL' % (m >> 2), s))
    if w:
        v.append(n)
    return v

def xxtea_decrypt(data, key):
    """标准XXTEA解密"""
    if not data:
        return data
    
    v = _str2long(data, False)
    k = _str2long(key.ljust(16, b"\0"), False)
    n = len(v) - 1
    z = v[n]
    y = v[0]
    q = 6 + 52 // (n + 1)
    sum_val = (q * _DELTA) & 0xffffffff
    
    while sum_val != 0:
        e = (sum_val >> 2) & 3
        for p in range(n, 0, -1):
            z = v[p - 1]
            v[p] = (v[p] - ((z >> 5 ^ y << 2) + (y >> 3 ^ z << 4) ^ 
                            (sum_val ^ y) + (k[p & 3 ^ e] ^ z))) & 0xffffffff
            y = v[p]
        z = v[n]
        v[0] = (v[0] - ((z >> 5 ^ y << 2) + (y >> 3 ^ z << 4) ^ 
                        (sum_val ^ y) + (k[0 & 3 ^ e] ^ z))) & 0xffffffff
        y = v[0]
        sum_val = (sum_val - _DELTA) & 0xffffffff
    
    return _long2str(v, True)

# 步骤1: 逆向XOR累积
print("[*] 步骤1: 逆向XOR累积...")
# 官方WP: 每3个为一组，逆向解密
dec = b''

for i in range(7, -1, -1):  # 8组，从后往前
    res = b''
    for j in range(3):  # 每组3字节
        temp = TARGET_V20[i * 3 + j]
        # 需要异或的值
        for m in range(i):
            temp ^= TARGET_V20[m]
        res += bytes([temp])
    dec = res + dec

print(f"逆XOR后: {dec.hex()}")

# 步骤2: 逆向字节置换
print("\n[*] 步骤2: 逆向字节置换...")
# 原始置换: num = [2,0,3,1,6,4,7,5,10,8,11,9,14,12,15,13,18,16,19,17,22,20,23,21]
# 这意味着: enc[num[i]] = dec[i]
# 逆向: dec[num[i]] = enc[i]

num = [2,0,3,1,6,4,7,5,10,8,11,9,14,12,15,13,18,16,19,17,22,20,23,21]
enc = [0] * 24

for i in range(24):
    enc[num[i]] = dec[i]

dec2 = bytes(enc)
print(f"逆置换后: {dec2.hex()}")

# 步骤3: XXTEA解密
print("\n[*] 步骤3: XXTEA解密...")
key = b'flag' + b'\x00' * 12
print(f"密钥: {key}")

plaintext = xxtea_decrypt(dec2, key)
print(f"\n解密结果 (hex): {plaintext.hex()}")
print(f"解密结果 (bytes): {plaintext}")

try:
    flag = plaintext.decode('ascii')
    print("\n" + "=" * 60)
    print(f"🎉 FLAG: {flag}")
    print("=" * 60)
except Exception as e:
    print(f"\n[!] 解码失败: {e}")
    print(f"[*] 尝试去除尾部空字节...")
    flag = plaintext.rstrip(b'\x00').decode('ascii', errors='ignore')
    print(f"🎉 FLAG: {flag}")
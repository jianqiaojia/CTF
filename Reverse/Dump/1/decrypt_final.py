#!/usr/bin/env python3
"""
encrypted_full.bin 是由 WinDbg 使用 .writemem 命令从 crash dump 的内存地址 0x7ff7aefef0b0 导出的 24400 字节加密数据。然后 decrypt_final.py 用 XOR 0x76 解密生成了 decrypted.bin（您在 IDA 中打开的 DLL）。

Final decryption script - XOR with 0x76
Based on WinDbg analysis showing: pxor xmm0, xmm2
where xmm2 contains 16 bytes of 0x76
"""

def decrypt_dll():
    # Read the encrypted data from binary file
    with open('encrypted_full.bin', 'rb') as f:
        encrypted_data = f.read()
    
    print(f"[+] Loaded {len(encrypted_data)} bytes of encrypted data")
    print(f"[+] First 16 bytes (encrypted): {encrypted_data[:16].hex()}")
    
    # The XOR key is simply 0x76 (from WinDbg analysis of xmm2 register)
    xor_key = 0x76
    print(f"[+] XOR Key: 0x{xor_key:02x}")
    
    # Decrypt using simple XOR
    decrypted = bytearray()
    for byte in encrypted_data:
        decrypted_byte = byte ^ xor_key
        decrypted.append(decrypted_byte)
    
    print(f"[+] First 16 bytes (decrypted): {decrypted[:16].hex()}")
    
    # Save the decrypted data
    output_file = 'decrypted.bin'
    with open(output_file, 'wb') as f:
        f.write(decrypted)
    print(f"[+] Decrypted data saved to: {output_file} ({len(decrypted)} bytes)")

if __name__ == '__main__':
    decrypt_dll()
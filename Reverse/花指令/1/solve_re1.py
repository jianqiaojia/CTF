#!/usr/bin/env python3
"""
RE1 CTF Challenge Solver
This solves a reverse engineering challenge using TEA (Tiny Encryption Algorithm) decryption.
"""

import struct

def tea_decrypt(v, k):
    """
    TEA Decryption Algorithm
    v: list of 2 integers (64-bit block split into two 32-bit values)
    k: list of 4 integers (128-bit key)
    """
    v0, v1 = v[0], v[1]
    delta = 0x9e3779b9  # TEA delta constant
    sum_val = (delta * 32) & 0xFFFFFFFF  # Initial sum for decryption
    
    for i in range(32):
        v1 = (v1 - (((v0 << 4) + k[2]) ^ (v0 + sum_val) ^ ((v0 >> 5) + k[3]))) & 0xFFFFFFFF
        v0 = (v0 - (((v1 << 4) + k[0]) ^ (v1 + sum_val) ^ ((v1 >> 5) + k[1]))) & 0xFFFFFFFF
        sum_val = (sum_val - delta) & 0xFFFFFFFF
    
    return [v0, v1]

def to_signed_int(n):
    """Convert unsigned 32-bit int to signed"""
    if n >= 0x80000000:
        return n - 0x100000000
    return n

def to_unsigned_int(n):
    """Convert signed 32-bit int to unsigned"""
    if n < 0:
        return n + 0x100000000
    return n

def main():
    # TEA key from the binary
    key = [57315, 4414, 22679, 13908]
    
    # Encrypted data (target values from the binary)
    encrypted = [
        -2052683475, -1585989955, -1992153835, 362473584,
        1539350109, -1052825282, 632752207, -1380898228
    ]
    
    # Convert to unsigned for proper decryption
    encrypted_unsigned = [to_unsigned_int(x) for x in encrypted]
    
    print("Encrypted values (unsigned):")
    for i in range(0, 8, 2):
        print(f"  Block {i//2}: [{hex(encrypted_unsigned[i])}, {hex(encrypted_unsigned[i+1])}]")
    
    # Decrypt each 64-bit block (2 integers)
    decrypted = []
    for i in range(0, 8, 2):
        block = [encrypted_unsigned[i], encrypted_unsigned[i+1]]
        decrypted_block = tea_decrypt(block, key)
        decrypted.extend(decrypted_block)
        print(f"\nDecrypted block {i//2}: [{hex(decrypted_block[0])}, {hex(decrypted_block[1])}]")
    
    # Convert integers back to bytes (little-endian)
    flag_bytes = b''
    for val in decrypted:
        flag_bytes += struct.pack('<I', val)  # Little-endian unsigned int
    
    # Try to decode as ASCII
    try:
        flag = flag_bytes.decode('ascii')
        print(f"\n{'='*50}")
        print(f"FLAG: {flag}")
        print(f"{'='*50}")
    except:
        print(f"\nFlag (hex): {flag_bytes.hex()}")
        print(f"Flag (raw): {flag_bytes}")
    
    return flag_bytes

if __name__ == "__main__":
    main()
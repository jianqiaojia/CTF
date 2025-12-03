#!/usr/bin/env python3
"""
使用完整IDA数据的正确FLAG计算
"""

def final_correct_calculation():
    print("=== 使用完整IDA数据的正确计算 ===\n")
    
    # 1. shellcode计算密钥
    arg1 = 0xCCC12345  # 0xCCCCCCE5
    arg2 = 0x54321CCC   # 0x543216DC
    
    mask1 = 0x0F0F0F0F
    mask2 = 0xF0F0F0F0
    decrypt_key = (arg1 & mask1) ^ (arg2 & mask2)
    print(f"解密密钥: 0x{decrypt_key:08X} ({decrypt_key})")
    
    # 2. 从IDA获得的完整128字节数据 (0x16310到0x16390)
    complete_data = [
        0x95, 0x13, 0x6e, 0x5c, 0xa2, 0x13, 0x58, 0x5c, 0xb3, 0x13, 0x54, 0x5c, 0x88, 0x13, 0x54, 0x5c, 
        0x9a, 0x13, 0x57, 0x5c, 0xa9, 0x13, 0x50, 0x5c, 0xa2, 0x13, 0x6e, 0x5c, 0xf7, 0x13, 0x2, 0x5c, 
        0xf6, 0x13, 0x1f, 0x5c, 0xb1, 0x13, 0x49, 0x5c, 0xb1, 0x13, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 
        0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 
        0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 
        0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 
        0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 
        0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0, 0x0
    ]
    
    print(f"完整数据长度: {len(complete_data)} 字节")
    
    # 3. 第一阶段解密：对整个128字节数据使用decrypt_key进行XOR
    key_bytes = [(decrypt_key >> (8 * i)) & 0xFF for i in range(4)]
    print(f"密钥字节: {[f'0x{b:02x}' for b in key_bytes]}")
    
    first_decrypted = []
    for i in range(len(complete_data)):
        decrypted_byte = complete_data[i] ^ key_bytes[i % 4]
        first_decrypted.append(decrypted_byte)
    
    # 4. 提取触发文件名 (宽字符串)
    trigger_filename = ""
    for i in range(0, len(first_decrypted) - 1, 2):
        low_byte = first_decrypted[i]
        high_byte = first_decrypted[i + 1]
        
        if low_byte == 0 and high_byte == 0:
            break
            
        # 宽字符：低字节 + 高字节*256
        char_code = low_byte + (high_byte << 8)
        if 0 < char_code < 65536:
            try:
                trigger_filename += chr(char_code)
            except:
                break
    
    print(f"解密的触发文件名: '{trigger_filename}'")
    
    # 5. 计算v2和密钥长度
    v2 = decrypt_key - 1546720155
    print(f"v2 = {decrypt_key} - 1546720155 = {v2}")
    
    if v2 < 0:
        v2 = abs(v2)
        print(f"使用绝对值: {v2}")
    
    # 6. FLAG数据
    flag_data = [
        0x70, 0x74, 0x37, 0x65, 0x47, 0x66, 0x5, 0x61, 0x11, 0x20, 0xc, 0x73, 0x6d, 0x41, 0x3a, 0x73,
        0x36, 0x6d, 0x16, 0x6c, 0x9, 0x5f, 0x28, 0x6e, 0xb, 0x69, 0x31, 0x65, 0x6d, 0x68, 0x5c, 0x6f,
        0x58, 0x5f, 0x6a, 0x72
    ]
    
    print(f"\nFLAG数据长度: {len(flag_data)} 字节")
    
    # 7. 第二阶段解密：模拟sub_113C8中的循环
    print(f"第二阶段解密逻辑:")
    print(f"使用第一阶段解密结果作为密钥")
    print(f"密钥长度由v2确定，但如果v2太大，使用合理值")
    
    # 根据算法，使用first_decrypted作为密钥
    key_length = min(v2, len(first_decrypted), 50) if v2 > 0 else len(trigger_filename.encode('utf-8'))
    print(f"实际使用的密钥长度: {key_length}")
    
    if key_length > 0:
        second_key = first_decrypted[:key_length]
        
        # 执行第二阶段解密 (模拟算法中的128次循环)
        final_flag = []
        v4 = 0
        
        for i in range(128):
            if i < len(flag_data):
                if key_length > 0:
                    decrypted_byte = flag_data[i] ^ second_key[v4]
                    final_flag.append(decrypted_byte)
                    v4 = (v4 + 1) % key_length
                else:
                    final_flag.append(flag_data[i])
        
        # 只保留原flag_data长度的结果
        final_flag = final_flag[:len(flag_data)]
        
        print(f"\n=== 最终解密结果 ===")
        result_str = ""
        clean_str = ""
        
        for i, byte_val in enumerate(final_flag):
            char = chr(byte_val) if 32 <= byte_val <= 126 else f"[{byte_val:02x}]"
            result_str += char
            if 32 <= byte_val <= 126:
                clean_str += chr(byte_val)
            print(f"位置 {i:2d}: 0x{byte_val:02x} = {char}")
        
        print(f"\n完整结果: {result_str}")
        print(f"纯文本:   {clean_str}")
        
        return clean_str
    
    # 8. 如果上面失败，尝试其他策略
    print(f"\n=== 备选解密策略 ===")
    
    # 策略1：直接用触发文件名作为密钥
    if trigger_filename:
        filename_key = [ord(c) for c in trigger_filename if c.isalnum()]
        alt_result = []
        
        for i in range(len(flag_data)):
            if filename_key:
                alt_result.append(flag_data[i] ^ filename_key[i % len(filename_key)])
            else:
                alt_result.append(flag_data[i])
        
        alt_clean = "".join([chr(b) for b in alt_result if 32 <= b <= 126])
        print(f"策略1 - 文件名字符作为密钥: {alt_clean}")
    
    # 策略2：用decrypt_key的字节循环
    key_cycle = [(decrypt_key >> (8 * i)) & 0xFF for i in range(4)]
    alt2_result = []
    
    for i in range(len(flag_data)):
        alt2_result.append(flag_data[i] ^ key_cycle[i % 4])
    
    alt2_clean = "".join([chr(b) for b in alt2_result if 32 <= b <= 126])
    print(f"策略2 - 原始密钥循环: {alt2_clean}")
    
    return None

if __name__ == "__main__":
    result = final_correct_calculation()
    if result:
        print(f"\n🎉 最终FLAG: {result}")
    else:
        print(f"\n⚠️  需要进一步分析")
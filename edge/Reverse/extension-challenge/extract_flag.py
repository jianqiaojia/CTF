import base64
from PIL import Image
import sys

def extract_lsb_from_image(image_path):
    """从图像中提取LSB隐写内容"""
    try:
        img = Image.open(image_path)
        img = img.convert('RGB')
        width, height = img.size
        
        binary = ''
        for y in range(height):
            for x in range(width):
                r, g, b = img.getpixel((x, y))
                # 提取蓝色通道的最低位
                binary += str(b & 1)
        
        # 将二进制转换为文本
        text = ''
        for i in range(0, len(binary), 8):
            byte = binary[i:i+8]
            if len(byte) == 8:
                # 检查终止条件
                if byte == '11111111' and i + 8 < len(binary):
                    next_byte = binary[i+8:i+16]
                    if next_byte == '11111110':
                        break
                
                char_code = int(byte, 2)
                if char_code == 0:
                    break
                if 32 <= char_code <= 126:  # 可打印ASCII字符
                    text += chr(char_code)
        
        return text
    except Exception as e:
        print(f"Error extracting from image: {e}")
        return ''

def decrypt_parts():
    """解密flag的各个部分"""
    print("=== CTF Flag Extraction ===\n")
    
    # Part 1: 从flag.png提取
    print("Part 1: 从flag.png提取隐写内容...")
    part1 = extract_lsb_from_image('flag.png')
    print(f"Part 1: {part1}")
    
    # Part 2: 解密
    print("\nPart 2: 解密编码字符串...")
    part2_b64 = 'b30EXgFARVwERAEAXm8='
    part2_decoded = base64.b64decode(part2_b64)
    part2_decrypted = ''.join(chr(b ^ 0x30) for b in part2_decoded)
    print(f"Part 2: {part2_decrypted}")
    
    # Part 3: 解密
    print("\nPart 3: 解密编码字符串...")
    part3_b64 = 'IwhUDAxTDgdTHQ=='
    part3_decoded = base64.b64decode(part3_b64)  
    part3_decrypted = ''.join(chr(b ^ 0x60) for b in part3_decoded)
    print(f"Part 3: {part3_decrypted}")
    
    # 组合完整flag
    complete_flag = part1 + part2_decrypted + part3_decrypted
    print(f"\n🚩 完整FLAG: {complete_flag}")
    
    return complete_flag

if __name__ == "__main__":
    flag = decrypt_parts()
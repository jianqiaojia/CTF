import struct

def analyze_png(filename):
    with open(filename, 'rb') as f:
        data = f.read()
    
    # 检查PNG签名
    if data[:8] != b'\x89PNG\r\n\x1a\n':
        print("不是有效的PNG文件")
        return
    
    print("PNG文件分析:")
    print("-" * 50)
    
    # 解析PNG chunks
    pos = 8
    chunks = []
    while pos < len(data):
        if pos + 8 > len(data):
            break
        
        length = struct.unpack('>I', data[pos:pos+4])[0]
        chunk_type = data[pos+4:pos+8].decode('ascii', errors='ignore')
        chunk_data = data[pos+8:pos+8+length]
        crc = struct.unpack('>I', data[pos+8+length:pos+12+length])[0]
        
        chunks.append({
            'type': chunk_type,
            'length': length,
            'pos': pos
        })
        
        print(f"Chunk: {chunk_type}, 长度: {length}, 位置: {pos}")
        
        # 检查是否有特殊的文本chunk
        if chunk_type in ['tEXt', 'zTXt', 'iTXt']:
            try:
                text = chunk_data.decode('latin1', errors='ignore')
                print(f"  文本内容: {text[:100]}")
            except:
                pass
        
        pos += 12 + length
        
        if chunk_type == 'IEND':
            break
    
    print(f"\n文件总大小: {len(data)}")
    print(f"PNG结构结束位置: {pos}")
    
    # 检查文件末尾是否有额外数据
    if pos < len(data):
        extra_data = data[pos:]
        print(f"\n发现额外数据! 大小: {len(extra_data)} 字节")
        print(f"额外数据开始的前100字节:")
        print(extra_data[:100])
        
        # 尝试找到可读文本
        try:
            text = extra_data.decode('utf-8', errors='ignore')
            if 'EdgeCTF' in text or 'flag' in text.lower():
                print(f"\n可能的Flag内容:")
                print(text[:500])
        except:
            pass
        
        # 查找EdgeCTF字符串
        search_str = b'EdgeCTF'
        if search_str in extra_data:
            idx = extra_data.index(search_str)
            print(f"\n找到 'EdgeCTF' 在额外数据中的位置: {idx}")
            print(f"周围内容: {extra_data[max(0, idx-20):idx+100]}")
    
    # 在整个文件中搜索EdgeCTF
    if b'EdgeCTF' in data:
        print(f"\n在文件中找到 'EdgeCTF'!")
        idx = data.index(b'EdgeCTF')
        print(f"位置: {idx}")
        print(f"周围内容: {data[max(0, idx-20):idx+100]}")

if __name__ == "__main__":
    analyze_png('message.png')
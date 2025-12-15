#!/usr/bin/env python3
"""
Advanced steganography analysis with PNG chunk inspection
"""

import struct
import zlib
from PIL import Image
import numpy as np

def parse_png_chunks(filepath):
    """Parse all PNG chunks including text chunks"""
    print("\n[*] Parsing PNG chunks in detail...")
    
    with open(filepath, 'rb') as f:
        # Check PNG signature
        signature = f.read(8)
        if signature != b'\x89PNG\r\n\x1a\n':
            print("[-] Not a valid PNG file!")
            return
        
        print("[+] Valid PNG signature found")
        
        while True:
            # Read chunk length
            length_data = f.read(4)
            if len(length_data) < 4:
                break
            
            length = struct.unpack('>I', length_data)[0]
            
            # Read chunk type
            chunk_type = f.read(4)
            if len(chunk_type) < 4:
                break
            
            # Read chunk data
            chunk_data = f.read(length)
            
            # Read CRC
            crc = f.read(4)
            
            chunk_name = chunk_type.decode('latin1', errors='ignore')
            print(f"\n[+] Chunk: {chunk_name}, Length: {length}")
            
            # Check for text chunks
            if chunk_type in [b'tEXt', b'zTXt', b'iTXt']:
                print(f"[+] TEXT CHUNK FOUND: {chunk_type.decode()}")
                try:
                    if chunk_type == b'tEXt':
                        # tEXt: keyword\0text
                        null_pos = chunk_data.find(b'\x00')
                        if null_pos != -1:
                            keyword = chunk_data[:null_pos].decode('latin1')
                            text = chunk_data[null_pos+1:].decode('latin1', errors='ignore')
                            print(f"    Keyword: {keyword}")
                            print(f"    Text: {text}")
                    
                    elif chunk_type == b'zTXt':
                        # zTXt: keyword\0compression\0compressed_text
                        null_pos = chunk_data.find(b'\x00')
                        if null_pos != -1:
                            keyword = chunk_data[:null_pos].decode('latin1')
                            compression = chunk_data[null_pos+1]
                            compressed = chunk_data[null_pos+2:]
                            text = zlib.decompress(compressed).decode('latin1', errors='ignore')
                            print(f"    Keyword: {keyword}")
                            print(f"    Compression: {compression}")
                            print(f"    Text: {text}")
                    
                    elif chunk_type == b'iTXt':
                        # iTXt: more complex format
                        print(f"    Raw data: {chunk_data[:100]}")
                        try:
                            decoded = chunk_data.decode('utf-8', errors='ignore')
                            print(f"    Decoded: {decoded}")
                        except:
                            pass
                
                except Exception as e:
                    print(f"    Error decoding: {e}")
                    print(f"    Raw data: {chunk_data[:100]}")
            
            # Check for custom chunks
            elif chunk_type[0:1].islower():
                print(f"[!] Ancillary (possibly custom) chunk: {chunk_name}")
                print(f"    Data preview: {chunk_data[:100]}")
                try:
                    decoded = chunk_data.decode('utf-8', errors='ignore')
                    if decoded.strip():
                        print(f"    Decoded: {decoded[:200]}")
                except:
                    pass
            
            if chunk_type == b'IEND':
                print("\n[+] Reached IEND chunk")
                # Check if there's anything after IEND
                remaining = f.read()
                if remaining:
                    print(f"[!] Found {len(remaining)} bytes after IEND!")
                    print(f"    Data: {remaining[:200]}")
                break

def extract_all_bits(filepath):
    """Extract different bit planes, not just LSB"""
    print("\n[*] Extracting all bit planes...")
    
    img = Image.open(filepath)
    img_array = np.array(img)
    
    for bit in range(8):
        print(f"\n[*] Bit plane {bit}:")
        
        for channel, color in enumerate(['R', 'G', 'B']):
            if channel >= img_array.shape[2]:
                break
            
            # Extract specific bit
            bit_plane = (img_array[:, :, channel] >> bit) & 1
            
            # Try to read as text
            bits = ''.join(bit_plane.flatten().astype(str))
            
            # Convert to bytes
            message = ''
            for i in range(0, min(len(bits), 10000), 8):
                byte = bits[i:i+8]
                if len(byte) == 8:
                    char_code = int(byte, 2)
                    if 32 <= char_code <= 126:
                        message += chr(char_code)
                    elif char_code == 0 and len(message) > 10:
                        break
            
            if len(message) > 20:
                print(f"  [{color}] Found possible text (len={len(message)}): {message[:100]}")
                
                # Save to file
                filename = f'bit{bit}_{color}.txt'
                with open(filename, 'w') as f:
                    f.write(message)
            
            # Create visualization
            visual = (bit_plane * 255).astype(np.uint8)
            Image.fromarray(visual).save(f'bit{bit}_{color}_visual.png')

def check_pixel_differences(filepath):
    """Check for patterns in pixel value differences"""
    print("\n[*] Analyzing pixel value patterns...")
    
    img = Image.open(filepath)
    img_array = np.array(img)
    
    # Check if consecutive pixels have meaningful differences
    for channel, color in enumerate(['R', 'G', 'B']):
        if channel >= img_array.shape[2]:
            break
        
        flat = img_array[:, :, channel].flatten()
        
        # Get differences between consecutive pixels
        diffs = np.diff(flat) & 1  # LSB of differences
        
        bits = ''.join(diffs.astype(str))
        message = ''
        
        for i in range(0, min(len(bits), 10000), 8):
            byte = bits[i:i+8]
            if len(byte) == 8:
                char_code = int(byte, 2)
                if 32 <= char_code <= 126:
                    message += chr(char_code)
                elif char_code == 0 and len(message) > 10:
                    break
        
        if len(message) > 20:
            print(f"[{color}] Pixel diff message: {message[:100]}")

def main():
    filepath = 'airobot_stego.png'
    
    parse_png_chunks(filepath)
    extract_all_bits(filepath)
    check_pixel_differences(filepath)
    
    print("\n[*] Advanced analysis complete!")

if __name__ == '__main__':
    main()
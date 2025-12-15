#!/usr/bin/env python3
"""
CTF Steganography Challenge Solver
Analyzes PNG files for hidden messages using various techniques
"""

import os
import sys
from PIL import Image
import numpy as np

def check_file_structure(filepath):
    """Check for data appended after PNG IEND chunk"""
    print("\n[*] Checking file structure...")
    with open(filepath, 'rb') as f:
        content = f.read()
        
    # Find IEND chunk (marks end of PNG)
    iend_marker = b'IEND'
    iend_pos = content.find(iend_marker)
    
    if iend_pos != -1:
        # IEND chunk is 12 bytes: 4 (length) + 4 (IEND) + 4 (CRC)
        iend_end = iend_pos + 8  # After IEND + CRC
        extra_data = content[iend_end:]
        
        if extra_data:
            print(f"[+] Found {len(extra_data)} bytes after IEND chunk!")
            print(f"[+] Extra data (first 200 bytes): {extra_data[:200]}")
            
            # Try to decode as text
            try:
                decoded = extra_data.decode('utf-8', errors='ignore')
                if decoded.strip():
                    print(f"[+] Decoded text: {decoded[:500]}")
            except:
                pass
            
            # Save to file
            with open('hidden_data.bin', 'wb') as f:
                f.write(extra_data)
            print("[+] Saved extra data to 'hidden_data.bin'")
            return True
    
    print("[-] No extra data found after IEND")
    return False

def extract_lsb(filepath):
    """Extract LSB steganography from all color channels"""
    print("\n[*] Analyzing LSB (Least Significant Bit) steganography...")
    
    img = Image.open(filepath)
    img_array = np.array(img)
    
    print(f"[+] Image shape: {img_array.shape}")
    print(f"[+] Image mode: {img.mode}")
    
    # Extract LSB from each channel
    if len(img_array.shape) == 3:
        channels = img_array.shape[2]
        for channel in range(channels):
            channel_names = ['Red', 'Green', 'Blue', 'Alpha']
            print(f"\n[*] Extracting LSB from {channel_names[channel]} channel...")
            
            # Get LSB
            lsb = img_array[:, :, channel] & 1
            
            # Convert to binary string
            bits = ''.join(lsb.flatten().astype(str))
            
            # Try to decode as ASCII (8 bits per character)
            try:
                message = ''
                for i in range(0, len(bits) - 8, 8):
                    byte = bits[i:i+8]
                    char_code = int(byte, 2)
                    if 32 <= char_code <= 126:  # Printable ASCII
                        message += chr(char_code)
                    elif char_code == 0:  # Null terminator
                        break
                
                if len(message) > 10:  # Likely found something
                    print(f"[+] Possible message in {channel_names[channel]} channel:")
                    print(f"    {message[:200]}")
                    
                    with open(f'lsb_{channel_names[channel].lower()}.txt', 'w') as f:
                        f.write(message)
            except Exception as e:
                print(f"[-] Error decoding: {e}")
    
    # Create LSB visualization
    print("\n[*] Creating LSB visualization...")
    if len(img_array.shape) == 3:
        lsb_img = np.zeros_like(img_array)
        for i in range(img_array.shape[2]):
            lsb_img[:, :, i] = (img_array[:, :, i] & 1) * 255
        
        Image.fromarray(lsb_img.astype(np.uint8)).save('lsb_visual.png')
        print("[+] Saved LSB visualization to 'lsb_visual.png'")

def analyze_metadata(filepath):
    """Extract and display image metadata"""
    print("\n[*] Checking metadata...")
    
    img = Image.open(filepath)
    
    # Check for EXIF data
    if hasattr(img, '_getexif') and img._getexif():
        exif = img._getexif()
        print("[+] EXIF data found:")
        for tag, value in exif.items():
            print(f"    {tag}: {value}")
    
    # Check PNG info chunks
    if hasattr(img, 'info'):
        print("[+] PNG info chunks:")
        for key, value in img.info.items():
            print(f"    {key}: {value}")
            if isinstance(value, str) and len(value) > 0:
                print(f"    [+] Possible hidden message in {key}: {value}")

def check_color_planes(filepath):
    """Check individual color planes for hidden images"""
    print("\n[*] Checking individual color planes...")
    
    img = Image.open(filepath)
    img_array = np.array(img)
    
    if len(img_array.shape) == 3:
        for i, color in enumerate(['red', 'green', 'blue', 'alpha'][:img_array.shape[2]]):
            plane = np.zeros_like(img_array)
            plane[:, :, i] = img_array[:, :, i]
            Image.fromarray(plane.astype(np.uint8)).save(f'plane_{color}.png')
            print(f"[+] Saved {color} plane to 'plane_{color}.png'")

def main():
    filepath = 'airobot_stego.png'
    
    if not os.path.exists(filepath):
        print(f"[-] File {filepath} not found!")
        return
    
    print("="*60)
    print("CTF Steganography Analysis Tool")
    print("="*60)
    
    # Run all analysis techniques
    analyze_metadata(filepath)
    check_file_structure(filepath)
    extract_lsb(filepath)
    check_color_planes(filepath)
    
    print("\n" + "="*60)
    print("[*] Analysis complete! Check the generated files.")
    print("="*60)

if __name__ == '__main__':
    main()
#!/usr/bin/env python3
"""
Extract all readable strings from the PNG file
"""

def extract_strings(filepath, min_length=4):
    """Extract printable strings from binary file"""
    print(f"\n[*] Extracting strings (min length: {min_length})...")
    
    with open(filepath, 'rb') as f:
        content = f.read()
    
    strings = []
    current = b''
    
    for byte in content:
        # Check if printable ASCII
        if 32 <= byte <= 126:
            current += bytes([byte])
        else:
            if len(current) >= min_length:
                strings.append(current.decode('ascii'))
            current = b''
    
    # Don't forget last string
    if len(current) >= min_length:
        strings.append(current.decode('ascii'))
    
    print(f"[+] Found {len(strings)} strings")
    
    # Look for interesting patterns
    interesting = []
    for s in strings:
        # Look for flag formats
        if any(pattern in s.lower() for pattern in ['flag', 'ctf', 'password', 'secret', 'key']):
            interesting.append(s)
        # Look for base64-like strings
        elif len(s) > 20 and s.replace('=', '').replace('+', '').replace('/', '').isalnum():
            interesting.append(s)
        # Look for hex strings
        elif len(s) > 20 and all(c in '0123456789abcdefABCDEF' for c in s):
            interesting.append(s)
    
    print("\n[*] All strings:")
    for s in strings[:50]:  # Print first 50
        print(f"    {s}")
    
    if interesting:
        print("\n[!] Interesting strings found:")
        for s in interesting:
            print(f"    {s}")
    
    # Save all strings to file
    with open('extracted_strings.txt', 'w') as f:
        f.write('\n'.join(strings))
    
    print("\n[+] All strings saved to 'extracted_strings.txt'")
    
    return strings

def check_file_format(filepath):
    """Check file format and look for embedded files"""
    print("\n[*] Checking for embedded files...")
    
    with open(filepath, 'rb') as f:
        content = f.read()
    
    # Common file signatures
    signatures = {
        b'PK\x03\x04': 'ZIP archive',
        b'\x1f\x8b\x08': 'GZIP',
        b'Rar!': 'RAR archive',
        b'\x50\x4b\x03\x04': 'ZIP',
        b'\x89PNG': 'PNG image',
        b'\xff\xd8\xff': 'JPEG image',
        b'GIF8': 'GIF image',
        b'%PDF': 'PDF document',
    }
    
    for sig, desc in signatures.items():
        positions = []
        start = 0
        while True:
            pos = content.find(sig, start)
            if pos == -1:
                break
            positions.append(pos)
            start = pos + 1
        
        if len(positions) > 1:  # More than one occurrence (first is the file itself)
            print(f"[!] Multiple {desc} signatures found at positions: {positions}")
            
            # Try to extract
            for i, pos in enumerate(positions[1:], 1):
                extracted = content[pos:]
                filename = f'embedded_{desc.replace(" ", "_")}_{i}.bin'
                with open(filename, 'wb') as f:
                    f.write(extracted)
                print(f"    Extracted to: {filename}")

def analyze_pixel_order(filepath):
    """Read pixels in different orders to find hidden messages"""
    from PIL import Image
    import numpy as np
    
    print("\n[*] Analyzing different pixel reading orders...")
    
    img = Image.open(filepath)
    img_array = np.array(img)
    
    height, width = img_array.shape[:2]
    
    # Try reading in spiral order
    print("[*] Trying spiral order...")
    # Create spiral coordinates
    
    # Try reading by rows with LSB
    print("[*] Reading LSB row by row...")
    bits = ''
    for row in img_array:
        for pixel in row:
            for channel in pixel:
                bits += str(channel & 1)
    
    # Convert to text
    message = ''
    for i in range(0, min(len(bits), 100000), 8):
        byte = bits[i:i+8]
        if len(byte) == 8:
            char_code = int(byte, 2)
            if 32 <= char_code <= 126:
                message += chr(char_code)
            elif char_code == 0 and len(message) > 20:
                if 'flag' in message.lower() or 'ctf' in message.lower():
                    print(f"[!] FOUND MESSAGE: {message}")
                    return message
    
    if len(message) > 50:
        print(f"[+] Row-by-row message (first 200 chars): {message[:200]}")
        with open('row_order_message.txt', 'w') as f:
            f.write(message)

def main():
    filepath = 'airobot_stego.png'
    
    strings = extract_strings(filepath, min_length=4)
    check_file_format(filepath)
    analyze_pixel_order(filepath)
    
    print("\n" + "="*60)
    print("[*] String extraction complete!")
    print("="*60)

if __name__ == '__main__':
    main()
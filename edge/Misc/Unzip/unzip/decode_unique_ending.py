#!/usr/bin/env python3
import base64

# The unique ending string
unique = '&}K9zrO$g0}p`Y04o3l0EW+88UP3&0Cf$iKmdA=Q#68VsRn~gKxlgJyIptv{ScHD(h!sth5`Wz03_|#6IgbwXw&zxYAfDN=FkEG6czkk$rRy2L03CHH~'

print(f"Unique string: {unique}")
print(f"Length: {len(unique)}\n")

# The unique string contains characters that look like they could be:
# - Base85 encoded
# - ASCII85 encoded  
# - Or some custom encoding

# Let's try various approaches

# 1. Check if removing certain characters reveals something
for remove_char in ['&', '$', '~', '#', '|']:
    cleaned = unique.replace(remove_char, '')
    print(f"Removing '{remove_char}': {cleaned}")
    if 'Edge' in cleaned or 'CTF' in cleaned:
        print(f"  -> Found match!")

print("\n" + "="*80 + "\n")

# 2. Try base64 on parts that look base64-ish
# Looking for sequences with A-Za-z0-9+/=
import re
base64_pattern = r'[A-Za-z0-9+/=]{20,}'
matches = re.findall(base64_pattern, unique)
print(f"Base64-like sequences found: {len(matches)}")
for i, match in enumerate(matches):
    print(f"  Match {i}: {match}")
    try:
        decoded = base64.b64decode(match + '==')  # Add padding
        print(f"    Decoded: {decoded}")
        if b'Edge' in decoded or b'CTF' in decoded:
            print(f"    -> Contains flag marker!")
    except:
        pass

print("\n" + "="*80 + "\n")

# 3. The pattern ends with exactly this string - maybe it's telling us
# the rotation offset or key?
# Let's see if it's related to the base pattern

base_pattern = 'LRx4!F+o`-Q(1XNt&;&?jsyUp000Oe05E_}Mna$^sS1FXF+'

# Try XOR with the base pattern
print("Trying XOR with base pattern (first chars):")
for i in range(min(len(unique), len(base_pattern))):
    xor_val = ord(unique[i]) ^ ord(base_pattern[i])
    print(f"  {unique[i]} ^ {base_pattern[i]} = {xor_val} ({chr(xor_val) if 32 <= xor_val < 127 else '?'})")

print("\n" + "="*80 + "\n")

# 4. Maybe the flag IS in the base pattern itself!
print(f"Base pattern: {base_pattern}")
if 'Edge' in base_pattern or '{' in base_pattern:
    print("Pattern contains flag markers!")

# 5. Let's look at what comes BEFORE the unique string
with open('decoded_text.txt', 'r') as f:
    content = f.read()

# Find where the unique string starts
unique_pos = content.find(unique)
if unique_pos != -1:
    before = content[max(0, unique_pos-200):unique_pos]
    print(f"200 chars before unique string:")
    print(before)
    print(f"\nUnique string position: {unique_pos}")
    print(f"Content length: {len(content)}")
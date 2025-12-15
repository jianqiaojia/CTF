#!/usr/bin/env python3

# The unique ending string
unique_str = '&}K9zrO$g0}p`Y04o3l0EW+88UP3&0Cf$iKmdA=Q#68VsRn~gKxlgJyIptv{ScHD(h!sth5`Wz03_|#6IgbwXw&zxYAfDN=FkEG6czkk$rRy2L03CHH~'

print(f"Unique string: {unique_str}")
print(f"Length: {len(unique_str)}\n")

# Find all { and } positions
for i, c in enumerate(unique_str):
    if c in '{}':
        print(f"Position {i}: '{c}' - context: ...{unique_str[max(0,i-10):i+11]}...")

# Look for EdgeCTF pattern by combining parts
# The transition shows: ...FXF+o`-Q&}K9zr...
# Maybe we need to look at the actual file ending more carefully

with open('decoded_text.txt', 'r', encoding='utf-8') as f:
    content = f.read()

# Get the absolute end
print(f"\n\nLast 300 characters of entire file:")
print(repr(content[-300:]))

# Search for any occurrence of "Edge" or "CTF"
if 'Edge' in content:
    print("\n'Edge' found in content!")
    idx = content.find('Edge')
    print(f"Position: {idx}")
    print(f"Context: {content[idx:idx+50]}")
else:
    print("\n'Edge' NOT found")

if 'CTF' in content:
    print("\n'CTF' found in content!")
    idx = content.find('CTF')
    print(f"Position: {idx}")
    print(f"Context: {content[idx-10:idx+50]}")
else:
    print("\n'CTF' NOT found")
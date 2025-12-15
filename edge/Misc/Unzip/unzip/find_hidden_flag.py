#!/usr/bin/env python3

# The repeating pattern
pattern = 'LRx4!F+o`-Q(1XNt&;&?jsyUp000Oe05E_}Mna$^sS1FXF+'

print(f"Repeating pattern: {pattern}")
print(f"Length: {len(pattern)}\n")

# Look for flag-like sequences
# Check each character position across repetitions
with open('decoded_text.txt', 'r', encoding='utf-8') as f:
    content = f.read()

# Count how many times the pattern repeats
pattern_count = content.count(pattern)
print(f"Pattern appears {pattern_count} times\n")

# Try taking first character of each repetition
first_chars = ''
pos = 0
for i in range(pattern_count):
    idx = content.find(pattern, pos)
    if idx != -1:
        first_chars += pattern[0]
        pos = idx + 1

# Try taking specific positions from each pattern
# Let's try each position 0-49 and see if any spell out something
for char_pos in range(min(50, len(pattern))):
    chars = ''
    pos = 0
    for i in range(min(100, pattern_count)):  # Check first 100 repetitions
        idx = content.find(pattern, pos)
        if idx != -1 and idx + char_pos < len(content):
            chars += content[idx + char_pos]
            pos = idx + len(pattern)
    
    # Check if this looks like it could contain "Edge" or "CTF"
    if 'Edge' in chars or 'CTF' in chars or 'edge' in chars:
        print(f"Position {char_pos}: {chars[:100]}")
        print(f"Full: {chars}\n")

# Maybe the flag is encoded by taking every Nth character?
# Let's try different strides
print("\nTrying different character strides through entire file:")
for stride in [52, 53, 54, 100, 200, 500, 1000]:
    chars = content[::stride]
    if 'Edge' in chars or 'CTF' in chars or 'edge' in chars or 'flag' in chars:
        print(f"Stride {stride}: FOUND!")
        print(chars[:200])
#!/usr/bin/env python3

with open('decoded_text.txt', 'r', encoding='utf-8') as f:
    content = f.read()

# The chunks rotate through a 52-character base pattern
# Each chunk starts at a different offset in the pattern
# Let's reconstruct the original by aligning them

chunk_size = 52
chunks = []
for i in range(0, min(5000, len(content) - chunk_size), chunk_size):
    chunks.append(content[i:i+chunk_size])

print(f"Total chunks analyzed: {len(chunks)}")

# The pattern repeats every 52 chunks (one full rotation)
# Let's extract the base pattern by aligning the chunks

# Method 1: Build the base pattern from the rotation
# If chunk i starts at position (i % 52), we can reconstruct
base_pattern = [''] * chunk_size

for i, chunk in enumerate(chunks[:52]):  # First 52 chunks cover all rotations
    offset = i % chunk_size
    for j in range(len(chunk)):
        pos = (j - offset) % chunk_size
        if base_pattern[pos] == '':
            base_pattern[pos] = chunk[j]

reconstructed = ''.join(base_pattern)
print(f"\nReconstructed base pattern ({len(reconstructed)} chars):")
print(reconstructed)

# Now check if reading vertically through all chunks gives us the flag
print("\n" + "="*80)
print("Trying to extract flag by reading through chunk positions:")

for pos in range(52):
    vertical_read = ''.join(chunks[i][pos] if pos < len(chunks[i]) else '' for i in range(min(200, len(chunks))))
    if 'Edge' in vertical_read or 'CTF' in vertical_read or '{' in vertical_read[:50]:
        print(f"\nPosition {pos} (first 200 chars):")
        print(vertical_read[:200])
        if 'EdgeCTF{' in vertical_read:
            # Extract the flag
            start = vertical_read.find('EdgeCTF{')
            end = vertical_read.find('}', start)
            if end != -1:
                flag = vertical_read[start:end+1]
                print(f"\n🎯 FOUND FLAG: {flag}")
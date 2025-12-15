#!/usr/bin/env python3

with open('decoded_text.txt', 'r', encoding='utf-8') as f:
    content = f.read()

# The pattern rotates - each chunk is the same pattern shifted
# Let's extract by taking the first character of each chunk

chunk_size = 52
chunks = [content[i:i+chunk_size] for i in range(0, len(content) - 100, chunk_size)]

print(f"Total chunks: {len(chunks)}")
print(f"First few chunks:")
for i in range(min(5, len(chunks))):
    print(f"  {i}: {chunks[i]}")

# Extract the first character from each chunk
flag_chars = ''.join(chunk[0] if len(chunk) > 0 else '' for chunk in chunks[:1000])
print(f"\nFirst characters from each chunk (first 1000):")
print(flag_chars)
print()

# Try each position
for pos in range(52):
    chars = ''.join(chunk[pos] if pos < len(chunk) else '' for chunk in chunks[:200])
    if 'EdgeCTF{' in chars or 'Edge' in chars:
        print(f"Position {pos} contains 'Edge' or flag!")
        print(f"Content: {chars}")
        print()
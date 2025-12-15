#!/usr/bin/env python3

with open('decoded_text.txt', 'r', encoding='utf-8') as f:
    content = f.read()

# The pattern length seems to be around 47-52 characters
# Let's find what the actual repeating unit is
# Based on the output, it seems like chunks repeat with variation

# Let's try a different approach: find the chunk size
# Split into equal chunks and compare them
chunk_size = 52  # Trying the full pattern with end

# Try to identify the pattern by looking at the first few chunks
print("First 500 characters:")
print(content[:500])
print("\n" + "="*80 + "\n")

# The pattern seems to be: LRx4!F+o`-Q(1XNt&;&?jsyUp000Oe05E_}Mna$^sS1FXF+
# Let me look for where it varies

# Split into chunks of 52 characters
chunks = []
for i in range(0, len(content) - 52, 52):
    chunks.append(content[i:i+52])

print(f"Total chunks of 52 chars: {len(chunks)}")

# Compare consecutive chunks to find differences
differences = []
if len(chunks) > 1:
    reference = chunks[0]
    for i, chunk in enumerate(chunks[1:100], 1):  # Check first 100
        for j, (c1, c2) in enumerate(zip(reference, chunk)):
            if c1 != c2:
                differences.append((i, j, c2))
                print(f"Chunk {i}, Position {j}: '{c1}' -> '{c2}'")
        if len(chunks) > 1 and i == 1:
            reference = chunk

# Try extracting the differing characters
print("\n" + "="*80)
print("Trying to extract flag from differences:")

# Let's try different chunk sizes
for size in [47, 48, 49, 50, 51, 52, 53]:
    print(f"\nChunk size {size}:")
    chunks = [content[i:i+size] for i in range(0, min(10000, len(content) - size), size)]
    
    if len(chunks) < 2:
        continue
        
    # Find position that varies
    varying_positions = set()
    reference = chunks[0]
    
    for chunk in chunks[1:min(50, len(chunks))]:
        if len(chunk) == len(reference):
            for j, (c1, c2) in enumerate(zip(reference, chunk)):
                if c1 != c2:
                    varying_positions.add(j)
    
    if varying_positions:
        print(f"  Varying positions: {sorted(varying_positions)}")
        
        # Extract characters from varying positions
        for pos in sorted(varying_positions):
            chars = ''.join(chunk[pos] if pos < len(chunk) else '?' for chunk in chunks[:100])
            if 'Edge' in chars or 'CTF' in chars or '{' in chars:
                print(f"  Position {pos}: {chars}")
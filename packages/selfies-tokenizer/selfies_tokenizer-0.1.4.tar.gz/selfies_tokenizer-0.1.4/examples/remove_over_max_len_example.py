"""
Example demonstrating the remove_over_max_len feature.

This feature allows you to completely remove sequences that exceed max_len
instead of truncating them, which is useful when you don't want to lose
information by truncating long sequences.
"""

from selfies_tokenizer import SELFIESTokenizer

# Example SELFIES strings with varying lengths
selfies_data = [
    '[C][=O]',  # Short: 2 tokens + 2 special = 4 total
    '[N][C][C]',  # Medium: 3 tokens + 2 special = 5 total
    '[C][Branch1][C][O][C][C][C]',  # Long: 7 tokens + 2 special = 9 total
    '[C][=C]',  # Short: 2 tokens + 2 special = 4 total
    '[N][C][C][C][C][C]',  # Very long: 6 tokens + 2 special = 8 total
]

print("=" * 70)
print("REMOVE_OVER_MAX_LEN EXAMPLE")
print("=" * 70)

# Initialize and fit tokenizer
tokenizer = SELFIESTokenizer()
tokenizer.fit(selfies_data)

print(f"\nOriginal data ({len(selfies_data)} sequences):")
for idx, s in enumerate(selfies_data):
    tokens = tokenizer.tokenize(s)
    seq_len = len(tokens) + 2  # +2 for <start> and <end>
    print(f"  [{idx}] {s:30s} → {len(tokens)} tokens ({seq_len} with special tokens)")

# Set max_len
max_len = 6

print(f"\n{'=' * 70}")
print(f"ENCODING WITH max_len={max_len}")
print(f"{'=' * 70}")

# Example 1: Standard encoding with truncation
print(f"\n1. Standard encoding (truncation enabled):")
encoded_truncate = tokenizer.encode(
    selfies_data,
    max_len=max_len,
    padding=True,
    truncation=True,
    add_special_tokens=True
)
print(f"   → Encoded {len(encoded_truncate)} sequences")
print(f"   → All sequences kept, long ones truncated to max_len={max_len}")
for idx, enc in enumerate(encoded_truncate):
    print(f"   [{idx}] Length: {len(enc)}")

# Example 2: Encoding with remove_over_max_len
print(f"\n2. Encoding with remove_over_max_len=True:")
encoded_filtered = tokenizer.encode(
    selfies_data,
    max_len=max_len,
    padding=True,
    truncation=True,
    add_special_tokens=True,
    remove_over_max_len=True
)
print(f"   → Encoded {len(encoded_filtered)} sequences")
print(f"   → Dropped sequences: {tokenizer.dropped_indices}")
print(f"   → Kept sequences: {[i for i in range(len(selfies_data)) if i not in tokenizer.dropped_indices]}")

# Show which sequences were kept
print(f"\n   Kept sequences:")
kept_idx = 0
for idx in range(len(selfies_data)):
    if idx not in tokenizer.dropped_indices:
        print(f"   [{idx}] {selfies_data[idx]:30s} → {encoded_filtered[kept_idx]}")
        kept_idx += 1

# Show which sequences were dropped
if tokenizer.dropped_indices:
    print(f"\n   Dropped sequences (exceeded max_len={max_len}):")
    for idx in tokenizer.dropped_indices:
        tokens = tokenizer.tokenize(selfies_data[idx])
        seq_len = len(tokens) + 2
        print(f"   [{idx}] {selfies_data[idx]:30s} → length {seq_len} > {max_len}")

# Example 3: Decode the filtered results
print(f"\n3. Decoding filtered results:")
decoded = tokenizer.decode(encoded_filtered)
print(f"   → Decoded {len(decoded)} sequences")
for idx, dec in enumerate(decoded):
    print(f"   [{idx}] {dec}")

# Example 4: Using with save_encoded_dataset
print(f"\n{'=' * 70}")
print(f"SAVING DATASET WITH remove_over_max_len=True")
print(f"{'=' * 70}")

from selfies_tokenizer import save_encoded_dataset
import os
import tempfile

# Create a temporary directory for the example
with tempfile.TemporaryDirectory() as tmpdir:
    save_dir = os.path.join(tmpdir, 'filtered_dataset')

    paths = save_encoded_dataset(
        selfies_data=selfies_data,
        tokenizer=tokenizer,
        save_dir=save_dir,
        max_len=max_len,
        remove_over_max_len=True,
        show_progress=False
    )

    print(f"\nDataset saved with dropped indices tracked!")
    if 'dropped_indices_path' in paths:
        print(f"Dropped indices file: {paths['dropped_indices_path']}")

# Example 5: Practical use case - filtering a dataset
print(f"\n{'=' * 70}")
print(f"PRACTICAL USE CASE: DATASET FILTERING")
print(f"{'=' * 70}")

# Simulate a larger dataset
large_dataset = [
    '[C][=O]',
    '[N][C]' * 10,  # Very long sequence
    '[C][Branch1][C][O]',
    '[C]' * 20,  # Extremely long sequence
    '[N][C][C]',
    '[C][=C]',
]

print(f"\nOriginal dataset: {len(large_dataset)} sequences")

# First pass: analyze lengths
tokenizer_temp = SELFIESTokenizer()
tokenizer_temp.fit(large_dataset)
lengths = []
for s in large_dataset:
    tokens = tokenizer_temp.tokenize(s)
    lengths.append(len(tokens) + 2)

print(f"Length distribution:")
print(f"  Min: {min(lengths)}, Max: {max(lengths)}, Mean: {sum(lengths)/len(lengths):.1f}")

# Choose max_len
chosen_max_len = 10
print(f"\nChoosing max_len={chosen_max_len}")

# Encode with filtering
filtered = tokenizer_temp.encode(
    large_dataset,
    max_len=chosen_max_len,
    remove_over_max_len=True
)

print(f"\nResults:")
print(f"  Original: {len(large_dataset)} sequences")
print(f"  Kept: {len(filtered)} sequences")
print(f"  Dropped: {len(tokenizer_temp.dropped_indices)} sequences")
print(f"  Retention rate: {100*len(filtered)/len(large_dataset):.1f}%")

print(f"\n{'=' * 70}")
print("Example completed successfully!")
print(f"{'=' * 70}")

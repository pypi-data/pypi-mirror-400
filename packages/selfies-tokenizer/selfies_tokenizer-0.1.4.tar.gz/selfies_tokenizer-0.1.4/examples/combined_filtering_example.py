"""
Example demonstrating combined filtering with both remove_tokens and remove_over_max_len.

This feature allows you to filter sequences by multiple criteria simultaneously:
- Remove sequences containing specific unwanted tokens
- Remove sequences that exceed a maximum length

The tokenizer.dropped_indices will contain all sequences that failed either criterion.
"""

from selfies_tokenizer import SELFIESTokenizer, save_encoded_dataset

# Sample SELFIES dataset with various tokens and lengths
selfies_data = [
    '[C][=O]',                          # Short, simple
    '[C][Branch1][C][O]',               # Has Branch1
    '[N][C][C]',                        # Short, simple
    '[C][Branch2][Ring1][C][N]',        # Has Branch2 and Ring1
    '[C][=C]',                          # Short, simple
    '[C][C][C][C][C][C][C][C]',         # Very long
    '[C][Ring1][C]',                    # Has Ring1
    '[N][C]',                           # Short, simple
    '[C][Branch1][C][C][C][C]',         # Has Branch1, medium length
    '[C][=O][O]',                       # Short, simple
]

print("=" * 70)
print("COMBINED FILTERING EXAMPLE")
print("=" * 70)

# Initialize and fit tokenizer
tokenizer = SELFIESTokenizer()
tokenizer.fit(selfies_data)

print(f"\nOriginal data ({len(selfies_data)} sequences):")
for idx, s in enumerate(selfies_data):
    tokens = tokenizer.tokenize(s)
    seq_len = len(tokens) + 2  # +2 for <start> and <end>
    print(f"  [{idx}] {s:35s} → {len(tokens)} tokens ({seq_len} with special)")

# Define filtering criteria
max_len = 6
unwanted_tokens = ['[Branch1]', '[Branch2]', '[Ring1]']

print(f"\n{'=' * 70}")
print(f"FILTERING CRITERIA")
print(f"{'=' * 70}")
print(f"  Max length: {max_len}")
print(f"  Unwanted tokens: {unwanted_tokens}")

# ============================================================================
# Example 1: Filter by tokens only
# ============================================================================
print(f"\n{'=' * 70}")
print(f"EXAMPLE 1: FILTER BY TOKENS ONLY")
print(f"{'=' * 70}")

encoded_tokens_only = tokenizer.encode(
    selfies_data,
    max_len=max_len,
    remove_tokens=unwanted_tokens
)

print(f"\nResults:")
print(f"  Original sequences: {len(selfies_data)}")
print(f"  Kept sequences: {len(encoded_tokens_only)}")
print(f"  Dropped sequences: {len(tokenizer.dropped_indices)}")
print(f"  Dropped indices: {tokenizer.dropped_indices}")

print(f"\n  Dropped sequences (containing unwanted tokens):")
for idx in tokenizer.dropped_indices:
    print(f"    [{idx}] {selfies_data[idx]}")

# ============================================================================
# Example 2: Filter by length only
# ============================================================================
print(f"\n{'=' * 70}")
print(f"EXAMPLE 2: FILTER BY LENGTH ONLY")
print(f"{'=' * 70}")

encoded_length_only = tokenizer.encode(
    selfies_data,
    max_len=max_len,
    remove_over_max_len=True
)

print(f"\nResults:")
print(f"  Original sequences: {len(selfies_data)}")
print(f"  Kept sequences: {len(encoded_length_only)}")
print(f"  Dropped sequences: {len(tokenizer.dropped_indices)}")
print(f"  Dropped indices: {tokenizer.dropped_indices}")

print(f"\n  Dropped sequences (exceeding max_len={max_len}):")
for idx in tokenizer.dropped_indices:
    tokens = tokenizer.tokenize(selfies_data[idx])
    seq_len = len(tokens) + 2
    print(f"    [{idx}] {selfies_data[idx]:35s} → length {seq_len} > {max_len}")

# ============================================================================
# Example 3: COMBINED FILTERING (both criteria)
# ============================================================================
print(f"\n{'=' * 70}")
print(f"EXAMPLE 3: COMBINED FILTERING (TOKENS + LENGTH)")
print(f"{'=' * 70}")

encoded_combined = tokenizer.encode(
    selfies_data,
    max_len=max_len,
    remove_over_max_len=True,
    remove_tokens=unwanted_tokens
)

print(f"\nResults:")
print(f"  Original sequences: {len(selfies_data)}")
print(f"  Kept sequences: {len(encoded_combined)}")
print(f"  Dropped sequences: {len(tokenizer.dropped_indices)}")
print(f"  Dropped indices: {tokenizer.dropped_indices}")

print(f"\n  Kept sequences:")
kept_count = 0
for idx in range(len(selfies_data)):
    if idx not in tokenizer.dropped_indices:
        print(f"    [{idx}] {selfies_data[idx]}")
        kept_count += 1

print(f"\n  Dropped sequences (by reason):")
for idx in tokenizer.dropped_indices:
    tokens = tokenizer.tokenize(selfies_data[idx])
    seq_len = len(tokens) + 2

    # Determine reason(s) for dropping
    has_unwanted = any(token in unwanted_tokens for token in tokens)
    exceeds_length = seq_len > max_len

    reason = []
    if has_unwanted:
        reason.append("has unwanted tokens")
    if exceeds_length:
        reason.append(f"length {seq_len} > {max_len}")

    reason_str = " AND ".join(reason)
    print(f"    [{idx}] {selfies_data[idx]:35s} → {reason_str}")

# ============================================================================
# Example 4: Decode the filtered results
# ============================================================================
print(f"\n{'=' * 70}")
print(f"EXAMPLE 4: DECODE FILTERED RESULTS")
print(f"{'=' * 70}")

decoded = tokenizer.decode(encoded_combined)
print(f"\nDecoded {len(decoded)} sequences:")
for idx, dec in enumerate(decoded):
    print(f"  [{idx}] {dec}")

# ============================================================================
# Example 5: Save dataset with combined filtering
# ============================================================================
print(f"\n{'=' * 70}")
print(f"EXAMPLE 5: SAVE DATASET WITH COMBINED FILTERING")
print(f"{'=' * 70}")

import tempfile
import os

# Create a temporary directory for the example
with tempfile.TemporaryDirectory() as tmpdir:
    save_dir = os.path.join(tmpdir, 'combined_filtered_dataset')

    paths = save_encoded_dataset(
        selfies_data=selfies_data,
        tokenizer=tokenizer,
        save_dir=save_dir,
        max_len=max_len,
        remove_over_max_len=True,
        remove_tokens=unwanted_tokens,
        show_progress=False
    )

    print(f"\nDataset saved successfully!")
    print(f"  Dropped indices file: {paths.get('dropped_indices_path', 'N/A')}")

    # Show the metadata
    import json
    with open(paths['metadata_path'], 'r') as f:
        metadata = json.load(f)

    print(f"\n  Encoding settings from metadata:")
    for key, value in metadata['encoding_settings'].items():
        print(f"    {key}: {value}")

# ============================================================================
# Example 6: Practical use case - curate a clean dataset
# ============================================================================
print(f"\n{'=' * 70}")
print(f"EXAMPLE 6: PRACTICAL USE CASE - DATASET CURATION")
print(f"{'=' * 70}")

# Simulate a real-world scenario
print(f"\nScenario: Clean a dataset for training")
print(f"  - Remove complex branching/ring structures for simpler model")
print(f"  - Remove long sequences that don't fit in model context")
print(f"  - Keep only sequences that meet both criteria")

# Statistics before filtering
print(f"\n  Before filtering:")
print(f"    Total sequences: {len(selfies_data)}")

# Get statistics
stats = tokenizer.token_stats(selfies_data)
branch_count = sum(1 for s in selfies_data if any(t in tokenizer.tokenize(s) for t in unwanted_tokens))
long_count = sum(1 for s in selfies_data if len(tokenizer.tokenize(s)) + 2 > max_len)

print(f"    Sequences with unwanted tokens: {branch_count}")
print(f"    Sequences exceeding max_len: {long_count}")

# Apply combined filtering
curated = tokenizer.encode(
    selfies_data,
    max_len=max_len,
    remove_over_max_len=True,
    remove_tokens=unwanted_tokens
)

print(f"\n  After filtering:")
print(f"    Curated sequences: {len(curated)}")
print(f"    Dropped sequences: {len(tokenizer.dropped_indices)}")
print(f"    Retention rate: {100*len(curated)/len(selfies_data):.1f}%")

print(f"\n  Curated dataset is now ready for ML training!")
print(f"  - All sequences fit within max_len={max_len}")
print(f"  - No complex branching/ring structures")
print(f"  - Consistent, clean data")

print(f"\n{'=' * 70}")
print("Example completed successfully!")
print(f"{'=' * 70}")

print(f"\nKey takeaway:")
print(f"  Use encode(data, remove_over_max_len=True, remove_tokens=[...]) to filter")
print(f"  by both length AND token content in a single call. The dropped_indices")
print(f"  will contain ALL sequences that failed either criterion.")

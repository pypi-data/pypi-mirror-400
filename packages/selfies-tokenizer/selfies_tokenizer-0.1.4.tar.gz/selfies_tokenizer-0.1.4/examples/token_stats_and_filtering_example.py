"""
Example demonstrating token_stats() and remove_tokens() features.

These features help you analyze and filter your SELFIES dataset:
- token_stats(): Analyze token frequency distribution
- remove_tokens(): Filter out sequences containing unwanted tokens
"""

from selfies_tokenizer import SELFIESTokenizer
import json

# Sample SELFIES dataset with various tokens
selfies_data = [
    '[C][=O][O]',
    '[N][C][C]',
    '[C][Branch1][C][O]',
    '[C][=C]',
    '[N][C][C][C]',
    '[C][Ring1][C]',
    '[C][Branch1][C][N]',
    '[C][=O]',
    '[C][C]',
    '[C][Branch2][Ring1][C][N]',
]

print("=" * 70)
print("TOKEN STATISTICS AND FILTERING EXAMPLE")
print("=" * 70)

# Initialize tokenizer
tokenizer = SELFIESTokenizer()

print(f"\nOriginal dataset: {len(selfies_data)} sequences")
for idx, s in enumerate(selfies_data):
    print(f"  [{idx}] {s}")

# ============================================================================
# PART 1: TOKEN STATISTICS
# ============================================================================
print(f"\n{'=' * 70}")
print("PART 1: TOKEN STATISTICS")
print(f"{'=' * 70}")

# Analyze token frequencies
stats = tokenizer.token_stats(selfies_data)

print(f"\n1. Overall Statistics:")
print(f"   Total tokens: {stats['total_tokens']}")
print(f"   Unique tokens: {stats['unique_tokens']}")

print(f"\n2. Top 10 Most Common Tokens:")
for i, (token, count) in enumerate(stats['ranked_tokens'][:10], 1):
    freq = stats['token_frequencies'][token]
    print(f"   {i:2d}. {token:15s} → Count: {count:3d}, Frequency: {freq:.2%}")

print(f"\n3. Token Counts (all tokens):")
for token, count in sorted(stats['token_counts'].items(), key=lambda x: x[1], reverse=True):
    print(f"   {token:15s}: {count}")

# Save to file
stats_file = '/tmp/token_stats.json'
stats_saved = tokenizer.token_stats(selfies_data, save_path=stats_file)
print(f"\n4. Token statistics saved to: {stats_file}")

# Show saved JSON structure
with open(stats_file, 'r') as f:
    saved_stats = json.load(f)
print(f"   Saved data structure:")
print(f"   - total_tokens: {saved_stats['total_tokens']}")
print(f"   - unique_tokens: {saved_stats['unique_tokens']}")
print(f"   - token_counts: dictionary with {len(saved_stats['token_counts'])} entries")
print(f"   - ranked_tokens: list with {len(saved_stats['ranked_tokens'])} entries")

# ============================================================================
# PART 2: REMOVING TOKENS
# ============================================================================
print(f"\n{'=' * 70}")
print("PART 2: FILTERING SEQUENCES BY TOKENS")
print(f"{'=' * 70}")

# Example 1: Remove sequences with branching tokens
print(f"\n1. Remove sequences containing [Branch1] or [Branch2]:")
tokens_to_remove = ['[Branch1]', '[Branch2]']
filtered_data_1 = tokenizer.remove_tokens(selfies_data, tokens_to_remove)

print(f"   Tokens to remove: {tokens_to_remove}")
print(f"   Original: {len(selfies_data)} sequences")
print(f"   Filtered: {len(filtered_data_1)} sequences")
print(f"   Dropped: {len(tokenizer.dropped_indices)} sequences")
print(f"   Dropped indices: {tokenizer.dropped_indices}")

print(f"\n   Kept sequences:")
for idx, s in enumerate(filtered_data_1):
    print(f"   [{idx}] {s}")

print(f"\n   Dropped sequences:")
for idx in tokenizer.dropped_indices:
    print(f"   [{idx}] {selfies_data[idx]}")

# Example 2: Remove sequences with ring tokens
print(f"\n2. Remove sequences containing [Ring1]:")
tokens_to_remove = ['[Ring1]']
filtered_data_2 = tokenizer.remove_tokens(selfies_data, tokens_to_remove)

print(f"   Tokens to remove: {tokens_to_remove}")
print(f"   Original: {len(selfies_data)} sequences")
print(f"   Filtered: {len(filtered_data_2)} sequences")
print(f"   Dropped: {len(tokenizer.dropped_indices)} sequences")
print(f"   Dropped indices: {tokenizer.dropped_indices}")

# Example 3: Remove rare tokens based on statistics
print(f"\n3. Remove sequences with rare tokens (frequency < 5%):")

# Get rare tokens from statistics
rare_tokens = [
    token for token, freq in stats['token_frequencies'].items()
    if freq < 0.05  # Less than 5% frequency
]

print(f"   Rare tokens identified: {rare_tokens}")

if rare_tokens:
    filtered_data_3 = tokenizer.remove_tokens(selfies_data, rare_tokens)
    print(f"   Original: {len(selfies_data)} sequences")
    print(f"   Filtered: {len(filtered_data_3)} sequences")
    print(f"   Dropped: {len(tokenizer.dropped_indices)} sequences")
else:
    print(f"   No rare tokens found!")

# ============================================================================
# PART 3: PRACTICAL WORKFLOW
# ============================================================================
print(f"\n{'=' * 70}")
print("PART 3: PRACTICAL WORKFLOW - DATASET CURATION")
print(f"{'=' * 70}")

# Step 1: Analyze token distribution
print(f"\nStep 1: Analyze token distribution")
stats = tokenizer.token_stats(selfies_data)

# Step 2: Identify tokens to filter
print(f"\nStep 2: Identify unwanted tokens")
# Find tokens that appear in very few sequences
min_count = 2
unwanted_tokens = [
    token for token, count in stats['token_counts'].items()
    if count < min_count
]
print(f"   Tokens appearing less than {min_count} times: {unwanted_tokens}")

# Step 3: Filter dataset
print(f"\nStep 3: Filter dataset")
if unwanted_tokens:
    curated_data = tokenizer.remove_tokens(selfies_data, unwanted_tokens)
    print(f"   Original dataset: {len(selfies_data)} sequences")
    print(f"   Curated dataset: {len(curated_data)} sequences")
    print(f"   Removed: {len(tokenizer.dropped_indices)} sequences ({100*len(tokenizer.dropped_indices)/len(selfies_data):.1f}%)")
else:
    curated_data = selfies_data
    print(f"   No filtering needed - all tokens meet minimum count threshold")

# Step 4: Verify curation
print(f"\nStep 4: Verify curation results")
curated_stats = tokenizer.token_stats(curated_data)
print(f"   Unique tokens before: {stats['unique_tokens']}")
print(f"   Unique tokens after: {curated_stats['unique_tokens']}")
print(f"   Token reduction: {stats['unique_tokens'] - curated_stats['unique_tokens']}")

# ============================================================================
# PART 4: COMBINING WITH OTHER FEATURES
# ============================================================================
print(f"\n{'=' * 70}")
print("PART 4: COMBINING WITH remove_over_max_len")
print(f"{'=' * 70}")

# First filter by tokens, then by length
print(f"\nCombining filtering strategies:")

# Filter unwanted tokens first
step1_filtered = tokenizer.remove_tokens(selfies_data, ['[Branch2]'])
print(f"   After token filtering: {len(step1_filtered)} sequences")
print(f"   Dropped (tokens): {tokenizer.dropped_indices}")

# Then filter by length
tokenizer.fit(step1_filtered)
step2_filtered = tokenizer.encode(
    step1_filtered,
    max_len=5,
    remove_over_max_len=True
)
print(f"   After length filtering: {len(step2_filtered)} sequences")
print(f"   Dropped (length): {tokenizer.dropped_indices}")

print(f"\n{'=' * 70}")
print("Example completed successfully!")
print(f"{'=' * 70}")

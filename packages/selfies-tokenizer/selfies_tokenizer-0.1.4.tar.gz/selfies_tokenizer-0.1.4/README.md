# SELFIES Tokenizer

A **super fast** tokenizer for SELFIES (SELF-referencIng Embedded Strings) molecular representations with **ML-ready** batch processing and vocabulary management.

## Features

- **Blazing fast**: Optimized regex-based tokenization (~109k molecules/sec on real datasets)
- **ML-ready**: Batch processing, vocabulary management, and encoding to indices
- **Dataset packaging**: Save/load encoded datasets with full metadata (vocab, data, index mapping, statistics)
- **Smart max_len selection**: Interactive `suggest_len()` suggests optimal sequence lengths based on coverage (100%, 90%, 75%)
- **Special tokens**: Automatic `<start>` and `<end>` token insertion for sequence models
- **Smart decoding**: Stops at `<end>` token and removes all special tokens automatically
- **Padding & Truncation**: Built-in `max_len` support with `<pad>` always at index 0
- **Metadata management**: Saves `max_len` and `vocab_len` in vocabulary file
- **Progress bars**: Built-in tqdm support for large dataset processing
- **Flexible encoding**: Return token strings or indices with `return_str` flag
- **Vocabulary management**: Build, save, and load vocabularies for consistent encoding
- **Multiple methods**: Regex (fastest), manual parsing, or selfies library
- **Simple API**: Easy to use with sensible defaults
- **Well-tested**: Tested on 768k real SELFIES molecules
- **Zero dependencies**: Core functionality requires no external libraries (numpy for dataset saving, tqdm optional)

## Installation

```bash
pip install selfies-tokenizer  
```


## Quick Start

### Basic Tokenization
```python
from selfies_tokenizer import tokenize

# Simple usage
tokens = tokenize('[C][=O]')
# Returns: ['[C]', '[=O]']
```

### ML Workflow with Special Tokens

```python
from selfies_tokenizer import SELFIESTokenizer

# 1. Build vocabulary from training data with default max_len
tokenizer = SELFIESTokenizer(
    max_len=15,  # Saved in metadata
    vocab_path='./vocab.json',
    refresh_dict=True
)
train_data = ['[C][=O][O]', '[N][C][C]', '[C][Branch1][C][O]']
tokenizer.fit(train_data, show_progress=True)  # Progress bar for large datasets
tokenizer.save_vocab()  # Saves max_len and vocab_len in metadata

# Note: <pad> is always at index 0
print(tokenizer.token2idx['<pad>'])  # 0

# 2. Encode to indices (adds <start> and <end>, then pads)
indices = tokenizer.encode('[C][=O]')
# Returns: [2, 6, 5, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
# Format: <start>, [C], [=O], <end>, <pad>... (length 15)

# 3. Batch processing with uniform length
batch_indices = tokenizer.encode(['[C][=O]', '[N]', '[C][O]'], show_progress=True)
# All sequences have same length (15 from metadata)

# 4. Load existing vocabulary for inference (max_len auto-loaded)
inference_tokenizer = SELFIESTokenizer(vocab_path='./vocab.json')
test_indices = inference_tokenizer.encode('[C][=O]')  # Uses max_len=15 from metadata

# 5. Decode predictions (stops at <end>, removes special tokens)
decoded = inference_tokenizer.decode([2, 6, 5, 1, 0, 0, 0])
# Returns: '[C][=O]' (clean output, special tokens removed!)

# 6. Batch decode
decoded_batch = inference_tokenizer.decode(batch_indices)
# Returns: ['[C][=O]', '[N]', '[C][O]'] (all clean)
```

### Smart max_len Selection with `suggest_len()`

Let the tokenizer analyze your data and suggest optimal `max_len` values based on coverage:

```python
from selfies_tokenizer import SELFIESTokenizer

# Build vocabulary
tokenizer = SELFIESTokenizer(vocab_path='./vocab.json', refresh_dict=True)
tokenizer.fit(train_data)

# Get smart max_len suggestions (interactive)
max_len = tokenizer.suggest_len(train_data, show_progress=True)

# Output:
# ======================================================================
# SEQUENCE LENGTH ANALYSIS
# ======================================================================
#
# Dataset: 1000 sequences
# Min length: 10
# Median length: 37
# Max length: 73
#
# ----------------------------------------------------------------------
# SUGGESTED MAX_LEN OPTIONS
# ----------------------------------------------------------------------
#
# [1] 100% coverage (max_len=73)
#     → 0 sequences truncated (0.0%)
#     → All sequences preserved completely
#
# [2] 90% coverage (max_len=55)
#     → 93 sequences truncated (9.3%)
#     → 907 sequences preserved (90.7%)
#
# [3] 75% coverage (max_len=48)
#     → 249 sequences truncated (24.9%)
#     → 751 sequences preserved (75.1%)
#
# [4] Custom max_len
#
# ----------------------------------------------------------------------
# Select option [1-4]: 2
# ✓ Selected: max_len=55 (90% coverage)

# Now encode with the selected max_len
encoded_data = tokenizer.encode(train_data, max_len=max_len)
```

**Benefits:**
- **Data-driven**: Analyzes your actual sequence lengths
- **Trade-off visualization**: See exactly how many sequences get truncated
- **Interactive**: Choose the coverage that fits your needs
- **Custom option**: Enter your own max_len with automatic coverage calculation

### Save Dataset to NumPy with Metadata

Save your encoded dataset with full metadata for ML training:

```python
from selfies_tokenizer import SELFIESTokenizer
from selfies_tokenizer import save_encoded_dataset, load_encoded_dataset

# Build tokenizer
tokenizer = SELFIESTokenizer()
tokenizer.fit(train_data)

# Save complete dataset package
paths = save_encoded_dataset(
    selfies_data=train_data,
    tokenizer=tokenizer,
    save_dir='./datasets/my_dataset',
    max_len=50,
    show_progress=True
)

# Creates directory structure:
# ./datasets/my_dataset/
#     ├── vocab.json              # Tokenizer vocabulary
#     ├── encoded_data.npy        # Encoded sequences (shape: [N, 50])
#     ├── index_mapping.json      # Maps array index -> SELFIES string
#     └── metadata.json           # Timestamp, settings, statistics

# Later, load everything back
dataset = load_encoded_dataset('./datasets/my_dataset')
# Note: load_map=False by default (faster, less memory)
# Use load_map=True if you need the index_mapping

# Ready for ML!
X = dataset['encoded_data']        # numpy array
tokenizer = dataset['tokenizer']   # SELFIESTokenizer instance
metadata = dataset['metadata']     # dict with creation time, settings, etc.

# Use with PyTorch/TensorFlow
import torch
X_tensor = torch.tensor(X, dtype=torch.long)
```

**What gets saved:**
- **vocab.json**: Complete tokenizer vocabulary with all settings
- **encoded_data.npy**: Encoded sequences as numpy array (int32)
- **index_mapping.json**: Maps each array index to its SELFIES string
- **metadata.json**: Creation timestamp, encoding settings, dataset statistics, coverage info

**Metadata includes:**
- Creation timestamp
- Dataset size and statistics (min/max/mean/median sequence lengths)
- Encoding settings (max_len, padding, truncation, special tokens)
- Tokenizer configuration (vocab size, method)
- Coverage percentage (how many sequences were not truncated)
- Array shape and dtype

## API Reference

### SELFIESTokenizer

#### Initialization

```python
tokenizer = SELFIESTokenizer(
    method='auto',              # Tokenization method: 'auto', 'regex', 'manual', 'selfies_lib'
    vocab_path=None,            # Path to vocabulary JSON file
    refresh_dict=False,         # Force rebuild vocab even if exists
    special_tokens=None,        # Custom special tokens (default: ['<pad>', '<unk>', '<start>', '<end>'])
    max_len=None                # Default max sequence length (saved in metadata)
)
```

**Parameters:**
- `method`: Tokenization algorithm
  - `'auto'`: Automatically select fastest (default: regex)
  - `'regex'`: Pre-compiled regex (fastest)
  - `'manual'`: Manual string parsing
  - `'selfies_lib'`: Use selfies library (requires: `pip install selfies`)

- `vocab_path`: Path to vocabulary file
  - If file exists and `refresh_dict=False`: Loads existing vocabulary (including `max_len`)
  - If file doesn't exist: Will save vocabulary here when calling `save_vocab()`

- `refresh_dict`: Force vocabulary rebuild
  - `True`: Ignore existing vocabulary file, start fresh
  - `False`: Load existing vocabulary if available

- `special_tokens`: List of special tokens
  - Default: `['<pad>', '<unk>', '<start>', '<end>']`
  - Customize for your use case: `['<pad>', '<mask>', '<cls>', '<sep>']`
  - **`<pad>` is always placed at index 0**

- `max_len`: Default maximum sequence length
  - Saved in metadata when calling `save_vocab()`
  - Auto-loaded when loading vocabulary
  - Used as default in `encode()` if not specified

#### Methods

##### `fit(selfies_data, show_progress=False)`
Build vocabulary from SELFIES data.

```python
tokenizer.fit(['[C][=O]', '[N][C]', '[C][O]'])
# Builds vocabulary from training data

# With progress bar for large datasets
tokenizer.fit(large_dataset, show_progress=True)
```

**Parameters:**
- `selfies_data`: `str` or `List[str]` - SELFIES string(s) to build vocabulary from
- `show_progress`: `bool` - Show progress bar (requires `tqdm`)

**Returns:** `self` (for method chaining)

---

##### `suggest_len(selfies_data, add_special_tokens=True, show_progress=False)`
Analyze sequence lengths and suggest optimal `max_len` values with interactive coverage selection.

```python
# Analyze data and get suggestions
max_len = tokenizer.suggest_len(train_data, show_progress=True)

# Interactive prompt shows:
# - Min/median/max lengths
# - 100% coverage (no truncation)
# - 90% coverage
# - 75% coverage
# - Custom max_len option

# Returns user's chosen max_len
```

**Parameters:**
- `selfies_data`: `str` or `List[str]` - SELFIES string(s) to analyze
- `add_special_tokens`: `bool` (default: `True`) - Account for `<start>` and `<end>` in length calculations
- `show_progress`: `bool` (default: `False`) - Show progress bar during analysis

**Returns:** `int` - User's selected `max_len` value (or `None` if cancelled)

**Interactive Options:**
1. **100% coverage**: `max_len` = longest sequence (no truncation)
2. **90% coverage**: `max_len` at 90th percentile (~10% truncated)
3. **75% coverage**: `max_len` at 75th percentile (~25% truncated)
4. **Custom**: Enter your own `max_len` with automatic coverage calculation

**Use Case:**
Perfect for finding the optimal trade-off between sequence length and truncation. Longer `max_len` preserves more data but increases memory usage and computation. This tool helps you make an informed decision based on your actual data distribution.

---

##### `encode(selfies_data, return_str=False, max_len=None, padding=True, truncation=True, show_progress=False, add_special_tokens=True)`
Encode SELFIES to indices or token strings. Automatically adds `<start>` and `<end>` tokens. Supports both single and batch inputs with padding and truncation.

```python
# Single string to indices (adds <start> and <end>)
indices = tokenizer.encode('[C][=O]', max_len=10)
# Returns: [2, 5, 4, 1, 0, 0, 0, 0, 0, 0]
# Format: <start>, [C], [=O], <end>, <pad>...

# Batch encoding with progress bar
batch_indices = tokenizer.encode(large_dataset, max_len=10, show_progress=True)

# Without special tokens
indices = tokenizer.encode('[C][=O]', max_len=10, add_special_tokens=False)
# Returns: [5, 4, 0, 0, 0, 0, 0, 0, 0, 0]

# Return string tokens instead of indices
tokens = tokenizer.encode('[C]', max_len=5, return_str=True)
# Returns: ['<start>', '[C]', '<end>', '<pad>', '<pad>']
```

**Parameters:**
- `selfies_data`: `str` or `List[str]` - SELFIES string(s) to encode
- `return_str`: `bool` (default: `False`) - Return token strings instead of indices
- `max_len`: `int` or `None` (default: `None`) - Maximum sequence length. Uses `self.max_len` if not specified
- `padding`: `bool` (default: `True`) - Pad sequences shorter than `max_len` with `<pad>` (index 0)
- `truncation`: `bool` (default: `True`) - Truncate sequences longer than `max_len`
- `show_progress`: `bool` (default: `False`) - Show progress bar (requires `tqdm`)
- `add_special_tokens`: `bool` (default: `True`) - Add `<start>` and `<end>` tokens

**Returns:**
- Single input + `return_str=False`: `List[int]` (token indices)
- Single input + `return_str=True`: `List[str]` (token strings)
- Batch input + `return_str=False`: `List[List[int]]` (batch of indices)
- Batch input + `return_str=True`: `List[List[str]]` (batch of tokens)

**Notes:**
- **`<pad>` token is always at index 0** for efficient masking in ML models
- **`<start>` and `<end>` tokens are automatically added** by default
- Sequence format: `[<start>, token1, token2, ..., <end>, <pad>, ...]`
- When `max_len` is specified, all output sequences will have the same length
- Essential for batching in PyTorch/TensorFlow

---

##### `decode(indices, skip_special_tokens=True)`
Decode token indices back to SELFIES strings. Automatically stops at `<end>` token and removes special tokens.

```python
# Single decode (stops at <end>, removes special tokens)
selfies = tokenizer.decode([2, 5, 4, 1, 0, 0])
# Input: <start>, [C], [=O], <end>, <pad>, <pad>
# Returns: '[C][=O]' (clean output!)

# Batch decode
batch_selfies = tokenizer.decode([[2, 5, 4, 1], [2, 6, 5, 1]])
# Returns: ['[C][=O]', '[N][C]']

# Keep special tokens if needed
selfies = tokenizer.decode([2, 5, 4, 1], skip_special_tokens=False)
# Returns: '<start>[C][=O]' (stops at <end>, but keeps other special tokens)
```

**Parameters:**
- `indices`: `List[int]` or `List[List[int]]` - Token indices to decode
- `skip_special_tokens`: `bool` (default: `True`) - Remove all special tokens from output

**Returns:**
- Single input: `str` (SELFIES string)
- Batch input: `List[str]` (batch of SELFIES strings)

**Behavior:**
- **Always stops at `<end>` token** (doesn't decode beyond it)
- **Removes all special tokens** by default (`<start>`, `<end>`, `<pad>`, `<unk>`)
- Perfect for decoding model predictions

---

##### `save_vocab(path=None)`
Save vocabulary to JSON file.

```python
tokenizer.save_vocab('./vocab.json')
# Or use vocab_path from __init__
tokenizer.save_vocab()
```

**Parameters:**
- `path`: `str` (optional) - Path to save vocabulary. Uses `vocab_path` from init if not specified.

---

##### `load_vocab(path=None)`
Load vocabulary from JSON file.

```python
tokenizer.load_vocab('./vocab.json')
# Or use vocab_path from __init__
tokenizer.load_vocab()
```

**Parameters:**
- `path`: `str` (optional) - Path to vocabulary file. Uses `vocab_path` from init if not specified.

**Returns:** `self` (for method chaining)

---

##### `tokenize(selfies_string)`
Low-level tokenization to strings only (no vocabulary needed).

```python
tokens = tokenizer.tokenize('[C][=O]')
# Returns: ['[C]', '[=O]']
```

**Parameters:**
- `selfies_string`: `str` - SELFIES string to tokenize

**Returns:** `List[str]` - Token strings

---

#### Properties

##### `vocab_size`
Get the size of the vocabulary.

```python
size = tokenizer.vocab_size
# Returns: int
```

---

### Convenience Functions

#### `tokenize(selfies_string, method='auto')`
Quick tokenization without creating a tokenizer instance.

```python
from selfies_tokenizer import tokenize

tokens = tokenize('[C][=O]')
# Returns: ['[C]', '[=O]']
```

### Utility Functions

#### `save_encoded_dataset(...)`
Save encoded SELFIES dataset with complete metadata package.

```python
from selfies_tokenizer import save_encoded_dataset

paths = save_encoded_dataset(
    selfies_data=train_data,        # SELFIES strings to encode
    tokenizer=tokenizer,             # Fitted tokenizer
    save_dir='./datasets/my_data',   # Output directory
    max_len=50,                      # Sequence length
    padding=True,                    # Pad sequences
    truncation=True,                 # Truncate long sequences
    add_special_tokens=True,         # Add <start> and <end>
    show_progress=True               # Show progress bar
)
```

**Parameters:**
- `selfies_data`: `str` or `List[str]` - SELFIES strings to encode and save
- `tokenizer`: `SELFIESTokenizer` - Fitted tokenizer instance
- `save_dir`: `str` - Directory to save dataset (created if doesn't exist)
- `max_len`: `int` or `None` - Maximum sequence length
- `padding`: `bool` - Pad sequences to max_len
- `truncation`: `bool` - Truncate sequences longer than max_len
- `add_special_tokens`: `bool` - Add `<start>` and `<end>` tokens
- `show_progress`: `bool` - Show progress bar
- `vocab_filename`: `str` - Vocabulary filename (default: 'vocab.json')
- `data_filename`: `str` - Data filename (default: 'encoded_data.npy')
- `index_filename`: `str` - Index mapping filename (default: 'index_mapping.json')
- `metadata_filename`: `str` - Metadata filename (default: 'metadata.json')

**Returns:** `dict` with paths to all saved files

**Creates:**
- `vocab.json` - Tokenizer vocabulary
- `encoded_data.npy` - Encoded sequences as numpy array (int32, shape: [N, max_len])
- `index_mapping.json` - Maps each array index to its SELFIES string
- `metadata.json` - Timestamp, settings, statistics, coverage info

---

#### `load_encoded_dataset(...)`
Load encoded SELFIES dataset with all metadata.

```python
from selfies_tokenizer import load_encoded_dataset

dataset = load_encoded_dataset(
    load_dir='./datasets/my_data',
    load_tokenizer=True,
    load_map=False  # Set to True if you need index mapping
)

# Access components
X = dataset['encoded_data']        # numpy array
tokenizer = dataset['tokenizer']   # SELFIESTokenizer
metadata = dataset['metadata']     # dict with all info
index_mapping = dataset['index_mapping']  # None by default, dict if load_map=True
```

**Parameters:**
- `load_dir`: `str` - Directory containing the dataset
- `vocab_filename`: `str` - Vocabulary filename (default: 'vocab.json')
- `data_filename`: `str` - Data filename (default: 'encoded_data.npy')
- `index_filename`: `str` - Index mapping filename (default: 'index_mapping.json')
- `metadata_filename`: `str` - Metadata filename (default: 'metadata.json')
- `load_tokenizer`: `bool` - If True, load and return tokenizer instance (default: True)
- `load_map`: `bool` - If True, load and return index mapping (default: False)

**Returns:** `dict` containing:
- `encoded_data`: `np.ndarray` - Encoded sequences
- `index_mapping`: `dict` or `None` - Maps array index to SELFIES string (only if `load_map=True`)
- `metadata`: `dict` - Full metadata (timestamp, settings, statistics)
- `tokenizer`: `SELFIESTokenizer` or `None` - Tokenizer instance (if `load_tokenizer=True`)

**Performance tip:** Keep `load_map=False` (default) for faster loading and lower memory usage when you don't need the index mapping.

## Padding and Truncation

The tokenizer provides built-in padding and truncation for ML training. **The `<pad>` token is always at index 0**, making it easy to create attention masks and work with PyTorch/TensorFlow.

### Why Padding and Truncation?

Neural networks require fixed-length input sequences for batching. Variable-length SELFIES strings need to be:
- **Padded**: Short sequences extended to `max_len` with `<pad>` tokens
- **Truncated**: Long sequences cut to `max_len`

### Basic Usage

```python
from selfies_tokenizer import SELFIESTokenizer

tokenizer = SELFIESTokenizer()
tokenizer.fit(['[C][=O]', '[N][C][C]'])

# Pad short sequence
result = tokenizer.encode('[C]', max_len=4)
# Returns: [5, 0, 0, 0]  (padded with 0)

# Truncate long sequence
result = tokenizer.encode('[C][C][C][C][C]', max_len=3)
# Returns: [5, 5, 5]  (truncated)

# Batch with uniform length
batch = ['[C]', '[C][=O]', '[N][C][C]']
result = tokenizer.encode(batch, max_len=4)
# Returns: [[5, 0, 0, 0], [5, 4, 0, 0], [6, 5, 5, 0]]
# All sequences now have length 4!
```

### Key Features

- **`<pad>` always at index 0**: Guaranteed for all vocabularies
- **Batch processing**: Entire batches padded/truncated in one call
- **Flexible control**: Enable/disable padding and truncation independently
- **String support**: Works with `return_str=True` for debugging

### Control Flags

```python
# Only padding, no truncation
tokenizer.encode('[C]', max_len=5, padding=True, truncation=False)

# Only truncation, no padding
tokenizer.encode('[C][C][C]', max_len=2, padding=False, truncation=True)

# Neither (variable length output)
tokenizer.encode('[C][=O]', max_len=5, padding=False, truncation=False)
```

### PyTorch Example

```python
import torch

# Encode with fixed length
data = ['[C][=O]', '[N]', '[C][C][C]']
encoded = tokenizer.encode(data, max_len=4)

# Convert to tensor
tensor = torch.tensor(encoded)
print(tensor.shape)  # torch.Size([3, 4])

# Create attention mask (1 for real tokens, 0 for padding)
attention_mask = (tensor != 0).long()
```

## Filtering Long Sequences with `remove_over_max_len`

Instead of truncating sequences that exceed `max_len`, you can completely remove them from the output. This is useful when you don't want to lose information by truncating long sequences.

### Basic Usage

```python
from selfies_tokenizer import SELFIESTokenizer

tokenizer = SELFIESTokenizer()
tokenizer.fit(['[C][=O]', '[N][C][C]', '[C][Branch1][C][O]'])

# Example data with varying lengths
data = [
    '[C][=O]',                      # Short: 4 tokens with special tokens
    '[N][C][C][C][C][C]',           # Long: 8 tokens with special tokens
    '[C][Branch1][C][O]'            # Medium: 6 tokens with special tokens
]

# Encode with remove_over_max_len=True
encoded = tokenizer.encode(
    data,
    max_len=6,
    remove_over_max_len=True  # Remove sequences exceeding max_len
)

# Check which sequences were dropped
print(tokenizer.dropped_indices)  # [1] - second sequence was dropped
# Returns: [[2, 4, 5, 1, 0, 0], [2, 4, 7, 6, 8, 1]]
# Only sequences that fit within max_len=6 are returned
```

### Key Features

- **No information loss**: Sequences are either kept completely or dropped entirely
- **Track dropped sequences**: `tokenizer.dropped_indices` contains indices of dropped sequences
- **Works with batches**: Efficiently filters large datasets
- **Compatible with `save_encoded_dataset`**: Dropped indices are saved to metadata

### Using with `save_encoded_dataset`

```python
from selfies_tokenizer import save_encoded_dataset

# Save dataset with filtering
paths = save_encoded_dataset(
    selfies_data=train_data,
    tokenizer=tokenizer,
    save_dir='./datasets/filtered_data',
    max_len=50,
    remove_over_max_len=True,
    show_progress=True
)

# Dropped indices are automatically saved
# ./datasets/filtered_data/dropped_indices.json
```

### Practical Use Case

```python
# Analyze your data first
max_len = tokenizer.suggest_len(train_data)  # Interactive selection

# Filter out sequences that are too long
filtered_data = tokenizer.encode(
    train_data,
    max_len=max_len,
    remove_over_max_len=True
)

# Get the kept sequences for further processing
kept_indices = [i for i in range(len(train_data)) if i not in tokenizer.dropped_indices]
kept_selfies = [train_data[i] for i in kept_indices]

print(f"Original: {len(train_data)} sequences")
print(f"Kept: {len(filtered_data)} sequences")
print(f"Dropped: {len(tokenizer.dropped_indices)} sequences")
print(f"Retention rate: {100*len(filtered_data)/len(train_data):.1f}%")
```

### When to Use

- **Data quality**: Remove outliers with extremely long sequences
- **Memory constraints**: Ensure all sequences fit within your model's context window
- **Training stability**: Avoid truncation artifacts in your training data
- **Dataset curation**: Build clean datasets with consistent sequence lengths

## Token Statistics and Analysis

Analyze token frequency distribution in your dataset to understand composition and identify rare or problematic tokens.

### `token_stats()` - Analyze Token Frequencies

```python
from selfies_tokenizer import SELFIESTokenizer

tokenizer = SELFIESTokenizer()

# Sample dataset
data = ['[C][=O]', '[C][C]', '[N][C]', '[C][Branch1][C][O]']

# Get token statistics
stats = tokenizer.token_stats(data)

# View results
print(f"Total tokens: {stats['total_tokens']}")
print(f"Unique tokens: {stats['unique_tokens']}")

# Most common tokens
for token, count in stats['ranked_tokens'][:5]:
    freq = stats['token_frequencies'][token]
    print(f"{token}: {count} occurrences ({freq:.1%})")

# Save to JSON file
stats = tokenizer.token_stats(data, save_path='./token_stats.json')
```

**Returns:**
- `total_tokens`: Total number of tokens in dataset
- `unique_tokens`: Number of distinct tokens
- `token_counts`: Dictionary mapping each token to its count
- `token_frequencies`: Dictionary mapping each token to its frequency (0-1)
- `ranked_tokens`: List of (token, count) tuples sorted by frequency

### Use Cases

- **Dataset exploration**: Understand token distribution before training
- **Identify rare tokens**: Find tokens that appear infrequently
- **Vocabulary optimization**: Decide which tokens to keep/remove
- **Data quality checks**: Detect unexpected or problematic tokens

## Filtering by Token Content

Remove sequences containing specific unwanted tokens while tracking which sequences were filtered.

### `remove_tokens()` - Filter Unwanted Tokens

```python
from selfies_tokenizer import SELFIESTokenizer

tokenizer = SELFIESTokenizer()

# Sample dataset
data = [
    '[C][=O]',
    '[C][Branch1][C][O]',  # Contains Branch1
    '[N][C]',
    '[C][Ring1][C]',       # Contains Ring1
    '[C][=C]'
]

# Remove sequences with branching or ring tokens
unwanted_tokens = ['[Branch1]', '[Branch2]', '[Ring1]', '[Ring2]']
filtered_data = tokenizer.remove_tokens(data, unwanted_tokens)

# Check results
print(f"Original: {len(data)} sequences")
print(f"Filtered: {len(filtered_data)} sequences")
print(f"Dropped indices: {tokenizer.dropped_indices}")
# Dropped indices: [1, 3]

# Filtered data contains only: ['[C][=O]', '[N][C]', '[C][=C]']
```

### Key Features

- **Flexible filtering**: Remove any combination of tokens
- **Track dropped sequences**: `tokenizer.dropped_indices` shows which sequences were removed
- **Batch processing**: Efficiently filter large datasets
- **Preserve original indices**: Know exactly which sequences were filtered

### Combining with Token Statistics

```python
# Step 1: Analyze token distribution
stats = tokenizer.token_stats(train_data)

# Step 2: Identify rare tokens (< 1% frequency)
rare_tokens = [
    token for token, freq in stats['token_frequencies'].items()
    if freq < 0.01
]

# Step 3: Remove sequences with rare tokens
curated_data = tokenizer.remove_tokens(train_data, rare_tokens)

print(f"Removed {len(tokenizer.dropped_indices)} sequences")
print(f"Curated dataset: {len(curated_data)} sequences")
```

### Practical Workflow

```python
# 1. Analyze your dataset
stats = tokenizer.token_stats(train_data, save_path='./stats.json')

# 2. Define filtering criteria
unwanted = ['[Branch2]', '[Ring2]']  # Complex structures
min_frequency = 0.001  # Remove tokens < 0.1%

rare = [t for t, f in stats['token_frequencies'].items() if f < min_frequency]
tokens_to_remove = unwanted + rare

# 3. Filter dataset
filtered = tokenizer.remove_tokens(train_data, tokens_to_remove)

# 4. Combine with length filtering
tokenizer.fit(filtered)
final_data = tokenizer.encode(
    filtered,
    max_len=50,
    remove_over_max_len=True
)

print(f"Original: {len(train_data)}")
print(f"After token filter: {len(filtered)}")
print(f"Final dataset: {len(final_data)}")
```

## Performance

Benchmarked on a standard machine with 10,000 iterations:

| Method | Simple Molecule | Complex Molecule | Long Chain (500 tokens) |
|--------|----------------|------------------|------------------------|
| **Regex** | **0.74µs** | **1.33µs** | **60.11µs** |
| Manual | 0.81µs | 3.55µs | 141.08µs |
| Selfies Lib | 1.24µs | 3.18µs | 195.86µs |

The regex method is **2-3x faster** than alternatives.

## Examples

### Example 1: Training a Model

```python
from selfies_tokenizer import SELFIESTokenizer

# Load your training data
train_selfies = [
    '[C][=O][O]',
    '[N][C][C][C]',
    '[C][Branch1][C][O][C]',
    # ... more training data
]

# Create tokenizer and build vocabulary
tokenizer = SELFIESTokenizer(vocab_path='./model_vocab.json', refresh_dict=True)
tokenizer.fit(train_selfies)
tokenizer.save_vocab()

print(f"Vocabulary size: {tokenizer.vocab_size}")

# Encode training data to indices
train_indices = tokenizer.encode(train_selfies)

# Now train your model with train_indices...
```

### Example 2: Inference with Saved Vocabulary

```python
from selfies_tokenizer import SELFIESTokenizer

# Load pre-built vocabulary
tokenizer = SELFIESTokenizer(vocab_path='./model_vocab.json')

# Encode new molecule
molecule = '[C][=C][C][=O]'
indices = tokenizer.encode(molecule)

# Pass to your trained model...
prediction = model.predict(indices)

# Decode prediction back to SELFIES
predicted_selfies = tokenizer.decode(prediction)
print(f"Predicted molecule: {predicted_selfies}")
```

### Example 3: Batch Processing

```python
from selfies_tokenizer import SELFIESTokenizer

tokenizer = SELFIESTokenizer(vocab_path='./vocab.json')

# Process large batch efficiently
large_batch = ['[C][=O]', '[N][C]', ...] * 1000  # 1000s of molecules

# Single call for entire batch
batch_indices = tokenizer.encode(large_batch)

# Process batch...
```

### Example 4: Custom Special Tokens

```python
from selfies_tokenizer import SELFIESTokenizer

# Use custom special tokens for BERT-style models
tokenizer = SELFIESTokenizer(
    special_tokens=['<pad>', '<mask>', '<cls>', '<sep>'],
    vocab_path='./bert_vocab.json'
)

tokenizer.fit(train_data)

# <mask> token is now in vocabulary
mask_idx = tokenizer.token2idx['<mask>']
```

### Example 5: Unknown Token Handling

```python
from selfies_tokenizer import SELFIESTokenizer

# Train with limited vocabulary
tokenizer = SELFIESTokenizer()
tokenizer.fit(['[C][=O]', '[N][C]'])

# Encode molecule with unknown token
result = tokenizer.encode('[S][=O]')  # [S] not in vocabulary

# [S] is mapped to <unk>
unk_idx = tokenizer.token2idx['<unk>']
# result will contain unk_idx for [S]
```


## How It Works

SELFIES strings are formatted with tokens enclosed in square brackets:
- Input: `[C][=O]`
- Output: `['[C]', '[=O]']`

The tokenizer:
1. **Tokenizes** using pre-compiled regex pattern `\[[^\]]+\]` (fastest method)
2. **Builds vocabulary** from training data with special tokens (`<pad>` always at index 0)
3. **Encodes** by mapping tokens to indices using the vocabulary
4. **Pads/Truncates** sequences to `max_len` if specified (for ML batching)
5. **Handles unknown tokens** by mapping them to `<unk>`
6. **Decodes** by mapping indices back to tokens and joining them

## Requirements

- Python 3.6+
- Optional: `selfies` library (only for `selfies_lib` method)

```bash
pip install selfies  # Optional
```

## Use Cases

- **Machine Learning**: Train models on molecular representations
- **Drug Discovery**: Process large chemical databases efficiently
- **Chemical Informatics**: Fast tokenization for analysis pipelines
- **Model Deployment**: Consistent vocabulary for training and inference

## License

MIT

## Contributing

Contributions welcome! Please feel free to submit a Pull Request.

## Roadmap

- [x] Add padding and truncation utilities
- [ ] Add PyTorch/TensorFlow dataset adapters
- [ ] Add CLI tool for vocabulary building
- [ ] Publish to PyPI
- [ ] Add sequence alignment utilities
- [ ] Add attention mask generation utilities

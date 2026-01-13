"""
Utility functions for SELFIES tokenizer dataset management.

Provides tools for saving and loading encoded datasets with full metadata.
"""

import json
import os
from datetime import datetime
from typing import List, Union, Optional, Dict, Any
import numpy as np


def save_encoded_dataset(
    selfies_data: Union[str, List[str]],
    tokenizer: 'SELFIESTokenizer',
    save_dir: str,
    max_len: Optional[int] = None,
    padding: bool = True,
    truncation: bool = True,
    add_special_tokens: bool = True,
    show_progress: bool = False,
    remove_over_max_len: bool = False,
    remove_tokens: Optional[List[str]] = None,
    vocab_filename: str = 'vocab.json',
    data_filename: str = 'encoded_data.npy',
    index_filename: str = 'index_mapping.json',
    metadata_filename: str = 'metadata.json',
    dropped_indices_filename: str = 'dropped_indices.json'
) -> Dict[str, str]:
    """
    Save encoded SELFIES dataset with vocabulary, index mapping, and metadata.

    Creates a complete dataset package with:
    - Tokenizer vocabulary
    - Encoded data as numpy array
    - Index mapping (array index -> SELFIES string)
    - Metadata (timestamp, settings, statistics)

    Args:
        selfies_data: Single SELFIES string or list of SELFIES strings to encode
        tokenizer: Fitted SELFIESTokenizer instance with vocabulary
        save_dir: Directory path to save dataset (will be created if doesn't exist)
        max_len: Maximum sequence length for encoding
        padding: Pad sequences to max_len
        truncation: Truncate sequences longer than max_len
        add_special_tokens: Add <start> and <end> tokens
        show_progress: Show progress bar during encoding
        remove_over_max_len: Remove sequences exceeding max_len instead of truncating
        remove_tokens: Optional list of tokens to exclude from dataset
        vocab_filename: Name for vocabulary file (default: 'vocab.json')
        data_filename: Name for encoded data file (default: 'encoded_data.npy')
        index_filename: Name for index mapping file (default: 'index_mapping.json')
        metadata_filename: Name for metadata file (default: 'metadata.json')
        dropped_indices_filename: Name for dropped indices file (default: 'dropped_indices.json')

    Returns:
        Dictionary with paths to all saved files:
        {
            'save_dir': str,
            'vocab_path': str,
            'data_path': str,
            'index_path': str,
            'metadata_path': str
        }

    Examples:
        >>> from selfies_tokenizer import SELFIESTokenizer, save_encoded_dataset
        >>>
        >>> # Prepare tokenizer
        >>> tokenizer = SELFIESTokenizer()
        >>> tokenizer.fit(train_data)
        >>>
        >>> # Save dataset
        >>> paths = save_encoded_dataset(
        ...     selfies_data=train_data,
        ...     tokenizer=tokenizer,
        ...     save_dir='./datasets/my_dataset',
        ...     max_len=50,
        ...     show_progress=True
        ... )
        >>>
        >>> print(f"Dataset saved to: {paths['save_dir']}")

    Directory Structure:
        save_dir/
            ├── vocab.json              # Tokenizer vocabulary
            ├── encoded_data.npy        # Encoded sequences (shape: [N, max_len])
            ├── index_mapping.json      # Maps array index -> SELFIES string
            └── metadata.json           # Dataset metadata and settings
    """
    # Convert single string to list
    if isinstance(selfies_data, str):
        selfies_data = [selfies_data]

    # Create save directory
    os.makedirs(save_dir, exist_ok=True)

    # Define file paths
    vocab_path = os.path.join(save_dir, vocab_filename)
    data_path = os.path.join(save_dir, data_filename)
    index_path = os.path.join(save_dir, index_filename)
    metadata_path = os.path.join(save_dir, metadata_filename)
    dropped_indices_path = os.path.join(save_dir, dropped_indices_filename)

    # 1. Save vocabulary
    tokenizer.save_vocab(vocab_path)

    # 2. Encode data
    print(f"\nEncoding {len(selfies_data)} sequences...")
    encoded_data = tokenizer.encode(
        selfies_data,
        max_len=max_len,
        padding=padding,
        truncation=truncation,
        add_special_tokens=add_special_tokens,
        show_progress=show_progress,
        remove_over_max_len=remove_over_max_len,
        remove_tokens=remove_tokens
    )

    # Store dropped indices from encoding
    dropped_indices = tokenizer.dropped_indices.copy()

    # Convert to numpy array and save
    encoded_array = np.array(encoded_data, dtype=np.int32)
    np.save(data_path, encoded_array)
    print(f"✓ Saved encoded data: {data_path}")
    print(f"  Shape: {encoded_array.shape}")
    print(f"  Dtype: {encoded_array.dtype}")

    # 3. Save dropped indices if any were dropped
    if (remove_over_max_len or remove_tokens) and dropped_indices:
        with open(dropped_indices_path, 'w') as f:
            json.dump(dropped_indices, f, indent=2)
        print(f"✓ Saved dropped indices: {dropped_indices_path}")
        print(f"  Dropped: {len(dropped_indices)} sequences")

    # 4. Create index mapping (array index -> SELFIES) for non-dropped sequences only
    # Maps each array index to its SELFIES string
    print(f"\nCreating index mapping...")
    # Filter out dropped sequences from the original data
    kept_selfies = [s for idx, s in enumerate(selfies_data) if idx not in dropped_indices]
    index_mapping = {str(idx): selfies for idx, selfies in enumerate(kept_selfies)}

    with open(index_path, 'w') as f:
        json.dump(index_mapping, f, indent=2)
    print(f"✓ Saved index mapping: {index_path}")
    print(f"  Total mappings: {len(index_mapping)}")

    # 5. Calculate statistics (for kept sequences only)
    sequence_lengths = [len(tokenizer.tokenize(s)) for s in kept_selfies]
    if add_special_tokens:
        sequence_lengths = [l + 2 for l in sequence_lengths]  # Account for <start> and <end>

    # Count truncated sequences (only among kept sequences)
    if max_len is not None and truncation and not remove_over_max_len:
        num_truncated = sum(1 for l in sequence_lengths if l > max_len)
    else:
        num_truncated = 0

    # 6. Create metadata
    metadata = {
        'created_at': datetime.now().isoformat(),
        'dataset': {
            'num_sequences_original': len(selfies_data),
            'num_sequences_kept': len(kept_selfies),
            'num_sequences_dropped': len(dropped_indices),
            'sequence_length': {
                'min': int(min(sequence_lengths)) if sequence_lengths else 0,
                'max': int(max(sequence_lengths)) if sequence_lengths else 0,
                'mean': float(np.mean(sequence_lengths)) if sequence_lengths else 0.0,
                'median': float(np.median(sequence_lengths)) if sequence_lengths else 0.0
            },
            'num_truncated': num_truncated,
            'coverage': 100.0 * (len(kept_selfies) - num_truncated) / len(kept_selfies) if kept_selfies else 0.0
        },
        'encoding_settings': {
            'max_len': max_len,
            'padding': padding,
            'truncation': truncation,
            'add_special_tokens': add_special_tokens,
            'remove_over_max_len': remove_over_max_len,
            'remove_tokens': remove_tokens
        },
        'tokenizer': {
            'vocab_size': tokenizer.vocab_size,
            'special_tokens': tokenizer.special_tokens,
            'method': tokenizer.method,
            'tokenizer_max_len': tokenizer.max_len
        },
        'files': {
            'vocab': vocab_filename,
            'data': data_filename,
            'index_mapping': index_filename,
            'metadata': metadata_filename
        },
        'array_info': {
            'shape': list(encoded_array.shape),
            'dtype': str(encoded_array.dtype)
        }
    }

    # Add dropped indices file to metadata if sequences were dropped
    if (remove_over_max_len or remove_tokens) and dropped_indices:
        metadata['files']['dropped_indices'] = dropped_indices_filename

    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"✓ Saved metadata: {metadata_path}")

    # Print summary
    print("\n" + "=" * 70)
    print("DATASET SAVED SUCCESSFULLY")
    print("=" * 70)
    print(f"\nLocation: {save_dir}")
    print(f"\nFiles created:")
    print(f"  ✓ {vocab_filename:30s} - Tokenizer vocabulary")
    print(f"  ✓ {data_filename:30s} - Encoded data ({encoded_array.shape})")
    print(f"  ✓ {index_filename:30s} - Index mapping ({len(index_mapping)} entries)")
    print(f"  ✓ {metadata_filename:30s} - Dataset metadata")
    if (remove_over_max_len or remove_tokens) and dropped_indices:
        print(f"  ✓ {dropped_indices_filename:30s} - Dropped indices ({len(dropped_indices)} sequences)")
    print(f"\nDataset Statistics:")
    print(f"  Original sequences: {len(selfies_data)}")
    if remove_over_max_len or remove_tokens:
        print(f"  Kept sequences: {len(kept_selfies)}")
        print(f"  Dropped sequences: {len(dropped_indices)} ({100*len(dropped_indices)/len(selfies_data):.1f}%)")
    print(f"  Vocab size: {tokenizer.vocab_size}")
    print(f"  Max length: {max_len}")
    if not (remove_over_max_len or remove_tokens):
        print(f"  Truncated: {num_truncated} ({100*num_truncated/len(selfies_data):.1f}%)")
    print(f"  Coverage: {metadata['dataset']['coverage']:.1f}%")
    print("=" * 70)

    # Return all paths
    result = {
        'save_dir': save_dir,
        'vocab_path': vocab_path,
        'data_path': data_path,
        'index_path': index_path,
        'metadata_path': metadata_path
    }
    if (remove_over_max_len or remove_tokens) and dropped_indices:
        result['dropped_indices_path'] = dropped_indices_path
    return result


def load_encoded_dataset(
    load_dir: str,
    vocab_filename: str = 'vocab.json',
    data_filename: str = 'encoded_data.npy',
    index_filename: str = 'index_mapping.json',
    metadata_filename: str = 'metadata.json',
    load_tokenizer: bool = True,
    load_map: bool = False
) -> Dict[str, Any]:
    """
    Load encoded SELFIES dataset with all metadata.

    Args:
        load_dir: Directory containing the dataset
        vocab_filename: Name of vocabulary file (default: 'vocab.json')
        data_filename: Name of encoded data file (default: 'encoded_data.npy')
        index_filename: Name of index mapping file (default: 'index_mapping.json')
        metadata_filename: Name of metadata file (default: 'metadata.json')
        load_tokenizer: If True, load and return tokenizer instance
        load_map: If True, load and return index mapping (default: False)

    Returns:
        Dictionary containing:
        {
            'encoded_data': np.ndarray,           # Encoded sequences
            'index_mapping': dict or None,         # index -> SELFIES (if load_map=True)
            'metadata': dict,                      # Dataset metadata
            'tokenizer': SELFIESTokenizer or None  # Tokenizer instance (if load_tokenizer=True)
        }

    Examples:
        >>> from selfies_tokenizer import load_encoded_dataset
        >>>
        >>> # Load dataset without index mapping (faster)
        >>> dataset = load_encoded_dataset('./datasets/my_dataset')
        >>> X = dataset['encoded_data']
        >>> tokenizer = dataset['tokenizer']
        >>> metadata = dataset['metadata']
        >>> # dataset['index_mapping'] is None
        >>>
        >>> # Load dataset with index mapping
        >>> dataset = load_encoded_dataset('./datasets/my_dataset', load_map=True)
        >>> index_mapping = dataset['index_mapping']  # Now available
    """
    # Define file paths
    vocab_path = os.path.join(load_dir, vocab_filename)
    data_path = os.path.join(load_dir, data_filename)
    index_path = os.path.join(load_dir, index_filename)
    metadata_path = os.path.join(load_dir, metadata_filename)

    # Verify required files exist
    required_files = [
        (vocab_path, 'vocabulary'),
        (data_path, 'encoded data'),
        (metadata_path, 'metadata')
    ]

    # Only check index mapping if it will be loaded
    if load_map:
        required_files.append((index_path, 'index mapping'))

    for path, name in required_files:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Missing {name} file: {path}")

    print(f"\nLoading dataset from: {load_dir}")

    # Load encoded data
    encoded_data = np.load(data_path)
    print(f"✓ Loaded encoded data: {encoded_data.shape}")

    # Load index mapping only if requested
    index_mapping = None
    if load_map:
        with open(index_path, 'r') as f:
            index_mapping = json.load(f)
        print(f"✓ Loaded index mapping: {len(index_mapping)} entries")

    # Load metadata
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)
    print(f"✓ Loaded metadata")

    # Load tokenizer if requested
    tokenizer = None
    if load_tokenizer:
        from selfies_tokenizer import SELFIESTokenizer
        tokenizer = SELFIESTokenizer(vocab_path=vocab_path)
        print(f"✓ Loaded tokenizer: vocab_size={tokenizer.vocab_size}")

    print(f"\n{'=' * 70}")
    print("DATASET LOADED SUCCESSFULLY")
    print(f"{'=' * 70}")
    print(f"\nDataset info:")
    print(f"  Created: {metadata['created_at']}")
    # Handle both old and new metadata formats
    if 'num_sequences_kept' in metadata['dataset']:
        print(f"  Original sequences: {metadata['dataset']['num_sequences_original']}")
        print(f"  Kept sequences: {metadata['dataset']['num_sequences_kept']}")
        print(f"  Dropped sequences: {metadata['dataset']['num_sequences_dropped']}")
    else:
        print(f"  Sequences: {metadata['dataset'].get('num_sequences', 'N/A')}")
    print(f"  Shape: {encoded_data.shape}")
    print(f"  Vocab size: {metadata['tokenizer']['vocab_size']}")
    print(f"  Max length: {metadata['encoding_settings']['max_len']}")
    print(f"  Coverage: {metadata['dataset']['coverage']:.1f}%")
    print(f"{'=' * 70}")

    return {
        'encoded_data': encoded_data,
        'index_mapping': index_mapping,
        'metadata': metadata,
        'tokenizer': tokenizer
    }

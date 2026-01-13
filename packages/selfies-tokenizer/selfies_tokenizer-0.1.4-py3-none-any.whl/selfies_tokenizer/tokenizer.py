"""
Fast SELFIES tokenizer for chemistry applications.

This module provides an optimized tokenizer for SELFIES (SELF-referencIng Embedded Strings)
molecular representations with ML-ready batch processing and vocabulary management.
"""

import json
import os
import re
from typing import List, Union, Dict, Optional


try:
    import selfies
    SELFIES_AVAILABLE = True
except ImportError:
    SELFIES_AVAILABLE = False

try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False


class SELFIESTokenizer:
    """
    Fast tokenizer for SELFIES strings with ML support.

    Supports multiple tokenization strategies with automatic selection
    of the fastest available method. Includes vocabulary management
    and batch processing for efficient ML training.
    """

    # Pre-compiled regex pattern for better performance
    _PATTERN = re.compile(r'\[[^\]]+\]')

    def __init__(
        self,
        method: str = 'auto',
        vocab_path: Optional[str] = None,
        refresh_dict: bool = False,
        special_tokens: Optional[List[str]] = None,
        max_len: Optional[int] = None
    ):
        """
        Initialize the tokenizer.

        Args:
            method: Tokenization method ('auto', 'regex', 'manual', 'selfies_lib')
                   'auto' automatically selects the best available method
            vocab_path: Path to vocabulary JSON file. If exists and refresh_dict=False,
                       will load existing vocab. Otherwise creates new vocab.
            refresh_dict: If True, create new vocabulary even if vocab_path exists
            special_tokens: List of special tokens to add to vocabulary
                          Default: ['<pad>', '<unk>', '<start>', '<end>']
                          Note: Special tokens are hard-coded to indices:
                                <pad>=0, <unk>=1, <start>=2, <end>=3
            max_len: Default maximum sequence length (saved in metadata)
        """
        self.method = method
        self.vocab_path = vocab_path
        self.refresh_dict = refresh_dict
        self.max_len = max_len

        # Special tokens
        if special_tokens is None:
            self.special_tokens = ['<pad>', '<unk>', '<start>', '<end>']
        else:
            self.special_tokens = special_tokens

        # Vocabulary mappings
        self.token2idx: Dict[str, int] = {}
        self.idx2token: Dict[int, str] = {}

        # Track dropped indices when using remove_over_max_len
        self.dropped_indices: List[int] = []

        # Auto-select best method
        if method == 'auto':
            self.method = 'regex'  # Default to regex as it's consistently fast
        elif method == 'selfies_lib' and not SELFIES_AVAILABLE:
            raise ValueError("selfies library not available. Install with: pip install selfies")

        # Load existing vocabulary if available
        if vocab_path and os.path.exists(vocab_path) and not refresh_dict:
            self.load_vocab(vocab_path)

    def tokenize(self, selfies_string: str) -> List[str]:
        """
        Tokenize a SELFIES string into individual tokens.

        Args:
            selfies_string: SELFIES formatted string (e.g., '[C][=O][OH]')

        Returns:
            List of tokens (e.g., ['[C]', '[=O]', '[OH]'])

        Examples:
            >>> tokenizer = SELFIESTokenizer()
            >>> tokenizer.tokenize('[C][=O]')
            ['[C]', '[=O]']
        """
        if not selfies_string:
            return []

        if self.method == 'selfies_lib':
            return self._tokenize_selfies_lib(selfies_string)
        elif self.method == 'manual':
            return self._tokenize_manual(selfies_string)
        else:  # regex (default)
            return self._tokenize_regex(selfies_string)

    def _tokenize_regex(self, selfies_string: str) -> List[str]:
        """
        Tokenize using pre-compiled regex pattern.
        Fast and reliable for well-formed SELFIES strings.
        """
        return self._PATTERN.findall(selfies_string)

    def _tokenize_manual(self, selfies_string: str) -> List[str]:
        """
        Tokenize using manual string parsing.
        Fastest for simple cases, no regex overhead.
        """
        tokens = []
        current_token = []
        in_bracket = False

        for char in selfies_string:
            if char == '[':
                in_bracket = True
                current_token = ['[']
            elif char == ']':
                if in_bracket:
                    current_token.append(']')
                    tokens.append(''.join(current_token))
                    current_token = []
                    in_bracket = False
            elif in_bracket:
                current_token.append(char)

        return tokens

    def _tokenize_selfies_lib(self, selfies_string: str) -> List[str]:
        """
        Tokenize using the selfies library's split_selfies function.
        Requires selfies library to be installed.
        """
        return list(selfies.split_selfies(selfies_string))

    def fit(self, selfies_data: Union[str, List[str]], show_progress: bool = False) -> 'SELFIESTokenizer':
        """
        Build vocabulary from SELFIES data.

        Special tokens are always assigned to fixed indices:
        - <pad> = 0
        - <unk> = 1
        - <start> = 2
        - <end> = 3

        Args:
            selfies_data: Single SELFIES string or list of SELFIES strings
            show_progress: Show progress bar during vocabulary building (requires tqdm)

        Returns:
            self for method chaining

        Examples:
            >>> tokenizer = SELFIESTokenizer()
            >>> tokenizer.fit(['[C][=O]', '[N][C]'])
            >>> tokenizer.vocab_size
            7  # <pad>=0, <unk>=1, <start>=2, <end>=3, [C]=4, [=O]=5, [N]=6
            >>> tokenizer.token2idx['<pad>']
            0
            >>> tokenizer.fit(large_dataset, show_progress=True)  # With progress bar
        """
        # Convert single string to list
        if isinstance(selfies_data, str):
            selfies_data = [selfies_data]

        # Extract all unique tokens (excluding special tokens)
        token_set = set()

        # Extract all unique tokens with optional progress bar
        if show_progress and TQDM_AVAILABLE:
            iterator = tqdm(selfies_data, desc="Building vocabulary", unit="molecules")
        else:
            iterator = selfies_data

        for selfies_string in iterator:
            tokens = self.tokenize(selfies_string)
            token_set.update(tokens)

        # Remove any special tokens that might have been in the data
        token_set = token_set - set(self.special_tokens)

        # Create vocabulary with hard-coded special token order
        # Special tokens are ALWAYS: <pad>=0, <unk>=1, <start>=2, <end>=3
        vocab_list = ['<pad>', '<unk>', '<start>', '<end>'] + sorted(token_set)

        # Build token2idx and idx2token mappings
        self.token2idx = {token: idx for idx, token in enumerate(vocab_list)}
        self.idx2token = {idx: token for token, idx in self.token2idx.items()}

        return self

    def encode(
        self,
        selfies_data: Union[str, List[str]],
        return_str: bool = False,
        max_len: Optional[int] = None,
        padding: bool = True,
        truncation: bool = True,
        show_progress: bool = False,
        add_special_tokens: bool = True,
        remove_over_max_len: bool = False,
        remove_tokens: Optional[List[str]] = None
    ) -> Union[List[int], List[str], List[List[int]], List[List[str]]]:
        """
        Encode SELFIES string(s) to token indices or token strings.

        Supports both single string and batch processing for ML efficiency.
        Includes padding and truncation for fixed-length sequences.

        Args:
            selfies_data: Single SELFIES string or list of SELFIES strings
            return_str: If True, return token strings instead of indices
            max_len: Maximum sequence length. If None, uses self.max_len. No padding/truncation if both are None.
            padding: If True, pad sequences shorter than max_len with <pad> (index 0)
            truncation: If True, truncate sequences longer than max_len
            show_progress: Show progress bar during encoding (requires tqdm)
            add_special_tokens: If True, add <start> and <end> tokens to sequences
            remove_over_max_len: If True, completely remove sequences that exceed max_len instead of truncating.
                                 Dropped sequence indices are stored in self.dropped_indices.
            remove_tokens: Optional list of tokens to exclude. Sequences containing any of these tokens
                          will be removed. Dropped sequence indices are stored in self.dropped_indices.
                          Can be combined with remove_over_max_len for multi-criteria filtering.

        Returns:
            - If input is str and return_str=False: List[int] (token indices)
            - If input is str and return_str=True: List[str] (token strings)
            - If input is List[str] and return_str=False: List[List[int]] (batch of token indices)
            - If input is List[str] and return_str=True: List[List[str]] (batch of token strings)

        Examples:
            >>> tokenizer = SELFIESTokenizer()
            >>> tokenizer.fit(['[C][=O]', '[N][C]'])
            >>> tokenizer.encode('[C][=O]')
            [1, 2]
            >>> tokenizer.encode('[C][=O]', return_str=True)
            ['[C]', '[=O]']
            >>> tokenizer.encode('[C][=O]', max_len=5)
            [1, 2, 0, 0, 0]  # Padded with 0 (<pad>)
            >>> tokenizer.encode(['[C][=O]', '[N][C]'], max_len=3)
            [[1, 2, 0], [3, 1, 0]]  # All sequences padded to length 3
            >>> tokenizer.encode(large_dataset, show_progress=True)  # With progress bar
            >>> # Remove sequences that exceed max_len
            >>> tokenizer.encode(['[C][=O]', '[N][C][C][C][C]'], max_len=5, remove_over_max_len=True)
            [[2, 4, 5, 1, 0]]  # Only first sequence kept
            >>> tokenizer.dropped_indices
            [1]  # Second sequence was dropped
            >>> # Remove sequences containing specific tokens
            >>> tokenizer.encode(['[C][=O]', '[C][Branch1][C]'], remove_tokens=['[Branch1]'])
            [[2, 4, 5, 1]]  # Only first sequence kept
            >>> tokenizer.dropped_indices
            [1]  # Second sequence was dropped
            >>> # Combine both filters
            >>> tokenizer.encode(data, max_len=10, remove_over_max_len=True, remove_tokens=['[Branch1]'])
            # Drops sequences with [Branch1] OR exceeding max_len=10
        """
        # Check if vocabulary is built
        if not self.token2idx:
            raise ValueError("Vocabulary not built. Call fit() first or load existing vocabulary.")

        # Use self.max_len if max_len not provided
        if max_len is None:
            max_len = self.max_len

        # Reset dropped indices
        self.dropped_indices = []

        # Handle single string
        is_single = isinstance(selfies_data, str)
        if is_single:
            selfies_data = [selfies_data]

        # Filter sequences if remove_over_max_len or remove_tokens is enabled
        if remove_over_max_len or remove_tokens:
            filtered_data = []
            tokens_to_remove_set = set(remove_tokens) if remove_tokens else set()

            for idx, selfies_string in enumerate(selfies_data):
                tokens = self.tokenize(selfies_string)
                should_drop = False

                # Check if sequence contains unwanted tokens
                if remove_tokens and any(token in tokens_to_remove_set for token in tokens):
                    should_drop = True

                # Check if sequence exceeds max_len (only if remove_over_max_len is enabled)
                if remove_over_max_len and max_len is not None:
                    # Calculate final length (including special tokens if they will be added)
                    final_len = len(tokens)
                    if add_special_tokens:
                        final_len += 2  # <start> and <end>

                    if final_len > max_len:
                        should_drop = True

                # Drop or keep the sequence
                if should_drop:
                    self.dropped_indices.append(idx)
                else:
                    filtered_data.append(selfies_string)

            selfies_data = filtered_data

            # If all sequences were dropped, return empty result
            if len(selfies_data) == 0:
                if is_single:
                    return [] if return_str else []
                return []

        # Batch process all strings with optional progress bar
        if show_progress and TQDM_AVAILABLE and len(selfies_data) > 1:
            iterator = tqdm(selfies_data, desc="Encoding", unit="molecules")
        else:
            iterator = selfies_data

        results = []
        for selfies_string in iterator:
            tokens = self.tokenize(selfies_string)

            # Add special tokens (<start> and <end>)
            if add_special_tokens:
                tokens = ['<start>'] + tokens + ['<end>']

            if return_str:
                # Return token strings with padding/truncation
                if max_len is not None:
                    if truncation and len(tokens) > max_len:
                        tokens = tokens[:max_len]
                    if padding and len(tokens) < max_len:
                        tokens = tokens + ['<pad>'] * (max_len - len(tokens))
                results.append(tokens)
            else:
                # Convert to indices, use <unk> for unknown tokens
                unk_idx = self.token2idx.get('<unk>', 0)
                indices = [self.token2idx.get(token, unk_idx) for token in tokens]

                # Apply padding and truncation to indices
                if max_len is not None:
                    if truncation and len(indices) > max_len:
                        indices = indices[:max_len]
                    if padding and len(indices) < max_len:
                        # Pad with 0 (which should be <pad>)
                        indices = indices + [0] * (max_len - len(indices))

                results.append(indices)

        # Return single list if input was single string
        if is_single:
            return results[0] if results else ([] if return_str else [])
        return results

    def decode(
        self,
        indices: Union[List[int], List[List[int]]],
        skip_special_tokens: bool = True
    ) -> Union[str, List[str]]:
        """
        Decode token indices back to SELFIES string(s).

        Automatically stops at <end> token and removes special tokens.

        Args:
            indices: Single list of indices or batch of index lists
            skip_special_tokens: If True, remove all special tokens from output

        Returns:
            - If input is List[int]: str (single SELFIES string)
            - If input is List[List[int]]: List[str] (batch of SELFIES strings)

        Examples:
            >>> tokenizer = SELFIESTokenizer()
            >>> tokenizer.fit(['[C][=O]'])
            >>> tokenizer.decode([2, 3])
            '[C][=O]'
            >>> tokenizer.decode([[2, 3], [4, 2]])
            ['[C][=O]', '[N][C]']
        """
        # Check if vocabulary is built
        if not self.idx2token:
            raise ValueError("Vocabulary not built. Call fit() first or load existing vocabulary.")

        # Handle single list
        is_single = not isinstance(indices[0], list)
        if is_single:
            indices = [indices]

        # Batch decode
        results = []
        for idx_list in indices:
            tokens = []
            for idx in idx_list:
                token = self.idx2token.get(idx, '<unk>')

                # Stop at <end> token
                if token == '<end>':
                    break

                # Skip special tokens if requested
                if skip_special_tokens and token in self.special_tokens:
                    continue

                tokens.append(token)

            selfies_string = ''.join(tokens)
            results.append(selfies_string)

        # Return single string if input was single list
        if is_single:
            return results[0]
        return results

    def save_vocab(self, path: Optional[str] = None) -> None:
        """
        Save vocabulary to JSON file.

        Args:
            path: Path to save vocabulary. If None, uses self.vocab_path

        Examples:
            >>> tokenizer = SELFIESTokenizer()
            >>> tokenizer.fit(['[C][=O]'])
            >>> tokenizer.save_vocab('./vocab.json')
        """
        save_path = path or self.vocab_path

        if not save_path:
            raise ValueError("No path specified. Provide path or set vocab_path in __init__")

        vocab_data = {
            'token2idx': self.token2idx,
            'idx2token': {str(k): v for k, v in self.idx2token.items()},  # JSON keys must be strings
            'special_tokens': self.special_tokens,
            'method': self.method,
            'vocab_len': self.vocab_len,
            'max_len': self.max_len
        }

        with open(save_path, 'w') as f:
            json.dump(vocab_data, f, indent=2)

        print(f"Vocabulary saved to {save_path}")

    def load_vocab(self, path: Optional[str] = None) -> 'SELFIESTokenizer':
        """
        Load vocabulary from JSON file.

        Args:
            path: Path to vocabulary file. If None, uses self.vocab_path

        Returns:
            self for method chaining

        Examples:
            >>> tokenizer = SELFIESTokenizer()
            >>> tokenizer.load_vocab('./vocab.json')
        """
        load_path = path or self.vocab_path

        if not load_path:
            raise ValueError("No path specified. Provide path or set vocab_path in __init__")

        if not os.path.exists(load_path):
            raise FileNotFoundError(f"Vocabulary file not found: {load_path}")

        with open(load_path, 'r') as f:
            vocab_data = json.load(f)

        self.token2idx = vocab_data['token2idx']
        self.idx2token = {int(k): v for k, v in vocab_data['idx2token'].items()}
        self.special_tokens = vocab_data.get('special_tokens', self.special_tokens)
        self.max_len = vocab_data.get('max_len', self.max_len)

        print(f"Vocabulary loaded from {load_path}")
        return self

    @property
    def vocab_size(self) -> int:
        """Return the size of the vocabulary."""
        return len(self.token2idx)

    @property
    def vocab_len(self) -> int:
        """Return the length of the vocabulary (alias for vocab_size)."""
        return len(self.token2idx)

    def suggest_len(
        self,
        selfies_data: Union[str, List[str]],
        add_special_tokens: bool = True,
        show_progress: bool = False
    ) -> int:
        """
        Analyze sequence lengths and suggest optimal max_len values.

        Tokenizes the data and calculates length distribution, then presents
        three coverage options for the user to choose from:
        - 100% coverage: No sequences will be truncated
        - 90% coverage: 90% of sequences fit without truncation
        - 75% coverage: 75% of sequences fit without truncation

        Args:
            selfies_data: Single SELFIES string or list of SELFIES strings
            add_special_tokens: If True, account for <start> and <end> tokens in length
            show_progress: Show progress bar during length calculation

        Returns:
            User's chosen max_len value

        Examples:
            >>> tokenizer = SELFIESTokenizer()
            >>> max_len = tokenizer.suggest_len(selfies_data)
            # Interactive prompt shows coverage options
            >>> tokenizer.encode(selfies_data, max_len=max_len)
        """
        # Convert single string to list
        if isinstance(selfies_data, str):
            selfies_data = [selfies_data]

        # Tokenize all sequences and calculate lengths
        if show_progress and TQDM_AVAILABLE:
            iterator = tqdm(selfies_data, desc="Analyzing lengths", unit="molecules")
        else:
            iterator = selfies_data

        lengths = []
        for selfies_string in iterator:
            tokens = self.tokenize(selfies_string)
            seq_len = len(tokens)

            # Account for special tokens if they will be added
            if add_special_tokens:
                seq_len += 2  # <start> and <end>

            lengths.append(seq_len)

        # Calculate statistics
        lengths_sorted = sorted(lengths)
        n = len(lengths_sorted)

        # Calculate percentiles
        max_len_100 = lengths_sorted[-1]  # 100th percentile (max)
        max_len_90 = lengths_sorted[int(0.90 * n)]  # 90th percentile
        max_len_75 = lengths_sorted[int(0.75 * n)]  # 75th percentile
        min_len = lengths_sorted[0]
        median_len = lengths_sorted[n // 2]

        # Display statistics
        print("\n" + "=" * 70)
        print("SEQUENCE LENGTH ANALYSIS")
        print("=" * 70)
        print(f"\nDataset: {len(selfies_data)} sequences")
        print(f"Min length: {min_len}")
        print(f"Median length: {median_len}")
        print(f"Max length: {max_len_100}")

        # Display coverage options
        print("\n" + "-" * 70)
        print("SUGGESTED MAX_LEN OPTIONS")
        print("-" * 70)

        # Calculate how many sequences would be truncated for each option
        truncated_90 = sum(1 for l in lengths if l > max_len_90)
        truncated_75 = sum(1 for l in lengths if l > max_len_75)

        print(f"\n[1] 100% coverage (max_len={max_len_100})")
        print(f"    → 0 sequences truncated (0.0%)")
        print(f"    → All sequences preserved completely")

        print(f"\n[2] 90% coverage (max_len={max_len_90})")
        print(f"    → {truncated_90} sequences truncated ({100*truncated_90/n:.1f}%)")
        print(f"    → {n - truncated_90} sequences preserved ({100*(n-truncated_90)/n:.1f}%)")

        print(f"\n[3] 75% coverage (max_len={max_len_75})")
        print(f"    → {truncated_75} sequences truncated ({100*truncated_75/n:.1f}%)")
        print(f"    → {n - truncated_75} sequences preserved ({100*(n-truncated_75)/n:.1f}%)")

        print(f"\n[4] Custom max_len")

        # Get user choice
        print("\n" + "-" * 70)
        while True:
            try:
                choice = input("Select option [1-4]: ").strip()

                if choice == '1':
                    selected_len = max_len_100
                    print(f"\n✓ Selected: max_len={selected_len} (100% coverage)")
                    break
                elif choice == '2':
                    selected_len = max_len_90
                    print(f"\n✓ Selected: max_len={selected_len} (90% coverage)")
                    break
                elif choice == '3':
                    selected_len = max_len_75
                    print(f"\n✓ Selected: max_len={selected_len} (75% coverage)")
                    break
                elif choice == '4':
                    custom_len = input("Enter custom max_len: ").strip()
                    selected_len = int(custom_len)
                    # Calculate coverage for custom length
                    truncated_custom = sum(1 for l in lengths if l > selected_len)
                    coverage = 100 * (n - truncated_custom) / n
                    print(f"\n✓ Selected: max_len={selected_len} ({coverage:.1f}% coverage)")
                    break
                else:
                    print("Invalid choice. Please enter 1, 2, 3, or 4.")
            except ValueError:
                print("Invalid input. Please enter a number.")
            except KeyboardInterrupt:
                print("\n\nCancelled.")
                return None

        print("=" * 70)
        return selected_len

    def token_stats(
        self,
        selfies_data: Union[str, List[str]],
        save_path: Optional[str] = None,
        show_progress: bool = False
    ) -> Dict[str, any]:
        """
        Analyze token frequency statistics in SELFIES data.

        Counts token occurrences and ranks them from most to least common.
        Useful for understanding dataset composition and identifying rare tokens.

        Args:
            selfies_data: Single SELFIES string or list of SELFIES strings to analyze
            save_path: Optional path to save statistics as JSON file
            show_progress: Show progress bar during analysis (requires tqdm)

        Returns:
            Dictionary containing:
            {
                'total_tokens': int,              # Total number of tokens analyzed
                'unique_tokens': int,             # Number of unique tokens found
                'token_counts': {token: count},   # Count for each token
                'token_frequencies': {token: freq}, # Frequency (0-1) for each token
                'ranked_tokens': [(token, count), ...] # Sorted by count (descending)
            }

        Examples:
            >>> tokenizer = SELFIESTokenizer()
            >>> data = ['[C][=O]', '[C][C]', '[N][C]']
            >>> stats = tokenizer.token_stats(data)
            >>> stats['ranked_tokens']
            [('[C]', 4), ('[=O]', 1), ('[N]', 1)]
            >>> # Save to file
            >>> stats = tokenizer.token_stats(data, save_path='./token_stats.json')
        """
        # Convert single string to list
        if isinstance(selfies_data, str):
            selfies_data = [selfies_data]

        # Count token occurrences
        token_counts = {}
        total_tokens = 0

        # Analyze with optional progress bar
        if show_progress and TQDM_AVAILABLE:
            iterator = tqdm(selfies_data, desc="Analyzing tokens", unit="molecules")
        else:
            iterator = selfies_data

        for selfies_string in iterator:
            tokens = self.tokenize(selfies_string)
            for token in tokens:
                token_counts[token] = token_counts.get(token, 0) + 1
                total_tokens += 1

        # Calculate frequencies
        token_frequencies = {
            token: count / total_tokens if total_tokens > 0 else 0
            for token, count in token_counts.items()
        }

        # Rank tokens by frequency (descending)
        ranked_tokens = sorted(token_counts.items(), key=lambda x: x[1], reverse=True)

        # Prepare statistics
        stats = {
            'total_tokens': total_tokens,
            'unique_tokens': len(token_counts),
            'token_counts': token_counts,
            'token_frequencies': token_frequencies,
            'ranked_tokens': ranked_tokens
        }

        # Save to file if path provided
        if save_path:
            with open(save_path, 'w') as f:
                # Convert ranked_tokens tuples to dict for JSON serialization
                stats_to_save = stats.copy()
                stats_to_save['ranked_tokens'] = [
                    {'token': token, 'count': count}
                    for token, count in ranked_tokens
                ]
                json.dump(stats_to_save, f, indent=2)
            print(f"Token statistics saved to {save_path}")

        return stats

    def remove_tokens(
        self,
        selfies_data: Union[str, List[str]],
        tokens_to_remove: List[str],
        show_progress: bool = False
    ) -> Union[str, List[str]]:
        """
        Remove SELFIES sequences that contain any of the specified tokens.

        Filters out sequences containing unwanted tokens and tracks which
        sequences were dropped via self.dropped_indices.

        Args:
            selfies_data: Single SELFIES string or list of SELFIES strings to filter
            tokens_to_remove: List of tokens to exclude (e.g., ['[Branch1]', '[Ring1]'])
            show_progress: Show progress bar during filtering (requires tqdm)

        Returns:
            Filtered SELFIES data (same type as input - str or List[str])

        Side Effects:
            Updates self.dropped_indices with indices of sequences that were removed

        Examples:
            >>> tokenizer = SELFIESTokenizer()
            >>> data = ['[C][=O]', '[C][Branch1][C][O]', '[N][C]']
            >>> filtered = tokenizer.remove_tokens(data, ['[Branch1]'])
            >>> # Returns: ['[C][=O]', '[N][C]']
            >>> tokenizer.dropped_indices
            [1]  # Second sequence was dropped

            >>> # Single string input
            >>> filtered = tokenizer.remove_tokens('[C][Ring1][C]', ['[Ring1]'])
            >>> # Returns: '' (empty string if all tokens match)
            >>> tokenizer.dropped_indices
            [0]  # Single sequence was dropped
        """
        # Reset dropped indices
        self.dropped_indices = []

        # Handle single string
        is_single = isinstance(selfies_data, str)
        if is_single:
            selfies_data = [selfies_data]

        # Convert tokens_to_remove to set for faster lookup
        tokens_to_remove_set = set(tokens_to_remove)

        # Filter sequences with optional progress bar
        if show_progress and TQDM_AVAILABLE:
            iterator = enumerate(selfies_data)
            iterator = tqdm(iterator, desc="Filtering sequences", unit="molecules", total=len(selfies_data))
        else:
            iterator = enumerate(selfies_data)

        filtered_data = []
        for idx, selfies_string in iterator:
            tokens = self.tokenize(selfies_string)

            # Check if any unwanted token is present
            has_unwanted_token = any(token in tokens_to_remove_set for token in tokens)

            if has_unwanted_token:
                self.dropped_indices.append(idx)
            else:
                filtered_data.append(selfies_string)

        # Return same type as input
        if is_single:
            return filtered_data[0] if filtered_data else ''
        return filtered_data

    def __call__(
        self,
        selfies_data: Union[str, List[str]],
        return_str: bool = False,
        max_len: Optional[int] = None,
        padding: bool = True,
        truncation: bool = True,
        show_progress: bool = False,
        add_special_tokens: bool = True,
        remove_over_max_len: bool = False,
        remove_tokens: Optional[List[str]] = None
    ) -> Union[List[int], List[str], List[List[int]], List[List[str]]]:
        """
        Allow tokenizer to be called directly for encoding.

        Examples:
            >>> tokenizer = SELFIESTokenizer()
            >>> tokenizer.fit(['[C][=O]'])
            >>> tokenizer('[C][=O]')
            [1, 2]
            >>> tokenizer('[C][=O]', max_len=5)
            [1, 2, 0, 0, 0]
            >>> tokenizer(large_dataset, show_progress=True)  # With progress bar
        """
        return self.encode(selfies_data, return_str=return_str, max_len=max_len,
                          padding=padding, truncation=truncation, show_progress=show_progress,
                          add_special_tokens=add_special_tokens, remove_over_max_len=remove_over_max_len,
                          remove_tokens=remove_tokens)


# Convenience function for quick tokenization
def tokenize(selfies_string: str, method: str = 'auto') -> List[str]:
    """
    Tokenize a SELFIES string.

    Args:
        selfies_string: SELFIES formatted string (e.g., '[C][=O][OH]')
        method: Tokenization method ('auto', 'regex', 'manual', 'selfies_lib')

    Returns:
        List of tokens (e.g., ['[C]', '[=O]', '[OH]'])

    Examples:
        >>> tokenize('[C][=O]')
        ['[C]', '[=O]']
    """
    tokenizer = SELFIESTokenizer(method=method)
    return tokenizer.tokenize(selfies_string)

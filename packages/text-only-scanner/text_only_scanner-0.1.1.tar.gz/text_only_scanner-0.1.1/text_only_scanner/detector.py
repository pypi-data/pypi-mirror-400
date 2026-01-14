from typing import Iterable, List, Tuple
import os
import math
import re
from collections import Counter

# A conservative set of bytes considered "text" (ASCII printable + common whitespace)
_TEXT_BYTES = bytes(range(32, 127)) + b"\n\r\t\f\v"

# Regex patterns for ciphertext-like content (base64, hex-encoded)
_BASE64_PATTERN = re.compile(r'^[A-Za-z0-9+/]{44,}={0,2}$')  # Base64 with min length
_HEX_PATTERN = re.compile(r'^[0-9A-Fa-f]{32,}$')  # Hex with min length


def _is_ciphertext_line(line: str) -> bool:
    """Return True if a line looks like base64 or hex-encoded ciphertext."""
    stripped = line.strip()
    if not stripped or len(stripped) < 16:
        return False
    return bool(_BASE64_PATTERN.match(stripped)) or bool(_HEX_PATTERN.match(stripped))


def is_text_file(path: str, blocksize: int = 8192, nontext_threshold: float = 0.30, ciphertext_threshold: float = 0.2) -> bool:
    """Return True if *path* looks like a text file.

    Heuristic used:
    - Non-existent or directories -> False
    - Empty files -> True
    - If the sample contains a NUL byte -> False (very likely binary)
    - Count control characters (bytes < 32) excluding common whitespace; if their
      fraction exceeds *nontext_threshold* the file is treated as binary.
    - Check for lines that look like ciphertext (base64/hex); if the fraction exceeds
      *ciphertext_threshold*, treat as non-text (e.g., encrypted payloads in XML).
    - Analyze entropy and letter ratios to catch encoded/encrypted blobs.

    This approach is pragmatic and matches common editor heuristics for distinguishing
    text vs binary files.
    """
    if not os.path.exists(path) or os.path.isdir(path):
        return False

    try:
        with open(path, "rb") as f:
            sample = f.read(blocksize)
    except Exception:
        return False

    if not sample:
        return True

    if b"\x00" in sample:
        return False

    # Count bytes that are control characters (0-31) except common whitespace
    ctrl_count = 0
    for b in sample:
        if b < 32 and b not in (9, 10, 13):
            ctrl_count += 1

    ratio = ctrl_count / len(sample)
    if ratio > nontext_threshold:
        return False

    # Line-by-line ciphertext detection: check for base64/hex patterns
    try:
        sample_text = sample.decode('utf-8', errors='ignore')
        lines = sample_text.split('\n')
        ciphertext_lines = sum(1 for line in lines if _is_ciphertext_line(line))
        if lines:
            ciphertext_ratio = ciphertext_lines / len(lines)
            if ciphertext_ratio >= ciphertext_threshold:
                return False
    except Exception:
        pass

    # Additional heuristics to detect encrypted or unreadable-but-printable data.
    # Compute printable fraction and letter/whitespace fraction.
    printable_count = 0
    letter_or_space_count = 0
    for b in sample:
        if 32 <= b < 127 or b in (9, 10, 13):
            printable_count += 1
        # ASCII letters (A-Z, a-z) and common whitespace
        if (65 <= b <= 90) or (97 <= b <= 122) or b in (32, 9, 10, 13):
            letter_or_space_count += 1

    printable_ratio = printable_count / len(sample)
    letter_ratio = letter_or_space_count / len(sample)

    # Shannon entropy (bits per byte)
    def _shannon_entropy(data: bytes) -> float:
        if not data:
            return 0.0
        counts = Counter(data)
        length = len(data)
        ent = 0.0
        for c in counts.values():
            p = c / length
            ent -= p * math.log2(p)
        return ent

    entropy = _shannon_entropy(sample)

    # Heuristics:
    # - If the sample is mostly printable but entropy is very high, it's likely
    #   encoded/encrypted data (e.g. base64 of ciphertext) and should be rejected.
    # - If the sample is printable but contains few alphabetic characters, it's
    #   probably unreadable text (e.g. hex dumps, encoded blobs) and should be rejected.
    # Lowered entropy threshold to catch common encodings (e.g. base64 of ciphertext)
    if printable_ratio >= 0.9 and entropy > 5.5:
        return False

    if printable_ratio >= 0.8 and letter_ratio < 0.6:
        return False

    return True



def filter_text_files(paths: Iterable[str]) -> Tuple[List[str], List[str]]:
    """Given an iterable of paths, return (accepted, rejected).

    - accepted: list of paths that are likely text files
    - rejected: list of paths that are not text files or could not be opened
    """
    accepted: List[str] = []
    rejected: List[str] = []

    for p in paths:
        if is_text_file(p):
            accepted.append(p)
        else:
            rejected.append(p)

    return accepted, rejected

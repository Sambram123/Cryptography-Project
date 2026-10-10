"""Playfair cipher: pure-Python, standard-library-only implementation.

A 5x5 key matrix is built from a keyword/phrase, combining 'I' and 'J'
into 'I' (25-letter alphabet). Text is split into digraphs (pairs), with
filler characters ('X' or 'Z') inserted between duplicate letters in a pair
and to pad any odd trailing letter.
"""

from __future__ import annotations

import re

ALPHABET = "ABCDEFGHIKLMNOPQRSTUVWXYZ"  # 25 letters; 'J' is omitted and merged into 'I'
GRID_SIZE = 5


def clean_key(key: object) -> str:
    """Normalize and validate a key phrase.

    Converts to uppercase, maps 'J' to 'I', strips non-letters, and removes duplicates
    while preserving the original character order.
    """
    if not isinstance(key, str):
        raise ValueError("Key must be a text string.")
    
    # Keep only ASCII letters, convert to uppercase, replace J with I
    letters = [ch for ch in key.upper() if "A" <= ch <= "Z"]
    if not letters:
        raise ValueError("Key must contain at least one alphabetic letter (A-Z).")
    
    letters = [("I" if ch == "J" else ch) for ch in letters]
    
    seen: set[str] = set()
    deduped: list[str] = []
    for ch in letters:
        if ch not in seen:
            seen.add(ch)
            deduped.append(ch)
    return "".join(deduped)


def generate_key_matrix(key: object) -> list[list[str]]:
    """Generate a 5x5 Playfair key matrix from a key string."""
    deduped_key = clean_key(key)
    used_chars = set(deduped_key)
    
    remaining = [ch for ch in ALPHABET if ch not in used_chars]
    combined = list(deduped_key) + remaining
    
    return [combined[i * GRID_SIZE : (i + 1) * GRID_SIZE] for i in range(GRID_SIZE)]


def get_char_positions(matrix: list[list[str]]) -> dict[str, tuple[int, int]]:
    """Return a mapping from character to (row, col) coordinates."""
    pos: dict[str, tuple[int, int]] = {}
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            pos[matrix[r][c]] = (r, c)
    return pos


def format_matrix(matrix: list[list[str]]) -> str:
    """Format the 5x5 matrix into a clean grid string for display."""
    return "\n".join("  ".join(row) for row in matrix)


def prepare_plaintext(plaintext: object) -> list[str]:
    """Clean plaintext and split into Playfair digraphs (letter pairs).

    Non-alphabet characters are stripped, 'J' is replaced with 'I', duplicate
    letters in a pair are separated by filler character 'X' (or 'Z' if the letter is 'X'),
    and an odd-length text is padded with 'X' (or 'Z').
    """
    if not isinstance(plaintext, str):
        raise ValueError("Input text must be a text string.")
    
    letters = [ch for ch in plaintext.upper() if "A" <= ch <= "Z"]
    if not letters:
        raise ValueError("Input text must contain at least one alphabetic letter (A-Z).")
    
    letters = [("I" if ch == "J" else ch) for ch in letters]
    
    digraphs: list[str] = []
    i = 0
    while i < len(letters):
        c1 = letters[i]
        if i + 1 == len(letters):
            # Odd trailing character: pad with filler
            filler = "Z" if c1 == "X" else "X"
            digraphs.append(c1 + filler)
            i += 1
        elif c1 == letters[i + 1]:
            # Repeated character in same pair: insert filler
            filler = "Z" if c1 == "X" else "X"
            digraphs.append(c1 + filler)
            i += 1
        else:
            digraphs.append(c1 + letters[i + 1])
            i += 2
            
    return digraphs


def prepare_ciphertext(ciphertext: object) -> list[str]:
    """Validate and split ciphertext into digraph pairs.

    Non-alphabet characters (including spaces) are ignored. Ciphertext must contain
    an even number of letters to form valid Playfair digraphs.
    """
    if not isinstance(ciphertext, str):
        raise ValueError("Input ciphertext must be a text string.")
    
    letters = [ch for ch in ciphertext.upper() if "A" <= ch <= "Z"]
    if not letters:
        raise ValueError("Ciphertext must contain at least one alphabetic letter (A-Z).")
    
    letters = [("I" if ch == "J" else ch) for ch in letters]
    
    if len(letters) % 2 != 0:
        raise ValueError(
            f"Ciphertext has {len(letters)} letters, which is odd. "
            "Playfair ciphertext must contain an even number of letters (digraph pairs)."
        )
        
    return ["".join(letters[i : i + 2]) for i in range(0, len(letters), 2)]


def _transform_digraph(
    pair: str,
    matrix: list[list[str]],
    pos: dict[str, tuple[int, int]],
    mode: str,
) -> str:
    """Transform one digraph according to Playfair rules."""
    c1, c2 = pair[0], pair[1]
    r1, c1_col = pos[c1]
    r2, c2_col = pos[c2]
    
    shift = 1 if mode == "encrypt" else -1
    
    if r1 == r2:
        # Same row: shift columns horizontally
        out1 = matrix[r1][(c1_col + shift) % GRID_SIZE]
        out2 = matrix[r2][(c2_col + shift) % GRID_SIZE]
    elif c1_col == c2_col:
        # Same column: shift rows vertically
        out1 = matrix[(r1 + shift) % GRID_SIZE][c1_col]
        out2 = matrix[(r2 + shift) % GRID_SIZE][c2_col]
    else:
        # Rectangle: swap columns
        out1 = matrix[r1][c2_col]
        out2 = matrix[r2][c1_col]
        
    return out1 + out2


def playfair_encrypt(plaintext: str, key: str) -> str:
    """Encrypt plaintext using Playfair cipher with the given key."""
    matrix = generate_key_matrix(key)
    pos = get_char_positions(matrix)
    digraphs = prepare_plaintext(plaintext)
    return "".join(_transform_digraph(d, matrix, pos, "encrypt") for d in digraphs)


def playfair_decrypt(ciphertext: str, key: str) -> str:
    """Decrypt ciphertext using Playfair cipher with the given key."""
    matrix = generate_key_matrix(key)
    pos = get_char_positions(matrix)
    digraphs = prepare_ciphertext(ciphertext)
    return "".join(_transform_digraph(d, matrix, pos, "decrypt") for d in digraphs)


def playfair_process(text: str, key: str, mode: str) -> dict:
    """Run Playfair encryption or decryption and return complete diagnostic details."""
    matrix = generate_key_matrix(key)
    pos = get_char_positions(matrix)
    
    if mode == "encrypt":
        digraphs_in = prepare_plaintext(text)
    elif mode == "decrypt":
        digraphs_in = prepare_ciphertext(text)
    else:
        raise ValueError(f"Unknown mode: {mode}")
        
    digraphs_out = [_transform_digraph(d, matrix, pos, mode) for d in digraphs_in]
    output = "".join(digraphs_out)
    
    return {
        "mode": mode,
        "input_text": text,
        "key": key,
        "cleaned_key": clean_key(key),
        "matrix": matrix,
        "matrix_str": format_matrix(matrix),
        "digraphs_in": digraphs_in,
        "digraphs_out": digraphs_out,
        "formatted_digraphs_in": " ".join(digraphs_in),
        "formatted_digraphs_out": " ".join(digraphs_out),
        "output": output,
    }

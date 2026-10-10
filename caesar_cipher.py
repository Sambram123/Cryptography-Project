"""Caesar cipher: pure-Python, standard-library-only implementation.

Only ASCII letters A-Z and a-z are shifted. Case is preserved, and every other
character (spaces, digits, punctuation, Unicode symbols) passes through unchanged.
"""

from __future__ import annotations

ALPHABET_SIZE = 26


def normalize_shift(shift: object) -> int:
    """Return `shift` as an int, or raise ValueError if it is not a whole number.

    Accepts ints, whole-number floats (3.0) and numeric strings ("-5").
    Booleans are rejected because True/False are almost certainly a mistake.
    """
    if isinstance(shift, bool):
        raise ValueError("Shift key must be a whole number, not True/False.")
    if isinstance(shift, int):
        return shift
    if isinstance(shift, float):
        if shift.is_integer():
            return int(shift)
        raise ValueError("Shift key must be a whole number (no decimals).")
    if isinstance(shift, str):
        try:
            return int(shift.strip())
        except ValueError:
            raise ValueError("Shift key must be a whole number.") from None
    raise ValueError("Shift key must be a whole number.")


def _shift_char(char: str, shift: int) -> str:
    """Shift one character; non-letters are returned unchanged."""
    if "A" <= char <= "Z":
        base = ord("A")
    elif "a" <= char <= "z":
        base = ord("a")
    else:
        return char
    return chr((ord(char) - base + shift) % ALPHABET_SIZE + base)


def _transform(text: str, shift: int) -> str:
    """Apply the shift to every character in `text`."""
    if not isinstance(text, str):
        raise ValueError("Input text must be a string.")
    # Reduce first so very large shifts stay cheap; Python's % is always non-negative here.
    effective_shift = shift % ALPHABET_SIZE
    return "".join(_shift_char(ch, effective_shift) for ch in text)


def caesar_encrypt(plaintext: str, shift: object) -> str:
    """Encrypt `plaintext` by moving each letter `shift` places forward."""
    return _transform(plaintext, normalize_shift(shift))


def caesar_decrypt(ciphertext: str, shift: object) -> str:
    """Decrypt `ciphertext` by moving each letter `shift` places backward."""
    return _transform(ciphertext, -normalize_shift(shift))

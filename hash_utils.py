# hash_utils.py

import hashlib
import struct


# ============================================================
# RIPEMD-256 — Pure Python Implementation
# Ref: https://homes.esat.kuleuven.be/~bosselae/ripemd160.html
# ============================================================

def _ripemd256(message: bytes) -> bytes:
    """Pure Python RIPEMD-256 implementation."""

    # --- constants ---
    KL = [0x00000000, 0x5A827999, 0x6ED9EBA1, 0x8F1BBCDC]
    KR = [0x50A28BE6, 0x5C4DD124, 0x6D703EF3, 0x00000000]

    # --- boolean functions ---
    def f(j, x, y, z):
        if   j < 16: return x ^ y ^ z
        elif j < 32: return (x & y) | (~x & z)
        elif j < 48: return (x | ~y) ^ z
        else:        return (x & z) | (y & ~z)

    # --- message schedule (left and right) ---
    RL = [
         0,  1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11, 12, 13, 14, 15,
         7,  4, 13,  1, 10,  6, 15,  3, 12,  0,  9,  5,  2, 14, 11,  8,
         3, 10, 14,  4,  9, 15,  8,  1,  2,  7,  0,  6, 13, 11,  5, 12,
         1,  9, 11, 10,  0,  8, 12,  4, 13,  3,  7, 15, 14,  5,  6,  2,
    ]
    RR = [
         5, 14,  7,  0,  9,  2, 11,  4, 13,  6, 15,  8,  1, 10,  3, 12,
         6, 11,  3,  7,  0, 13,  5, 10, 14, 15,  8, 12,  4,  9,  1,  2,
        15,  5,  1,  3,  7, 14,  6,  9, 11,  8, 12,  2, 10,  0,  4, 13,
         8,  6,  4,  1,  3, 11, 15,  0,  5, 12,  2, 13,  9,  7, 10, 14,
    ]

    # --- rotation amounts ---
    SL = [
        11, 14, 15, 12,  5,  8,  7,  9, 11, 13, 14, 15,  6,  7,  9,  8,
         7,  6,  8, 13, 11,  9,  7, 15,  7, 12, 15,  9, 11,  7, 13, 12,
        11, 13,  6,  7, 14,  9, 13, 15, 14,  8, 13,  6,  5, 12,  7,  5,
        11, 12, 14, 15, 14, 15,  9,  8,  9, 14,  5,  6,  8,  6,  5, 12,
    ]
    SR = [
         8,  9,  9, 11, 13, 15, 15,  5,  7,  7,  8, 11, 14, 14, 12,  6,
         9, 13, 15,  7, 12,  8,  9, 11,  7,  7, 12,  7,  6, 15, 13, 11,
         9,  7, 15, 11,  8,  6,  6, 14, 12, 13,  5, 14, 13, 13,  7,  5,
        15,  5,  8, 11, 14, 14,  6, 14,  6,  9, 12,  9, 12,  5, 15,  8,
    ]

    MASK = 0xFFFFFFFF

    def rol32(x, n):
        return ((x << n) | (x >> (32 - n))) & MASK

    # --- pre-processing ---
    msg = bytearray(message)
    orig_len = len(message) * 8
    msg.append(0x80)
    while len(msg) % 64 != 56:
        msg.append(0x00)
    msg += struct.pack('<Q', orig_len)

    # --- initial hash values ---
    h0, h1, h2, h3 = 0x67452301, 0xEFCDAB89, 0x98BADCFE, 0x10325476
    h4, h5, h6, h7 = 0x76543210, 0xFEDCBA98, 0x89ABCDEF, 0x01234567

    # --- process each 512-bit block ---
    for i in range(0, len(msg), 64):
        block = msg[i:i+64]
        X = list(struct.unpack('<16I', block))

        al, bl, cl, dl = h0, h1, h2, h3
        ar, br, cr, dr = h4, h5, h6, h7

        for j in range(64):
            fj = f(j, bl, cl, dl)
            T = rol32((al + fj + X[RL[j]] + KL[j // 16]) & MASK, SL[j])
            al, bl, cl, dl = dl, T, bl, cl

            fj = f(63 - j, br, cr, dr)
            T = rol32((ar + fj + X[RR[j]] + KR[j // 16]) & MASK, SR[j])
            ar, br, cr, dr = dr, T, br, cr

            # swap at round boundaries
            if j == 15:  al, ar = ar, al
            elif j == 31: bl, br = br, bl
            elif j == 47: cl, cr = cr, cl
            elif j == 63: dl, dr = dr, dl

        h0 = (h0 + al) & MASK
        h1 = (h1 + bl) & MASK
        h2 = (h2 + cl) & MASK
        h3 = (h3 + dl) & MASK
        h4 = (h4 + ar) & MASK
        h5 = (h5 + br) & MASK
        h6 = (h6 + cr) & MASK
        h7 = (h7 + dr) & MASK

    return struct.pack('<8I', h0, h1, h2, h3, h4, h5, h6, h7)


def _verify_ripemd256():
    """Verify against known test vectors."""
    # RIPEMD-256("") = 02ba4c4e5f8ecd1877fc52d64d30e37a2d9774fb1e5d026380ae0168e3c5522d
    expected = "02ba4c4e5f8ecd1877fc52d64d30e37a2d9774fb1e5d026380ae0168e3c5522d"
    result = _ripemd256(b"").hex()
    assert result == expected, f"RIPEMD-256 self-test FAILED:\n  got:      {result}\n  expected: {expected}"


_verify_ripemd256()


# ============================================================
# PUBLIC API
# ============================================================

def sha256_hash(message: bytes) -> int:
    digest = hashlib.sha256(message).digest()
    return int.from_bytes(digest, byteorder="big")


def sha384_hash(message: bytes) -> int:
    digest = hashlib.sha384(message).digest()
    return int.from_bytes(digest, byteorder="big")


def ripemd256_hash(message: bytes) -> int:
    digest = _ripemd256(message)
    return int.from_bytes(digest, byteorder="big")

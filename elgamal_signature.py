# elgamal_signature.py

import secrets
import math

# ============================================================
# PRIME GENERATION (Miller-Rabin)
# ============================================================

def is_probable_prime(n, k=40):
    if n < 2:
        return False

    small_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]

    for p in small_primes:
        if n % p == 0:
            return n == p

    r = 0
    d = n - 1

    while d % 2 == 0:
        r += 1
        d //= 2

    for _ in range(k):
        a = secrets.randbelow(n - 3) + 2

        x = pow(a, d, n)

        if x == 1 or x == n - 1:
            continue

        for _ in range(r - 1):
            x = pow(x, 2, n)

            if x == n - 1:
                break
        else:
            return False

    return True


def generate_prime(bits):
    while True:
        candidate = secrets.randbits(bits)

        # force odd
        candidate |= 1

        # force exact bit length
        candidate |= (1 << (bits - 1))

        if is_probable_prime(candidate):
            return candidate


# ============================================================
# MODULAR INVERSE
# ============================================================

def mod_inverse(a, m):
    return pow(a, -1, m)


# ============================================================
# KEY GENERATION
# ============================================================

def generate_keys(bits=512):
    """
    Returns:
        public_key  = (p, g, y)
        private_key = x
    """

    p = generate_prime(bits)

    g = secrets.randbelow(p - 3) + 2

    x = secrets.randbelow(p - 2) + 1

    y = pow(g, x, p)

    public_key = (p, g, y)

    return public_key, x


# ============================================================
# SIGNATURE
# ============================================================

def sign(message_hash: int, private_key: int, public_key):
    """
    ElGamal Signature

    Returns:
        (r, s)
    """

    p, g, y = public_key
    x = private_key

    while True:

        k = secrets.randbelow(p - 2) + 1

        if math.gcd(k, p - 1) == 1:
            break

    r = pow(g, k, p)

    k_inv = mod_inverse(k, p - 1)

    s = ((message_hash - x * r) * k_inv) % (p - 1)

    return (r, s)


# ============================================================
# VERIFICATION
# ============================================================

def verify(message_hash: int, signature, public_key):
    """
    Returns:
        True / False
    """

    p, g, y = public_key

    r, s = signature

    if not (0 < r < p):
        return False

    left = pow(g, message_hash, p)

    right = (
        pow(y, r, p) *
        pow(r, s, p)
    ) % p

    return left == right


# ============================================================
# SIMPLE SELF TEST
# ============================================================

if __name__ == "__main__":

    print("Generating keys...")

    public_key, private_key = generate_keys(bits=512)

    message_hash = 123456789

    signature = sign(
        message_hash,
        private_key,
        public_key
    )

    result = verify(
        message_hash,
        signature,
        public_key
    )

    print("Public Key:")
    print(public_key)

    print("\nSignature:")
    print(signature)

    print("\nValid:", result)
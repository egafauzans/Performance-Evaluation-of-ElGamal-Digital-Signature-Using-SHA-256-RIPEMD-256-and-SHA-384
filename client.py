# client.py

import socket
import pickle
import time

from elgamal_signature import (
    generate_keys,
    sign
)

from hash_utils import (
    sha256_hash,
    sha384_hash,
    ripemd256_hash
)

from config import HOST, PORT


def compute_hash(message, hash_algo):

    if hash_algo == "SHA256":
        return sha256_hash(message)

    elif hash_algo == "RIPEMD256":
        return ripemd256_hash(message)

    elif hash_algo == "SHA384":
        return sha384_hash(message)

    else:
        raise ValueError(
            f"Unsupported hash: {hash_algo}"
        )


def generate_message(size):

    return b"A" * size


def run_client(
    message_size,
    key_size,
    hash_algo
):

    message = generate_message(
        message_size
    )

    public_key, private_key = (
        generate_keys(key_size)
    )

    message_hash = compute_hash(
        message,
        hash_algo
    )

    # ===================================
    # SIGN DELAY
    # ===================================

    start_sign = time.perf_counter()

    signature = sign(
        message_hash,
        private_key,
        public_key
    )

    sign_delay_ms = (
        time.perf_counter()
        - start_sign
    ) * 1000

    packet = {
        "message": message,
        "signature": signature,
        "public_key": public_key,
        "hash_algo": hash_algo
    }

    client_socket = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    client_socket.connect(
        (HOST, PORT)
    )

    # ===================================
    # TRANSMISSION DELAY
    # ===================================

    start_tx = time.perf_counter()

    client_socket.sendall(
        pickle.dumps(packet)
    )

    data = client_socket.recv(
        4096
    )

    transmission_delay_ms = (
        time.perf_counter()
        - start_tx
    ) * 1000

    client_socket.close()

    response = pickle.loads(data)

    return {
        "sign_delay_ms":
            sign_delay_ms,

        "verify_delay_ms":
            response[
                "verify_delay_ms"
            ],

        "transmission_delay_ms":
            transmission_delay_ms,

        "valid":
            response["valid"]
    }


if __name__ == "__main__":

    result = run_client(
        message_size=100,
        key_size=512,
        hash_algo="SHA256"
    )

    print(result)